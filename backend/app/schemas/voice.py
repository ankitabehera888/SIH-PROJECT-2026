from typing import Any

from pydantic import BaseModel, Field


class SynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str = Field(default="marin", pattern="^(alloy|ash|ballad|coral|echo|fable|marin|nova|onyx|sage|shimmer|verse|cedar)$")
    speed: float = Field(default=1.0, ge=0.25, le=4.0)


class SynthesizeResponse(BaseModel):
    audio_base64: str | None = None
    format: str = "mp3"
    message: str | None = None


class VoiceSessionStartRequest(BaseModel):
    language: str = "en"
    voice_preset: str = Field(default="marin", pattern="^(alloy|ash|ballad|coral|echo|fable|marin|nova|onyx|sage|shimmer|verse|cedar)$")


class VoiceSessionMessageRequest(BaseModel):
    session_id: str
    text_message: str | None = Field(default=None, max_length=5000)
    audio_base64: str | None = None
    language: str = "en"


class VoiceSessionResponse(BaseModel):
    session_id: str
    doctor_message: str
    doctor_audio_base64: str | None = None
    conversation_turn: int
    is_final_assessment: bool = False
    assessment_data: dict[str, Any] | None = None
