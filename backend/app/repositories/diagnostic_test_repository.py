import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.diagnostic_test import DiagnosticTest
from app.schemas.diagnostic import DiagnosticTestCreate


class DiagnosticTestRepository:
    """Data access repository for diagnostic test catalog."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DiagnosticTestCreate) -> DiagnosticTest:
        test = DiagnosticTest(
            code=data.code,
            name=data.name,
            category=data.category,
            specimen_type=data.specimen_type,
            description=data.description,
            is_active=data.is_active,
        )
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test

    def get_by_id(self, test_id: uuid.UUID) -> Optional[DiagnosticTest]:
        stmt = select(DiagnosticTest).where(DiagnosticTest.id == test_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, code: str) -> Optional[DiagnosticTest]:
        stmt = select(DiagnosticTest).where(DiagnosticTest.code == code)
        return self.db.scalars(stmt).first()

    def list_tests(self, active_only: bool = True) -> List[DiagnosticTest]:
        stmt = select(DiagnosticTest)
        if active_only:
            stmt = stmt.where(DiagnosticTest.is_active.is_(True))
        stmt = stmt.order_by(DiagnosticTest.category.asc(), DiagnosticTest.name.asc())
        return list(self.db.scalars(stmt).all())
