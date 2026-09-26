from datetime import date, datetime, timezone
from typing import List
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.consultation import Consultation, ConsultationStatus
from app.models.facility import Facility
from app.models.followup import Followup, FollowupStatus
from app.models.patient import Patient
from app.models.referral import Referral, ReferralStatus
from app.models.user import User
from app.schemas.dashboard_views import (
    DoctorDashboardResponse,
    FollowupAlertSchema,
    JourneyStepSchema,
    PatientDashboardResponse,
    QueueItemSchema,
    ReferralAlertSchema,
)


class DashboardViewService:
    def __init__(self, db: Session):
        self.db = db

    def get_doctor_dashboard(self, current_user: User) -> DoctorDashboardResponse:
        today = date.today()

        # Todays appointments
        appointments_stmt = (
            select(Appointment)
            .where(
                Appointment.provider_id == current_user.id,
                Appointment.appointment_date == today,
                Appointment.status != AppointmentStatus.CANCELLED.value,
            )
            .order_by(Appointment.start_time)
        )
        appointments = self.db.scalars(appointments_stmt).all()

        in_person_queue: List[QueueItemSchema] = []
        video_queue: List[QueueItemSchema] = []

        for appt in appointments:
            p = appt.patient
            p_name = f"{p.first_name} {p.last_name}" if p else "Patient"
            p_age = None
            if p and p.date_of_birth:
                p_age = today.year - p.date_of_birth.year
            avatar = p_name[0] if p_name else "P"
            location = (p.address_line1 or "Local") if p else "Local"
            mode = "Video" if appt.appointment_type == AppointmentType.TELECONSULTATION.value else "In-Person"

            time_str = appt.start_time.strftime("%I:%M %p") if appt.start_time else "10:00 AM"

            item = QueueItemSchema(
                id=appt.id,
                patient_id=appt.patient_id,
                patient_name=p_name,
                patient_age=p_age,
                patient_avatar=avatar,
                patient_location=location,
                time=time_str,
                reason=appt.reason or "Clinical Consultation",
                mode=mode,
                priority="normal",
            )

            if mode == "Video":
                video_queue.append(item)
            else:
                in_person_queue.append(item)

        # Pending consultations count
        consultations_count = self.db.query(Consultation).filter(
            Consultation.doctor_id == current_user.id,
            Consultation.status.in_([ConsultationStatus.SCHEDULED.value, ConsultationStatus.READY.value]),
        ).count()

        # Pending referrals
        referrals_stmt = (
            select(Referral)
            .where(
                Referral.receiving_facility_id == current_user.facility_id,
                Referral.status == ReferralStatus.SUBMITTED.value,
            )
            .order_by(desc(Referral.created_at))
            .limit(5)
        )
        referrals = self.db.scalars(referrals_stmt).all()
        pending_referrals = [
            ReferralAlertSchema(
                id=ref.id,
                patient_name=f"{ref.patient.first_name} {ref.patient.last_name}" if ref.patient else "Patient",
                from_facility=ref.referring_facility.name if ref.referring_facility else "Referring Facility",
                reason=ref.reason_for_referral or "Specialist evaluation",
                created_at=ref.created_at,
            )
            for ref in referrals
        ]

        # Follow-ups due
        followups_stmt = (
            select(Followup)
            .where(
                Followup.provider_id == current_user.id,
                Followup.status == FollowupStatus.UPCOMING.value,
            )
            .order_by(Followup.scheduled_date)
            .limit(5)
        )
        followups = self.db.scalars(followups_stmt).all()
        followup_alerts = [
            FollowupAlertSchema(
                id=f.id,
                patient_name=f"{f.patient.first_name} {f.patient.last_name}" if f.patient else "Patient",
                condition=f.condition,
                due_date=f.scheduled_date.strftime("%b %d"),
                is_overdue=f.scheduled_date < today,
            )
            for f in followups
        ]

        return DoctorDashboardResponse(
            todays_patients_count=len(appointments),
            pending_consultations_count=consultations_count,
            pending_referrals_count=len(pending_referrals),
            followups_due_count=len(followup_alerts),
            in_person_queue=in_person_queue,
            video_queue=video_queue,
            pending_referrals=pending_referrals,
            followup_alerts=followup_alerts,
        )

    def get_patient_dashboard(self, current_user: User) -> PatientDashboardResponse:
        patient = self.db.scalars(select(Patient).where(Patient.created_by_id == current_user.id)).first()
        patient_id = patient.id if patient else None

        next_appt_dict = None
        if patient_id:
            appt = self.db.scalars(
                select(Appointment)
                .where(
                    Appointment.patient_id == patient_id,
                    Appointment.status == AppointmentStatus.SCHEDULED.value,
                )
                .order_by(Appointment.appointment_date)
            ).first()
            if appt:
                next_appt_dict = {
                    "id": str(appt.id),
                    "doctor": f"Dr. {appt.provider.email.split('@')[0].capitalize()}" if appt.provider else "Dr. Specialist",
                    "date": appt.appointment_date.strftime("%b %d, %Y"),
                    "time": appt.start_time.strftime("%I:%M %p") if appt.start_time else "10:00 AM",
                    "mode": appt.appointment_type,
                    "facility": appt.facility.name if appt.facility else "Central PHC",
                }

        # Care journey steps
        journey_steps = [
            JourneyStepSchema(label="Registration", status="completed", date="Aug 1"),
            JourneyStepSchema(label="Initial Assessment", status="completed", date="Aug 5"),
            JourneyStepSchema(label="PHC Consultation", status="completed", date="Aug 12"),
            JourneyStepSchema(label="Diagnostics & Vitals", status="current"),
            JourneyStepSchema(label="Treatment Plan", status="upcoming"),
            JourneyStepSchema(label="Follow-up Care", status="upcoming"),
        ]

        # Recommended facilities
        facs = self.db.scalars(select(Facility).limit(4)).all()
        rec_facilities = [
            {
                "id": str(fac.id),
                "name": fac.name,
                "type": fac.facility_type,
                "distance": "2.5",
                "doctorsAvailable": 4,
                "waitingTime": 15,
                "medicines": "Available",
            }
            for fac in facs
        ]

        return PatientDashboardResponse(
            next_appointment=next_appt_dict,
            care_journey=journey_steps,
            journey_percent=50,
            recommended_facilities=rec_facilities,
            urgent_alerts=[
                {"title": "Follow-up Reminder", "message": "Blood pressure review due this week"}
            ],
        )

    def get_worker_dashboard(self, current_user: User) -> WorkerDashboardResponse:
        pts = self.db.scalars(select(Patient).order_by(desc(Patient.created_at)).limit(5)).all()
        recent_patients = [
            {
                "id": str(p.id),
                "name": f"{p.first_name} {p.last_name}",
                "location": p.address_line1 or "Village Zone A",
                "avatar": p.first_name[0],
            }
            for p in pts
        ]

        facility_name = "PHC Chandrapur"
        if current_user.facility_id:
            fac = self.db.get(Facility, current_user.facility_id)
            if fac:
                facility_name = fac.name

        return WorkerDashboardResponse(
            todays_patients_count=len(recent_patients),
            pending_referrals_count=3,
            followups_count=5,
            high_priority_count=2,
            assigned_facility_name=facility_name,
            recent_patients=recent_patients,
        )

