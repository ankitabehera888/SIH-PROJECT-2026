"""Symptom service — business logic for symptom check sessions."""

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import get_config
from app.models.symptom_session import Base, SymptomSession
from app.schemas.symptom_schema import (
    SendMessageRequest,
    StartSessionRequest,
    SymptomSessionResponse,
)

logger = logging.getLogger(__name__)

# Database setup
config = get_config()
engine = create_engine(config.DATABASE_URL, echo=False)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(engine)


class SymptomService:
    """Handles creating, messaging, and managing symptom check sessions."""

    def start_session(
        self, patient_id: str, data: StartSessionRequest
    ) -> SymptomSessionResponse:
        """Start a new symptom check session.

        Calls the AI agent immediately with the chief complaint so the
        conversation starts with both a user message and an AI response.

        Args:
            patient_id: UUID of the patient.
            data: Validated session start data.

        Returns:
            SymptomSessionResponse with the created session.
        """
        with Session(engine) as session:
            # Build initial conversation log with user complaint
            conversation_log = [{"role": "user", "content": data.chief_complaint}]

            symptom_session = SymptomSession(
                patient_id=patient_id,
                status="in_progress",
                chief_complaint=data.chief_complaint,
                symptoms=json.dumps(data.symptoms) if data.symptoms else None,
                conversation_log=json.dumps(conversation_log),
            )
            session.add(symptom_session)
            session.commit()
            session.refresh(symptom_session)

            # Call AI agent to generate the first response
            try:
                ai_response = self._get_ai_response(
                    symptom_session, conversation_log, data.chief_complaint
                )
                conversation_log.append({"role": "assistant", "content": ai_response})
                symptom_session.conversation_log = json.dumps(conversation_log)
                symptom_session.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(symptom_session)
            except Exception as e:
                logger.warning("AI agent failed during session start: %s", e)

            return self._to_response(symptom_session)

    def send_message(
        self, session_id: str, data: SendMessageRequest
    ) -> SymptomSessionResponse | None:
        """Send a message in a symptom session and get AI response.

        Args:
            session_id: UUID of the session.
            data: Validated message data.

        Returns:
            Updated SymptomSessionResponse with AI response, or None if session not found.
        """
        with Session(engine) as session:
            stmt = select(SymptomSession).where(SymptomSession.id == session_id)
            symptom_session = session.execute(stmt).scalar_one_or_none()
            if symptom_session is None:
                return None

            if symptom_session.status != "in_progress":
                return None

            # Parse conversation log from JSON string
            conversation_log = []
            if symptom_session.conversation_log:
                try:
                    conversation_log = json.loads(symptom_session.conversation_log)
                except (json.JSONDecodeError, TypeError):
                    conversation_log = []

            # Append user message to conversation log
            conversation_log.append({"role": "user", "content": data.message})

            # Call AI agent to generate a response
            ai_response_text = self._get_ai_response(
                symptom_session, conversation_log, data.message
            )

            # Append AI response to conversation log
            conversation_log.append({"role": "assistant", "content": ai_response_text})
            symptom_session.conversation_log = json.dumps(conversation_log)
            symptom_session.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(symptom_session)

            return self._to_response(symptom_session)

    def _get_ai_response(
        self,
        symptom_session: SymptomSession,
        conversation_log: list[dict],
        user_message: str,
    ) -> str:
        """Call the AI to generate a symptom analysis response.

        Uses the SymptomAnalystAgent if available, falls back to direct
        OpenAI chat completion.

        Args:
            symptom_session: The current symptom session.
            conversation_log: Full conversation history.
            user_message: The latest user message.

        Returns:
            AI response text.
        """
        try:
            from app.agents.base_agent import AgentInput
            from app.agents.symptom_analyst import SymptomAnalystAgent

            agent = SymptomAnalystAgent()
            agent_input = AgentInput(
                session_id=str(symptom_session.id),
                user_id=str(symptom_session.patient_id),
                patient_id=str(symptom_session.patient_id),
                message=user_message,
                conversation_history=conversation_log[:-1],  # exclude the latest user msg (agent adds it)
            )
            result = agent.run(agent_input)

            # Store analysis results on the session if we got structured output
            if result.differential_diagnoses:
                symptom_session.ai_analysis = json.dumps({
                    "urgency_score": result.urgency_score,
                    "differential_diagnosis": result.differential_diagnoses,
                    "recommended_action": result.recommended_action,
                    "recommended_specialist": result.recommended_specialist,
                    "follow_up_questions": result.follow_up_questions,
                    "confidence": result.confidence,
                })
                if result.urgency_score >= 8:
                    symptom_session.triage_level = "emergency"
                elif result.urgency_score >= 6:
                    symptom_session.triage_level = "urgent"
                elif result.urgency_score >= 4:
                    symptom_session.triage_level = "semi_urgent"
                else:
                    symptom_session.triage_level = "non_urgent"
                symptom_session.recommended_action = result.recommended_action

            return result.response_text

        except Exception as agent_err:
            logger.warning("Symptom agent failed, falling back to direct chat: %s", agent_err)

        # Fallback: direct OpenAI chat completion
        try:
            from app.integrations.openai_client import openai_client

            system_prompt = (
                "You are MedAssist AI Symptom Analyst. Conduct a thorough symptom interview "
                "using the OLDCARTS framework (Onset, Location, Duration, Character, "
                "Alleviating/Aggravating factors, Radiation, Timing, Severity). "
                "Ask follow-up questions to narrow down the diagnosis. Be empathetic and clear. "
                "Use plain language at a 6th-8th grade reading level. "
                "Always remind users this is not a substitute for professional medical advice."
            )
            messages = [{"role": "system", "content": system_prompt}]
            # Include recent conversation history (last 20 messages for context)
            for msg in conversation_log[-20:]:
                role = msg.get("role", "user")
                if role in ("user", "assistant"):
                    messages.append({"role": role, "content": msg.get("content", "")})
            # Ensure the last message is the current user message
            if not messages or messages[-1].get("role") != "user" or messages[-1].get("content") != user_message:
                messages.append({"role": "user", "content": user_message})

            result = openai_client.chat_completion(
                messages=messages,
                max_tokens=800,
                temperature=0.3,
            )
            return result.content or "I'm processing your symptoms. Could you provide more details?"

        except Exception as chat_err:
            logger.error("Direct chat fallback also failed: %s", chat_err)
            return (
                "I'm having trouble analyzing your symptoms right now. "
                "Please try again in a moment, or contact your healthcare provider directly."
            )

    def get_session(self, session_id: str) -> SymptomSessionResponse | None:
        """Get a symptom session by ID.

        Args:
            session_id: UUID of the session.

        Returns:
            SymptomSessionResponse if found, None otherwise.
        """
        with Session(engine) as session:
            stmt = select(SymptomSession).where(SymptomSession.id == session_id)
            symptom_session = session.execute(stmt).scalar_one_or_none()
            if symptom_session is None:
                return None
            return self._to_response(symptom_session)

    def complete_session(self, session_id: str) -> SymptomSessionResponse | None:
        """Complete a symptom session.

        Args:
            session_id: UUID of the session.

        Returns:
            Updated SymptomSessionResponse, or None if not found.
        """
        with Session(engine) as session:
            stmt = select(SymptomSession).where(SymptomSession.id == session_id)
            symptom_session = session.execute(stmt).scalar_one_or_none()
            if symptom_session is None:
                return None

            symptom_session.status = "completed"
            symptom_session.completed_at = datetime.now(timezone.utc)
            symptom_session.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(symptom_session)

            return self._to_response(symptom_session)

    def get_patient_sessions(
        self,
        patient_id: str,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SymptomSessionResponse]:
        """Get symptom sessions for a patient.

        Args:
            patient_id: UUID of the patient.
            status: Optional filter by session status.
            limit: Maximum number of sessions to return.
            offset: Number of sessions to skip.

        Returns:
            List of SymptomSessionResponse matching the criteria.
        """
        with Session(engine) as session:
            stmt = select(SymptomSession).where(SymptomSession.patient_id == patient_id)

            if status:
                stmt = stmt.where(SymptomSession.status == status)

            stmt = stmt.order_by(SymptomSession.created_at.desc()).offset(offset).limit(limit)
            sessions = session.execute(stmt).scalars().all()
            return [self._to_response(s) for s in sessions]

    def _to_response(self, symptom_session: SymptomSession) -> SymptomSessionResponse:
        """Convert a SymptomSession model to a SymptomSessionResponse schema."""
        # Parse JSON fields from strings
        symptoms = None
        if symptom_session.symptoms:
            try:
                symptoms = json.loads(symptom_session.symptoms)
            except (json.JSONDecodeError, TypeError):
                symptoms = symptom_session.symptoms

        ai_analysis = None
        if symptom_session.ai_analysis:
            try:
                ai_analysis = json.loads(symptom_session.ai_analysis)
            except (json.JSONDecodeError, TypeError):
                ai_analysis = symptom_session.ai_analysis

        conversation_log = None
        if symptom_session.conversation_log:
            try:
                conversation_log = json.loads(symptom_session.conversation_log)
            except (json.JSONDecodeError, TypeError):
                conversation_log = symptom_session.conversation_log

        return SymptomSessionResponse(
            id=str(symptom_session.id),
            patient_id=str(symptom_session.patient_id),
            status=symptom_session.status,
            chief_complaint=symptom_session.chief_complaint,
            symptoms=symptoms,
            ai_analysis=ai_analysis,
            triage_level=symptom_session.triage_level,
            recommended_action=symptom_session.recommended_action,
            escalated_to=str(symptom_session.escalated_to) if symptom_session.escalated_to else None,
            conversation_log=conversation_log,
            completed_at=symptom_session.completed_at,
            created_at=symptom_session.created_at,
            updated_at=symptom_session.updated_at,
        )


# Module-level instance for use by routes
symptom_service = SymptomService()
