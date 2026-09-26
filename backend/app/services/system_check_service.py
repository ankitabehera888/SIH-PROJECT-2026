from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.repositories.system_check_repository import SystemCheckRepository
from app.schemas.system_check import SystemCheckCreate, SystemCheckResponse


class SystemCheckService:
    """Service layer coordinating business logic and repository interactions."""

    def __init__(self, db: Session):
        self.repository = SystemCheckRepository(db)

    def record_check(self, data: SystemCheckCreate) -> SystemCheckResponse:
        created = self.repository.create(data)
        return SystemCheckResponse.model_validate(created)

    def list_checks(self, skip: int = 0, limit: int = 100) -> List[SystemCheckResponse]:
        items = self.repository.get_all(skip=skip, limit=limit)
        return [SystemCheckResponse.model_validate(item) for item in items]

    def get_check(self, check_id: int) -> SystemCheckResponse:
        item = self.repository.get_by_id(check_id)
        if not item:
            raise NotFoundException(f"SystemCheck with id {check_id} does not exist")
        return SystemCheckResponse.model_validate(item)
