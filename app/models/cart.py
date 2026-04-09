from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, int_pk


class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    id: Mapped[int_pk]
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=True)
    guest_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    user: Mapped["User"] = relationship(back_populates="cart")
    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")


Index("ix_carts_guest_id_unique", Cart.guest_id, unique=True, mssql_where=Cart.guest_id.isnot(None))


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)

    id: Mapped[int_pk]
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(default=1)

    cart: Mapped["Cart"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
