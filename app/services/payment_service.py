from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.enums import OrderStatus
from app.models.order import Order


class PaymentService:
    def create_payment(self, db: Session, order: Order) -> dict:
        reference = f"PAY-{uuid.uuid4()}"
        order.payment_reference = reference
        order.status = OrderStatus.confirmed
        db.flush()
        return {"payment_reference": reference, "status": "confirmed"}

    def process_webhook(self, db: Session, reference: str, success: bool) -> None:
        order = db.query(Order).filter(Order.payment_reference == reference).first()
        if not order:
            return
        order.status = OrderStatus.confirmed if success else OrderStatus.cancelled
        db.flush()


payment_service = PaymentService()
