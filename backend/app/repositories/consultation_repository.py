import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.consultation import Consultation, ConsultationStatus
from app.models.consultation_participant import ConnectionStatus, ConsultationParticipant


class ConsultationRepository:
    """Repository handling database operations for teleconsultations and participant attendance."""

    @staticmethod
    def create(db: Session, consultation: Consultation) -> Consultation:
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
        return consultation

    @staticmethod
    def get_by_id(db: Session, consultation_id: uuid.UUID) -> Optional[Consultation]:
        return db.scalars(select(Consultation).where(Consultation.id == consultation_id)).first()

    @staticmethod
    def get_by_appointment_id(db: Session, appointment_id: uuid.UUID) -> Optional[Consultation]:
        return db.scalars(select(Consultation).where(Consultation.appointment_id == appointment_id)).first()

    @staticmethod
    def get_by_room_name(db: Session, room_name: str) -> Optional[Consultation]:
        return db.scalars(select(Consultation).where(Consultation.room_name == room_name)).first()

    @staticmethod
    def list_consultations(
        db: Session,
        patient_id: Optional[uuid.UUID] = None,
        provider_id: Optional[int] = None,
        facility_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Consultation], int]:
        stmt = select(Consultation)
        count_stmt = select(func.count(Consultation.id))

        if patient_id:
            stmt = stmt.where(Consultation.patient_id == patient_id)
            count_stmt = count_stmt.where(Consultation.patient_id == patient_id)
        if provider_id:
            stmt = stmt.where(Consultation.provider_id == provider_id)
            count_stmt = count_stmt.where(Consultation.provider_id == provider_id)
        if facility_id:
            stmt = stmt.where(Consultation.facility_id == facility_id)
            count_stmt = count_stmt.where(Consultation.facility_id == facility_id)
        if status:
            stmt = stmt.where(Consultation.status == status)
            count_stmt = count_stmt.where(Consultation.status == status)

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.order_by(Consultation.scheduled_start.desc()).offset(skip).limit(limit)).all())
        return items, total

    @staticmethod
    def update_status(db: Session, consultation: Consultation, new_status: str) -> Consultation:
        consultation.status = new_status
        if new_status == ConsultationStatus.IN_PROGRESS.value and not consultation.started_at:
            consultation.started_at = datetime.now(timezone.utc)
        elif new_status in (ConsultationStatus.COMPLETED.value, ConsultationStatus.CANCELLED.value):
            if not consultation.ended_at:
                consultation.ended_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(consultation)
        return consultation

    @staticmethod
    def get_participant(db: Session, consultation_id: uuid.UUID, user_id: int) -> Optional[ConsultationParticipant]:
        stmt = select(ConsultationParticipant).where(
            ConsultationParticipant.consultation_id == consultation_id,
            ConsultationParticipant.user_id == user_id,
        )
        return db.scalars(stmt).first()

    @staticmethod
    def list_participants(db: Session, consultation_id: uuid.UUID) -> List[ConsultationParticipant]:
        stmt = select(ConsultationParticipant).where(ConsultationParticipant.consultation_id == consultation_id)
        return list(db.scalars(stmt).all())

    @staticmethod
    def record_participant_join(
        db: Session,
        consultation_id: uuid.UUID,
        user_id: int,
        role: str,
    ) -> ConsultationParticipant:
        participant = ConsultationRepository.get_participant(db, consultation_id, user_id)
        now = datetime.now(timezone.utc)

        if not participant:
            participant = ConsultationParticipant(
                id=uuid.uuid4(),
                consultation_id=consultation_id,
                user_id=user_id,
                role=role,
                joined_at=now,
                connection_status=ConnectionStatus.CONNECTED.value,
                reconnect_count=0,
            )
            db.add(participant)
        else:
            participant.connection_status = ConnectionStatus.CONNECTED.value
            participant.reconnect_count += 1
            if not participant.joined_at:
                participant.joined_at = now

        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def record_participant_leave(
        db: Session,
        consultation_id: uuid.UUID,
        user_id: int,
    ) -> Optional[ConsultationParticipant]:
        participant = ConsultationRepository.get_participant(db, consultation_id, user_id)
        if participant:
            now = datetime.now(timezone.utc)
            participant.left_at = now
            participant.connection_status = ConnectionStatus.DISCONNECTED.value
            if participant.joined_at:
                duration = (now - participant.joined_at).total_seconds()
                participant.duration_seconds = max(0, int(duration))
            db.commit()
            db.refresh(participant)
        return participant
