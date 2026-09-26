import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException
from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)


class PatientService:
    """Service layer orchestrating patient domain workflows and business invariants."""

    def __init__(self, db: Session):
        self.repository = PatientRepository(db)

    def create_patient(
        self,
        data: PatientCreate,
        created_by_id: Optional[int] = None,
    ) -> PatientResponse:
        # Duplicate detection check (First Name + Last Name + DOB + Phone)
        duplicate = self.repository.find_potential_duplicate(
            first_name=data.first_name,
            last_name=data.last_name,
            dob=data.date_of_birth,
            phone=data.phone,
        )
        if duplicate:
            raise ConflictException(
                message=(
                    f"Potential duplicate patient detected with matching name, DOB, and phone: "
                    f"Patient Number {duplicate.patient_number}"
                ),
                details={"existing_patient_number": duplicate.patient_number},
            )

        # Generate human-readable sequence
        patient_number = self.repository.generate_next_patient_number()

        # Persist
        patient = self.repository.create(
            data=data,
            patient_number=patient_number,
            created_by_id=created_by_id,
        )
        return PatientResponse.model_validate(patient)

    def get_patient(self, patient_id: uuid.UUID) -> PatientResponse:
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(
                message=f"Patient with id '{patient_id}' not found",
            )
        return PatientResponse.model_validate(patient)

    def get_patient_by_number(self, patient_number: str) -> PatientResponse:
        patient = self.repository.get_by_number(patient_number)
        if not patient:
            raise NotFoundException(
                message=f"Patient with number '{patient_number}' not found",
            )
        return PatientResponse.model_validate(patient)

    def list_patients(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active_only: bool = True,
    ) -> PatientListResponse:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.list(
            skip=skip,
            limit=page_size,
            is_active_only=is_active_only,
        )
        response_items = [PatientResponse.model_validate(p) for p in items]
        return PatientListResponse.create(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def search_patients(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
        is_active_only: bool = True,
    ) -> PatientListResponse:
        if not query or len(query.strip()) == 0:
            return self.list_patients(page=page, page_size=page_size, is_active_only=is_active_only)

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.search(
            query_str=query,
            skip=skip,
            limit=page_size,
            is_active_only=is_active_only,
        )
        response_items = [PatientResponse.model_validate(p) for p in items]
        return PatientListResponse.create(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def update_patient(
        self,
        patient_id: uuid.UUID,
        data: PatientUpdate,
        updated_by_id: Optional[int] = None,
    ) -> PatientResponse:
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{patient_id}' not found")

        updated = self.repository.update(
            patient=patient,
            data=data,
            updated_by_id=updated_by_id,
        )
        return PatientResponse.model_validate(updated)

    def deactivate_patient(
        self,
        patient_id: uuid.UUID,
        updated_by_id: Optional[int] = None,
    ) -> PatientResponse:
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{patient_id}' not found")

        deactivated = self.repository.deactivate(
            patient=patient,
            updated_by_id=updated_by_id,
        )
        return PatientResponse.model_validate(deactivated)
