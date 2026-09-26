import base64
import json
import os
import uuid
from dataclasses import dataclass, field
from io import BytesIO

from app.core.config import settings
from app.schemas.voice import (
    SynthesizeRequest,
    VoiceSessionMessageRequest,
    VoiceSessionResponse,
    VoiceSessionStartRequest,
)
from app.services.voice_service import voice_service


@dataclass
class VoiceSession:
    language: str
    voice_preset: str
    history: list[dict[str, str]] = field(default_factory=list)
    assessment: dict[str, object] | None = None


class VoiceSymptomService:
    def __init__(self) -> None:
        self.sessions: dict[str, VoiceSession] = {}

    def start(self, payload: VoiceSessionStartRequest) -> dict[str, str | None]:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = VoiceSession(payload.language, payload.voice_preset)
        greeting = "Hello! I am your AI health assistant. Please tell me what symptoms you are experiencing today."
        audio = self._audio(greeting, payload.voice_preset)
        return {
            "session_id": session_id,
            "status": "in_progress",
            "doctor_message": greeting,
            "doctor_audio_base64": audio,
            "language": payload.language,
            "voice_preset": payload.voice_preset,
        }

    def message(self, payload: VoiceSessionMessageRequest) -> VoiceSessionResponse:
        session = self.sessions.get(payload.session_id)
        if session is None:
            raise KeyError("Voice session not found")

        text = payload.text_message
        if payload.audio_base64:
            try:
                text = voice_service.transcribe(
                    base64.b64decode(payload.audio_base64), "audio.webm", payload.language
                )
            except Exception as exc:
                raise ValueError(f"Audio transcription failed: {exc}") from exc
        if not text or not text.strip():
            raise ValueError("No message content provided")

        text = text.strip()
        session.history.append({"role": "user", "content": text})
        response, assessment = self._answer(session.history)
        session.assessment = assessment
        session.history.append({"role": "assistant", "content": response})
        return VoiceSessionResponse(
            session_id=payload.session_id,
            doctor_message=response,
            doctor_audio_base64=self._audio(response, session.voice_preset),
            conversation_turn=len(session.history) // 2,
            is_final_assessment=assessment is not None,
            assessment_data=assessment,
        )

    @staticmethod
    def _answer(history: list[dict[str, str]]) -> tuple[str, dict[str, object] | None]:
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI

                base_url = settings.OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL")
                client = OpenAI(api_key=api_key, **({"base_url": base_url} if base_url else {}))
                user_turns = len([item for item in history if item["role"] == "user"])
                result = client.chat.completions.create(
                    model=settings.OPENAI_MODEL_FAST,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a cautious medical voice assistant conducting a symptom interview. Never diagnose. Ask one concise follow-up question per turn. Gather onset, severity, associated symptoms, medical history, medicines, and allergies. After 3 patient answers, return a concise plain-language assessment and suggested lab tests. Tell users with emergency symptoms to call local emergency services immediately. Return JSON with keys response, final, summary, urgency, recommendations, suggested_lab_tests. suggested_lab_tests must be an array of objects with name and reason. Set final true only after 3 patient answers.",
                        },
                        *history,
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                parsed = json.loads(result.choices[0].message.content or "{}")
                assessment = None
                if parsed.get("final"):
                    assessment = {
                        "summary": parsed.get("summary", "Symptoms require clinical review."),
                        "urgency": parsed.get("urgency", "routine"),
                        "recommendations": parsed.get("recommendations", []),
                        "suggested_lab_tests": parsed.get("suggested_lab_tests", []),
                    }
                return parsed.get("response", "Please tell me more about your symptoms."), assessment
            except Exception:
                pass

        lower = " ".join(item["content"] for item in history if item["role"] == "user").lower()
        if any(term in lower for term in ("chest pain", "can't breathe", "difficulty breathing", "stroke", "fainting", "seizure")):
            return "This may be an emergency. Call local emergency services now. Do not drive yourself.", {
                "summary": "Emergency warning signs reported.",
                "urgency": "emergency",
                "recommendations": ["Call local emergency services immediately."],
                "suggested_lab_tests": [],
            }
        user_turns = len([item for item in history if item["role"] == "user"])
        if user_turns == 1:
            return "I heard your main symptom. When did it start, and how severe is it from 1 to 10?", None
        if user_turns == 2:
            return "Thank you. Do you have any other symptoms, medical conditions, medicines, or allergies I should consider?", None
        if "headache" in lower or "migraine" in lower:
            return "Based on your answers, your symptoms need clinical review. Rest in a quiet room, drink water, and monitor changes. Seek urgent care for sudden severe pain, weakness, confusion, vision changes, or trouble speaking.", {
                "summary": "Headache symptoms reported; cause cannot be confirmed by voice screening.",
                "urgency": "routine",
                "recommendations": ["Arrange a clinician review.", "Seek urgent care if red-flag symptoms appear."],
                "suggested_lab_tests": [{"name": "Complete blood count (CBC)", "reason": "May help evaluate infection or anemia when clinically indicated."}],
            }
        if "fever" in lower or "temperature" in lower or "chills" in lower:
            return "Based on your answers, your fever symptoms need clinical review. Rest, drink fluids, and monitor temperature. Seek urgent care for trouble breathing, confusion, or severe weakness.", {
                "summary": "Fever symptoms reported; cause cannot be confirmed by voice screening.",
                "urgency": "routine",
                "recommendations": ["Arrange a clinician review.", "Continue monitoring temperature."],
                "suggested_lab_tests": [{"name": "Complete blood count (CBC)", "reason": "May help evaluate infection when clinically indicated."}, {"name": "Urinalysis", "reason": "May help evaluate urinary infection when symptoms support it."}],
            }
        if "cough" in lower or "cold" in lower or "sore throat" in lower:
            return "Based on your answers, your respiratory symptoms need clinical review. Rest, drink warm fluids, and monitor breathing. Seek urgent care for chest pain, blue lips, or difficulty breathing.", {
                "summary": "Respiratory symptoms reported; cause cannot be confirmed by voice screening.",
                "urgency": "routine",
                "recommendations": ["Arrange a clinician review.", "Seek urgent care if breathing worsens."],
                "suggested_lab_tests": [{"name": "COVID-19 or influenza test", "reason": "May help identify a respiratory infection when clinically indicated."}],
            }
        if "nausea" in lower or "vomit" in lower or "stomach" in lower or "diarrhea" in lower:
            return "Based on your answers, your digestive symptoms need clinical review. Take small sips of fluid and eat light foods. Seek care for severe pain, blood, confusion, or dehydration.", {
                "summary": "Digestive symptoms reported; cause cannot be confirmed by voice screening.",
                "urgency": "routine",
                "recommendations": ["Arrange a clinician review.", "Continue hydration."],
                "suggested_lab_tests": [{"name": "Electrolyte panel", "reason": "May help assess dehydration when clinically indicated."}],
            }
        if "pain" in lower or "ache" in lower:
            return "Based on your answers, your pain needs clinical review. Rest the affected area and monitor changes. Seek urgent care if pain is severe, worsening, or linked to weakness or breathing trouble.", {
                "summary": "Pain symptoms reported; cause cannot be confirmed by voice screening.",
                "urgency": "routine",
                "recommendations": ["Arrange a clinician review.", "Seek urgent care for severe or worsening pain."],
                "suggested_lab_tests": [{"name": "Basic metabolic panel", "reason": "May help evaluate systemic causes when clinically indicated."}],
            }
        return f"Based on your answers, your symptoms need clinical review. Monitor changes and seek care if they worsen.", {
            "summary": f"Reported symptom: {history[0]['content']}",
            "urgency": "routine",
            "recommendations": ["Arrange a clinician review.", "Seek urgent care if symptoms become severe."],
            "suggested_lab_tests": [],
        }

    def report_pdf(self, session_id: str) -> BytesIO:
        session = self.sessions.get(session_id)
        if session is None:
            raise KeyError("Voice session not found")
        if session.assessment is None:
            raise ValueError("Complete symptom interview before downloading report")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError as exc:
            raise RuntimeError("PDF support requires reportlab") from exc

        output = BytesIO()
        pdf = canvas.Canvas(output, pagesize=letter)
        width, height = letter
        y = height - 54
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(54, y, "Sahaay Voice Symptom Report")
        y -= 30
        pdf.setFont("Helvetica", 10)
        pdf.drawString(54, y, "Screening summary only. Not a diagnosis or replacement for clinical care.")
        y -= 28
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(54, y, "Assessment")
        y -= 18
        pdf.setFont("Helvetica", 10)
        for line in self._wrap(str(session.assessment["summary"]), 92):
            pdf.drawString(54, y, line)
            y -= 14
        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(54, y, f"Urgency: {session.assessment['urgency']}")
        y -= 24
        pdf.drawString(54, y, "Suggested lab tests")
        y -= 18
        pdf.setFont("Helvetica", 10)
        tests = session.assessment.get("suggested_lab_tests", [])
        for test in tests:
            for line in self._wrap(f"- {test.get('name')}: {test.get('reason')}", 92):
                pdf.drawString(54, y, line)
                y -= 14
        if not tests:
            pdf.drawString(54, y, "No lab test suggested by screening.")
            y -= 14
        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(54, y, "Recommendations")
        y -= 18
        pdf.setFont("Helvetica", 10)
        for recommendation in session.assessment.get("recommendations", []):
            for line in self._wrap(f"- {recommendation}", 92):
                pdf.drawString(54, y, line)
                y -= 14
        pdf.save()
        output.seek(0)
        return output

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > width:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        return lines

    @staticmethod
    def _audio(text: str, voice: str) -> str | None:
        try:
            return voice_service.synthesize(SynthesizeRequest(text=text, voice=voice)).audio_base64
        except Exception:
            return None


voice_symptom_service = VoiceSymptomService()
