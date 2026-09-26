from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.voice import (
    VoiceSessionMessageRequest,
    VoiceSessionStartRequest,
)
from app.services.voice_symptom_service import voice_symptom_service

router = APIRouter(prefix="/voice-symptom", tags=["Voice Symptom Assistant"])


@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_session(payload: VoiceSessionStartRequest):
    return voice_symptom_service.start(payload)


@router.post("/message")
def send_message(payload: VoiceSessionMessageRequest):
    try:
        return voice_symptom_service.message(payload)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.get("/{session_id}/report", response_class=StreamingResponse)
def download_report(session_id: str):
    try:
        report = voice_symptom_service.report_pdf(session_id)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    return StreamingResponse(
        report,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="sahaay-symptom-report-{session_id}.pdf"'},
    )
