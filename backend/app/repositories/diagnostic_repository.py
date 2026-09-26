import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.diagnostic_order import DiagnosticOrder, DiagnosticOrderStatus
from app.models.diagnostic_order_item import DiagnosticItemStatus, DiagnosticOrderItem
from app.models.diagnostic_result import DiagnosticResult, DiagnosticResultStatus
from app.schemas.diagnostic import DiagnosticOrderCreate, DiagnosticResultCreate


class DiagnosticRepository:
    """Data access repository for diagnostic orders, order items, and lab results."""

    def __init__(self, db: Session):
        self.db = db

    def create_order(
        self,
        patient_id: uuid.UUID,
        encounter_id: uuid.UUID,
        ordering_provider_id: int,
        facility_id: uuid.UUID,
        data: DiagnosticOrderCreate,
    ) -> DiagnosticOrder:
        order = DiagnosticOrder(
            patient_id=patient_id,
            encounter_id=encounter_id,
            ordering_provider_id=ordering_provider_id,
            facility_id=facility_id,
            status=DiagnosticOrderStatus.ORDERED.value,
            priority=data.priority.value,
            notes=data.notes,
        )
        self.db.add(order)
        self.db.flush()

        for item in data.items:
            order_item = DiagnosticOrderItem(
                diagnostic_order_id=order.id,
                diagnostic_test_id=item.diagnostic_test_id,
                status=DiagnosticItemStatus.PENDING.value,
                notes=item.notes,
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_by_id(self, order_id: uuid.UUID) -> Optional[DiagnosticOrder]:
        stmt = select(DiagnosticOrder).where(DiagnosticOrder.id == order_id)
        return self.db.scalars(stmt).first()

    def get_patient_orders(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[DiagnosticOrder], int]:
        base_query = select(DiagnosticOrder).where(DiagnosticOrder.patient_id == patient_id)
        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

        stmt = base_query.order_by(DiagnosticOrder.ordered_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_encounter_orders(self, encounter_id: uuid.UUID) -> List[DiagnosticOrder]:
        stmt = (
            select(DiagnosticOrder)
            .where(DiagnosticOrder.encounter_id == encounter_id)
            .order_by(DiagnosticOrder.ordered_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def cancel_order(self, order: DiagnosticOrder, cancelled_by_id: int, reason: str) -> DiagnosticOrder:
        order.status = DiagnosticOrderStatus.CANCELLED.value
        order.cancelled_at = func.now()
        order.cancelled_by = cancelled_by_id
        order.cancellation_reason = reason
        for item in order.items:
            item.status = DiagnosticItemStatus.CANCELLED.value
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_item_by_id(self, item_id: uuid.UUID) -> Optional[DiagnosticOrderItem]:
        stmt = select(DiagnosticOrderItem).where(DiagnosticOrderItem.id == item_id)
        return self.db.scalars(stmt).first()

    def create_result(
        self,
        order_item: DiagnosticOrderItem,
        patient_id: uuid.UUID,
        data: DiagnosticResultCreate,
        created_by_id: Optional[int] = None,
    ) -> DiagnosticResult:
        result = DiagnosticResult(
            diagnostic_order_item_id=order_item.id,
            patient_id=patient_id,
            result_value=data.result_value,
            unit=data.unit,
            reference_range=data.reference_range,
            abnormal_flag=data.abnormal_flag,
            result_status=DiagnosticResultStatus.FINAL.value,
            notes=data.notes,
            created_by=created_by_id,
            verified_by=created_by_id,
            verified_at=func.now(),
        )
        self.db.add(result)
        order_item.status = DiagnosticItemStatus.COMPLETED.value
        order_item.performed_at = func.now()

        # Check if all items in order are completed
        order = order_item.order
        if order and all(i.status == DiagnosticItemStatus.COMPLETED.value for i in order.items):
            order.status = DiagnosticOrderStatus.COMPLETED.value

        self.db.commit()
        self.db.refresh(result)
        return result

    def get_result_by_item_id(self, item_id: uuid.UUID) -> Optional[DiagnosticResult]:
        stmt = select(DiagnosticResult).where(DiagnosticResult.diagnostic_order_item_id == item_id)
        return self.db.scalars(stmt).first()
