import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interoperability import FHIRBundleExportRequest
from app.services.fhir_service import FHIRService
from app.tasks.fhir_tasks import export_patient_fhir_bundle_task

router = APIRouter(prefix="/fhir", tags=["FHIR R4 Interoperability"])


@router.get(
    "/Patient/{patient_id}",
    summary="Get FHIR R4 Patient Resource",
    response_model=Dict[str, Any],
)
def get_fhir_patient(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_patient_resource(patient_id, current_user)


@router.get(
    "/Practitioner/{practitioner_id}",
    summary="Get FHIR R4 Practitioner Resource",
    response_model=Dict[str, Any],
)
def get_fhir_practitioner(
    practitioner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_practitioner_resource(practitioner_id, current_user)


@router.get(
    "/Organization/{facility_id}",
    summary="Get FHIR R4 Organization Resource",
    response_model=Dict[str, Any],
)
def get_fhir_organization(
    facility_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_organization_resource(facility_id, current_user)


@router.get(
    "/Appointment/{appointment_id}",
    summary="Get FHIR R4 Appointment Resource",
    response_model=Dict[str, Any],
)
def get_fhir_appointment(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_appointment_resource(appointment_id, current_user)


@router.get(
    "/Encounter/{encounter_id}",
    summary="Get FHIR R4 Encounter Resource",
    response_model=Dict[str, Any],
)
def get_fhir_encounter(
    encounter_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_encounter_resource(encounter_id, current_user)


@router.get(
    "/Observation/{observation_id}",
    summary="Get FHIR R4 Observation Resource (Vital Sign or Diagnostic Result)",
    response_model=Dict[str, Any],
)
def get_fhir_observation(
    observation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_observation_resource(observation_id, current_user)


@router.get(
    "/Medication/{medication_id}",
    summary="Get FHIR R4 Medication Resource",
    response_model=Dict[str, Any],
)
def get_fhir_medication(
    medication_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_medication_resource(medication_id, current_user)


@router.get(
    "/MedicationRequest/{prescription_item_id}",
    summary="Get FHIR R4 MedicationRequest Resource",
    response_model=Dict[str, Any],
)
def get_fhir_medication_request(
    prescription_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_medication_request_resource(prescription_item_id, current_user)


@router.get(
    "/ServiceRequest/{service_request_id}",
    summary="Get FHIR R4 ServiceRequest Resource (Diagnostic Order or Referral)",
    response_model=Dict[str, Any],
)
def get_fhir_service_request(
    service_request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_service_request_resource(service_request_id, current_user)


@router.get(
    "/DiagnosticReport/{diagnostic_order_id}",
    summary="Get FHIR R4 DiagnosticReport Resource",
    response_model=Dict[str, Any],
)
def get_fhir_diagnostic_report(
    diagnostic_order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_diagnostic_report_resource(diagnostic_order_id, current_user)


@router.get(
    "/patient/{patient_id}/bundle",
    summary="Export Complete Longitudinal Patient FHIR R4 Bundle",
    response_model=Dict[str, Any],
)
def export_patient_bundle(
    patient_id: uuid.UUID,
    bundle_type: str = Query("collection", pattern="^(collection|document)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FHIRService(db)
    return service.get_patient_bundle(patient_id, bundle_type=bundle_type, current_user=current_user)


@router.post(
    "/patient/{patient_id}/export-async",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Asynchronous Background FHIR Bundle Export (Celery)",
)
def export_patient_bundle_async(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify access before enqueuing task
    service = FHIRService(db)
    service._verify_patient_access(patient_id, current_user)

    task = export_patient_fhir_bundle_task.delay(str(patient_id), current_user.id)
    return {
        "status": "ACCEPTED",
        "task_id": task.id,
        "patient_id": patient_id,
        "message": "FHIR Bundle generation task dispatched. You will receive an in-app notification when ready.",
    }
