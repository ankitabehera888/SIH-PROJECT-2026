import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FacilityTypeEnum(str, Enum):
    SUB_CENTER = "SUB_CENTER"
    PHC = "PHC"
    RURAL_HOSPITAL = "RURAL_HOSPITAL"
    DISTRICT_HOSPITAL = "DISTRICT_HOSPITAL"


class FacilityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    facility_code: str = Field(..., min_length=2, max_length=50)
    facility_type: FacilityTypeEnum = FacilityTypeEnum.PHC
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)


class FacilityResponse(BaseModel):
    id: uuid.UUID
    name: str
    facility_code: str
    facility_type: FacilityTypeEnum
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FacilityListResponse(BaseModel):
    items: List[FacilityResponse]
    total: int
