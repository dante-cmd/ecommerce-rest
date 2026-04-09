from __future__ import annotations

from app.core.security import get_password_hash
from app.models.enums import UserRole
from app.models.user import User


def test_admin_dashboard(client, db_session):
    admin = User(email="admin@test.com", username="admin1", hashed_password=get_password_hash("Password123!"), role=UserRole.admin)
    db_session.add(admin)
    db_session.commit()

    token = client.post("/api/v1/auth/login", data={"username": "admin1", "password": "Password123!"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/admin/dashboard", headers=headers)
    assert r.status_code == 200
