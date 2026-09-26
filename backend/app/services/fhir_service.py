from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.interoperability.fhir import (
    AppointmentFHIRMapper,
    BundleBuilder,
    DiagnosticReportFHIRMapper,
    EncounterFHIRMapper,
    FHIRValidator,
    MedicationFHIRMapper,
    MedicationRequestFHIRMapper,
    ObservationFHIRMapper,
    OrganizationFHIRMapper,
    PatientFHIRMapper,
    PractitionerFHIRMapper,
    ServiceRequestFHIRMapper,
)
from app.models.appointment import Appointment
from app.models.diagnostic_order import DiagnosticOrder
from app.models.diagnostic_result import DiagnosticResult
from app.models.encounter import Encounter
from app.models.facility import Facility
from app.models.interoperability_audit import InteropAction
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.prescription_item import PrescriptionItem
from app.models.referral import Referral
from app.models.user import User
from app.models.vital import Vital
from app.repositories.interoperability_repository import InteroperabilityRepository
from app.repositories.patient_repository import PatientRepository


class FHIRService:
    """Service layer orchestrating HL7 FHIR R4 resource conversion, validation, security, and export."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = InteroperabilityRepository

    def _verify_patient_access(self, patient_id: uuid.UUID, current_user: User):
        patient = self.db.get(Patient, patient_id)
        if not patient:
            raise NotFoundException(f"Patient with id '{patient_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException("Access denied: Cannot access another patient's clinical records")
        elif current_user.role not in (
            UserRole.DOCTOR.value,
            UserRole.ADMIN.value,
            UserRole.NURSE.value,
        ):
            raise ForbiddenException("Access denied: Insufficient privileges")

        return patient

    def get_patient_resource(self, patient_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        patient = self._verify_patient_access(patient_id, current_user)
        identifiers = self.repo.list_identifiers_by_patient(self.db, patient_id)
        fhir_res = PatientFHIRMapper.to_fhir(patient, identifiers)
        FHIRValidator.assert_valid(fhir_res)

        self.repo.record_audit(
            self.db,
            action=InteropAction.FHIR_READ.value,
            resource_type="Patient",
            resource_id=str(patient_id),
            patient_id=patient_id,
            user_id=current_user.id,
        )
        return fhir_res

    def get_practitioner_resource(self, practitioner_id: int, current_user: User) -> Dict[str, Any]:
        user = self.db.get(User, practitioner_id)
        if not user or user.role not in (UserRole.DOCTOR.value, UserRole.NURSE.value):
            raise NotFoundException(f"Practitioner with id '{practitioner_id}' not found")

        fhir_res = PractitionerFHIRMapper.to_fhir(user)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_organization_resource(self, facility_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        facility = self.db.get(Facility, facility_id)
        if not facility:
            raise NotFoundException(f"Organization with id '{facility_id}' not found")

        fhir_res = OrganizationFHIRMapper.to_fhir(facility)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_appointment_resource(self, appointment_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        appt = self.db.get(Appointment, appointment_id)
        if not appt:
            raise NotFoundException(f"Appointment with id '{appointment_id}' not found")

        self._verify_patient_access(appt.patient_id, current_user)
        fhir_res = AppointmentFHIRMapper.to_fhir(appt)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_encounter_resource(self, encounter_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        encounter = self.db.get(Encounter, encounter_id)
        if not encounter:
            raise NotFoundException(f"Encounter with id '{encounter_id}' not found")

        self._verify_patient_access(encounter.patient_id, current_user)
        fhir_res = EncounterFHIRMapper.to_fhir(encounter)
        FHIRValidator.assert_valid(fhir_res)

        self.repo.record_audit(
            self.db,
            action=InteropAction.FHIR_READ.value,
            resource_type="Encounter",
            resource_id=str(encounter_id),
            patient_id=encounter.patient_id,
            user_id=current_user.id,
        )
        return fhir_res

    def get_observation_resource(self, observation_id: str, current_user: User) -> Dict[str, Any]:
        # Observation can be derived from vital or diagnostic result
        vital_uuid_str = observation_id
        if "-" in observation_id and observation_id.rsplit("-", 1)[-1] in (
            "bp", "hr", "temp", "spo2", "rr", "wt", "ht"
        ):
            vital_uuid_str = observation_id.rsplit("-", 1)[0]

        try:
            vital_uuid = uuid.UUID(vital_uuid_str)
            vital = self.db.get(Vital, vital_uuid)
            if vital:
                self._verify_patient_access(vital.patient_id, current_user)
                v_obs_list = ObservationFHIRMapper.from_vital(vital)
                match = next((o for o in v_obs_list if o["id"] == observation_id), None)
                if match:
                    FHIRValidator.assert_valid(match)
                    return match
                elif v_obs_list:
                    return v_obs_list[0]
        except ValueError:
            pass

        # Check DiagnosticResult
        try:
            diag_uuid = uuid.UUID(observation_id)
            result = self.db.get(DiagnosticResult, diag_uuid)
            if result:
                self._verify_patient_access(result.patient_id, current_user)
                obs = ObservationFHIRMapper.from_diagnostic_result(result)
                FHIRValidator.assert_valid(obs)
                return obs
        except ValueError:
            pass

        raise NotFoundException(f"Observation with id '{observation_id}' not found")

    def get_medication_resource(self, medication_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        med = self.db.get(Medication, medication_id)
        if not med:
            raise NotFoundException(f"Medication with id '{medication_id}' not found")
        fhir_res = MedicationFHIRMapper.to_fhir(med)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_medication_request_resource(self, item_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        item = self.db.get(PrescriptionItem, item_id)
        if not item:
            raise NotFoundException(f"Prescription item with id '{item_id}' not found")

        prescription = self.db.get(Prescription, item.prescription_id)
        self._verify_patient_access(prescription.patient_id, current_user)

        fhir_res = MedicationRequestFHIRMapper.to_fhir(item, prescription)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_service_request_resource(self, request_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        order = self.db.get(DiagnosticOrder, request_id)
        if order:
            self._verify_patient_access(order.patient_id, current_user)
            test_names = [it.diagnostic_test.name for it in order.items if getattr(it, "diagnostic_test", None)]
            fhir_res = ServiceRequestFHIRMapper.from_diagnostic_order(order, test_names)
            FHIRValidator.assert_valid(fhir_res)
            return fhir_res

        referral = self.db.get(Referral, request_id)
        if referral:
            self._verify_patient_access(referral.patient_id, current_user)
            fhir_res = ServiceRequestFHIRMapper.from_referral(referral)
            FHIRValidator.assert_valid(fhir_res)
            return fhir_res

        raise NotFoundException(f"ServiceRequest with id '{request_id}' not found")

    def get_diagnostic_report_resource(self, order_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        order = self.db.get(DiagnosticOrder, order_id)
        if not order:
            raise NotFoundException(f"DiagnosticOrder with id '{order_id}' not found")

        self._verify_patient_access(order.patient_id, current_user)

        results = []
        test_names = []
        for it in order.items:
            if getattr(it, "diagnostic_test", None):
                test_names.append(it.diagnostic_test.name)
            if getattr(it, "result", None):
                results.append(it.result)

        fhir_res = DiagnosticReportFHIRMapper.to_fhir(order, results, test_names)
        FHIRValidator.assert_valid(fhir_res)
        return fhir_res

    def get_patient_bundle(
        self,
        patient_id: uuid.UUID,
        bundle_type: str = "collection",
        current_user: User = None,
    ) -> Dict[str, Any]:
        """Assembles a consolidated, fully cross-referenced FHIR R4 Bundle for the patient."""
        patient = self._verify_patient_access(patient_id, current_user)
        resources: List[Dict[str, Any]] = []

        # 1. Patient
        identifiers = self.repo.list_identifiers_by_patient(self.db, patient_id)
        resources.append(PatientFHIRMapper.to_fhir(patient, identifiers))

        # 2. Encounters & Participating Entities
        encounters = self.db.scalars(
            select(Encounter).where(Encounter.patient_id == patient_id).order_by(Encounter.started_at.asc())
        ).all()

        practitioner_ids = set()
        facility_ids = set()

        for enc in encounters:
            resources.append(EncounterFHIRMapper.to_fhir(enc))
            practitioner_ids.add(enc.provider_id)
            facility_ids.add(enc.facility_id)

        # 3. Practitioners & Organizations
        for pr_id in practitioner_ids:
            u = self.db.get(User, pr_id)
            if u:
                resources.append(PractitionerFHIRMapper.to_fhir(u))

        for fac_id in facility_ids:
            fac = self.db.get(Facility, fac_id)
            if fac:
                resources.append(OrganizationFHIRMapper.to_fhir(fac))

        # 4. Vitals -> Observations
        vitals = self.db.scalars(select(Vital).where(Vital.patient_id == patient_id)).all()
        for v in vitals:
            obs_list = ObservationFHIRMapper.from_vital(v)
            resources.extend(obs_list)

        # 5. Prescriptions -> MedicationRequests & Medications
        prescriptions = self.db.scalars(
            select(Prescription).where(Prescription.patient_id == patient_id)
        ).all()
        for p in prescriptions:
            for it in p.items:
                if getattr(it, "medication", None):
                    resources.append(MedicationFHIRMapper.to_fhir(it.medication))
                resources.append(MedicationRequestFHIRMapper.to_fhir(it, p))

        # 6. Diagnostics -> ServiceRequests, DiagnosticReports, Observations
        diag_orders = self.db.scalars(
            select(DiagnosticOrder).where(DiagnosticOrder.patient_id == patient_id)
        ).all()
        for o in diag_orders:
            test_names = [it.diagnostic_test.name for it in o.items if getattr(it, "diagnostic_test", None)]
            results = [it.result for it in o.items if getattr(it, "result", None)]

            resources.append(ServiceRequestFHIRMapper.from_diagnostic_order(o, test_names))
            resources.append(DiagnosticReportFHIRMapper.to_fhir(o, results, test_names))
            for r in results:
                resources.append(ObservationFHIRMapper.from_diagnostic_result(r))

        # 7. Referrals -> ServiceRequests
        referrals = self.db.scalars(
            select(Referral).where(Referral.patient_id == patient_id)
        ).all()
        for ref in referrals:
            resources.append(ServiceRequestFHIRMapper.from_referral(ref))

        # Assemble Bundle
        bundle = BundleBuilder.build_collection_bundle(resources, bundle_type=bundle_type)
        FHIRValidator.assert_valid(bundle)

        # Record Audit Trail
        self.repo.record_audit(
            self.db,
            action=InteropAction.FHIR_BUNDLE_EXPORT.value,
            resource_type="Bundle",
            resource_id=bundle["id"],
            patient_id=patient_id,
            user_id=current_user.id if current_user else None,
            purpose="LONGITUDINAL_EXPORT",
            details=f"Exported {bundle['total']} FHIR R4 resources in bundle.",
        )

        return bundle
