import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.encounter import Encounter, EncounterStatus
from app.schemas.encounter import EncounterCreate


class EncounterRepository:
    """Data access repository for clinical encounters."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EncounterCreate, created_by_id: Optional[int] = None) -> Encounter:
        encounter = Encounter(
            patient_id=data.patient_id,
            appointment_id=data.appointment_id,
            provider_id=data.provider_id,
            facility_id=data.facility_id,
            encounter_type=data.encounter_type.value,
            status=EncounterStatus.IN_PROGRESS.value,
            chief_complaint=data.chief_complaint,
            clinical_notes=data.clinical_notes,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(encounter)
        self.db.commit()
        self.db.refresh(encounter)
        return encounter

    def get_by_id(self, encounter_id: uuid.UUID) -> Optional[Encounter]:
        stmt = select(Encounter).where(Encounter.id == encounter_id)
        return self.db.scalars(stmt).first()

    def get_by_appointment_id(self, appointment_id: uuid.UUID) -> Optional[Encounter]:
        stmt = select(Encounter).where(Encounter.appointment_id == appointment_id)
        return self.db.scalars(stmt).first()

    def get_patient_encounters(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Encounter], int]:
        base_query = select(Encounter).where(Encounter.patient_id == patient_id)
        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

        stmt = base_query.order_by(Encounter.started_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(
        self,
        encounter: Encounter,
        chief_complaint: Optional[str] = None,
        clinical_notes: Optional[str] = None,
        updated_by_id: Optional[int] = None,
    ) -> Encounter:
        if chief_complaint is not None:
            encounter.chief_complaint = chief_complaint
        if clinical_notes is not None:
            encounter.clinical_notes = clinical_notes

        encounter.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(encounter)
        return encounter

    def complete(
        self,
        encounter: Encounter,
        clinical_notes: Optional[str] = None,
        updated_by_id: Optional[int] = None,
    ) -> Encounter:
        encounter.status = EncounterStatus.COMPLETED.value
        encounter.ended_at = func.now()
        if clinical_notes is not None:
            encounter.clinical_notes = clinical_notes
        encounter.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(encounter)
        return encounter
