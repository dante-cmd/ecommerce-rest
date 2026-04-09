from __future__ import annotations

from decimal import Decimal
import json

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.crud.category import category_crud
from app.crud.product import product_crud
from app.models.product import Tag
from app.dependencies.auth import require_role
from app.dependencies.db import get_db
from app.models.enums import UserRole
from app.core.cache import get_redis_client
from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.schemas.product import CategoryOut, ProductCreate, ProductList, ProductOut, ProductUpdate, TagCreate, TagOut
from app.services.product_service import product_service
from app.utils.pagination import paginate


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductList)
def list_products(
    db: Session = Depends(get_db),
    query: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_rating: Decimal | None = None,
    sort: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    skip = (page - 1) * size
    items, total = product_crud.search(
        db,
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort=sort,
        skip=skip,
        limit=size,
    )
    return ProductList(items=items, pagination=paginate(total, page, size))


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    settings = get_settings()
    redis_client = get_redis_client()
    cache_key = f"product:{product_id}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        cached = None

    product = product_crud.get(db, product_id)
    if not product or product.is_deleted:
        raise NotFoundException("Product not found")
    payload = ProductOut.model_validate(product).model_dump()
    try:
        redis_client.setex(cache_key, settings.redis_cache_ttl_seconds, json.dumps(payload))
    except Exception:
        pass
    return payload


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.seller, UserRole.admin)),
):
    return product_service.create_product(
        db,
        seller_id=user.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        sku=payload.sku,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
        image_urls=payload.image_urls,
    )


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.seller, UserRole.admin)),
):
    product = product_crud.get(db, product_id)
    if not product or product.is_deleted:
        raise NotFoundException("Product not found")
    if user.role != UserRole.admin and product.seller_id != user.id:
        raise ForbiddenException()
    updated = product_service.update_product(db, product, payload.model_dump())
    try:
        get_redis_client().delete(f"product:{product_id}")
    except Exception:
        pass
    return updated


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.seller, UserRole.admin)),
):
    product = product_crud.get(db, product_id)
    if not product or product.is_deleted:
        raise NotFoundException("Product not found")
    if user.role != UserRole.admin and product.seller_id != user.id:
        raise ForbiddenException()
    product_service.soft_delete(db, product)
    try:
        get_redis_client().delete(f"product:{product_id}")
    except Exception:
        pass
    return {"detail": "Deleted"}


@router.get("/categories/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return category_crud.list(db, limit=200)


@router.get("/tags/", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.post("/tags/", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db), user=Depends(require_role(UserRole.admin))):
    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    return tag
