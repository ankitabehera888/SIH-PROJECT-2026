from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from app.models.consent import Consent, ConsentStatus


class ABDMConsentManager:
    """Manages ABDM Consent Flow and Artefacts for Health Information Exchange."""

    @staticmethod
    def create_consent_request(
        patient_id: str,
        purpose: str,
        hi_types: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        req_id = str(uuid.uuid4())
        return {
            "consent_request_id": req_id,
            "patient_id": patient_id,
            "purpose": purpose,
            "hi_types": hi_types,
            "status": "REQUESTED",
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def is_consent_valid(consent: Consent) -> bool:
        """Evaluates whether the consent grant is active and not expired."""
        if consent.status != ConsentStatus.GRANTED.value:
            return False

        if consent.revoked_at is not None:
            return False

        if consent.expires_at is not None:
            if datetime.now(timezone.utc) > consent.expires_at:
                return False

        return True
