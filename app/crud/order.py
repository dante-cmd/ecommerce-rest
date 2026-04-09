from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order


class OrderCRUD(CRUDBase[Order]):
    def list_by_user(self, db: Session, user_id: int, *, skip: int = 0, limit: int = 50) -> tuple[list[Order], int]:
        q = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc())
        total = q.count()
        items = q.offset(skip).limit(limit).all()
        return items, total


order_crud = OrderCRUD(Order)
