from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.review_service import review_service


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def add_review(payload: ReviewCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    review = review_service.add_review(
        db, user_id=user.id, product_id=payload.product_id, rating=payload.rating, comment=payload.comment
    )
    review_service.update_product_rating(db, payload.product_id)
    return review
