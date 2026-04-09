from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.crud.order import order_crud
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.db import get_db
from app.models.enums import UserRole
from app.schemas.order import OrderCancel, OrderList, OrderOut, OrderStatusUpdate
from app.core.exceptions import NotFoundException
from app.services.cart_service import cart_service
from app.services.order_service import order_service
from app.utils.pagination import paginate


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = cart_service.get_or_create_cart(db, user.id)
    order = order_service.create_from_cart(db, cart, user.id)
    return order


@router.get("/", response_model=OrderList)
def list_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    skip = (page - 1) * size
    items, total = order_crud.list_by_user(db, user.id, skip=skip, limit=size)
    return OrderList(items=items, pagination=paginate(total, page, size))


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user), payload: OrderCancel | None = None):
    order = order_crud.get(db, order_id)
    if not order or order.user_id != user.id:
        raise NotFoundException("Order not found")
    return order_service.cancel_order(db, order)


@router.patch("/{order_id}/status", response_model=OrderOut, dependencies=[Depends(require_role(UserRole.admin))])
def update_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = order_crud.get(db, order_id)
    if not order:
        raise NotFoundException("Order not found")
    order.status = payload.status
    db.flush()
    return order
