import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from app.models.queue import QueueEntry, QueuePriority, QueueStatus


class QueueRepository:
    """Data access repository for Facility daily operational queues."""

    def __init__(self, db: Session):
        self.db = db

    def generate_next_queue_number(self, facility_id: uuid.UUID, queue_date: date) -> str:
        """Generates sequential queue number scoped to facility and date (e.g. Q001, Q002)."""
        stmt = select(func.count(QueueEntry.id)).where(
            QueueEntry.facility_id == facility_id,
            QueueEntry.queue_date == queue_date,
        )
        count = self.db.scalar(stmt) or 0
        return f"Q{count + 1:03d}"

    def create(
        self,
        appointment_id: uuid.UUID,
        patient_id: uuid.UUID,
        facility_id: uuid.UUID,
        queue_date: date,
        queue_number: str,
        priority: str = QueuePriority.NORMAL.value,
    ) -> QueueEntry:
        entry = QueueEntry(
            appointment_id=appointment_id,
            patient_id=patient_id,
            facility_id=facility_id,
            queue_date=queue_date,
            queue_number=queue_number,
            priority=priority,
            status=QueueStatus.WAITING.value,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_id(self, entry_id: uuid.UUID) -> Optional[QueueEntry]:
        stmt = select(QueueEntry).where(QueueEntry.id == entry_id)
        return self.db.scalars(stmt).first()

    def get_by_appointment_id(self, appointment_id: uuid.UUID) -> Optional[QueueEntry]:
        stmt = select(QueueEntry).where(QueueEntry.appointment_id == appointment_id)
        return self.db.scalars(stmt).first()

    def list_for_facility(
        self,
        facility_id: uuid.UUID,
        queue_date: date,
        status: Optional[str] = None,
    ) -> List[QueueEntry]:
        stmt = select(QueueEntry).where(
            QueueEntry.facility_id == facility_id,
            QueueEntry.queue_date == queue_date,
        )
        if status:
            stmt = stmt.where(QueueEntry.status == status)

        # Priority ordering: URGENT (1) -> HIGH (2) -> NORMAL (3), then arrival order
        priority_order = case(
            (QueueEntry.priority == QueuePriority.URGENT.value, 1),
            (QueueEntry.priority == QueuePriority.HIGH.value, 2),
            else_=3,
        )
        stmt = stmt.order_by(priority_order, QueueEntry.checked_in_at.asc())
        return list(self.db.scalars(stmt).all())

    def get_next_waiting(self, facility_id: uuid.UUID, queue_date: date) -> Optional[QueueEntry]:
        """Picks the next eligible patient according to clinical triage priority then arrival order."""
        priority_order = case(
            (QueueEntry.priority == QueuePriority.URGENT.value, 1),
            (QueueEntry.priority == QueuePriority.HIGH.value, 2),
            else_=3,
        )
        stmt = (
            select(QueueEntry)
            .where(
                QueueEntry.facility_id == facility_id,
                QueueEntry.queue_date == queue_date,
                QueueEntry.status == QueueStatus.WAITING.value,
            )
            .order_by(priority_order, QueueEntry.checked_in_at.asc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def mark_called(self, entry: QueueEntry) -> QueueEntry:
        entry.status = QueueStatus.CALLED.value
        entry.called_at = func.now()
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def mark_in_consultation(self, entry: QueueEntry) -> QueueEntry:
        entry.status = QueueStatus.IN_CONSULTATION.value
        entry.consultation_started_at = func.now()
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def mark_completed(self, entry: QueueEntry) -> QueueEntry:
        entry.status = QueueStatus.COMPLETED.value
        entry.completed_at = func.now()
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def mark_skipped(self, entry: QueueEntry) -> QueueEntry:
        entry.status = QueueStatus.SKIPPED.value
        self.db.commit()
        self.db.refresh(entry)
        return entry
