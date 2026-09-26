import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.medication import Medication
from app.schemas.medication import MedicationCreate


class MedicationRepository:
    """Data access repository for medication drug catalog."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MedicationCreate) -> Medication:
        medication = Medication(
            name=data.name,
            generic_name=data.generic_name,
            strength=data.strength,
            dosage_form=data.dosage_form,
            route=data.route,
            unit=data.unit,
            is_active=data.is_active,
        )
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def get_by_id(self, medication_id: uuid.UUID) -> Optional[Medication]:
        stmt = select(Medication).where(Medication.id == medication_id)
        return self.db.scalars(stmt).first()

    def list_medications(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Medication], int]:
        base_query = select(Medication)
        if active_only:
            base_query = base_query.where(Medication.is_active.is_(True))

        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        stmt = base_query.order_by(Medication.name.asc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total
