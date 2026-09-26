from fastapi import APIRouter

from app.schemas.symptom import SymptomAnalysisRequest, SymptomAnalysisResponse
from app.services.symptom_analysis_service import symptom_analysis_service

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])


@router.post("/analyze", response_model=SymptomAnalysisResponse)
def analyze_symptoms(payload: SymptomAnalysisRequest):
    return symptom_analysis_service.analyze(payload)
