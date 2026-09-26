from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.models.consent import ConsentPurpose, ConsentScope, ConsentStatus
from app.models.patient_identifier import IdentifierStatus, IdentifierType


class PatientIdentifierCreate(BaseModel):
    system: str = Field(default="https://healthid.abdm.gov.in", description="Authority or namespace URI")
    value: str = Field(..., min_length=3, max_length=255, description="Identifier value (e.g. ABHA number or address)")
    identifier_type: IdentifierType = Field(default=IdentifierType.ABHA_NUMBER)


class PatientIdentifierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    system: str
    value: str
    identifier_type: str
    status: str
    verified_at: Optional[datetime] = None
    created_at: datetime


class ConsentCreateRequest(BaseModel):
    patient_id: uuid.UUID
    purpose: ConsentPurpose = Field(default=ConsentPurpose.CARE_MANAGEMENT)
    scope: ConsentScope = Field(default=ConsentScope.ALL)
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    consent_artefact_id: Optional[str] = None
    purpose: str
    scope: str
    status: str
    granted_by: Optional[int] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    notes: Optional[str] = None


class FHIRBundleExportRequest(BaseModel):
    bundle_type: str = Field(default="collection", pattern="^(collection|document|transaction)$")
    include_vitals: bool = True
    include_prescriptions: bool = True
    include_diagnostics: bool = True
    include_referrals: bool = True


class InteroperabilityAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    purpose: Optional[str] = None
    status: str
    timestamp: datetime
