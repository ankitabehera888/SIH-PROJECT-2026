import json
import os
from typing import Any

from app.core.config import settings
from app.schemas.symptom import SymptomAnalysisRequest, SymptomAnalysisResponse
from app.services.voice_service import voice_service


class SymptomAnalysisService:
    def analyze(self, payload: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
        client = None
        try:
            client = voice_service._client()
        except Exception:
            pass
        if client:
            try:
                result = client.chat.completions.create(
                    model=settings.OPENAI_MODEL_FAST,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a cautious clinical symptom triage assistant. Analyze every field in the patient context, including free-text notes, selected body regions, duration, severity, warning flags, and secondary answers. Do not ignore or repeat the patient's free-text description. Return a clear, empathetic, patient-friendly response that reflects their actual context. Never diagnose or claim certainty. Emergency warning signs always raise urgency. Return JSON only with keys summary, urgency_score (1-10), urgency_tier (self, office, h24, now, er, call911), reasons (array), conditions (array of name, icd10, specialist, score 0-96, factors array), specialist, home_care (array), recommended_tests (array). Recommend tests only when clinically justified. Always include a safety disclaimer in summary.",
                        },
                        {"role": "user", "content": json.dumps(payload.model_dump(), ensure_ascii=False)},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                return self._response(json.loads(result.choices[0].message.content or "{}"), True)
            except Exception:
                pass
        return self._fallback(payload)

    def _response(self, data: dict[str, Any], connected: bool) -> SymptomAnalysisResponse:
        score = max(1, min(10, int(data.get("urgency_score", 3))))
        tier = str(data.get("urgency_tier", "office"))
        if tier not in {"self", "office", "h24", "now", "er", "call911"}:
            tier = "h24" if score >= 6 else "office"
        conditions = []
        for condition in data.get("conditions", []):
            if isinstance(condition, dict) and condition.get("name"):
                conditions.append({
                    "name": str(condition["name"]),
                    "icd10": str(condition.get("icd10", "R68.89")),
                    "specialist": str(condition.get("specialist", "General physician")),
                    "score": max(1, min(96, int(condition.get("score", 30)))),
                    "factors": [str(factor) for factor in condition.get("factors", [])],
                })
        return SymptomAnalysisResponse(
            ai_connected=connected,
            summary=str(data.get("summary", "Symptoms require clinical review. This is not a diagnosis.")),
            urgency_score=score,
            urgency_tier=tier,
            reasons=[str(reason) for reason in data.get("reasons", [])][:8],
            conditions=conditions[:5],
            specialist=str(data["specialist"]) if data.get("specialist") else None,
            home_care=[str(item) for item in data.get("home_care", [])][:8],
            recommended_tests=[str(item) for item in data.get("recommended_tests", [])][:8],
            disclaimer="AI guidance is informational only and is not a medical diagnosis.",
        )

    def _fallback(self, payload: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
        text = " ".join(item.label for item in payload.symptoms).lower() + " " + payload.notes.lower()
        score = max((item.severity for item in payload.symptoms), default=1)
        emergency = any(term in text for term in ("chest pain", "difficulty breathing", "can't breathe", "stroke", "seizure", "fainting"))
        if emergency:
            score = 10
            tier = "call911"
            action = "Call emergency services now. Do not drive yourself."
        elif score >= 7:
            tier = "h24"
            action = "Arrange medical review within 24 hours."
        else:
            tier = "office"
            action = "Arrange a routine clinician review if symptoms persist or worsen."
        return self._response({
            "summary": f"You described {len(payload.symptoms)} selected symptom(s) and additional details. {action} This is not a diagnosis.",
            "urgency_score": score,
            "urgency_tier": tier,
            "reasons": ["Severity, duration, body region, and reported warning signs were considered."],
            "conditions": [],
            "specialist": "General physician",
            "home_care": ["Monitor symptoms and note changes.", "Stay hydrated and rest unless a clinician advised otherwise."],
            "recommended_tests": [],
        }, False)


symptom_analysis_service = SymptomAnalysisService()
