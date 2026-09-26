import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.appointment import Appointment
from app.models.diagnostic_result import DiagnosticResult
from app.models.notification import Notification, NotificationChannel, NotificationStatus, NotificationType
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.referral import Referral
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationChannelEnum,
    NotificationCreate,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
    NotificationTypeEnum,
)
from app.tasks.notification_tasks import send_notification_task


class NotificationService:
    """Service orchestrating notification triggers, user preferences, and Celery dispatch."""

    def __init__(self, db: Session):
        self.db = db

    def create_and_dispatch(self, data: NotificationCreate) -> Notification:
        # 1. Idempotency check: Don't recreate or redispatch duplicate tasks
        if data.idempotency_key:
            existing = NotificationRepository.get_by_idempotency_key(self.db, data.idempotency_key)
            if existing:
                return existing

        # 2. Notification Preferences check
        pref = NotificationRepository.get_or_create_preferences(self.db, data.user_id)
        channel_val = data.channel.value if hasattr(data.channel, "value") else str(data.channel)
        type_val = data.notification_type.value if hasattr(data.notification_type, "value") else str(data.notification_type)

        # Respect channel toggles
        if channel_val == NotificationChannel.EMAIL.value and not pref.email_enabled:
            return None
        if channel_val == NotificationChannel.SMS.value and not pref.sms_enabled:
            return None
        if channel_val == NotificationChannel.IN_APP.value and not pref.in_app_enabled:
            return None

        # Respect category toggles (unless SYSTEM notification)
        if type_val == NotificationType.APPOINTMENT_REMINDER.value and not pref.appointment_reminders:
            return None
        if type_val in (NotificationType.REFERRAL_CREATED.value, NotificationType.REFERRAL_ACCEPTED.value, NotificationType.REFERRAL_COMPLETED.value) and not pref.referral_notifications:
            return None
        if type_val == NotificationType.DIAGNOSTIC_RESULT_AVAILABLE.value and not pref.diagnostic_notifications:
            return None
        if type_val == NotificationType.PRESCRIPTION_ISSUED.value and not pref.prescription_notifications:
            return None

        # 3. Persist notification in database
        notification = NotificationRepository.create(self.db, data, status=NotificationStatus.PENDING.value)

        # 4. Enqueue Celery task for asynchronous provider dispatch
        send_notification_task.delay(str(notification.id))

        return notification

    # Clinical Workflow Helpers
    def notify_appointment_reminder(self, appointment: Appointment, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        date_str = appointment.appointment_date.isoformat() if hasattr(appointment.appointment_date, "isoformat") else str(appointment.appointment_date)
        time_str = appointment.start_time.strftime('%H:%M') if hasattr(appointment.start_time, "strftime") else str(appointment.start_time)
        idempotency_key = f"NOTIF_APPT_REM_{appointment.id}_{date_str}_{channel.value}"
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.APPOINTMENT_REMINDER,
                channel=channel,
                subject="Appointment Reminder",
                message=f"Reminder: You have an upcoming appointment scheduled on {date_str} at {time_str}. Please log in to your portal for details.",
                related_entity_type="APPOINTMENT",
                related_entity_id=appointment.id,
                idempotency_key=idempotency_key,
            )
        )

    def notify_referral_created(self, referral: Referral, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        idempotency_key = f"NOTIF_REF_CREATE_{referral.id}_{channel.value}"
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.REFERRAL_CREATED,
                channel=channel,
                subject="Care Transfer Referral Created",
                message="A referral has been initiated for your care. Please log in to your portal to review transfer details.",
                related_entity_type="REFERRAL",
                related_entity_id=referral.id,
                idempotency_key=idempotency_key,
            )
        )

    def notify_referral_accepted(self, referral: Referral, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        idempotency_key = f"NOTIF_REF_ACCEPT_{referral.id}_{channel.value}"
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.REFERRAL_ACCEPTED,
                channel=channel,
                subject="Referral Accepted",
                message="Your care referral has been accepted by the receiving healthcare facility. Log in for scheduling details.",
                related_entity_type="REFERRAL",
                related_entity_id=referral.id,
                idempotency_key=idempotency_key,
            )
        )

    def notify_referral_completed(self, referral: Referral, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        idempotency_key = f"NOTIF_REF_COMPLETE_{referral.id}_{channel.value}"
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.REFERRAL_COMPLETED,
                channel=channel,
                subject="Referral Completed",
                message="Your care transfer referral has been marked completed. Transfer summary is available in your record.",
                related_entity_type="REFERRAL",
                related_entity_id=referral.id,
                idempotency_key=idempotency_key,
            )
        )

    def notify_prescription_issued(self, prescription: Prescription, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        idempotency_key = f"NOTIF_RX_ISSUED_{prescription.id}_{channel.value}"
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.PRESCRIPTION_ISSUED,
                channel=channel,
                subject="New Prescription Issued",
                message="A new prescription has been issued following your clinical visit. Please log in to your patient portal to view medication instructions.",
                related_entity_type="PRESCRIPTION",
                related_entity_id=prescription.id,
                idempotency_key=idempotency_key,
            )
        )

    def notify_diagnostic_result_available(self, result: DiagnosticResult, patient: Patient, channel: NotificationChannelEnum = NotificationChannelEnum.SMS) -> Optional[Notification]:
        if not patient.user_id:
            return None
        idempotency_key = f"NOTIF_DIAG_RES_{result.id}_{channel.value}"
        # PHI Safe: Notice that no specific test values or diagnoses are in the SMS message
        return self.create_and_dispatch(
            NotificationCreate(
                user_id=patient.user_id,
                patient_id=patient.id,
                notification_type=NotificationTypeEnum.DIAGNOSTIC_RESULT_AVAILABLE,
                channel=channel,
                subject="Diagnostic Results Ready",
                message="Your diagnostic test findings have been verified. Please log in to your secure portal to view full clinical details.",
                related_entity_type="DIAGNOSTIC_RESULT",
                related_entity_id=result.id,
                idempotency_key=idempotency_key,
            )
        )

    # API Query Methods
    def list_user_notifications(
        self,
        user_id: int,
        channel: Optional[str] = None,
        is_read: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> NotificationListResponse:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = NotificationRepository.list_by_user(
            self.db,
            user_id=user_id,
            channel=channel,
            is_read=is_read,
            skip=skip,
            limit=page_size,
        )
        return NotificationListResponse.create(
            items=[NotificationResponse.model_validate(n) for n in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_notification_by_id(self, notification_id: uuid.UUID, current_user: User) -> NotificationResponse:
        notification = NotificationRepository.get_by_id(self.db, notification_id)
        if not notification:
            raise NotFoundException(message=f"Notification '{notification_id}' not found")

        # Security isolation: User can only view their own notifications (unless ADMIN)
        if notification.user_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException(message="Access denied: You cannot view another user's notification")

        return NotificationResponse.model_validate(notification)

    def get_unread_count(self, user_id: int) -> int:
        return NotificationRepository.get_unread_count(self.db, user_id)

    def mark_as_read(self, notification_id: uuid.UUID, current_user: User) -> NotificationResponse:
        notification = NotificationRepository.get_by_id(self.db, notification_id)
        if not notification:
            raise NotFoundException(message=f"Notification '{notification_id}' not found")

        if notification.user_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException(message="Access denied: You cannot modify another user's notification")

        updated = NotificationRepository.mark_read(self.db, notification)
        return NotificationResponse.model_validate(updated)

    def cancel_notification(self, notification_id: uuid.UUID, current_user: User) -> NotificationResponse:
        notification = NotificationRepository.get_by_id(self.db, notification_id)
        if not notification:
            raise NotFoundException(message=f"Notification '{notification_id}' not found")

        if notification.user_id != current_user.id and current_user.role != "ADMIN":
            raise ForbiddenException(message="Access denied: You cannot cancel another user's notification")

        cancelled = NotificationRepository.cancel(self.db, notification)
        return NotificationResponse.model_validate(cancelled)

    def get_preferences(self, user_id: int) -> NotificationPreferenceResponse:
        pref = NotificationRepository.get_or_create_preferences(self.db, user_id)
        return NotificationPreferenceResponse.model_validate(pref)

    def update_preferences(
        self,
        user_id: int,
        update_data: NotificationPreferenceUpdate,
    ) -> NotificationPreferenceResponse:
        pref = NotificationRepository.update_preferences(self.db, user_id, update_data)
        return NotificationPreferenceResponse.model_validate(pref)
