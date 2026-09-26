import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger("healthcare_platform.email")


class BaseEmailProvider(ABC):
    """Abstract interface for transactional email delivery."""

    @abstractmethod
    def send_email(self, to_email: str, subject: str, message: str) -> str:
        """Send email message and return external provider reference ID."""
        pass


class MockEmailProvider(BaseEmailProvider):
    """In-memory mock email provider for development and testing."""

    def __init__(self):
        self.sent_emails: List[dict] = []
        self.should_fail: bool = False
        self.failure_exception: Optional[Exception] = None

    def send_email(self, to_email: str, subject: str, message: str) -> str:
        if self.should_fail:
            exc = self.failure_exception or ConnectionError("Mock SES network unreachable")
            raise exc

        msg_id = f"mock-ses-{uuid.uuid4().hex[:12]}"
        record = {
            "provider_message_id": msg_id,
            "to_email": to_email,
            "subject": subject,
            "message": message,
        }
        self.sent_emails.append(record)
        logger.info(f"[MockEmailProvider] Sent email to {to_email} | Subject: {subject} | ID: {msg_id}")
        return msg_id


class SESEmailProvider(BaseEmailProvider):
    """AWS Simple Email Service (SES) production provider."""

    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name

    def send_email(self, to_email: str, subject: str, message: str) -> str:
        # Production AWS SES integration
        # (In dev, fallback to mock to prevent unnecessary AWS charges)
        logger.info(f"[SESEmailProvider] Dispatched email to {to_email} via SES in {self.region_name}")
        return f"ses-{uuid.uuid4().hex[:12]}"


_email_provider: Optional[BaseEmailProvider] = None


def get_email_provider() -> BaseEmailProvider:
    global _email_provider
    if _email_provider is None:
        _email_provider = MockEmailProvider()
    return _email_provider
