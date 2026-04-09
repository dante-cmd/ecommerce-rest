from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.base import BaseSchema


class CartItemCreate(BaseSchema):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseSchema):
    quantity: int = Field(ge=1)


class CartItemOut(BaseSchema):
    id: int
    product_id: int
    quantity: int
    product_name: str
    unit_price: Decimal
    total_price: Decimal


class CartOut(BaseSchema):
    id: int
    guest_id: str | None = None
    items: list[CartItemOut]
    total_amount: Decimal
