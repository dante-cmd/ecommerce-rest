from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema


class Token(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseSchema):
    refresh_token: str


class TokenPayload(BaseSchema):
    sub: str
    role: str


class LoginRequest(BaseSchema):
    username: str
    password: str

    model_config = {"json_schema_extra": {"examples": [{"username": "demo_user", "password": "Password123!"}]}}


class RegisterRequest(BaseSchema):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "demo@example.com",
                    "username": "demo_user",
                    "password": "Password123!",
                    "full_name": "Demo User",
                }
            ]
        }
    }
