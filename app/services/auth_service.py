from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.crud.user import user_crud
from app.models.user import User


class AuthService:
    def register_user(self, db: Session, *, email: str, username: str, password: str, full_name: str | None) -> User:
        hashed = get_password_hash(password)
        user = User(email=email, username=username, hashed_password=hashed, full_name=full_name)
        return user_crud.create(db, user)

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = user_crud.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user: User) -> dict[str, str]:
        return {
            "access_token": create_access_token(user.username, user.role),
            "refresh_token": create_refresh_token(user.username, user.role),
            "token_type": "bearer",
        }


auth_service = AuthService()
