"""Symptoms API endpoints — manage symptom check sessions.

Routes:
    POST /api/v1/symptoms/session              — Start a new session
    POST /api/v1/symptoms/session/{session_id}/message — Send a message in a session
    GET  /api/v1/symptoms/session/{session_id}         — Get session details
    PUT  /api/v1/symptoms/session/{session_id}/complete — Complete a session
    GET  /api/v1/symptoms/history/{patient_id}         — Get session history
"""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.symptom_schema import (
    SendMessageRequest,
    SessionHistoryParams,
    StartSessionRequest,
    SymptomSessionResponse,
)
from app.services.symptom_service import symptom_service

router = APIRouter(prefix="/api/v1/symptoms", tags=["symptoms"])


@router.post("/session", response_model=SymptomSessionResponse, status_code=201)
async def start_session(data: StartSessionRequest):
    """Start a new symptom check session for the current patient.

    Creates a new session with the initial complaint and optional symptom data.
    The session will be used for multi-turn symptom analysis with the AI agent.
    """
    # For demo purposes, using a fixed patient ID
    # In production, this would come from JWT authentication
    patient_id = "demo-patient-001"

    session = symptom_service.start_session(patient_id, data)
    return session


@router.post("/session/{session_id}/message", response_model=SymptomSessionResponse)
async def send_message(session_id: str, data: SendMessageRequest):
    """Send a message in a symptom check session and get AI response.

    The AI agent will analyze the message in context of the conversation history
    and provide either follow-up questions or a structured analysis.
    """
    result = symptom_service.send_message(session_id, data)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Session not found or not in progress"}}
        )

    return result


@router.get("/session/{session_id}", response_model=SymptomSessionResponse)
async def get_session(session_id: str):
    """Get symptom session details and diagnosis."""
    session = symptom_service.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Session not found"}}
        )

    return session


@router.put("/session/{session_id}/complete", response_model=SymptomSessionResponse)
async def complete_session(session_id: str):
    """Complete a symptom check session."""
    result = symptom_service.complete_session(session_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Session not found"}}
        )

    return result


@router.get("/history/{patient_id}", response_model=list[SymptomSessionResponse])
async def get_history(
    patient_id: str,
    status: str | None = Query(None, description="Filter by session status"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of sessions"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
):
    """Get symptom session history for a patient."""
    params = SessionHistoryParams(
        status=status,
        limit=limit,
        offset=offset,
    )

    sessions = symptom_service.get_patient_sessions(
        patient_id,
        status=params.status,
        limit=params.limit,
        offset=params.offset,
    )
    return sessions
