from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.user import user_crud
from app.dependencies.auth import get_current_user, require_role
from app.dependencies.db import get_db
from app.models.enums import UserRole
from app.schemas.user import UserOut, UserPasswordChange, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
def update_profile(payload: UserUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if payload.full_name is not None:
        user.full_name = payload.full_name
    db.flush()
    return user


@router.post("/me/password")
def change_password(
    payload: UserPasswordChange,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid current password")
    user.hashed_password = get_password_hash(payload.new_password)
    db.flush()
    return {"detail": "Password updated"}


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_role(UserRole.admin))])
def list_users(db: Session = Depends(get_db)):
    return user_crud.list(db, limit=200)
