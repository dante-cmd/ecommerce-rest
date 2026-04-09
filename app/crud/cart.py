from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cart import Cart, CartItem


class CartCRUD(CRUDBase[Cart]):
    def get_by_user(self, db: Session, user_id: int) -> Cart | None:
        return db.query(Cart).filter(Cart.user_id == user_id).first()

    def get_by_guest(self, db: Session, guest_id: str) -> Cart | None:
        return db.query(Cart).filter(Cart.guest_id == guest_id).first()

    def get_item(self, db: Session, cart_id: int, product_id: int) -> CartItem | None:
        return (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )


cart_crud = CartCRUD(Cart)
