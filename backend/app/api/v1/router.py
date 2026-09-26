from fastapi import APIRouter
from app.api.v1.appointments import router as appointments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.consultations import router as consultations_router
from app.api.v1.diagnostic_tests import router as diagnostic_tests_router
from app.api.v1.diagnostics import router as diagnostics_router
from app.api.v1.encounters import router as encounters_router
from app.api.v1.facilities import router as facilities_router
from app.api.v1.fhir import router as fhir_router
from app.api.v1.health import router as health_router
from app.api.v1.interoperability import router as interoperability_router
from app.api.v1.medications import router as medications_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.patients import router as patients_router
from app.api.v1.patient_records import router as patient_records_router
from app.api.v1.prescriptions import router as prescriptions_router
from app.api.v1.queues import router as queues_router
from app.api.v1.referrals import router as referrals_router
from app.api.v1.system_check import router as system_check_router
from app.api.v1.test_rbac import router as test_rbac_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.voice import router as voice_router
from app.api.v1.voice_symptom import router as voice_symptom_router
from app.api.v1.reports import router as reports_router
from app.api.v1.symptoms import router as symptoms_router
from app.api.v1.chat import router as chat_router
from app.api.v1.followups import router as followups_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.dispensing import router as dispensing_router
from app.api.v1.billing import router as billing_router
from app.api.analytics import router as analytics_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(followups_router)
api_v1_router.include_router(dashboards_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(dispensing_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(facilities_router)






api_v1_router.include_router(patients_router)
api_v1_router.include_router(patient_records_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(consultations_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(fhir_router)
api_v1_router.include_router(interoperability_router)
api_v1_router.include_router(queues_router)
api_v1_router.include_router(encounters_router)
api_v1_router.include_router(referrals_router)
api_v1_router.include_router(medications_router)
api_v1_router.include_router(prescriptions_router)
api_v1_router.include_router(diagnostic_tests_router)
api_v1_router.include_router(diagnostics_router)
api_v1_router.include_router(test_rbac_router)
api_v1_router.include_router(system_check_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(voice_router)
api_v1_router.include_router(voice_symptom_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(symptoms_router)
