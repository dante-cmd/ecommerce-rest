from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.crud.category import category_crud
from app.crud.product import product_crud
from app.models.base import utc_now
from app.models.product import Product, ProductImage, Tag


class ProductService:
    def create_product(
        self,
        db: Session,
        *,
        seller_id: int,
        name: str,
        description: str,
        price: Decimal,
        stock: int,
        sku: str,
        category_id: int,
        tag_ids: list[int],
        image_urls: list[str],
    ) -> Product:
        category = category_crud.get(db, category_id)
        if not category:
            raise NotFoundException("Category not found")

        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            sku=sku,
            category_id=category_id,
            seller_id=seller_id,
        )
        product.images = [ProductImage(url=url) for url in image_urls]
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            product.tags = tags
        return product_crud.create(db, product)

    def update_product(self, db: Session, product: Product, data: dict) -> Product:
        for key, value in data.items():
            if value is None:
                continue
            if key == "image_urls":
                product.images = [ProductImage(url=url) for url in value]
            elif key == "tag_ids":
                product.tags = db.query(Tag).filter(Tag.id.in_(value)).all()
            else:
                setattr(product, key, value)
        db.flush()
        return product

    def soft_delete(self, db: Session, product: Product) -> None:
        product.is_deleted = True
        product.deleted_at = utc_now()
        db.flush()


product_service = ProductService()
