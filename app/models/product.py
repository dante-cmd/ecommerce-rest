from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DECIMAL, Column, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, int_pk


product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    products: Mapped[list["Product"]] = relationship(secondary=product_tags, back_populates="tags")


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    rating_avg: Mapped[Decimal] = mapped_column(DECIMAL(3, 2), default=Decimal("0.0"))
    rating_count: Mapped[int] = mapped_column(default=0)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    seller: Mapped["User"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    tags: Mapped[list[Tag]] = relationship(secondary=product_tags, back_populates="products")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")


Index("ix_products_name_price", Product.name, Product.price)


class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id: Mapped[int_pk]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(500))

    product: Mapped["Product"] = relationship(back_populates="images")
