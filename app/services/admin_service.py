from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User


class AdminService:
    def dashboard(self, db: Session) -> dict:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        total_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or Decimal("0.0")

        top_products = (
            db.query(
                Product.id,
                Product.name,
                func.coalesce(func.sum(OrderItem.quantity), 0).label("units_sold"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.coalesce(func.sum(OrderItem.quantity), 0).desc())
            .limit(5)
            .all()
        )
        top_products_data = [
            {"product_id": row.id, "name": row.name, "units_sold": int(row.units_sold)} for row in top_products
        ]

        return {
            "total_users": int(total_users),
            "total_orders": int(total_orders),
            "total_revenue": total_revenue,
            "top_products": top_products_data,
        }


admin_service = AdminService()
