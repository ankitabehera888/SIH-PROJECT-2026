from typing import Any, Dict
from app.models.medication import Medication


class MedicationFHIRMapper:
    """Maps internal Medication catalog model into FHIR R4 Medication."""

    @staticmethod
    def to_fhir(medication: Medication) -> Dict[str, Any]:
        return {
            "resourceType": "Medication",
            "id": str(medication.id),
            "code": {
                "coding": [
                    {
                        "system": "https://healthcare.gov.in/medications",
                        "code": getattr(medication, "code", medication.generic_name),
                        "display": medication.name,
                    }
                ],
                "text": f"{medication.name} {medication.strength or ''} {medication.dosage_form or ''}".strip(),
            },
            "status": "active" if medication.is_active else "inactive",
            "form": {
                "text": medication.dosage_form,
            },
        }
