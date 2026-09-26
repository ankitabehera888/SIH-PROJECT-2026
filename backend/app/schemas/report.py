from typing import Any

from pydantic import BaseModel


class LabResult(BaseModel):
    test: str
    value: str
    range: str = "Not available"
    status: str = "unknown"


class LabReportResponse(BaseModel):
    id: str
    name: str
    type: str
    uploadDate: str
    size: str
    status: str
    category: str
    summary: str
    results: list[LabResult]
    aiConnected: bool = False
    error: str | None = None
    metadata: dict[str, Any] | None = None
