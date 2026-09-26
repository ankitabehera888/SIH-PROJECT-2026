import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.notification_preference import NotificationPreference
from app.schemas.notification import NotificationCreate, NotificationPreferenceUpdate


class NotificationRepository:
    """Repository handling database operations for notifications and communication preferences."""

    @staticmethod
    def create(db: Session, data: NotificationCreate, status: str = NotificationStatus.PENDING.value) -> Notification:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=data.user_id,
            patient_id=data.patient_id,
            notification_type=data.notification_type.value if hasattr(data.notification_type, "value") else str(data.notification_type),
            channel=data.channel.value if hasattr(data.channel, "value") else str(data.channel),
            subject=data.subject,
            message=data.message,
            status=status,
            scheduled_at=data.scheduled_at,
            related_entity_type=data.related_entity_type,
            related_entity_id=data.related_entity_id,
            idempotency_key=data.idempotency_key,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_by_id(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        return db.scalars(select(Notification).where(Notification.id == notification_id)).first()

    @staticmethod
    def get_by_idempotency_key(db: Session, key: str) -> Optional[Notification]:
        return db.scalars(select(Notification).where(Notification.idempotency_key == key)).first()

    @staticmethod
    def list_by_user(
        db: Session,
        user_id: int,
        channel: Optional[str] = None,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Notification], int]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        count_stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)

        if channel:
            stmt = stmt.where(Notification.channel == channel)
            count_stmt = count_stmt.where(Notification.channel == channel)

        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
            count_stmt = count_stmt.where(Notification.is_read == is_read)

        total = db.scalar(count_stmt) or 0
        items = list(db.scalars(stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)).all())
        return items, total

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        return db.scalar(stmt) or 0

    @staticmethod
    def mark_read(db: Session, notification: Notification) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_queued(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
        notification = db.scalars(select(Notification).where(Notification.id == notification_id)).first()
        if notification:
            notification.status = NotificationStatus.QUEUED.value
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_sent(
        db: Session,
        notification_id: uuid.UUID,
        provider_message_id: Optional[str] = None,
    ) -> Optional[Notification]:
        notification = db.scalars(select(Notification).where(Notification.id == notification_id)).first()
        if notification:
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.now(timezone.utc)
            if provider_message_id:
                notification.provider_message_id = provider_message_id
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_failed(
        db: Session,
        notification_id: uuid.UUID,
        error_message: str,
        retry_count: int,
    ) -> Optional[Notification]:
        notification = db.scalars(select(Notification).where(Notification.id == notification_id)).first()
        if notification:
            notification.status = NotificationStatus.FAILED.value
            notification.failed_at = datetime.now(timezone.utc)
            notification.error_message = error_message
            notification.retry_count = retry_count
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def cancel(db: Session, notification: Notification) -> Notification:
        notification.status = NotificationStatus.CANCELLED.value
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_or_create_preferences(db: Session, user_id: int) -> NotificationPreference:
        pref = db.scalars(select(NotificationPreference).where(NotificationPreference.user_id == user_id)).first()
        if not pref:
            pref = NotificationPreference(
                id=uuid.uuid4(),
                user_id=user_id,
                email_enabled=True,
                sms_enabled=True,
                in_app_enabled=True,
                appointment_reminders=True,
                referral_notifications=True,
                diagnostic_notifications=True,
                prescription_notifications=True,
            )
            db.add(pref)
            db.commit()
            db.refresh(pref)
        return pref

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: int,
        update_data: NotificationPreferenceUpdate,
    ) -> NotificationPreference:
        pref = NotificationRepository.get_or_create_preferences(db, user_id)
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(pref, field, value)
        db.commit()
        db.refresh(pref)
        return pref
