from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, obj_id: int) -> ModelType | None:
        return db.get(self.model, obj_id)

    def list(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj: ModelType) -> ModelType:
        db.add(obj)
        db.flush()
        return obj

    def delete(self, db: Session, obj: ModelType) -> None:
        db.delete(obj)
