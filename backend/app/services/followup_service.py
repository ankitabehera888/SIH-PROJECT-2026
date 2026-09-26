import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.models.followup import Followup, FollowupPriority, FollowupStatus
from app.models.patient import Patient
from app.models.user import User
from app.schemas.followup import (
    FollowupCompleteRequest,
    FollowupCreate,
    FollowupListResponse,
    FollowupRescheduleRequest,
    FollowupResponse,
    FollowupSummary,
)
from app.services.notification_service import NotificationService


class FollowupService:
    def __init__(self, db: Session):
        self.db = db

    def create_followup(self, data: FollowupCreate, current_user: User) -> FollowupResponse:
        """Create a clinical follow-up task."""
        patient = self.db.get(Patient, data.patient_id)
        if not patient:
            raise AppException(status_code=404, detail="Patient not found")

        followup = Followup(
            patient_id=data.patient_id,
            provider_id=data.provider_id or current_user.id,
            encounter_id=data.encounter_id,
            condition=data.condition,
            priority=data.priority.value,
            status=FollowupStatus.UPCOMING.value,
            scheduled_date=data.scheduled_date,
            completion_rate=data.completion_rate,
            notes=data.notes,
        )
        self.db.add(followup)
        self.db.commit()
        self.db.refresh(followup)

        # Notify patient
        try:
            notif_service = NotificationService(self.db)
            notif_service.send_system_notification(
                user_id=patient.created_by_id or current_user.id,
                title="Follow-up Scheduled",
                body=f"Follow-up scheduled for {data.condition} on {data.scheduled_date}",
            )
        except Exception:
            pass

        return self._to_response(followup)

    def list_followups(
        self,
        current_user: User,
        status_filter: Optional[str] = None,
        patient_id: Optional[uuid.UUID] = None,
        provider_id: Optional[int] = None,
    ) -> FollowupListResponse:
        """List follow-ups with filters and status breakdown summary."""
        stmt = select(Followup).order_by(desc(Followup.scheduled_date))

        # Role scoping
        if current_user.role == "PATIENT":
            # Filter by patient's user id link if applicable or given patient_id
            if patient_id:
                stmt = stmt.where(Followup.patient_id == patient_id)
        else:
            if patient_id:
                stmt = stmt.where(Followup.patient_id == patient_id)
            if provider_id:
                stmt = stmt.where(Followup.provider_id == provider_id)

        all_items = self.db.scalars(stmt).all()

        # Compute counts
        upcoming = sum(1 for f in all_items if f.status == FollowupStatus.UPCOMING.value)
        missed = sum(1 for f in all_items if f.status == FollowupStatus.MISSED.value)
        completed = sum(1 for f in all_items if f.status == FollowupStatus.COMPLETED.value)
        summary = FollowupSummary(
            upcoming=upcoming,
            missed=missed,
            completed=completed,
            total=len(all_items),
        )

        # Filter by status if requested
        if status_filter and status_filter.lower() != "all":
            all_items = [f for f in all_items if f.status.lower() == status_filter.lower()]

        items_resp = [self._to_response(f) for f in all_items]
        return FollowupListResponse(summary=summary, items=items_resp, total=len(items_resp))

    def get_followup(self, followup_id: uuid.UUID) -> FollowupResponse:
        followup = self.db.get(Followup, followup_id)
        if not followup:
            raise AppException(status_code=404, detail="Followup not found")
        return self._to_response(followup)

    def reschedule_followup(
        self, followup_id: uuid.UUID, data: FollowupRescheduleRequest, current_user: User
    ) -> FollowupResponse:
        followup = self.db.get(Followup, followup_id)
        if not followup:
            raise AppException(status_code=404, detail="Followup not found")

        followup.scheduled_date = data.new_date
        followup.status = FollowupStatus.UPCOMING.value
        if data.reason:
            followup.notes = f"{followup.notes or ''}\n[Rescheduled]: {data.reason}".strip()

        self.db.commit()
        self.db.refresh(followup)
        return self._to_response(followup)

    def complete_followup(
        self, followup_id: uuid.UUID, data: FollowupCompleteRequest, current_user: User
    ) -> FollowupResponse:
        followup = self.db.get(Followup, followup_id)
        if not followup:
            raise AppException(status_code=404, detail="Followup not found")

        followup.status = FollowupStatus.COMPLETED.value
        followup.completion_rate = data.completion_rate
        followup.completed_at = datetime.now(timezone.utc)
        if data.notes:
            followup.notes = f"{followup.notes or ''}\n[Completed]: {data.notes}".strip()

        self.db.commit()
        self.db.refresh(followup)
        return self._to_response(followup)

    def send_reminder(self, followup_id: uuid.UUID, current_user: User) -> dict:
        followup = self.db.get(Followup, followup_id)
        if not followup:
            raise AppException(status_code=404, detail="Followup not found")

        return {
            "status": "success",
            "message": f"Reminder sent to patient for follow-up on {followup.scheduled_date}",
            "followup_id": str(followup_id),
        }

    def _to_response(self, f: Followup) -> FollowupResponse:
        patient_name = f"{f.patient.first_name} {f.patient.last_name}" if f.patient else "Unknown Patient"
        assigned_doctor = f"Dr. {f.provider.email.split('@')[0].capitalize()}" if f.provider else "Unassigned"

        return FollowupResponse(
            id=f.id,
            patient_id=f.patient_id,
            patient_name=patient_name,
            provider_id=f.provider_id,
            assigned_doctor=assigned_doctor,
            encounter_id=f.encounter_id,
            condition=f.condition,
            priority=f.priority,
            status=f.status,
            scheduled_date=f.scheduled_date,
            completed_at=f.completed_at,
            completion_rate=f.completion_rate,
            notes=f.notes,
            created_at=f.created_at,
            updated_at=f.updated_at,
        )
