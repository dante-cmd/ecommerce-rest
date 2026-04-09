from __future__ import annotations

from app.core.security import get_password_hash
from app.models.category import Category
from app.models.enums import UserRole
from app.models.product import Product
from app.models.user import User


def test_order_create(client, db_session):
    category = Category(name="Cat1", description="Test")
    buyer = User(email="buyer@test.com", username="buyer1", hashed_password=get_password_hash("Password123!"))
    seller = User(email="seller@test.com", username="seller1", hashed_password=get_password_hash("Password123!"), role=UserRole.seller)
    db_session.add_all([category, buyer, seller])
    db_session.commit()
    product = Product(
        name="Prod1",
        description="Desc",
        price=10,
        stock=100,
        sku="SKU-1",
        seller_id=seller.id,
        category_id=category.id,
    )
    db_session.add(product)
    db_session.commit()

    token = client.post("/api/v1/auth/login", data={"username": "buyer1", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/v1/cart/items", json={"product_id": product.id, "quantity": 1}, headers=headers)
    r = client.post("/api/v1/orders/", headers=headers)
    assert r.status_code == 201
