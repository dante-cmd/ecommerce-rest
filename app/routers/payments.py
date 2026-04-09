from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.order import order_crud
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.core.exceptions import NotFoundException
from app.services.payment_service import payment_service


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/pay/{order_id}")
def pay(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = order_crud.get(db, order_id)
    if not order or order.user_id != user.id:
        raise NotFoundException("Order not found")
    return payment_service.create_payment(db, order)


@router.post("/webhook", status_code=status.HTTP_200_OK)
def webhook(reference: str, success: bool, db: Session = Depends(get_db)):
    payment_service.process_webhook(db, reference, success)
    return {"detail": "Webhook processed"}
