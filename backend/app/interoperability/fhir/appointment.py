from datetime import datetime, timezone
from typing import Any, Dict
from app.models.appointment import Appointment


class AppointmentFHIRMapper:
    """Maps internal Appointment model into FHIR R4 Appointment."""

    @staticmethod
    def to_fhir(appointment: Appointment) -> Dict[str, Any]:
        status_map = {
            "BOOKED": "booked",
            "CONFIRMED": "booked",
            "CHECKED_IN": "arrived",
            "IN_PROGRESS": "arrived",
            "COMPLETED": "fulfilled",
            "CANCELLED": "cancelled",
            "NO_SHOW": "noshow",
        }
        fhir_status = status_map.get(str(appointment.status).upper(), "booked")

        start_dt = datetime.combine(
            appointment.appointment_date,
            appointment.start_time,
        ).replace(tzinfo=timezone.utc).isoformat()

        end_dt = datetime.combine(
            appointment.appointment_date,
            appointment.end_time,
        ).replace(tzinfo=timezone.utc).isoformat()

        participants = [
            {
                "actor": {
                    "reference": f"Patient/{appointment.patient_id}",
                },
                "status": "accepted",
            },
            {
                "actor": {
                    "reference": f"Practitioner/{appointment.provider_id}",
                },
                "status": "accepted",
            },
        ]

        if appointment.facility_id:
            participants.append({
                "actor": {
                    "reference": f"Organization/{appointment.facility_id}",
                },
                "status": "accepted",
            })

        res: Dict[str, Any] = {
            "resourceType": "Appointment",
            "id": str(appointment.id),
            "status": fhir_status,
            "appointmentType": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0276",
                        "code": "ROUTINE" if appointment.appointment_type == "IN_PERSON" else "TELEHEALTH",
                        "display": "Routine appointment" if appointment.appointment_type == "IN_PERSON" else "Telehealth consultation",
                    }
                ]
            },
            "description": appointment.reason or "Clinical Consultation",
            "start": start_dt,
            "end": end_dt,
            "participant": participants,
        }

        return res
