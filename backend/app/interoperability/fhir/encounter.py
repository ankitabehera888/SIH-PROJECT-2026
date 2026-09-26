from typing import Any, Dict
from app.models.encounter import Encounter


class EncounterFHIRMapper:
    """Maps internal Encounter model into FHIR R4 Encounter."""

    @staticmethod
    def to_fhir(encounter: Encounter) -> Dict[str, Any]:
        status_map = {
            "IN_PROGRESS": "in-progress",
            "COMPLETED": "finished",
            "CANCELLED": "cancelled",
        }
        fhir_status = status_map.get(str(encounter.status).upper(), "in-progress")

        res: Dict[str, Any] = {
            "resourceType": "Encounter",
            "id": str(encounter.id),
            "status": fhir_status,
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB" if encounter.encounter_type == "OUTPATIENT" else "EMER",
                "display": "ambulatory" if encounter.encounter_type == "OUTPATIENT" else "emergency",
            },
            "subject": {
                "reference": f"Patient/{encounter.patient_id}",
            },
            "participant": [
                {
                    "individual": {
                        "reference": f"Practitioner/{encounter.provider_id}",
                    }
                }
            ],
            "period": {
                "start": encounter.started_at.isoformat() if encounter.started_at else None,
                "end": encounter.ended_at.isoformat() if encounter.ended_at else None,
            },
            "serviceProvider": {
                "reference": f"Organization/{encounter.facility_id}",
            },
        }

        if encounter.appointment_id:
            res["appointment"] = [
                {
                    "reference": f"Appointment/{encounter.appointment_id}",
                }
            ]

        if encounter.chief_complaint:
            res["reasonCode"] = [
                {
                    "text": encounter.chief_complaint,
                }
            ]

        return res
