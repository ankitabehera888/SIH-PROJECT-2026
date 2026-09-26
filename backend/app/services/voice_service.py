import base64
import os
from io import BytesIO

from app.core.config import settings
from app.schemas.voice import SynthesizeRequest, SynthesizeResponse


class VoiceService:
    """OpenAI Whisper and TTS adapter with development fallbacks."""

    @staticmethod
    def _client():
        from openai import OpenAI

        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        base_url = settings.OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL")
        return OpenAI(api_key=api_key, **({"base_url": base_url} if base_url else {}))

    def transcribe(self, audio_data: bytes, filename: str, language: str | None = None) -> str:
        client = self._client()
        if client is None:
            raise ValueError("Voice transcription requires OPENAI_API_KEY")

        audio_file = BytesIO(audio_data)
        audio_file.name = filename
        kwargs = {"model": settings.OPENAI_WHISPER_MODEL, "file": audio_file}
        if language:
            kwargs["language"] = language
        return client.audio.transcriptions.create(**kwargs).text

    def connection_status(self) -> dict[str, str | bool]:
        """Check OpenAI credentials and API reachability without exposing secrets."""
        client = self._client()
        if client is None:
            return {
                "connected": False,
                "provider": "OpenAI",
                "model": settings.OPENAI_MODEL_FAST,
                "message": "OPENAI_API_KEY is not configured",
            }
        try:
            client.models.list()
            return {
                "connected": True,
                "provider": "OpenAI",
                "model": settings.OPENAI_MODEL_FAST,
                "message": "OpenAI API connected",
            }
        except Exception:
            return {
                "connected": False,
                "provider": "OpenAI",
                "model": settings.OPENAI_MODEL_FAST,
                "message": "OpenAI API unavailable or credentials invalid",
            }

    def synthesize(self, data: SynthesizeRequest) -> SynthesizeResponse:
        client = self._client()
        if client is None:
            return SynthesizeResponse(
                message="Audio synthesis unavailable. Configure OPENAI_API_KEY.",
            )

        response = client.audio.speech.create(
            model=settings.OPENAI_TTS_MODEL,
            voice=data.voice,
            input=data.text,
            speed=data.speed,
        )
        return SynthesizeResponse(audio_base64=base64.b64encode(response.content).decode("ascii"))


voice_service = VoiceService()
