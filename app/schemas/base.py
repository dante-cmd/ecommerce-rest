from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", strict=True)


class Pagination(BaseSchema):
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=200)
