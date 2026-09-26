import uuid
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.dispensing import MedicationDispense
from app.models.patient import Patient
from app.schemas.dispensing import (
    DispensingListResponse,
    MedicationDispenseCreate,
    MedicationDispenseResponse,
)


class DispensingService:
    def __init__(self, db: Session):
        self.db = db

    def record_dispense(self, data: MedicationDispenseCreate) -> MedicationDispenseResponse:
        patient = self.db.get(Patient, data.patient_id)
        if not patient:
            raise AppException(status_code=404, detail="Patient not found")

        dispense = MedicationDispense(
            patient_id=data.patient_id,
            prescription_id=data.prescription_id,
            medication_name=data.medication_name,
            dosage=data.dosage,
            frequency=data.frequency,
            status=data.status,
            start_date=data.start_date,
            end_date=data.end_date,
            refills_remaining=data.refills_remaining,
            instructions=data.instructions,
        )
        self.db.add(dispense)
        self.db.commit()
        self.db.refresh(dispense)
        return self._to_response(dispense)

    def list_active_medications(
        self, patient_id: uuid.UUID, status_filter: Optional[str] = None
    ) -> DispensingListResponse:
        stmt = select(MedicationDispense).where(MedicationDispense.patient_id == patient_id).order_by(desc(MedicationDispense.dispensed_at))
        if status_filter:
            stmt = stmt.where(MedicationDispense.status == status_filter)

        items = self.db.scalars(stmt).all()
        resp_items = [self._to_response(i) for i in items]
        return DispensingListResponse(items=resp_items, total=len(resp_items))

    def update_status(self, dispense_id: uuid.UUID, status: str) -> MedicationDispenseResponse:
        dispense = self.db.get(MedicationDispense, dispense_id)
        if not dispense:
            raise AppException(status_code=404, detail="Medication dispense record not found")

        dispense.status = status
        self.db.commit()
        self.db.refresh(dispense)
        return self._to_response(dispense)

    def _to_response(self, item: MedicationDispense) -> MedicationDispenseResponse:
        patient_name = f"{item.patient.first_name} {item.patient.last_name}" if item.patient else "Patient"
        return MedicationDispenseResponse(
            id=item.id,
            patient_id=item.patient_id,
            patient_name=patient_name,
            prescription_id=item.prescription_id,
            medication_name=item.medication_name,
            dosage=item.dosage,
            frequency=item.frequency,
            status=item.status,
            start_date=item.start_date,
            end_date=item.end_date,
            refills_remaining=item.refills_remaining,
            instructions=item.instructions,
            dispensed_at=item.dispensed_at,
        )
