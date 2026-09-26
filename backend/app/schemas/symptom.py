from typing import Any

from pydantic import BaseModel, Field


class SymptomItem(BaseModel):
    id: str
    label: str
    region: str
    duration_days: int = Field(ge=0, le=3650)
    severity: int = Field(ge=1, le=10)
    flags: list[str] = []


class SymptomAnalysisRequest(BaseModel):
    model: str = "male"
    age_months: int = Field(ge=0, le=1500)
    symptoms: list[SymptomItem] = Field(max_length=30)
    regions: list[str] = []
    secondary: list[str] = []
    notes: str = Field(default="", max_length=2000)
    language: str = "en"


class SymptomAnalysisResponse(BaseModel):
    ai_connected: bool
    summary: str
    urgency_score: int = Field(ge=1, le=10)
    urgency_tier: str
    reasons: list[str]
    conditions: list[dict[str, Any]]
    specialist: str | None = None
    home_care: list[str]
    recommended_tests: list[str]
    disclaimer: str
