from typing import Any, Dict, List, Optional
from app.models.patient import Patient
from app.models.patient_identifier import PatientIdentifier


class PatientFHIRMapper:
    """Maps internal Patient model + external PatientIdentifiers into FHIR R4 Patient."""

    @staticmethod
    def to_fhir(patient: Patient, identifiers: Optional[List[PatientIdentifier]] = None) -> Dict[str, Any]:
        fhir_identifiers = [
            {
                "use": "usual",
                "system": "https://healthcare.gov.in/patient-number",
                "value": patient.patient_number,
            }
        ]

        if identifiers:
            for ident in identifiers:
                if ident.status != "REVOKED":
                    fhir_identifiers.append({
                        "use": "official" if ident.identifier_type == "ABHA_NUMBER" else "secondary",
                        "system": ident.system,
                        "value": ident.value,
                    })

        # Name mapping
        given_names = [patient.first_name]
        if patient.middle_name:
            given_names.append(patient.middle_name)

        full_name = f"{patient.first_name} {patient.middle_name + ' ' if patient.middle_name else ''}{patient.last_name}"

        # Telecom mapping
        telecoms = []
        if patient.phone:
            telecoms.append({
                "system": "phone",
                "value": patient.phone,
                "use": "mobile",
            })
        if patient.email:
            telecoms.append({
                "system": "email",
                "value": patient.email,
                "use": "home",
            })

        # Gender mapping to FHIR code (male | female | other | unknown)
        gender_map = {
            "MALE": "male",
            "FEMALE": "female",
            "OTHER": "other",
        }
        fhir_gender = gender_map.get(str(patient.gender).upper(), "unknown")

        fhir_patient: Dict[str, Any] = {
            "resourceType": "Patient",
            "id": str(patient.id),
            "identifier": fhir_identifiers,
            "active": patient.is_active,
            "name": [
                {
                    "use": "official",
                    "text": full_name,
                    "family": patient.last_name,
                    "given": given_names,
                }
            ],
            "gender": fhir_gender,
            "birthDate": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        }

        if telecoms:
            fhir_patient["telecom"] = telecoms

        if patient.address:
            fhir_patient["address"] = [
                {
                    "use": "home",
                    "text": patient.address,
                }
            ]

        return fhir_patient
