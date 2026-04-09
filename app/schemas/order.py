from __future__ import annotations

from decimal import Decimal

from datetime import datetime
from pydantic import Field

from app.models.enums import OrderStatus
from app.schemas.base import BaseSchema, Pagination


class OrderItemOut(BaseSchema):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderOut(BaseSchema):
    id: int
    status: OrderStatus
    total_amount: Decimal
    items: list[OrderItemOut]
    created_at: datetime


class OrderList(BaseSchema):
    items: list[OrderOut]
    pagination: Pagination


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus


class OrderCancel(BaseSchema):
    reason: str = Field(min_length=3, max_length=200)
