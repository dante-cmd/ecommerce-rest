from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.core.exceptions import NotFoundException
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut
from app.services.cart_service import cart_service


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = cart_service.get_or_create_cart(db, user.id)
    items = []
    for item in cart.items:
        items.append(
            CartItemOut(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_name=item.product.name,
                unit_price=item.product.price,
                total_price=item.product.price * item.quantity,
            )
        )
    return CartOut(id=cart.id, guest_id=cart.guest_id, items=items, total_amount=cart_service.totals(cart))


@router.post("/guest", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def create_guest_cart(db: Session = Depends(get_db)):
    cart = cart_service.create_guest_cart(db)
    return CartOut(id=cart.id, guest_id=cart.guest_id, items=[], total_amount=0)


@router.get("/guest/{guest_id}", response_model=CartOut)
def get_guest_cart(guest_id: str, db: Session = Depends(get_db)):
    cart = cart_service.get_guest_cart(db, guest_id)
    if not cart:
        raise NotFoundException("Guest cart not found")
    items = []
    for item in cart.items:
        items.append(
            CartItemOut(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_name=item.product.name,
                unit_price=item.product.price,
                total_price=item.product.price * item.quantity,
            )
        )
    return CartOut(id=cart.id, guest_id=cart.guest_id, items=items, total_amount=cart_service.totals(cart))


@router.post("/guest/{guest_id}/items", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
def add_item_guest(guest_id: str, payload: CartItemCreate, db: Session = Depends(get_db)):
    cart = cart_service.get_guest_cart(db, guest_id)
    if not cart:
        raise NotFoundException("Guest cart not found")
    item = cart_service.add_item(db, cart, payload.product_id, payload.quantity)
    return CartItemOut(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_name=item.product.name,
        unit_price=item.product.price,
        total_price=item.product.price * item.quantity,
    )


@router.put("/guest/{guest_id}/items/{product_id}", response_model=CartItemOut)
def update_item_guest(guest_id: str, product_id: int, payload: CartItemUpdate, db: Session = Depends(get_db)):
    cart = cart_service.get_guest_cart(db, guest_id)
    if not cart:
        raise NotFoundException("Guest cart not found")
    item = cart_service.update_item(db, cart, product_id, payload.quantity)
    return CartItemOut(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_name=item.product.name,
        unit_price=item.product.price,
        total_price=item.product.price * item.quantity,
    )


@router.delete("/guest/{guest_id}/items/{product_id}")
def remove_item_guest(guest_id: str, product_id: int, db: Session = Depends(get_db)):
    cart = cart_service.get_guest_cart(db, guest_id)
    if not cart:
        raise NotFoundException("Guest cart not found")
    cart_service.remove_item(db, cart, product_id)
    return {"detail": "Item removed"}


@router.post("/items", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
def add_item(payload: CartItemCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = cart_service.get_or_create_cart(db, user.id)
    item = cart_service.add_item(db, cart, payload.product_id, payload.quantity)
    return CartItemOut(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_name=item.product.name,
        unit_price=item.product.price,
        total_price=item.product.price * item.quantity,
    )


@router.put("/items/{product_id}", response_model=CartItemOut)
def update_item(
    product_id: int, payload: CartItemUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    cart = cart_service.get_or_create_cart(db, user.id)
    item = cart_service.update_item(db, cart, product_id, payload.quantity)
    return CartItemOut(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        product_name=item.product.name,
        unit_price=item.product.price,
        total_price=item.product.price * item.quantity,
    )


@router.delete("/items/{product_id}")
def remove_item(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = cart_service.get_or_create_cart(db, user.id)
    cart_service.remove_item(db, cart, product_id)
    return {"detail": "Item removed"}
