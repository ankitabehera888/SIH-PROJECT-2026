from typing import Any, Dict
from app.models.user import User


class PractitionerFHIRMapper:
    """Maps internal User clinical providers (DOCTOR, NURSE) into FHIR R4 Practitioner."""

    @staticmethod
    def to_fhir(user: User) -> Dict[str, Any]:
        role_title = "Dr." if user.role == "DOCTOR" else "Nurse"

        # Construct name
        name_parts = user.email.split("@")[0].replace(".", " ").replace("_", " ").title()

        return {
            "resourceType": "Practitioner",
            "id": str(user.id),
            "identifier": [
                {
                    "system": "https://hpr.abdm.gov.in",
                    "value": f"HPR-{user.id}",
                    "use": "official",
                }
            ],
            "active": user.is_active,
            "name": [
                {
                    "use": "official",
                    "prefix": [role_title],
                    "text": f"{role_title} {name_parts}",
                }
            ],
            "telecom": [
                {
                    "system": "email",
                    "value": user.email,
                    "use": "work",
                }
            ],
            "qualification": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                                "code": "MD" if user.role == "DOCTOR" else "RN",
                                "display": "Medical Doctor" if user.role == "DOCTOR" else "Registered Nurse",
                            }
                        ]
                    }
                }
            ],
        }
