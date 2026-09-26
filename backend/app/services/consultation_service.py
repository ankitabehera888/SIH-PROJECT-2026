import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException, ConflictException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.core.socket_manager import broadcast_event
from app.integrations.daily import DailyService, get_daily_service
from app.models.appointment import Appointment, AppointmentStatus
from app.models.consultation import (
    VALID_CONSULTATION_TRANSITIONS,
    Consultation,
    ConsultationStatus,
    ConsultationType,
)
from app.models.consultation_participant import ConnectionStatus, ParticipantRole
from app.models.encounter import Encounter, EncounterStatus, EncounterType
from app.models.patient import Patient
from app.models.user import User
from app.repositories.consultation_repository import ConsultationRepository
from app.schemas.notification import NotificationChannelEnum, NotificationCreate, NotificationTypeEnum
from app.services.notification_service import NotificationService

logger = logging.getLogger("healthcare_platform.consultation")
from app.schemas.consultation import (
    ConsultationCancelRequest,
    ConsultationCreate,
    ConsultationJoinResponse,
    ConsultationListResponse,
    ConsultationParticipantResponse,
    ConsultationResponse,
)


class ConsultationService:
    """Service orchestrating teleconsultation sessions, WebRTC security tokens, and clinical attendance tracking."""

    def __init__(self, db: Session, daily_service: Optional[DailyService] = None):
        self.db = db
        self.daily = daily_service or get_daily_service()

    def create_consultation(
        self,
        appointment_id: uuid.UUID,
        data: ConsultationCreate,
        current_user: User,
    ) -> ConsultationResponse:
        # 1. Fetch appointment
        appointment = self.db.get(Appointment, appointment_id)
        if not appointment:
            raise NotFoundException(message=f"Appointment with id '{appointment_id}' not found")

        # 2. Check duplicate consultation
        existing = ConsultationRepository.get_by_appointment_id(self.db, appointment_id)
        if existing:
            raise ConflictException(message=f"A consultation session already exists for appointment '{appointment_id}'")

        # 3. Security: Only doctor, nurse, or admin can provision teleconsultation
        if current_user.role not in (UserRole.DOCTOR.value, UserRole.ADMIN.value, UserRole.NURSE.value):
            raise ForbiddenException(message="Access denied: Only clinical staff or admins can provision teleconsultations")

        # 4. Generate unique Daily.co private room
        room_name = f"consultation-{uuid.uuid4().hex}"
        room_data = self.daily.create_room(room_name=room_name)
        room_url = room_data.get("url", f"https://telehealth-demo.daily.co/{room_name}")

        scheduled_start = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        ).replace(tzinfo=timezone.utc)
        scheduled_end = datetime.combine(
            appointment.appointment_date,
            appointment.end_time,
        ).replace(tzinfo=timezone.utc)

        # 5. Check if clinical encounter already exists for this appointment
        encounter_stmt = select(Encounter).where(Encounter.appointment_id == appointment_id)
        encounter = self.db.scalars(encounter_stmt).first()

        consultation = Consultation(
            id=uuid.uuid4(),
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            provider_id=appointment.provider_id,
            facility_id=appointment.facility_id,
            consultation_type=data.consultation_type.value,
            status=ConsultationStatus.SCHEDULED.value,
            room_name=room_name,
            room_url=room_url,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            encounter_id=encounter.id if encounter else None,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        saved = ConsultationRepository.create(self.db, consultation)

        # Dispatch Phase 9 Notification to patient
        try:
            patient = self.db.get(Patient, consultation.patient_id)
            if patient and patient.user_id:
                notif_svc = NotificationService(self.db)
                notif_svc.create_and_dispatch(
                    NotificationCreate(
                        user_id=patient.user_id,
                        patient_id=patient.id,
                        notification_type=NotificationTypeEnum.APPOINTMENT_REMINDER,
                        channel=NotificationChannelEnum.IN_APP,
                        subject="Teleconsultation Scheduled",
                        message=f"Your teleconsultation session has been scheduled for {appointment.appointment_date.isoformat()} at {appointment.start_time.strftime('%H:%M')}. Please log in on time.",
                        related_entity_type="CONSULTATION",
                        related_entity_id=consultation.id,
                        idempotency_key=f"NOTIF_CONS_SCHED_{consultation.id}",
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to dispatch teleconsultation creation notification: {exc}")

        return ConsultationResponse.model_validate(saved)

    def get_consultation(self, consultation_id: uuid.UUID, current_user: User) -> ConsultationResponse:
        consultation = ConsultationRepository.get_by_id(self.db, consultation_id)
        if not consultation:
            raise NotFoundException(message=f"Consultation with id '{consultation_id}' not found")

        # Security: Patient can only view their own consultation; provider can only view their assigned consultation
        if current_user.role == UserRole.PATIENT.value:
            patient = self.db.get(Patient, consultation.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own teleconsultation")
        elif current_user.role == UserRole.DOCTOR.value and consultation.provider_id != current_user.id:
            raise ForbiddenException(message="Access denied: You are not the assigned provider for this consultation")

        return ConsultationResponse.model_validate(consultation)

    def list_consultations(
        self,
        current_user: User,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ConsultationListResponse:
        patient_id = None
        provider_id = None

        if current_user.role == UserRole.PATIENT.value:
            patient_stmt = select(Patient).where(Patient.user_id == current_user.id)
            patient = self.db.scalars(patient_stmt).first()
            if not patient:
                return ConsultationListResponse.create(items=[], total=0, page=page, page_size=page_size)
            patient_id = patient.id
        elif current_user.role == UserRole.DOCTOR.value:
            provider_id = current_user.id

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = ConsultationRepository.list_consultations(
            self.db,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status,
            skip=skip,
            limit=page_size,
        )
        return ConsultationListResponse.create(
            items=[ConsultationResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def generate_join_credentials(
        self,
        consultation_id: uuid.UUID,
        current_user: User,
    ) -> ConsultationJoinResponse:
        consultation = ConsultationRepository.get_by_id(self.db, consultation_id)
        if not consultation:
            raise NotFoundException(message=f"Consultation with id '{consultation_id}' not found")

        # Validate consultation lifecycle
        if consultation.status in (
            ConsultationStatus.CANCELLED.value,
            ConsultationStatus.COMPLETED.value,
            ConsultationStatus.EXPIRED.value,
        ):
            raise BadRequestException(
                message=f"Cannot join teleconsultation with terminal status '{consultation.status}'"
            )

        # 1. Authorize user identity & determine participant role
        role: str
        is_owner: bool = False

        if current_user.role == UserRole.PATIENT.value:
            patient = self.db.get(Patient, consultation.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You are not authorized to join this teleconsultation")
            role = ParticipantRole.PATIENT.value
            is_owner = False
        elif current_user.role in (UserRole.DOCTOR.value, UserRole.ADMIN.value):
            if current_user.role == UserRole.DOCTOR.value and consultation.provider_id != current_user.id:
                raise ForbiddenException(message="Access denied: You are not the assigned provider for this teleconsultation")
            role = ParticipantRole.PROVIDER.value
            is_owner = True
        elif current_user.role in (UserRole.NURSE.value, "HEALTH_WORKER"):
            role = ParticipantRole.HEALTH_WORKER.value
            is_owner = False
        else:
            raise ForbiddenException(message="Access denied: Unauthorized role for teleconsultation")

        # 2. Update status: If SCHEDULED -> READY (Patient waiting in waiting room)
        if consultation.status == ConsultationStatus.SCHEDULED.value:
            ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.READY.value)
            broadcast_event(
                "consultation:ready",
                {
                    "consultation_id": str(consultation.id),
                    "room_name": consultation.room_name,
                    "patient_id": str(consultation.patient_id),
                    "status": "READY",
                },
                room=consultation.room_name,
            )

        # 3. Record attendance join
        ConsultationRepository.record_participant_join(
            self.db,
            consultation_id=consultation.id,
            user_id=current_user.id,
            role=role,
        )

        broadcast_event(
            "consultation:participant_joined",
            {
                "consultation_id": str(consultation.id),
                "user_id": current_user.id,
                "role": role,
            },
            room=consultation.room_name,
        )

        # If provider joins and participants are waiting -> transition to IN_PROGRESS
        if role == ParticipantRole.PROVIDER.value and consultation.status == ConsultationStatus.READY.value:
            ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.IN_PROGRESS.value)
            broadcast_event(
                "consultation:started",
                {
                    "consultation_id": str(consultation.id),
                    "room_name": consultation.room_name,
                    "provider_id": current_user.id,
                    "status": "IN_PROGRESS",
                },
                room=consultation.room_name,
            )

        # 4. Generate Daily meeting token
        token = self.daily.create_meeting_token(
            room_name=consultation.room_name,
            user_name=current_user.email,
            is_owner=is_owner,
        )
        expires_at = datetime.now(timezone.utc).replace(microsecond=0)

        return ConsultationJoinResponse(
            consultation_id=consultation.id,
            room_name=consultation.room_name,
            room_url=consultation.room_url,
            token=token,
            role=role,
            expires_at=expires_at,
        )

    def end_consultation(self, consultation_id: uuid.UUID, current_user: User) -> ConsultationResponse:
        consultation = ConsultationRepository.get_by_id(self.db, consultation_id)
        if not consultation:
            raise NotFoundException(message=f"Consultation with id '{consultation_id}' not found")

        # Only provider or admin can end consultation
        if current_user.role == UserRole.DOCTOR.value and consultation.provider_id != current_user.id:
            raise ForbiddenException(message="Access denied: Only assigned provider or admin can end consultation")
        if current_user.role not in (UserRole.DOCTOR.value, UserRole.ADMIN.value):
            raise ForbiddenException(message="Access denied: Only provider can conclude consultation")

        if consultation.status not in (ConsultationStatus.READY.value, ConsultationStatus.IN_PROGRESS.value):
            raise BadRequestException(message=f"Cannot end consultation in status '{consultation.status}'")

        # Record leave for any active participants
        for p in consultation.participants:
            if p.connection_status == ConnectionStatus.CONNECTED.value:
                ConsultationRepository.record_participant_leave(self.db, consultation.id, p.user_id)

        # Connect / Create Clinical Encounter
        if not consultation.encounter_id:
            encounter_stmt = select(Encounter).where(Encounter.appointment_id == consultation.appointment_id)
            encounter = self.db.scalars(encounter_stmt).first()
            if not encounter:
                encounter = Encounter(
                    id=uuid.uuid4(),
                    appointment_id=consultation.appointment_id,
                    patient_id=consultation.patient_id,
                    provider_id=consultation.provider_id,
                    facility_id=consultation.facility_id,
                    encounter_type=EncounterType.OUTPATIENT.value,
                    status=EncounterStatus.IN_PROGRESS.value,
                    clinical_notes="Clinical encounter created via concluded teleconsultation session.",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                )
                self.db.add(encounter)
                self.db.commit()
                self.db.refresh(encounter)
            consultation.encounter_id = encounter.id

        updated = ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.COMPLETED.value)
        self.daily.delete_room(consultation.room_name)

        # Broadcast Socket.IO consultation ended event
        broadcast_event(
            "consultation:ended",
            {
                "consultation_id": str(consultation.id),
                "room_name": consultation.room_name,
                "status": "COMPLETED",
                "encounter_id": str(consultation.encounter_id) if consultation.encounter_id else None,
            },
            room=consultation.room_name,
        )

        # Dispatch Phase 9 Notification to patient
        try:
            patient = self.db.get(Patient, consultation.patient_id)
            if patient and patient.user_id:
                notif_svc = NotificationService(self.db)
                notif_svc.create_and_dispatch(
                    NotificationCreate(
                        user_id=patient.user_id,
                        patient_id=patient.id,
                        notification_type=NotificationTypeEnum.APPOINTMENT_REMINDER,
                        channel=NotificationChannelEnum.IN_APP,
                        subject="Teleconsultation Completed",
                        message="Your teleconsultation session has concluded. Your clinical encounter summary is now available.",
                        related_entity_type="CONSULTATION",
                        related_entity_id=consultation.id,
                        idempotency_key=f"NOTIF_CONS_COMP_{consultation.id}",
                    )
                )
        except Exception as exc:
            logger.warning(f"Failed to dispatch teleconsultation completion notification: {exc}")

        return ConsultationResponse.model_validate(updated)

    def cancel_consultation(
        self,
        consultation_id: uuid.UUID,
        data: ConsultationCancelRequest,
        current_user: User,
    ) -> ConsultationResponse:
        consultation = ConsultationRepository.get_by_id(self.db, consultation_id)
        if not consultation:
            raise NotFoundException(message=f"Consultation with id '{consultation_id}' not found")

        # Patients can cancel their own, or provider/admin can cancel
        if current_user.role == UserRole.PATIENT.value:
            patient = self.db.get(Patient, consultation.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: Cannot cancel another user's consultation")
        elif current_user.role == UserRole.DOCTOR.value and consultation.provider_id != current_user.id:
            raise ForbiddenException(message="Access denied: Cannot cancel consultation assigned to another doctor")

        if consultation.status in (ConsultationStatus.COMPLETED.value, ConsultationStatus.CANCELLED.value):
            raise BadRequestException(message=f"Consultation is already in terminal state '{consultation.status}'")

        updated = ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.CANCELLED.value)
        self.daily.delete_room(consultation.room_name)
        return ConsultationResponse.model_validate(updated)

    def list_participants(self, consultation_id: uuid.UUID, current_user: User) -> list:
        # Validate existence & security
        self.get_consultation(consultation_id, current_user)
        participants = ConsultationRepository.list_participants(self.db, consultation_id)
        return [ConsultationParticipantResponse.model_validate(p) for p in participants]

    _processed_events = set()

    def handle_webhook_event(self, event_type: str, room_name: str, payload: dict) -> dict:
        """Idempotently process real-time WebRTC room events from Daily.co webhook callbacks."""
        # 1. Idempotency Guard
        event_id = (
            payload.get("id")
            or payload.get("event_id")
            or f"{event_type}:{room_name}:{payload.get('timestamp') or payload.get('participant', {}).get('user_id', '')}"
        )
        if event_id in ConsultationService._processed_events:
            return {"status": "DUPLICATE_EVENT_IGNORED", "event_id": event_id}

        ConsultationService._processed_events.add(event_id)

        consultation = ConsultationRepository.get_by_room_name(self.db, room_name)
        if not consultation:
            return {"status": "ROOM_NOT_FOUND", "room_name": room_name}

        # 2. Process specific Daily.co WebRTC events
        if event_type in ("meeting.started", "meeting-started"):
            if consultation.status in (ConsultationStatus.SCHEDULED.value, ConsultationStatus.READY.value):
                ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.IN_PROGRESS.value)
            return {"status": "PROCESSED", "event": event_type, "event_id": event_id}

        elif event_type in ("meeting.ended", "meeting-ended"):
            if consultation.status in (ConsultationStatus.READY.value, ConsultationStatus.IN_PROGRESS.value):
                # Disconnect active participants
                for p in consultation.participants:
                    if p.connection_status == ConnectionStatus.CONNECTED.value:
                        ConsultationRepository.record_participant_leave(self.db, consultation.id, p.user_id)
                ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.COMPLETED.value)
            return {"status": "PROCESSED", "event": event_type, "event_id": event_id}

        elif event_type in ("participant.joined", "participant-joined"):
            participant_info = payload.get("participant", {})
            user_id = participant_info.get("user_id")
            role = participant_info.get("role", ParticipantRole.PATIENT.value)
            if user_id:
                ConsultationRepository.record_participant_join(
                    self.db,
                    consultation_id=consultation.id,
                    user_id=int(user_id),
                    role=role,
                )
            if consultation.status == ConsultationStatus.SCHEDULED.value:
                ConsultationRepository.update_status(self.db, consultation, ConsultationStatus.READY.value)
            return {"status": "PROCESSED", "event": event_type, "event_id": event_id}

        elif event_type in ("participant.left", "participant-left"):
            participant_info = payload.get("participant", {})
            user_id = participant_info.get("user_id")
            if user_id:
                ConsultationRepository.record_participant_leave(
                    self.db,
                    consultation_id=consultation.id,
                    user_id=int(user_id),
                )
            return {"status": "PROCESSED", "event": event_type, "event_id": event_id}

        return {"status": "ACKNOWLEDGED", "event": event_type, "event_id": event_id}
