from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

class FacilityAnalyticsItem(BaseModel):
    facility_key: int
    facility_name: str
    encounter_volume: int
    patients_served: int
    average_wait_minutes: Optional[Decimal] = None

class FacilityAnalyticsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[FacilityAnalyticsItem]

class GeographyAnalyticsItem(BaseModel):
    geography_key: int
    district_name: str
    encounter_volume: int

class GeographyAnalyticsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[GeographyAnalyticsItem]
