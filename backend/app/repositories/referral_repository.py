import uuid
from datetime import date, datetime, time
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.referral import Referral, ReferralStatus
from app.schemas.referral import ReferralCreate


class ReferralRepository:
    """Data access repository for clinical referrals."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_id: uuid.UUID,
        encounter_id: uuid.UUID,
        referring_facility_id: uuid.UUID,
        referring_provider_id: int,
        data: ReferralCreate,
        created_by_id: Optional[int] = None,
    ) -> Referral:
        referral = Referral(
            patient_id=patient_id,
            encounter_id=encounter_id,
            referring_facility_id=referring_facility_id,
            referring_provider_id=referring_provider_id,
            receiving_facility_id=data.receiving_facility_id,
            referral_type=data.referral_type.value,
            priority=data.priority.value,
            status=ReferralStatus.SENT.value,
            reason=data.reason,
            clinical_summary=data.clinical_summary,
            requested_specialty=data.requested_specialty,
            requested_date=data.requested_date,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(referral)
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def get_by_id(self, referral_id: uuid.UUID) -> Optional[Referral]:
        stmt = select(Referral).where(Referral.id == referral_id)
        return self.db.scalars(stmt).first()

    def get_patient_referrals(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Referral], int]:
        base_query = select(Referral).where(Referral.patient_id == patient_id)
        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

        stmt = base_query.order_by(Referral.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_facility_incoming_referrals(
        self,
        facility_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Referral], int]:
        base_query = select(Referral).where(Referral.receiving_facility_id == facility_id)
        if status:
            base_query = base_query.where(Referral.status == status)
        if priority:
            base_query = base_query.where(Referral.priority == priority)

        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        stmt = base_query.order_by(Referral.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_facility_outgoing_referrals(
        self,
        facility_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Referral], int]:
        base_query = select(Referral).where(Referral.referring_facility_id == facility_id)
        if status:
            base_query = base_query.where(Referral.status == status)
        if priority:
            base_query = base_query.where(Referral.priority == priority)

        total = self.db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
        stmt = base_query.order_by(Referral.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def accept(self, referral: Referral, accepted_by_id: int) -> Referral:
        referral.status = ReferralStatus.ACCEPTED.value
        referral.accepted_at = func.now()
        referral.accepted_by = accepted_by_id
        referral.updated_by = accepted_by_id
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def reject(self, referral: Referral, rejected_by_id: int, reason: str) -> Referral:
        referral.status = ReferralStatus.REJECTED.value
        referral.rejected_at = func.now()
        referral.rejected_by = rejected_by_id
        referral.rejection_reason = reason
        referral.updated_by = rejected_by_id
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def schedule(
        self,
        referral: Referral,
        scheduled_by_id: int,
        scheduled_date: date,
        scheduled_time: time,
    ) -> Referral:
        referral.status = ReferralStatus.SCHEDULED.value
        referral.scheduled_at = func.now()
        referral.scheduled_by = scheduled_by_id
        referral.scheduled_date = scheduled_date
        referral.scheduled_time = scheduled_time
        referral.updated_by = scheduled_by_id
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def complete(
        self,
        referral: Referral,
        completed_by_id: int,
        outcome_status: str,
        outcome_notes: str,
        follow_up_required: bool,
        follow_up_date: Optional[date] = None,
    ) -> Referral:
        referral.status = ReferralStatus.COMPLETED.value
        referral.completed_at = func.now()
        referral.completed_by = completed_by_id
        referral.outcome_status = outcome_status
        referral.outcome_notes = outcome_notes
        referral.follow_up_required = follow_up_required
        referral.follow_up_date = follow_up_date
        referral.updated_by = completed_by_id
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def cancel(self, referral: Referral, cancelled_by_id: int, reason: str) -> Referral:
        referral.status = ReferralStatus.CANCELLED.value
        referral.cancelled_at = func.now()
        referral.cancelled_by = cancelled_by_id
        referral.cancellation_reason = reason
        referral.updated_by = cancelled_by_id
        self.db.commit()
        self.db.refresh(referral)
        return referral
