import math
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class NotificationChannelEnum(str, Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"


class NotificationStatusEnum(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class NotificationTypeEnum(str, Enum):
    APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    REFERRAL_CREATED = "REFERRAL_CREATED"
    REFERRAL_ACCEPTED = "REFERRAL_ACCEPTED"
    REFERRAL_COMPLETED = "REFERRAL_COMPLETED"
    DIAGNOSTIC_RESULT_AVAILABLE = "DIAGNOSTIC_RESULT_AVAILABLE"
    PRESCRIPTION_ISSUED = "PRESCRIPTION_ISSUED"
    FOLLOW_UP_REMINDER = "FOLLOW_UP_REMINDER"
    SYSTEM = "SYSTEM"


class NotificationCreate(BaseModel):
    user_id: int
    patient_id: Optional[uuid.UUID] = None
    notification_type: NotificationTypeEnum = NotificationTypeEnum.SYSTEM
    channel: NotificationChannelEnum = NotificationChannelEnum.IN_APP
    subject: str = Field(..., max_length=255)
    message: str
    scheduled_at: Optional[datetime] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[uuid.UUID] = None
    idempotency_key: Optional[str] = None


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    patient_id: Optional[uuid.UUID] = None
    notification_type: str
    channel: str
    subject: str
    message: str
    status: str
    is_read: bool
    read_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    retry_count: int
    error_message: Optional[str] = None
    provider_message_id: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[NotificationResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    id: uuid.UUID
    user_id: int
    email_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool
    appointment_reminders: bool
    referral_notifications: bool
    diagnostic_notifications: bool
    prescription_notifications: bool
    preferred_email: Optional[str] = None
    preferred_phone: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    appointment_reminders: Optional[bool] = None
    referral_notifications: Optional[bool] = None
    diagnostic_notifications: Optional[bool] = None
    prescription_notifications: Optional[bool] = None
    preferred_email: Optional[str] = None
    preferred_phone: Optional[str] = None
