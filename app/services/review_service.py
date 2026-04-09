from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException
from app.crud.order import order_crud
from app.models.enums import OrderStatus
from app.models.review import Review


class ReviewService:
    def can_review(self, db: Session, user_id: int, product_id: int) -> bool:
        orders, _ = order_crud.list_by_user(db, user_id)
        for order in orders:
            if order.status != OrderStatus.delivered:
                continue
            if any(item.product_id == product_id for item in order.items):
                return True
        return False

    def add_review(self, db: Session, *, user_id: int, product_id: int, rating: int, comment: str | None) -> Review:
        if not self.can_review(db, user_id, product_id):
            raise BadRequestException("Product can only be reviewed after delivery")
        review = Review(user_id=user_id, product_id=product_id, rating=rating, comment=comment)
        db.add(review)
        db.flush()
        return review

    def update_product_rating(self, db: Session, product_id: int) -> None:
        from app.models.product import Product

        product = db.get(Product, product_id)
        if not product:
            return
        ratings = [review.rating for review in product.reviews]
        if ratings:
            avg = Decimal(sum(ratings)) / Decimal(len(ratings))
            product.rating_avg = avg.quantize(Decimal("0.01"))
            product.rating_count = len(ratings)
        else:
            product.rating_avg = Decimal("0.0")
            product.rating_count = 0
        db.flush()


review_service = ReviewService()
