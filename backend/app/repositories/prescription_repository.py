import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.prescription import Prescription, PrescriptionStatus
from app.models.prescription_item import PrescriptionItem
from app.schemas.prescription import PrescriptionCreate


class PrescriptionRepository:
    """Data access repository for prescriptions and line items."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_id: uuid.UUID,
        encounter_id: uuid.UUID,
        prescriber_id: int,
        facility_id: uuid.UUID,
        data: PrescriptionCreate,
        created_by_id: Optional[int] = None,
    ) -> Prescription:
        prescription = Prescription(
            patient_id=patient_id,
            encounter_id=encounter_id,
            prescriber_id=prescriber_id,
            facility_id=facility_id,
            status=PrescriptionStatus.ISSUED.value,
            notes=data.notes,
            created_by=created_by_id,
            issued_by=created_by_id,
            issued_at=func.now(),
            updated_by=created_by_id,
        )
        self.db.add(prescription)
        self.db.flush()

        for item in data.items:
            p_item = PrescriptionItem(
                prescription_id=prescription.id,
                medication_id=item.medication_id,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration,
                duration_unit=item.duration_unit,
                route=item.route,
                quantity=item.quantity,
                instructions=item.instructions,
                notes=item.notes,
            )
            self.db.add(p_item)

        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def get_by_id(self, prescription_id: uuid.UUID) -> Optional[Prescription]:
        stmt = select(Prescription).where(Prescription.id == prescription_id)
        return self.db.scalars(stmt).first()

    def get_patient_prescriptions(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Prescription], int]:
        base_query = select(Prescription).where(Prescription.patient_id == patient_id)
        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

        stmt = base_query.order_by(Prescription.prescribed_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_encounter_prescriptions(self, encounter_id: uuid.UUID) -> List[Prescription]:
        stmt = (
            select(Prescription)
            .where(Prescription.encounter_id == encounter_id)
            .order_by(Prescription.prescribed_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def issue(self, prescription: Prescription, issued_by_id: int) -> Prescription:
        prescription.status = PrescriptionStatus.ISSUED.value
        prescription.issued_at = func.now()
        prescription.issued_by = issued_by_id
        prescription.updated_by = issued_by_id
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def cancel(self, prescription: Prescription, cancelled_by_id: int, reason: str) -> Prescription:
        prescription.status = PrescriptionStatus.CANCELLED.value
        prescription.cancelled_at = func.now()
        prescription.cancelled_by = cancelled_by_id
        prescription.cancellation_reason = reason
        prescription.updated_by = cancelled_by_id
        self.db.commit()
        self.db.refresh(prescription)
        return prescription
