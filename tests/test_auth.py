from __future__ import annotations

def test_register_and_login(client):
    payload = {
        "email": "user@example.com",
        "username": "user1",
        "password": "Password123!",
        "full_name": "User One",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201

    r = client.post("/api/v1/auth/login", data={"username": "user1", "password": "Password123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()
