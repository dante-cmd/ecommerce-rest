from __future__ import annotations

from app.schemas.base import Pagination


def paginate(total: int, page: int, size: int) -> Pagination:
    return Pagination(total=total, page=page, size=size)
