from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User


class UserCRUD(CRUDBase[User]):
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()


user_crud = UserCRUD(User)
