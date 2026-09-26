import uuid
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException
from app.repositories.facility_repository import FacilityRepository
from app.schemas.facility import (
    FacilityCreate,
    FacilityListResponse,
    FacilityResponse,
)


class FacilityService:
    def __init__(self, db: Session):
        self.repository = FacilityRepository(db)

    def create_facility(self, data: FacilityCreate) -> FacilityResponse:
        existing = self.repository.get_by_code(data.facility_code)
        if existing:
            raise ConflictException(
                message=f"Facility with code '{data.facility_code}' already exists",
                details={"facility_code": data.facility_code},
            )
        facility = self.repository.create(data)
        return FacilityResponse.model_validate(facility)

    def get_facility(self, facility_id: uuid.UUID) -> FacilityResponse:
        facility = self.repository.get_by_id(facility_id)
        if not facility:
            raise NotFoundException(message=f"Facility with id '{facility_id}' not found")
        return FacilityResponse.model_validate(facility)

    def list_facilities(self, skip: int = 0, limit: int = 100) -> FacilityListResponse:
        items, total = self.repository.list(skip=skip, limit=limit)
        response_items = [FacilityResponse.model_validate(f) for f in items]
        return FacilityListResponse(items=response_items, total=total)
