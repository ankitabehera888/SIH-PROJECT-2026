from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

class KPIResponse(BaseModel):
    metric_code: str
    metric_name: str
    metric_type: str
    period_start: date
    period_end: date
    numerator: Optional[Decimal] = None
    denominator: Optional[Decimal] = None
    value: Optional[Decimal] = None
    calculation_version: str
    suppressed: bool = False
    suppression_reason: Optional[str] = None

class TimeSeriesPoint(BaseModel):
    period: str
    value: Optional[Decimal] = None
    numerator: Optional[Decimal] = None
    denominator: Optional[Decimal] = None

class KPITimeSeriesResponse(BaseModel):
    metric_code: str
    interval: str
    data: List[TimeSeriesPoint]

class ComparisonPoint(BaseModel):
    entity_id: str
    entity_name: str
    value: Optional[Decimal] = None

class KPIComparisonResponse(BaseModel):
    metric_code: str
    group_by: str
    data: List[ComparisonPoint]
