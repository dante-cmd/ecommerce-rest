from __future__ import annotations

from pydantic import Field

from app.schemas.base import BaseSchema


class ReviewCreate(BaseSchema):
    product_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


class ReviewOut(BaseSchema):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: str | None = None
