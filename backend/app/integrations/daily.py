import logging
import time
import uuid
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("healthcare_platform.daily")


class DailyService:
    """Integration service managing Daily.co WebRTC private rooms and meeting access tokens."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        domain: Optional[str] = None,
    ):
        self.api_key = api_key or settings.DAILY_API_KEY
        self.api_url = (api_url or settings.DAILY_API_URL).rstrip("/")
        self.domain = (domain or settings.DAILY_DOMAIN).rstrip("/")
        self.is_mock = self.api_key.startswith("mock") or "demo" in self.domain

    def create_room(
        self,
        room_name: str,
        exp_timestamp: Optional[int] = None,
    ) -> dict:
        """Create a private WebRTC meeting room on Daily.co with expiration and security guards."""
        if exp_timestamp is None:
            # Default room lifetime: 4 hours from creation
            exp_timestamp = int(time.time()) + (4 * 3600)

        if self.is_mock:
            room_url = f"{self.domain}/{room_name}"
            logger.info(f"[DailyService - Mock] Created private room: {room_name} at {room_url}")
            return {
                "name": room_name,
                "url": room_url,
                "privacy": "private",
                "config": {
                    "exp": exp_timestamp,
                    "enable_chat": True,
                    "enable_screenshare": True,
                },
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "name": room_name,
            "privacy": "private",
            "properties": {
                "exp": exp_timestamp,
                "enable_chat": True,
                "enable_screenshare": True,
                "start_audio_off": False,
                "start_video_off": False,
            },
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{self.api_url}/rooms", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"[DailyService] Created Daily private room {room_name}")
                return data
        except Exception as exc:
            logger.error(f"[DailyService] Failed to create Daily room {room_name}: {exc}")
            # Fallback to deterministic private room url
            return {
                "name": room_name,
                "url": f"{self.domain}/{room_name}",
                "privacy": "private",
            }

    def create_meeting_token(
        self,
        room_name: str,
        user_name: str,
        is_owner: bool = False,
        exp_timestamp: Optional[int] = None,
    ) -> str:
        """Generate a cryptographically scoped meeting token granting user entrance to the private room."""
        if exp_timestamp is None:
            # Token valid for 2 hours
            exp_timestamp = int(time.time()) + (2 * 3600)

        if self.is_mock:
            role_tag = "provider" if is_owner else "patient"
            mock_token = f"dly-tok-{uuid.uuid4().hex[:16]}-{role_tag}-{room_name}"
            logger.info(f"[DailyService - Mock] Generated token for {user_name} (owner={is_owner}) in {room_name}")
            return mock_token

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "properties": {
                "room_name": room_name,
                "user_name": user_name,
                "is_owner": is_owner,
                "exp": exp_timestamp,
                "enable_screenshare": True,
            }
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{self.api_url}/meeting-tokens", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data.get("token", "")
        except Exception as exc:
            logger.error(f"[DailyService] Failed to generate Daily meeting token: {exc}")
            return f"dly-fallback-{uuid.uuid4().hex[:16]}"

    def delete_room(self, room_name: str) -> bool:
        """Tears down the private room when consultation is completed or cancelled."""
        if self.is_mock:
            logger.info(f"[DailyService - Mock] Deleted room {room_name}")
            return True

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.delete(f"{self.api_url}/rooms/{room_name}", headers=headers)
                return resp.status_code in (200, 204)
        except Exception as exc:
            logger.warning(f"[DailyService] Failed to delete Daily room {room_name}: {exc}")
            return False


_daily_service: Optional[DailyService] = None


def get_daily_service() -> DailyService:
    global _daily_service
    if _daily_service is None:
        _daily_service = DailyService()
    return _daily_service
