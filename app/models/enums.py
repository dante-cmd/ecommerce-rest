from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
