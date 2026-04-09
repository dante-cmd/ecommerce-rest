from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, int_pk


class TokenBlacklist(Base, TimestampMixin):
    __tablename__ = "token_blacklist"

    id: Mapped[int_pk]
    jti: Mapped[str] = mapped_column(String(255), unique=True, index=True)
