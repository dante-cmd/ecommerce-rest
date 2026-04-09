from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.crud.cart import cart_crud
from app.crud.product import product_crud
import uuid

from app.models.cart import Cart, CartItem


class CartService:
    def get_or_create_cart(self, db: Session, user_id: int) -> Cart:
        cart = cart_crud.get_by_user(db, user_id)
        if cart:
            return cart
        cart = Cart(user_id=user_id)
        return cart_crud.create(db, cart)

    def create_guest_cart(self, db: Session) -> Cart:
        cart = Cart(guest_id=str(uuid.uuid4()))
        return cart_crud.create(db, cart)

    def get_guest_cart(self, db: Session, guest_id: str) -> Cart | None:
        return cart_crud.get_by_guest(db, guest_id)

    def merge_guest_cart(self, db: Session, guest_cart: Cart, user_cart: Cart) -> Cart:
        for item in guest_cart.items:
            existing = cart_crud.get_item(db, user_cart.id, item.product_id)
            if existing:
                existing.quantity += item.quantity
            else:
                db.add(CartItem(cart_id=user_cart.id, product_id=item.product_id, quantity=item.quantity))
        db.flush()
        db.delete(guest_cart)
        return user_cart

    def add_item(self, db: Session, cart: Cart, product_id: int, quantity: int) -> CartItem:
        product = product_crud.get(db, product_id)
        if not product or product.is_deleted:
            raise NotFoundException("Product not found")
        item = cart_crud.get_item(db, cart.id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.add(item)
        db.flush()
        return item

    def update_item(self, db: Session, cart: Cart, product_id: int, quantity: int) -> CartItem:
        item = cart_crud.get_item(db, cart.id, product_id)
        if not item:
            raise NotFoundException("Cart item not found")
        item.quantity = quantity
        db.flush()
        return item

    def remove_item(self, db: Session, cart: Cart, product_id: int) -> None:
        item = cart_crud.get_item(db, cart.id, product_id)
        if not item:
            raise NotFoundException("Cart item not found")
        db.delete(item)

    def totals(self, cart: Cart) -> Decimal:
        total = Decimal("0.0")
        for item in cart.items:
            total += item.product.price * item.quantity
        return total


cart_service = CartService()
