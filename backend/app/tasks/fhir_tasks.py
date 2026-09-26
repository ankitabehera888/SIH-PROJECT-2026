import logging
import uuid
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.patient import Patient
from app.models.user import User
from app.schemas.notification import NotificationChannelEnum, NotificationCreate, NotificationTypeEnum
from app.services.fhir_service import FHIRService
from app.services.notification_service import NotificationService

logger = logging.getLogger("healthcare_platform.tasks.fhir")


@celery_app.task(name="app.tasks.fhir_tasks.export_patient_fhir_bundle_task", bind=True)
def export_patient_fhir_bundle_task(self, patient_id_str: str, requester_id: int):
    """Asynchronous background Celery task for generating large longitudinal FHIR bundles."""
    logger.info(f"[Celery FHIR Export] Starting bundle export for patient {patient_id_str}")
    db = SessionLocal()
    try:
        patient_id = uuid.UUID(patient_id_str)
        requester = db.get(User, requester_id)
        if not requester:
            return {"status": "FAILED", "reason": "Requester user not found"}

        service = FHIRService(db)
        bundle = service.get_patient_bundle(patient_id=patient_id, current_user=requester)

        # Notify requester via Phase 9 Notification system
        notif_svc = NotificationService(db)
        patient = db.get(Patient, patient_id)
        pat_name = f"{patient.first_name} {patient.last_name}" if patient else str(patient_id)

        notif_svc.create_and_dispatch(
            NotificationCreate(
                user_id=requester.id,
                patient_id=patient_id,
                notification_type=NotificationTypeEnum.SYSTEM_ALERT,
                channel=NotificationChannelEnum.IN_APP,
                subject="FHIR Bundle Export Ready",
                message=f"Longitudinal FHIR R4 Bundle for patient '{pat_name}' containing {bundle.get('total', 0)} clinical resources has been compiled and is ready for download.",
                related_entity_type="FHIR_BUNDLE",
                related_entity_id=uuid.UUID(bundle["id"]),
                idempotency_key=f"NOTIF_FHIR_EXP_{bundle['id']}",
            )
        )

        return {
            "status": "SUCCESS",
            "bundle_id": bundle["id"],
            "total_resources": bundle.get("total", 0),
        }
    except Exception as exc:
        logger.error(f"[Celery FHIR Export] Task failed: {exc}", exc_info=True)
        return {"status": "FAILED", "error": str(exc)}
    finally:
        db.close()
