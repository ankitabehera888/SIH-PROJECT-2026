from typing import Any, Dict, List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.interoperability.abdm.identity import ABDMIdentityService
from app.models.user import User
from app.schemas.interoperability import (
    ConsentCreateRequest,
    ConsentResponse,
    PatientIdentifierCreate,
    PatientIdentifierResponse,
)
from app.services.abdm_service import ABDMService

router = APIRouter(prefix="/interoperability", tags=["ABDM & Interoperability"])


@router.post(
    "/patients/{patient_id}/identifiers",
    status_code=status.HTTP_201_CREATED,
    response_model=PatientIdentifierResponse,
    summary="Link ABHA or External Identifier to Patient",
)
def link_identifier(
    patient_id: uuid.UUID,
    data: PatientIdentifierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ABDMService(db)
    return service.link_patient_identifier(patient_id, data, current_user)


@router.get(
    "/patients/{patient_id}/identifiers",
    response_model=List[PatientIdentifierResponse],
    summary="List Linked External Identifiers for Patient",
)
def list_identifiers(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ABDMService(db)
    return service.list_patient_identifiers(patient_id, current_user)


@router.post(
    "/consents",
    status_code=status.HTTP_201_CREATED,
    response_model=ConsentResponse,
    summary="Register Patient Consent Artefact",
)
def create_consent(
    data: ConsentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ABDMService(db)
    return service.create_consent(data, current_user)


@router.post(
    "/consents/{consent_id}/revoke",
    response_model=ConsentResponse,
    summary="Revoke Patient Consent Artefact",
)
def revoke_consent(
    consent_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ABDMService(db)
    return service.revoke_consent(consent_id, current_user)


@router.get(
    "/abdm/verify-abha/{abha_number}",
    summary="Simulate ABHA Number Verification via ABDM Gateway",
    response_model=Dict[str, Any],
)
def verify_abha_number(
    abha_number: str,
    current_user: User = Depends(get_current_user),
):
    identity_svc = ABDMIdentityService()
    otp_res = identity_svc.request_otp(abha_number)
    verified = identity_svc.verify_otp(otp_res["transaction_id"], "123456", abha_number)
    return verified
