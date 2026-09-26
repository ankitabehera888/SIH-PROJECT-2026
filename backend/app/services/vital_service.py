import uuid
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.encounter import Encounter, EncounterStatus
from app.models.patient import Patient
from app.models.user import User
from app.repositories.encounter_repository import EncounterRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.vital_repository import VitalRepository
from app.schemas.vital import VitalCreate, VitalListResponse, VitalResponse


class VitalService:
    """Service handling observation vitals recording, clinical sanity validation, and history retrieval."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = VitalRepository(db)
        self.encounter_repo = EncounterRepository(db)
        self.patient_repo = PatientRepository(db)

    def record_vitals(
        self,
        encounter_id: uuid.UUID,
        data: VitalCreate,
        current_user: User,
    ) -> VitalResponse:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if encounter.status == EncounterStatus.COMPLETED.value:
            raise AppException(
                message="Cannot record vitals for a completed clinical encounter",
                code="ENCOUNTER_LOCKED",
                status_code=400,
            )

        vital = self.repository.create(
            encounter_id=encounter.id,
            patient_id=encounter.patient_id,
            data=data,
            recorded_by_id=current_user.id,
        )
        return VitalResponse.model_validate(vital)

    def get_encounter_vitals(
        self,
        encounter_id: uuid.UUID,
        current_user: User,
    ) -> VitalListResponse:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(encounter.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own clinical records")

        items = self.repository.get_by_encounter(encounter_id)
        response_items = [VitalResponse.model_validate(v) for v in items]
        return VitalListResponse(
            items=response_items,
            encounter_id=encounter_id,
            total=len(response_items),
        )
