from __future__ import annotations

from app.core.security import get_password_hash
from app.models.category import Category
from app.models.enums import UserRole
from app.models.user import User


def test_list_products_empty(client, db_session):
    category = Category(name="Cat1", description="Test")
    db_session.add(category)
    user = User(email="seller@test.com", username="seller1", hashed_password=get_password_hash("Password123!"), role=UserRole.seller)
    db_session.add(user)
    db_session.commit()

    r = client.get("/api/v1/products/")
    assert r.status_code == 200
    assert r.json()["items"] == []
