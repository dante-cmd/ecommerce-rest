from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.review import Review


class ReviewCRUD(CRUDBase[Review]):
    def get_by_user_product(self, db: Session, user_id: int, product_id: int) -> Review | None:
        return db.query(Review).filter(Review.user_id == user_id, Review.product_id == product_id).first()


review_crud = ReviewCRUD(Review)
