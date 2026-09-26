import base64

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.voice import SynthesizeRequest, SynthesizeResponse
from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.get("/status")
def connection_status():
    return voice_service.connection_status()


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language: str | None = Form(default=None),
):
    allowed = {"wav", "mp3", "mp4", "m4a", "webm", "ogg", "flac"}
    filename = audio.filename or "audio.webm"
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in allowed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported audio format '.{extension}'")
    data = await audio.read()
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Audio file is empty")
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Audio file exceeds 25MB limit")
    try:
        text = voice_service.transcribe(data, filename, language)
    except ValueError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    return {"text": text, "language": language}


@router.post("/synthesize", response_model=SynthesizeResponse)
def synthesize(payload: SynthesizeRequest):
    return voice_service.synthesize(payload)
