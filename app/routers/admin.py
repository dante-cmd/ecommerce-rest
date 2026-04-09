from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import require_role
from app.dependencies.db import get_db
from app.models.enums import UserRole
from app.crud.order import order_crud
from app.crud.product import product_crud
from app.crud.user import user_crud
from app.schemas.admin import DashboardStats
from app.schemas.order import OrderOut
from app.schemas.product import ProductOut
from app.schemas.user import UserOut
from app.services.admin_service import admin_service


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_role(UserRole.admin))])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    return admin_service.dashboard(db)


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return user_crud.list(db, limit=200)


@router.get("/orders", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return order_crud.list(db, limit=200)


@router.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return product_crud.list(db, limit=200)
