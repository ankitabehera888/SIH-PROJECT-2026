import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.facility import Facility
from app.schemas.facility import FacilityCreate


class FacilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: FacilityCreate) -> Facility:
        facility = Facility(
            name=data.name.strip(),
            facility_code=data.facility_code.strip().upper(),
            facility_type=data.facility_type.value,
            address=data.address,
            phone=data.phone,
            is_active=True,
        )
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        return facility

    def get_by_id(self, facility_id: uuid.UUID) -> Optional[Facility]:
        stmt = select(Facility).where(Facility.id == facility_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, code: str) -> Optional[Facility]:
        stmt = select(Facility).where(Facility.facility_code == code.strip().upper())
        return self.db.scalars(stmt).first()

    def list(self, skip: int = 0, limit: int = 100, is_active_only: bool = True) -> Tuple[List[Facility], int]:
        base_query = select(Facility)
        if is_active_only:
            base_query = base_query.where(Facility.is_active == True)

        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        stmt = base_query.order_by(Facility.name).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total
