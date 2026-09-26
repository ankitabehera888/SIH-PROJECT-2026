import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.vital import Vital
from app.schemas.vital import VitalCreate


class VitalRepository:
    """Data access repository for clinical observation Vitals."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        encounter_id: uuid.UUID,
        patient_id: uuid.UUID,
        data: VitalCreate,
        recorded_by_id: Optional[int] = None,
    ) -> Vital:
        vital = Vital(
            encounter_id=encounter_id,
            patient_id=patient_id,
            recorded_by=recorded_by_id,
            temperature=data.temperature,
            heart_rate=data.heart_rate,
            respiratory_rate=data.respiratory_rate,
            systolic_bp=data.systolic_bp,
            diastolic_bp=data.diastolic_bp,
            spo2=data.spo2,
            weight=data.weight,
            height=data.height,
            notes=data.notes,
        )
        self.db.add(vital)
        self.db.commit()
        self.db.refresh(vital)
        return vital

    def get_by_encounter(self, encounter_id: uuid.UUID) -> List[Vital]:
        stmt = (
            select(Vital)
            .where(Vital.encounter_id == encounter_id)
            .order_by(Vital.recorded_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, vital_id: uuid.UUID) -> Optional[Vital]:
        stmt = select(Vital).where(Vital.id == vital_id)
        return self.db.scalars(stmt).first()
