from __future__ import annotations

from decimal import Decimal

from app.schemas.base import BaseSchema


class DashboardStats(BaseSchema):
    total_users: int
    total_orders: int
    total_revenue: Decimal
    top_products: list[dict]
