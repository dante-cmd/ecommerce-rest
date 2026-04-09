from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.crud.order import order_crud
from app.crud.product import product_crud
from app.models.cart import Cart
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem


class OrderService:
    def create_from_cart(self, db: Session, cart: Cart, user_id: int) -> Order:
        if not cart.items:
            raise BadRequestException("Cart is empty")

        order = Order(user_id=user_id, status=OrderStatus.pending)
        db.add(order)
        db.flush()

        total = Decimal("0.0")
        for item in cart.items:
            product = product_crud.get(db, item.product_id)
            if not product or product.is_deleted:
                raise NotFoundException("Product not found")
            if product.stock < item.quantity:
                raise BadRequestException("Insufficient stock for product")
            product.stock -= item.quantity
            line_total = product.price * item.quantity
            total += line_total
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=line_total,
            )
            db.add(order_item)
        order.total_amount = total

        for item in list(cart.items):
            db.delete(item)
        db.flush()
        return order

    def cancel_order(self, db: Session, order: Order) -> Order:
        if order.status not in {OrderStatus.pending, OrderStatus.confirmed}:
            raise BadRequestException("Order cannot be cancelled")
        order.status = OrderStatus.cancelled
        for item in order.items:
            product = product_crud.get(db, item.product_id)
            if product:
                product.stock += item.quantity
        db.flush()
        return order


order_service = OrderService()
