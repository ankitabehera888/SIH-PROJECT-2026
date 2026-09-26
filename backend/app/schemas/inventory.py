import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InventoryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Medicine or supply name")
    category: str = Field("General", description="Category e.g. Antibiotics, Chronic Care")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    medication_id: Optional[uuid.UUID] = Field(None, description="Linked medication catalogue UUID")
    quantity: int = Field(..., ge=0, description="Stock quantity count")
    reorder_threshold: int = Field(20, ge=0, description="Reorder alert threshold level")


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    quantity: Optional[int] = None
    reorder_threshold: Optional[int] = None


class InventoryItemResponse(BaseModel):
    id: uuid.UUID
    facility_id: uuid.UUID
    facility_name: Optional[str] = None
    medication_id: Optional[uuid.UUID] = None
    name: str
    category: str
    manufacturer: Optional[str] = None
    quantity: int
    reorder_threshold: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventorySummary(BaseModel):
    items_tracked: int = 0
    available_percentage: int = 100
    low_stock_count: int = 0
    out_of_stock_count: int = 0
    reorder_alerts: List[str] = []


class InventoryListResponse(BaseModel):
    summary: InventorySummary
    items: List[InventoryItemResponse]
    categories: List[str]
    total: int
