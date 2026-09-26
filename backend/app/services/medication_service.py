import uuid
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories.medication_repository import MedicationRepository
from app.schemas.medication import (
    MedicationCreate,
    MedicationListResponse,
    MedicationResponse,
)


class MedicationService:
    """Service for managing pharmaceutical medication drug catalog."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = MedicationRepository(db)

    def create_medication(self, data: MedicationCreate) -> MedicationResponse:
        medication = self.repository.create(data)
        return MedicationResponse.model_validate(medication)

    def get_medication(self, medication_id: uuid.UUID) -> MedicationResponse:
        med = self.repository.get_by_id(medication_id)
        if not med:
            raise NotFoundException(message=f"Medication with id '{medication_id}' not found")
        return MedicationResponse.model_validate(med)

    def list_medications(
        self,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> MedicationListResponse:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50

        skip = (page - 1) * page_size
        items, total = self.repository.list_medications(
            active_only=active_only,
            skip=skip,
            limit=page_size,
        )
        response_items = [MedicationResponse.model_validate(m) for m in items]
        return MedicationListResponse.create(response_items, total, page, page_size)
