import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class NotificationPreference(Base):
    """User-specific communication preferences and channel authorization."""

    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Channel toggles
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Category toggles
    appointment_reminders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    referral_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    diagnostic_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prescription_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contact destination overrides
    preferred_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
