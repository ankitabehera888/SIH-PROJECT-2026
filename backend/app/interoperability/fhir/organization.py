from typing import Any, Dict
from app.models.facility import Facility


class OrganizationFHIRMapper:
    """Maps internal Facility models (PHC, Sub-centre, Hospital) into FHIR R4 Organization."""

    @staticmethod
    def to_fhir(facility: Facility) -> Dict[str, Any]:
        facility_type_display = facility.facility_type.replace("_", " ").title()

        res: Dict[str, Any] = {
            "resourceType": "Organization",
            "id": str(facility.id),
            "identifier": [
                {
                    "system": "https://facility.abdm.gov.in",
                    "value": facility.facility_code,
                    "use": "official",
                }
            ],
            "active": facility.is_active,
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                            "code": "prov",
                            "display": "Healthcare Provider",
                        },
                        {
                            "system": "https://abdm.gov.in/facility-type",
                            "code": facility.facility_type,
                            "display": facility_type_display,
                        },
                    ],
                    "text": facility_type_display,
                }
            ],
            "name": facility.name,
        }

        if facility.phone:
            res["telecom"] = [
                {
                    "system": "phone",
                    "value": facility.phone,
                    "use": "work",
                }
            ]

        if facility.address:
            res["address"] = [
                {
                    "use": "work",
                    "text": facility.address,
                }
            ]

        return res
