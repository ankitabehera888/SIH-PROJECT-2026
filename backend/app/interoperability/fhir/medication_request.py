from typing import Any, Dict
from app.models.prescription import Prescription
from app.models.prescription_item import PrescriptionItem


class MedicationRequestFHIRMapper:
    """Maps internal PrescriptionItem and Prescription into FHIR R4 MedicationRequest."""

    @staticmethod
    def to_fhir(item: PrescriptionItem, prescription: Prescription) -> Dict[str, Any]:
        status_map = {
            "ACTIVE": "active",
            "DISPENSED": "completed",
            "COMPLETED": "completed",
            "CANCELLED": "cancelled",
        }
        fhir_status = status_map.get(str(prescription.status).upper(), "active")

        # Dosage instruction
        dosage_text = item.instructions or f"{item.dosage}, {item.frequency} for {item.duration} {item.duration_unit}"

        # Frequency parsing helper
        freq_int = 1
        if "TWICE" in item.frequency.upper():
            freq_int = 2
        elif "THRICE" in item.frequency.upper() or "THREE" in item.frequency.upper():
            freq_int = 3
        elif "FOUR" in item.frequency.upper():
            freq_int = 4

        res: Dict[str, Any] = {
            "resourceType": "MedicationRequest",
            "id": str(item.id),
            "status": fhir_status,
            "intent": "order",
            "medicationReference": {
                "reference": f"Medication/{item.medication_id}",
                "display": item.medication.name if getattr(item, "medication", None) else None,
            },
            "subject": {
                "reference": f"Patient/{prescription.patient_id}",
            },
            "encounter": {
                "reference": f"Encounter/{prescription.encounter_id}",
            },
            "authoredOn": prescription.prescribed_at.isoformat() if prescription.prescribed_at else None,
            "requester": {
                "reference": f"Practitioner/{getattr(prescription, 'prescriber_id', getattr(prescription, 'provider_id', None))}",
            },
            "dosageInstruction": [
                {
                    "text": dosage_text,
                    "timing": {
                        "repeat": {
                            "frequency": freq_int,
                            "period": 1,
                            "periodUnit": "d",
                        }
                    },
                    "route": {
                        "text": item.route,
                    },
                }
            ],
            "dispenseRequest": {
                "quantity": {
                    "value": item.quantity,
                },
                "expectedSupplyDuration": {
                    "value": item.duration,
                    "unit": item.duration_unit.lower(),
                },
            },
        }

        return res
