import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class VitalCreate(BaseModel):
    """Clinical observations and vitals recording payload.
    
    Enforces physiological sanity checks without replacing clinical diagnosis.
    """

    temperature: Optional[float] = Field(None, ge=30.0, le=45.0, description="Temperature in Celsius (°C)")
    heart_rate: Optional[int] = Field(None, ge=20, le=260, description="Heart rate in beats per minute (bpm)")
    respiratory_rate: Optional[int] = Field(None, ge=5, le=80, description="Respiratory rate in breaths/min")
    systolic_bp: Optional[int] = Field(None, ge=50, le=300, description="Systolic blood pressure in mmHg")
    diastolic_bp: Optional[int] = Field(None, ge=30, le=200, description="Diastolic blood pressure in mmHg")
    spo2: Optional[float] = Field(None, ge=40.0, le=100.0, description="Blood oxygen saturation percentage (%)")
    weight: Optional[float] = Field(None, ge=0.5, le=400.0, description="Weight in kilograms (kg)")
    height: Optional[float] = Field(None, ge=20.0, le=280.0, description="Height in centimeters (cm)")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_blood_pressure_relationship(self):
        if self.systolic_bp is not None and self.diastolic_bp is not None:
            if self.diastolic_bp >= self.systolic_bp:
                raise ValueError("Diastolic blood pressure must be strictly less than systolic blood pressure")
        return self


class VitalResponse(BaseModel):
    id: uuid.UUID
    encounter_id: uuid.UUID
    patient_id: uuid.UUID
    recorded_by: Optional[int] = None
    recorded_at: datetime
    temperature: Optional[float] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    spo2: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VitalListResponse(BaseModel):
    items: List[VitalResponse]
    encounter_id: uuid.UUID
    total: int
