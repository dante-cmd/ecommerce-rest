from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.category import Category


class CategoryCRUD(CRUDBase[Category]):
    def get_by_name(self, db: Session, name: str) -> Category | None:
        return db.query(Category).filter(Category.name == name).first()


category_crud = CategoryCRUD(Category)
