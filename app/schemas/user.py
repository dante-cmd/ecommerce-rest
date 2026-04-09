from __future__ import annotations

from pydantic import EmailStr, Field

from app.models.enums import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: str
    full_name: str | None = None
    role: UserRole
    is_active: bool


class UserCreate(BaseSchema):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None
    role: UserRole = UserRole.customer


class UserUpdate(BaseSchema):
    full_name: str | None = None


class UserPasswordChange(BaseSchema):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    id: int
