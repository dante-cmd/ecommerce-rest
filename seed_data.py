from __future__ import annotations

import argparse
import random
from decimal import Decimal

from faker import Faker
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage, Review, Tag, User
from app.models.enums import OrderStatus, UserRole


fake = Faker()


def seed(force: bool = False) -> None:
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

        users: list[User] = []
        for i in range(50):
            role = random.choices([UserRole.customer, UserRole.seller, UserRole.admin], weights=[80, 15, 5])[0]
            user = User(
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                hashed_password=get_password_hash("Password123!"),
                full_name=fake.name(),
                role=role,
                is_active=True,
            )
            db.add(user)
            users.append(user)
        db.flush()

        categories: list[Category] = []
        for _ in range(20):
            category = Category(name=fake.unique.word().title(), description=fake.sentence())
            db.add(category)
            categories.append(category)
        db.flush()

        tags: list[Tag] = []
        for _ in range(20):
            tag = Tag(name=fake.unique.word())
            db.add(tag)
            tags.append(tag)
        db.flush()

        sellers = [u for u in users if u.role in {UserRole.seller, UserRole.admin}]
        products: list[Product] = []
        for _ in range(200):
            seller = random.choice(sellers)
            category = random.choice(categories)
            product = Product(
                name=fake.sentence(nb_words=3),
                description=fake.paragraph(),
                price=Decimal(str(round(random.uniform(5, 500), 2))),
                stock=random.randint(0, 200),
                sku=fake.unique.bothify(text="SKU-####-????"),
                seller_id=seller.id,
                category_id=category.id,
            )
            product.tags = random.sample(tags, k=random.randint(1, 4))
            product.images = [ProductImage(url=fake.image_url()) for _ in range(random.randint(1, 3))]
            db.add(product)
            products.append(product)
        db.flush()

        customers = [u for u in users if u.role == UserRole.customer]
        carts: list[Cart] = []
        for customer in customers:
            cart = Cart(user_id=customer.id)
            db.add(cart)
            carts.append(cart)
        db.flush()

        for _ in range(100):
            cart = random.choice(carts)
            product = random.choice(products)
            item = CartItem(cart_id=cart.id, product_id=product.id, quantity=random.randint(1, 3))
            db.add(item)
        db.flush()

        orders: list[Order] = []
        for _ in range(50):
            customer = random.choice(customers)
            order = Order(user_id=customer.id, status=random.choice(list(OrderStatus)))
            db.add(order)
            db.flush()
            total = Decimal("0.0")
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                qty = random.randint(1, 3)
                line_total = product.price * qty
                total += line_total
                db.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=qty,
                        unit_price=product.price,
                        total_price=line_total,
                    )
                )
            order.total_amount = total
            orders.append(order)
        db.flush()

        delivered_orders = [o for o in orders if o.status == OrderStatus.delivered]
        for order in delivered_orders:
            for item in order.items:
                if random.random() < 0.6:
                    review = Review(
                        user_id=order.user_id,
                        product_id=item.product_id,
                        rating=random.randint(3, 5),
                        comment=fake.sentence(),
                    )
                    db.add(review)
        db.commit()
        print("Seed data created.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Reseed data by clearing tables first")
    args = parser.parse_args()
    seed(force=args.force)
