from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository managing User persistence and queries via SQLAlchemy 2.0."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        return self.db.scalars(stmt).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def create(
        self,
        email: str,
        password_hash: str,
        role: str,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_active_status(self, user_id: int, is_active: bool) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.is_active = is_active
            self.db.commit()
            self.db.refresh(user)
        return user
