import math
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.appointment import Appointment
from app.models.diagnostic_order import DiagnosticOrder
from app.models.diagnostic_order_item import DiagnosticOrderItem
from app.models.encounter import Encounter
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.prescription_item import PrescriptionItem
from app.models.referral import Referral
from app.models.user import User
from app.models.vital import Vital
from app.schemas.appointment import AppointmentResponse
from app.schemas.diagnostic import DiagnosticOrderResponse
from app.schemas.encounter import EncounterResponse
from app.schemas.patient import PatientResponse
from app.schemas.patient_record import (
    PatientRecordResponse,
    PatientRecordSummary,
    PatientTimelineEvent,
    PatientTimelineResponse,
    TimelineEventType,
)
from app.schemas.prescription import PrescriptionResponse
from app.schemas.referral import ReferralResponse


class PatientRecordService:
    """Service orchestrating multi-domain longitudinal health records and clinical timeline projection."""

    def __init__(self, db: Session):
        self.db = db

    def _verify_patient_access(self, patient_id: uuid.UUID, current_user: User) -> Patient:
        stmt = select(Patient).where(Patient.id == patient_id)
        patient = self.db.scalars(stmt).first()
        if not patient or not patient.is_active:
            raise NotFoundException(message=f"Patient with id '{patient_id}' not found or inactive")

        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own longitudinal health record")

        return patient

    def _build_timeline_events(
        self,
        appointments: List[Appointment],
        encounters: List[Encounter],
        vitals: List[Vital],
        prescriptions: List[Prescription],
        diagnostic_orders: List[DiagnosticOrder],
        referrals: List[Referral],
    ) -> List[PatientTimelineEvent]:
        events: List[PatientTimelineEvent] = []

        # 1. Appointments
        for app in appointments:
            dt = datetime.combine(app.appointment_date, app.start_time).replace(tzinfo=timezone.utc)
            events.append(
                PatientTimelineEvent(
                    event_id=f"app_{app.id}",
                    event_type=TimelineEventType.APPOINTMENT,
                    event_date=dt,
                    title=f"Appointment ({app.appointment_type})",
                    summary_text=f"Status: {app.status}. Reason: {app.reason or 'Routine care'}",
                    source_id=app.id,
                    facility_id=app.facility_id,
                    provider_id=app.provider_id,
                    status=app.status,
                )
            )

        # 2. Encounters
        for enc in encounters:
            enc_dt = enc.started_at or enc.created_at
            events.append(
                PatientTimelineEvent(
                    event_id=f"enc_{enc.id}",
                    event_type=TimelineEventType.ENCOUNTER,
                    event_date=enc_dt,
                    title=f"Clinical Encounter ({enc.encounter_type})",
                    summary_text=f"Status: {enc.status}. Chief complaint: {enc.chief_complaint or 'Not recorded'}",
                    source_id=enc.id,
                    facility_id=enc.facility_id,
                    provider_id=enc.provider_id,
                    status=enc.status,
                )
            )

        # 3. Vitals
        for vit in vitals:
            vit_dt = vit.recorded_at
            summary_parts = []
            if vit.systolic_bp and vit.diastolic_bp:
                summary_parts.append(f"BP: {vit.systolic_bp}/{vit.diastolic_bp} mmHg")
            if vit.heart_rate:
                summary_parts.append(f"HR: {vit.heart_rate} bpm")
            if vit.spo2:
                summary_parts.append(f"SpO2: {vit.spo2}%")
            if vit.temperature:
                summary_parts.append(f"Temp: {vit.temperature}°C")

            events.append(
                PatientTimelineEvent(
                    event_id=f"vit_{vit.id}",
                    event_type=TimelineEventType.VITAL,
                    event_date=vit_dt,
                    title="Vitals Observation",
                    summary_text=", ".join(summary_parts) if summary_parts else "Observations recorded",
                    source_id=vit.id,
                    facility_id=None,
                    provider_id=vit.recorded_by,
                    status="RECORDED",
                )
            )

        # 4. Prescriptions
        for rx in prescriptions:
            rx_dt = rx.prescribed_at or rx.created_at
            med_names = [item.medication.name for item in rx.items if item.medication]
            items_str = ", ".join(med_names) if med_names else f"{len(rx.items)} medication(s)"
            events.append(
                PatientTimelineEvent(
                    event_id=f"rx_{rx.id}",
                    event_type=TimelineEventType.PRESCRIPTION,
                    event_date=rx_dt,
                    title="Medication Prescription",
                    summary_text=f"Status: {rx.status}. Prescribed: {items_str}",
                    source_id=rx.id,
                    facility_id=rx.facility_id,
                    provider_id=rx.prescriber_id,
                    status=rx.status,
                )
            )

        # 5. Diagnostic Orders and Results
        for ord_obj in diagnostic_orders:
            ord_dt = ord_obj.ordered_at or ord_obj.created_at
            test_names = [item.test.name for item in ord_obj.items if item.test]
            tests_str = ", ".join(test_names) if test_names else f"{len(ord_obj.items)} test(s)"
            events.append(
                PatientTimelineEvent(
                    event_id=f"diag_ord_{ord_obj.id}",
                    event_type=TimelineEventType.DIAGNOSTIC_ORDER,
                    event_date=ord_dt,
                    title=f"Diagnostic Order ({ord_obj.priority})",
                    summary_text=f"Status: {ord_obj.status}. Tests ordered: {tests_str}",
                    source_id=ord_obj.id,
                    facility_id=ord_obj.facility_id,
                    provider_id=ord_obj.ordering_provider_id,
                    status=ord_obj.status,
                )
            )

            for item in ord_obj.items:
                if item.result:
                    res = item.result
                    res_dt = res.verified_at or res.performed_at or ord_dt
                    test_label = item.test.name if item.test else "Investigation"
                    abnormal_str = " [ABNORMAL]" if res.abnormal_flag else ""
                    unit_str = f" {res.unit}" if res.unit else ""
                    events.append(
                        PatientTimelineEvent(
                            event_id=f"diag_res_{res.id}",
                            event_type=TimelineEventType.DIAGNOSTIC_RESULT,
                            event_date=res_dt,
                            title=f"Lab Finding: {test_label}",
                            summary_text=f"Result: {res.result_value}{unit_str}{abnormal_str}. Status: {res.result_status}",
                            source_id=res.id,
                            facility_id=ord_obj.facility_id,
                            provider_id=res.verified_by or ord_obj.ordering_provider_id,
                            status=res.result_status,
                        )
                    )

        # 6. Referrals
        for ref in referrals:
            ref_dt = ref.created_at
            events.append(
                PatientTimelineEvent(
                    event_id=f"ref_{ref.id}",
                    event_type=TimelineEventType.REFERRAL,
                    event_date=ref_dt,
                    title=f"Care Referral ({ref.priority})",
                    summary_text=f"Status: {ref.status}. Type: {ref.referral_type}. Reason: {ref.reason}",
                    source_id=ref.id,
                    facility_id=ref.referring_facility_id,
                    provider_id=ref.referring_provider_id,
                    status=ref.status,
                )
            )

        # Sort reverse chronologically (most recent clinical event first)
        events.sort(key=lambda e: e.event_date, reverse=True)
        return events

    def get_patient_record(
        self,
        patient_id: uuid.UUID,
        current_user: User,
    ) -> PatientRecordResponse:
        patient = self._verify_patient_access(patient_id, current_user)

        # 1. Encounters
        encounters = list(
            self.db.scalars(
                select(Encounter)
                .where(Encounter.patient_id == patient_id)
                .order_by(Encounter.created_at.desc())
            ).all()
        )

        # 2. Vitals
        vitals = list(
            self.db.scalars(
                select(Vital)
                .where(Vital.patient_id == patient_id)
                .order_by(Vital.recorded_at.desc())
            ).all()
        )

        # 3. Prescriptions with Items and Medications
        prescriptions = list(
            self.db.scalars(
                select(Prescription)
                .where(Prescription.patient_id == patient_id)
                .options(selectinload(Prescription.items).joinedload(PrescriptionItem.medication))
                .order_by(Prescription.prescribed_at.desc())
            ).all()
        )

        # 4. Diagnostic Orders with Items, Tests, and Results
        diagnostic_orders = list(
            self.db.scalars(
                select(DiagnosticOrder)
                .where(DiagnosticOrder.patient_id == patient_id)
                .options(
                    selectinload(DiagnosticOrder.items).joinedload(DiagnosticOrderItem.test),
                    selectinload(DiagnosticOrder.items).joinedload(DiagnosticOrderItem.result),
                )
                .order_by(DiagnosticOrder.ordered_at.desc())
            ).all()
        )

        # 5. Referrals
        referrals = list(
            self.db.scalars(
                select(Referral)
                .where(Referral.patient_id == patient_id)
                .order_by(Referral.created_at.desc())
            ).all()
        )

        # 6. Appointments
        appointments = list(
            self.db.scalars(
                select(Appointment)
                .where(Appointment.patient_id == patient_id)
                .order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
            ).all()
        )

        # Compute summary
        last_enc_at = encounters[0].started_at or encounters[0].created_at if encounters else None
        last_fac_id = encounters[0].facility_id if encounters else None

        summary = PatientRecordSummary(
            total_encounters=len(encounters),
            total_vitals_recorded=len(vitals),
            total_prescriptions=len(prescriptions),
            total_diagnostic_orders=len(diagnostic_orders),
            total_referrals=len(referrals),
            total_appointments=len(appointments),
            last_encounter_at=last_enc_at,
            last_facility_id=last_fac_id,
        )

        # Build chronological timeline
        timeline = self._build_timeline_events(
            appointments=appointments,
            encounters=encounters,
            vitals=vitals,
            prescriptions=prescriptions,
            diagnostic_orders=diagnostic_orders,
            referrals=referrals,
        )

        return PatientRecordResponse(
            patient=PatientResponse.model_validate(patient),
            summary=summary,
            timeline=timeline,
            encounters=[EncounterResponse.model_validate(e) for e in encounters],
            prescriptions=[PrescriptionResponse.model_validate(p) for p in prescriptions],
            diagnostic_orders=[DiagnosticOrderResponse.model_validate(d) for d in diagnostic_orders],
            referrals=[ReferralResponse.model_validate(r) for r in referrals],
            appointments=[AppointmentResponse.model_validate(a) for a in appointments],
        )

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @classmethod
    def _parse_dt(cls, val: Optional[Union[str, datetime]]) -> Optional[datetime]:
        if not val:
            return None
        if isinstance(val, datetime):
            return cls._ensure_utc(val)
        s = val.strip().replace(" ", "+")
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        return cls._ensure_utc(dt)

    def get_patient_timeline(
        self,
        patient_id: uuid.UUID,
        current_user: User,
        event_type: Optional[str] = None,
        from_date: Optional[Union[str, datetime]] = None,
        to_date: Optional[Union[str, datetime]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PatientTimelineResponse:
        patient = self._verify_patient_access(patient_id, current_user)

        # Fetch records efficiently
        encounters = list(
            self.db.scalars(
                select(Encounter).where(Encounter.patient_id == patient_id)
            ).all()
        )
        vitals = list(
            self.db.scalars(
                select(Vital).where(Vital.patient_id == patient_id)
            ).all()
        )
        prescriptions = list(
            self.db.scalars(
                select(Prescription)
                .where(Prescription.patient_id == patient_id)
                .options(selectinload(Prescription.items).joinedload(PrescriptionItem.medication))
            ).all()
        )
        diagnostic_orders = list(
            self.db.scalars(
                select(DiagnosticOrder)
                .where(DiagnosticOrder.patient_id == patient_id)
                .options(
                    selectinload(DiagnosticOrder.items).joinedload(DiagnosticOrderItem.test),
                    selectinload(DiagnosticOrder.items).joinedload(DiagnosticOrderItem.result),
                )
            ).all()
        )
        referrals = list(
            self.db.scalars(
                select(Referral).where(Referral.patient_id == patient_id)
            ).all()
        )
        appointments = list(
            self.db.scalars(
                select(Appointment).where(Appointment.patient_id == patient_id)
            ).all()
        )

        all_events = self._build_timeline_events(
            appointments=appointments,
            encounters=encounters,
            vitals=vitals,
            prescriptions=prescriptions,
            diagnostic_orders=diagnostic_orders,
            referrals=referrals,
        )

        # Filter events
        filtered_events = all_events

        if event_type:
            filtered_events = [
                e for e in filtered_events if e.event_type.value == event_type or e.event_type == event_type
            ]

        parsed_from = self._parse_dt(from_date)
        if parsed_from:
            filtered_events = [e for e in filtered_events if self._ensure_utc(e.event_date) >= parsed_from]

        parsed_to = self._parse_dt(to_date)
        if parsed_to:
            filtered_events = [e for e in filtered_events if self._ensure_utc(e.event_date) <= parsed_to]

        total = len(filtered_events)
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        paged_events = filtered_events[skip : skip + page_size]

        return PatientTimelineResponse.create(
            items=paged_events,
            total=total,
            page=page,
            page_size=page_size,
        )
