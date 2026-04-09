from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.token_blacklist import token_blacklist_crud
from app.crud.user import user_crud
from app.dependencies.db import get_db
from app.schemas.auth import RegisterRequest, Token, TokenRefresh
from app.schemas.user import UserOut
from app.services.auth_service import auth_service
from app.services.cart_service import cart_service
from app.core.security import decode_token
from app.models.token_blacklist import TokenBlacklist


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, payload.email) or user_crud.get_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user = auth_service.register_user(
        db, email=payload.email, username=payload.username, password=payload.password, full_name=payload.full_name
    )
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    guest_cart: str | None = Header(default=None, alias="X-Guest-Cart"),
):
    user = auth_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if guest_cart:
        guest = cart_service.get_guest_cart(db, guest_cart)
        if guest:
            user_cart = cart_service.get_or_create_cart(db, user.id)
            cart_service.merge_guest_cart(db, guest, user_cart)
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
    user = user_crud.get_by_username(db, data.get("sub", ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return auth_service.create_tokens(user)


@router.post("/logout")
def logout(
    token: TokenRefresh,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
):
    data = decode_token(token.refresh_token)
    jti = data.get("jti")
    if jti and not token_blacklist_crud.is_blacklisted(db, jti):
        db.add(TokenBlacklist(jti=jti))
        db.flush()
    if authorization:
        access_token = authorization.replace("Bearer ", "")
        access_data = decode_token(access_token)
        access_jti = access_data.get("jti")
        if access_jti and not token_blacklist_crud.is_blacklisted(db, access_jti):
            db.add(TokenBlacklist(jti=access_jti))
            db.flush()
    return {"detail": "Logged out"}
