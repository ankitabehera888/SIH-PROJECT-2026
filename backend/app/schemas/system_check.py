from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SystemCheckBase(BaseModel):
    check_name: str
    status: str = "healthy"


class SystemCheckCreate(SystemCheckBase):
    pass


class SystemCheckResponse(SystemCheckBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
