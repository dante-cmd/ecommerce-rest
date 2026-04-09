from __future__ import annotations

from decimal import Decimal

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.product import Product, Tag


class ProductCRUD(CRUDBase[Product]):
    def search(
        self,
        db: Session,
        *,
        query: str | None = None,
        category_id: int | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        min_rating: Decimal | None = None,
        sort: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Product], int]:
        q = db.query(Product).filter(Product.is_deleted == False)  # noqa: E712
        if query:
            q = q.filter(Product.name.ilike(f"%{query}%"))
        if category_id:
            q = q.filter(Product.category_id == category_id)
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)
        if min_rating is not None:
            q = q.filter(Product.rating_avg >= min_rating)

        if sort == "price_asc":
            q = q.order_by(asc(Product.price))
        elif sort == "price_desc":
            q = q.order_by(desc(Product.price))
        elif sort == "rating_desc":
            q = q.order_by(desc(Product.rating_avg))
        else:
            q = q.order_by(desc(Product.created_at))

        total = q.count()
        items = q.offset(skip).limit(limit).all()
        return items, total

    def get_tag_by_name(self, db: Session, name: str) -> Tag | None:
        return db.query(Tag).filter(Tag.name == name).first()


product_crud = ProductCRUD(Product)
