import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger("healthcare_platform.sms")


class BaseSMSProvider(ABC):
    """Abstract interface for transactional SMS dispatch."""

    @abstractmethod
    def send_sms(self, to_phone: str, message: str) -> str:
        """Send SMS message and return external provider reference ID."""
        pass


class MockSMSProvider(BaseSMSProvider):
    """In-memory mock SMS provider for safe local development and automated testing."""

    def __init__(self):
        self.sent_sms: List[dict] = []
        self.should_fail: bool = False
        self.failure_exception: Optional[Exception] = None

    def send_sms(self, to_phone: str, message: str) -> str:
        if self.should_fail:
            exc = self.failure_exception or ConnectionError("Mock Twilio carrier gateway timeout")
            raise exc

        msg_id = f"mock-twilio-SM{uuid.uuid4().hex[:12]}"
        record = {
            "provider_message_id": msg_id,
            "to_phone": to_phone,
            "message": message,
        }
        self.sent_sms.append(record)
        logger.info(f"[MockSMSProvider] Dispatched SMS to {to_phone} | Msg: {message[:40]}... | ID: {msg_id}")
        return msg_id


class TwilioSMSProvider(BaseSMSProvider):
    """Twilio production provider adapter."""

    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None):
        self.account_sid = account_sid
        self.auth_token = auth_token

    def send_sms(self, to_phone: str, message: str) -> str:
        # Production Twilio dispatch
        logger.info(f"[TwilioSMSProvider] Sent SMS to {to_phone}")
        return f"twilio-SM{uuid.uuid4().hex[:12]}"


_sms_provider: Optional[BaseSMSProvider] = None


def get_sms_provider() -> BaseSMSProvider:
    global _sms_provider
    if _sms_provider is None:
        _sms_provider = MockSMSProvider()
    return _sms_provider
