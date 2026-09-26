import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ConflictException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.diagnostic_order import DiagnosticOrder, DiagnosticOrderStatus
from app.models.diagnostic_order_item import DiagnosticItemStatus, DiagnosticOrderItem
from app.models.diagnostic_result import DiagnosticResult
from app.models.diagnostic_test import DiagnosticTest
from app.models.user import User
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.diagnostic_test_repository import DiagnosticTestRepository
from app.repositories.encounter_repository import EncounterRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.diagnostic import (
    DiagnosticOrderCancelRequest,
    DiagnosticOrderCreate,
    DiagnosticOrderListResponse,
    DiagnosticOrderResponse,
    DiagnosticResultCreate,
    DiagnosticResultResponse,
    DiagnosticTestCreate,
    DiagnosticTestListResponse,
    DiagnosticTestResponse,
)


class DiagnosticService:
    """Service governing diagnostic investigation orders, line items, and lab results."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DiagnosticRepository(db)
        self.test_repo = DiagnosticTestRepository(db)
        self.encounter_repo = EncounterRepository(db)
        self.patient_repo = PatientRepository(db)

    # Diagnostic Test Catalog
    def create_test(self, data: DiagnosticTestCreate) -> DiagnosticTestResponse:
        existing = self.test_repo.get_by_code(data.code)
        if existing:
            raise ConflictException(
                message=f"Diagnostic test with code '{data.code}' already exists",
                details={"code": "DIAGNOSTIC_TEST_EXISTS"},
            )
        test = self.test_repo.create(data)
        return DiagnosticTestResponse.model_validate(test)

    def list_tests(self, active_only: bool = True) -> DiagnosticTestListResponse:
        items = self.test_repo.list_tests(active_only=active_only)
        response_items = [DiagnosticTestResponse.model_validate(t) for t in items]
        return DiagnosticTestListResponse(items=response_items, total=len(response_items))

    # Diagnostic Orders
    def create_order_from_encounter(
        self,
        encounter_id: uuid.UUID,
        data: DiagnosticOrderCreate,
        current_user: User,
    ) -> DiagnosticOrderResponse:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        patient = self.patient_repo.get_by_id(encounter.patient_id)
        if not patient or not patient.is_active:
            raise NotFoundException(message=f"Patient with id '{encounter.patient_id}' not found or inactive")

        # Validate each test exists and is active
        for item in data.items:
            test = self.test_repo.get_by_id(item.diagnostic_test_id)
            if not test:
                raise NotFoundException(message=f"Diagnostic test with id '{item.diagnostic_test_id}' not found")
            if not test.is_active:
                raise AppException(
                    message=f"Diagnostic test '{test.name}' is inactive and cannot be ordered",
                    code="TEST_INACTIVE",
                    status_code=400,
                )

        order = self.repository.create_order(
            patient_id=encounter.patient_id,
            encounter_id=encounter.id,
            ordering_provider_id=current_user.id,
            facility_id=encounter.facility_id,
            data=data,
        )
        return DiagnosticOrderResponse.model_validate(order)

    def get_order(
        self,
        order_id: uuid.UUID,
        current_user: User,
    ) -> DiagnosticOrderResponse:
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise NotFoundException(message=f"Diagnostic order with id '{order_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(order.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own diagnostic orders")

        return DiagnosticOrderResponse.model_validate(order)

    def list_patient_orders(
        self,
        patient_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> DiagnosticOrderListResponse:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(message=f"Patient with id '{patient_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own diagnostic orders")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_patient_orders(
            patient_id=patient_id,
            skip=skip,
            limit=page_size,
        )
        response_items = [DiagnosticOrderResponse.model_validate(o) for o in items]
        return DiagnosticOrderListResponse.create(response_items, total, page, page_size)

    def list_encounter_orders(
        self,
        encounter_id: uuid.UUID,
        current_user: User,
    ) -> List[DiagnosticOrderResponse]:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(encounter.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own diagnostic orders")

        items = self.repository.get_encounter_orders(encounter_id)
        return [DiagnosticOrderResponse.model_validate(o) for o in items]

    def cancel_order(
        self,
        order_id: uuid.UUID,
        data: DiagnosticOrderCancelRequest,
        current_user: User,
    ) -> DiagnosticOrderResponse:
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise NotFoundException(message=f"Diagnostic order with id '{order_id}' not found")

        if order.status in [DiagnosticOrderStatus.COMPLETED.value, DiagnosticOrderStatus.CANCELLED.value]:
            raise AppException(
                message=f"Cannot cancel diagnostic order in terminal status '{order.status}'",
                code="INVALID_ORDER_TRANSITION",
                status_code=400,
            )

        updated = self.repository.cancel_order(
            order=order,
            cancelled_by_id=current_user.id,
            reason=data.reason,
        )
        return DiagnosticOrderResponse.model_validate(updated)

    # Diagnostic Results
    def record_result(
        self,
        item_id: uuid.UUID,
        data: DiagnosticResultCreate,
        current_user: User,
    ) -> DiagnosticResultResponse:
        order_item = self.repository.get_order_item_by_id(item_id)
        if not order_item:
            raise NotFoundException(message=f"Diagnostic order item with id '{item_id}' not found")

        if order_item.status == DiagnosticItemStatus.CANCELLED.value:
            raise AppException(
                message="Cannot record results for a cancelled diagnostic order item",
                code="ITEM_CANCELLED",
                status_code=400,
            )

        existing_result = self.repository.get_result_by_item_id(item_id)
        if existing_result:
            raise ConflictException(
                message="A result has already been recorded for this diagnostic item",
                details={"code": "RESULT_ALREADY_EXISTS"},
            )

        result = self.repository.create_result(
            order_item=order_item,
            patient_id=order_item.order.patient_id,
            data=data,
            created_by_id=current_user.id,
        )
        return DiagnosticResultResponse.model_validate(result)

    def get_item_result(
        self,
        item_id: uuid.UUID,
        current_user: User,
    ) -> DiagnosticResultResponse:
        order_item = self.repository.get_order_item_by_id(item_id)
        if not order_item:
            raise NotFoundException(message=f"Diagnostic order item with id '{item_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(order_item.order.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own diagnostic results")

        result = self.repository.get_result_by_item_id(item_id)
        if not result:
            raise NotFoundException(message=f"No result found for diagnostic order item '{item_id}'")

        return DiagnosticResultResponse.model_validate(result)
