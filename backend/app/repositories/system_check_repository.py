from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.system_check import SystemCheck
from app.schemas.system_check import SystemCheckCreate


class SystemCheckRepository:
    """Repository handling all direct database operations for SystemCheck."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: SystemCheckCreate) -> SystemCheck:
        instance = SystemCheck(
            check_name=data.check_name,
            status=data.status,
        )
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_all(self, skip: int = 0, limit: int = 100) -> List[SystemCheck]:
        stmt = select(SystemCheck).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, check_id: int) -> Optional[SystemCheck]:
        stmt = select(SystemCheck).where(SystemCheck.id == check_id)
        return self.db.scalars(stmt).first()
