from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from decimal import Decimal

import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler
from faker import Faker
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage, Review, Tag, User
from app.models.enums import OrderStatus, UserRole
from app.services.cart_service import cart_service
from app.services.order_service import order_service
from app.services.review_service import review_service


fake = Faker()

STATES = [
    "HOMEPAGE_BROWSE",
    "PRODUCT_LIST",
    "PRODUCT_DETAIL",
    "ADD_TO_CART",
    "VIEW_CART",
    "PROCEED_CHECKOUT",
    "PURCHASE",
    "ABANDON",
    "POST_PURCHASE_REVIEW",
]

STATE_INDEX = {state: idx for idx, state in enumerate(STATES)}

ABSORBING_STATES = {"PURCHASE", "ABANDON", "POST_PURCHASE_REVIEW"}


def _normalize_row(row: np.ndarray) -> np.ndarray:
    total = row.sum()
    if total <= 0:
        raise ValueError("Row total must be > 0")
    return row / total


def build_base_matrix() -> np.ndarray:
    """
    Base transition matrix informed by e-commerce funnel benchmarks.
    Sources (2024-2026 benchmarks):
    - Cart abandonment ~70.2% (Baymard Institute):
      https://baymard.com/lists/cart-abandonment-rate
    - Add-to-cart rate ~6-8% (industry benchmarks, 2024-2025):
      https://www.opensend.com/post/add-to-cart-rate-statistics-ecommerce
    - Overall conversion rate ~2-3% (industry benchmarks, 2025):
      https://redstagfulfillment.com/average-conversion-rate-for-ecommerce/
    Checkout/step-through rates are calibrated to be consistent with the above stats.
    """
    P = np.zeros((9, 9), dtype=float)

    # HOMEPAGE_BROWSE
    P[STATE_INDEX["HOMEPAGE_BROWSE"]] = _normalize_row(
        np.array([0.10, 0.45, 0.15, 0.00, 0.00, 0.00, 0.00, 0.30, 0.00])
    )

    # PRODUCT_LIST
    P[STATE_INDEX["PRODUCT_LIST"]] = _normalize_row(
        np.array([0.05, 0.20, 0.40, 0.05, 0.00, 0.00, 0.00, 0.30, 0.00])
    )

    # PRODUCT_DETAIL (target add-to-cart ~6-8%)
    P[STATE_INDEX["PRODUCT_DETAIL"]] = _normalize_row(
        np.array([0.05, 0.35, 0.20, 0.07, 0.00, 0.00, 0.00, 0.33, 0.00])
    )

    # ADD_TO_CART (cart-to-checkout ~40-50% with abandonment pressure)
    P[STATE_INDEX["ADD_TO_CART"]] = _normalize_row(
        np.array([0.00, 0.10, 0.15, 0.00, 0.45, 0.00, 0.00, 0.30, 0.00])
    )

    # VIEW_CART
    P[STATE_INDEX["VIEW_CART"]] = _normalize_row(
        np.array([0.00, 0.10, 0.00, 0.05, 0.00, 0.50, 0.00, 0.35, 0.00])
    )

    # PROCEED_CHECKOUT (checkout completion ~55-60%)
    P[STATE_INDEX["PROCEED_CHECKOUT"]] = _normalize_row(
        np.array([0.00, 0.00, 0.00, 0.00, 0.07, 0.00, 0.58, 0.35, 0.00])
    )

    # PURCHASE (absorbing for commerce; optional review transition)
    P[STATE_INDEX["PURCHASE"]] = _normalize_row(
        np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.85, 0.00, 0.15])
    )

    # ABANDON (absorbing)
    P[STATE_INDEX["ABANDON"]] = _normalize_row(
        np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00])
    )

    # POST_PURCHASE_REVIEW (absorbing)
    P[STATE_INDEX["POST_PURCHASE_REVIEW"]] = _normalize_row(
        np.array([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00])
    )

    return P


def apply_persona(base: np.ndarray, persona: str) -> np.ndarray:
    matrix = base.copy()

    if persona == "impulse":
        tweaks = {
            ("PRODUCT_DETAIL", "ADD_TO_CART"): 1.35,
            ("ADD_TO_CART", "VIEW_CART"): 1.20,
            ("VIEW_CART", "PROCEED_CHECKOUT"): 1.15,
            ("PROCEED_CHECKOUT", "PURCHASE"): 1.10,
            ("HOMEPAGE_BROWSE", "ABANDON"): 0.75,
            ("PRODUCT_LIST", "ABANDON"): 0.80,
        }
    elif persona == "researcher":
        tweaks = {
            ("PRODUCT_DETAIL", "ADD_TO_CART"): 0.75,
            ("PRODUCT_DETAIL", "PRODUCT_LIST"): 1.25,
            ("PRODUCT_LIST", "PRODUCT_DETAIL"): 1.20,
            ("ADD_TO_CART", "VIEW_CART"): 0.85,
            ("PROCEED_CHECKOUT", "PURCHASE"): 0.90,
        }
    else:  # window-shopper
        tweaks = {
            ("HOMEPAGE_BROWSE", "ABANDON"): 1.35,
            ("PRODUCT_LIST", "ABANDON"): 1.30,
            ("PRODUCT_DETAIL", "ABANDON"): 1.20,
            ("PRODUCT_DETAIL", "ADD_TO_CART"): 0.65,
        }

    for (src, dst), factor in tweaks.items():
        src_idx = STATE_INDEX[src]
        dst_idx = STATE_INDEX[dst]
        matrix[src_idx][dst_idx] *= factor
        matrix[src_idx] = _normalize_row(matrix[src_idx])

    return matrix


def absorption_probabilities(P: np.ndarray) -> Dict[str, float]:
    absorbing = [STATE_INDEX[s] for s in ["PURCHASE", "ABANDON", "POST_PURCHASE_REVIEW"]]
    transient = [i for i in range(len(STATES)) if i not in absorbing]

    Q = P[np.ix_(transient, transient)]
    R = P[np.ix_(transient, absorbing)]
    I = np.eye(Q.shape[0])
    N = np.linalg.inv(I - Q)
    B = N @ R

    start_idx = transient.index(STATE_INDEX["HOMEPAGE_BROWSE"])
    purchase_prob = B[start_idx][absorbing.index(STATE_INDEX["PURCHASE"])]
    abandon_prob = B[start_idx][absorbing.index(STATE_INDEX["ABANDON"])]
    review_prob = B[start_idx][absorbing.index(STATE_INDEX["POST_PURCHASE_REVIEW"])]

    return {
        "purchase": float(purchase_prob + review_prob),
        "abandon": float(abandon_prob),
        "review": float(review_prob),
    }


def simulate_session(rng: np.random.Generator, matrix: np.ndarray, max_steps: int = 50) -> List[str]:
    state = "HOMEPAGE_BROWSE"
    trajectory = [state]
    for _ in range(max_steps):
        if state in ABSORBING_STATES:
            break
        probs = matrix[STATE_INDEX[state]]
        next_state = rng.choice(STATES, p=probs)
        trajectory.append(next_state)
        state = next_state
        if state in ABSORBING_STATES:
            break
    return trajectory


def random_delay_seconds(state: str) -> int:
    means = {
        "HOMEPAGE_BROWSE": 25,
        "PRODUCT_LIST": 35,
        "PRODUCT_DETAIL": 55,
        "ADD_TO_CART": 15,
        "VIEW_CART": 20,
        "PROCEED_CHECKOUT": 60,
        "PURCHASE": 15,
        "ABANDON": 5,
        "POST_PURCHASE_REVIEW": 120,
    }
    mu = means.get(state, 20)
    return max(3, int(random.lognormvariate(3.0, 0.5) % (mu * 3)))


def ensure_seed_data(db, users_count: int, categories_count: int, products_count: int) -> dict:
    users = []
    for _ in range(users_count):
        role = random.choices([UserRole.customer, UserRole.seller, UserRole.admin], weights=[80, 15, 5])[0]
        users.append(
            User(
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                hashed_password=get_password_hash("Password123!"),
                full_name=fake.name(),
                role=role,
                is_active=True,
            )
        )
    db.add_all(users)
    db.flush()

    categories = []
    for _ in range(categories_count):
        categories.append(Category(name=fake.unique.word().title(), description=fake.sentence()))
    db.add_all(categories)
    db.flush()

    tags = []
    for _ in range(25):
        tags.append(Tag(name=fake.unique.word()))
    db.add_all(tags)
    db.flush()

    sellers = [u for u in users if u.role in {UserRole.seller, UserRole.admin}]
    products = []
    for _ in range(products_count):
        seller = random.choice(sellers)
        category = random.choice(categories)
        product = Product(
            name=fake.sentence(nb_words=3),
            description=fake.paragraph(),
            price=Decimal(str(round(random.uniform(5, 500), 2))),
            stock=random.randint(5, 300),
            sku=fake.unique.bothify(text="SKU-####-????"),
            seller_id=seller.id,
            category_id=category.id,
        )
        product.tags = random.sample(tags, k=random.randint(1, 4))
        product.images = [ProductImage(url=fake.image_url()) for _ in range(random.randint(1, 3))]
        products.append(product)
    db.add_all(products)
    db.flush()

    customers = [u for u in users if u.role == UserRole.customer]
    return {"users": users, "customers": customers, "categories": categories, "products": products}


def seed(force: bool, sessions: int, users_count: int, categories_count: int, products_count: int) -> None:
    rng = np.random.default_rng()
    base_matrix = build_base_matrix()
    persona_matrices = {
        "impulse": apply_persona(base_matrix, "impulse"),
        "researcher": apply_persona(base_matrix, "researcher"),
        "window": apply_persona(base_matrix, "window"),
    }

    db = SessionLocal()
    try:
        existing = db.query(User).count()
        if existing > 0 and not force:
            print("Seed data already exists. Use --force to reseed.")
            return

        if force:
            for model in [Review, OrderItem, Order, CartItem, Cart, ProductImage, Product, Tag, Category, User]:
                db.execute(delete(model))
            db.commit()

        data = ensure_seed_data(db, users_count, categories_count, products_count)
        customers: List[User] = data["customers"]
        products: List[Product] = data["products"]

        persona_weights = [0.30, 0.40, 0.30]
        personas = ["impulse", "researcher", "window"]
        persona_by_user = {u.id: random.choices(personas, weights=persona_weights)[0] for u in customers}

        summary = {"purchase": 0, "abandon": 0, "review": 0}
        for _ in range(sessions):
            user = random.choice(customers)
            persona = persona_by_user[user.id]
            matrix = persona_matrices[persona]

            is_guest = random.random() < 0.20
            guest_cart = cart_service.create_guest_cart(db) if is_guest else None
            user_cart = cart_service.get_or_create_cart(db, user.id)

            trajectory = simulate_session(rng, matrix)
            current_time = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            last_product: Product | None = None

            for state in trajectory:
                current_time += timedelta(seconds=random_delay_seconds(state))

                if state in {"PRODUCT_LIST", "PRODUCT_DETAIL"}:
                    last_product = random.choice(products)

                if state == "ADD_TO_CART":
                    product = last_product or random.choice(products)
                    target_cart = guest_cart or user_cart
                    cart_service.add_item(db, target_cart, product.id, quantity=random.randint(1, 2))

                if state == "PROCEED_CHECKOUT":
                    if guest_cart:
                        cart_service.merge_guest_cart(db, guest_cart, user_cart)
                        guest_cart = None

                if state == "PURCHASE":
                    if not user_cart.items and last_product:
                        cart_service.add_item(db, user_cart, last_product.id, quantity=1)
                    if user_cart.items:
                        order = order_service.create_from_cart(db, user_cart, user.id)
                        order.created_at = current_time
                        order.status = random.choices(
                            [OrderStatus.confirmed, OrderStatus.shipped, OrderStatus.delivered],
                            weights=[0.5, 0.3, 0.2],
                        )[0]
                        db.flush()
                        summary["purchase"] += 1

                if state == "ABANDON":
                    summary["abandon"] += 1

                if state == "POST_PURCHASE_REVIEW":
                    if user.orders:
                        order = random.choice(user.orders)
                        for item in order.items:
                            if random.random() < 0.5:
                                review = Review(
                                    user_id=user.id,
                                    product_id=item.product_id,
                                    rating=random.randint(3, 5),
                                    comment=fake.sentence(),
                                )
                                review.created_at = current_time + timedelta(days=random.randint(1, 7))
                                db.add(review)
                                review_service.update_product_rating(db, item.product_id)
                                summary["review"] += 1

            db.flush()

        db.commit()

        print("MCMC seed complete.")
        print("Absorption probabilities (base matrix):", absorption_probabilities(base_matrix))
        print("Sessions:", sessions, "Purchases:", summary["purchase"], "Abandons:", summary["abandon"])
    finally:
        db.close()


def run_scheduler(args) -> None:
    scheduler = BlockingScheduler()
    scheduler.add_job(
        seed,
        "interval",
        minutes=args.interval_minutes,
        args=[args.force, args.sessions, args.users, args.categories, args.products],
        next_run_time=datetime.now(timezone.utc),
    )
    print(f"Scheduler started. Seeding every {args.interval_minutes} minute(s).")
    scheduler.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Reseed data by clearing tables first")
    parser.add_argument("--sessions", type=int, default=5000, help="Number of simulated sessions")
    parser.add_argument("--users", type=int, default=80, help="Number of users")
    parser.add_argument("--categories", type=int, default=20, help="Number of categories")
    parser.add_argument("--products", type=int, default=250, help="Number of products")
    parser.add_argument("--interval-minutes", type=int, default=0, help="Run on a schedule (minutes)")
    args = parser.parse_args()

    if args.interval_minutes > 0:
        run_scheduler(args)
    else:
        seed(args.force, args.sessions, args.users, args.categories, args.products)
