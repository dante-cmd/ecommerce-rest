from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.base import BaseSchema, Pagination


class CategoryOut(BaseSchema):
    id: int
    name: str
    description: str | None = None


class TagOut(BaseSchema):
    id: int
    name: str


class TagCreate(BaseSchema):
    name: str = Field(min_length=2, max_length=50)


class ProductImageOut(BaseSchema):
    id: int
    url: str


class ProductBase(BaseSchema):
    name: str = Field(min_length=2, max_length=200)
    description: str
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int
    sku: str = Field(min_length=3, max_length=100)
    tag_ids: list[int] = []
    image_urls: list[str] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None
    image_urls: list[str] | None = None


class ProductOut(BaseSchema):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    sku: str
    rating_avg: Decimal
    rating_count: int
    category: CategoryOut
    images: list[ProductImageOut]
    tags: list[TagOut]


class ProductList(BaseSchema):
    items: list[ProductOut]
    pagination: Pagination
