from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.token_blacklist import TokenBlacklist


class TokenBlacklistCRUD(CRUDBase[TokenBlacklist]):
    def is_blacklisted(self, db: Session, jti: str) -> bool:
        return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


token_blacklist_crud = TokenBlacklistCRUD(TokenBlacklist)
