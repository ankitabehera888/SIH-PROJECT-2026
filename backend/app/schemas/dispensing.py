import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MedicationDispenseCreate(BaseModel):
    patient_id: uuid.UUID = Field(..., description="Target patient UUID")
    prescription_id: Optional[uuid.UUID] = Field(None, description="Linked prescription UUID")
    medication_name: str = Field(..., min_length=1, description="Medication name e.g. Amoxicillin")
    dosage: str = Field(..., description="Dosage string e.g. 500mg")
    frequency: str = Field(..., description="Frequency e.g. Twice daily")
    status: str = Field("Active", description="Active, Completed, Discontinued")
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    refills_remaining: int = Field(0, ge=0)
    instructions: Optional[str] = None


class MedicationDispenseResponse(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_name: Optional[str] = None
    prescription_id: Optional[uuid.UUID] = None
    medication_name: str
    dosage: str
    frequency: str
    status: str
    start_date: date
    end_date: Optional[date] = None
    refills_remaining: int
    instructions: Optional[str] = None
    dispensed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispensingListResponse(BaseModel):
    items: List[MedicationDispenseResponse]
    total: int
