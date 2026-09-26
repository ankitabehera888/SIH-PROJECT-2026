import math
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MedicationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    generic_name: str = Field(..., min_length=2, max_length=200)
    strength: str = Field(..., min_length=1, max_length=50)
    dosage_form: str = Field("TABLET", max_length=50)
    route: str = Field("ORAL", max_length=50)
    unit: str = Field("mg", max_length=50)
    is_active: bool = True


class MedicationResponse(BaseModel):
    id: uuid.UUID
    name: str
    generic_name: str
    strength: str
    dosage_form: str
    route: str
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationListResponse(BaseModel):
    items: List[MedicationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[MedicationResponse], total: int, page: int, page_size: int):
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
