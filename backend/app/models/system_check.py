from datetime import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class SystemCheck(Base):
    """Infrastructure verification model used to validate the ORM and migration pipeline."""

    __tablename__ = "system_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    check_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
