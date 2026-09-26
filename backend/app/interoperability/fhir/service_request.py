from typing import Any, Dict, List, Optional
from app.models.diagnostic_order import DiagnosticOrder
from app.models.referral import Referral


class ServiceRequestFHIRMapper:
    """Maps internal DiagnosticOrder and Referral into FHIR R4 ServiceRequest."""

    @staticmethod
    def from_diagnostic_order(order: DiagnosticOrder, test_names: Optional[List[str]] = None) -> Dict[str, Any]:
        status_map = {
            "DRAFT": "draft",
            "ORDERED": "active",
            "IN_PROGRESS": "active",
            "COMPLETED": "completed",
            "CANCELLED": "revoked",
        }
        priority_map = {
            "ROUTINE": "routine",
            "URGENT": "urgent",
            "STAT": "stat",
        }

        description = ", ".join(test_names) if test_names else (order.notes or "Diagnostic Investigation")

        return {
            "resourceType": "ServiceRequest",
            "id": str(order.id),
            "status": status_map.get(str(order.status).upper(), "active"),
            "intent": "order",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "108252007",
                            "display": "Laboratory procedure",
                        }
                    ],
                    "text": "Diagnostic Investigation",
                }
            ],
            "priority": priority_map.get(str(order.priority).upper(), "routine"),
            "code": {
                "text": description,
            },
            "subject": {
                "reference": f"Patient/{order.patient_id}",
            },
            "encounter": {
                "reference": f"Encounter/{order.encounter_id}",
            },
            "authoredOn": (order.ordered_at if getattr(order, "ordered_at", None) else getattr(order, "order_date", None)).isoformat() if (getattr(order, "ordered_at", None) or getattr(order, "order_date", None)) else None,
            "requester": {
                "reference": f"Practitioner/{order.ordering_provider_id}",
            },
        }

    @staticmethod
    def from_referral(referral: Referral) -> Dict[str, Any]:
        status_map = {
            "DRAFT": "draft",
            "SENT": "active",
            "ACCEPTED": "active",
            "SCHEDULED": "active",
            "COMPLETED": "completed",
            "REJECTED": "revoked",
            "CANCELLED": "revoked",
            "EXPIRED": "revoked",
        }
        priority_map = {
            "ROUTINE": "routine",
            "URGENT": "urgent",
            "EMERGENCY": "stat",
        }

        res: Dict[str, Any] = {
            "resourceType": "ServiceRequest",
            "id": str(referral.id),
            "status": status_map.get(str(referral.status).upper(), "active"),
            "intent": "order",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "3457005",
                            "display": "Patient referral",
                        }
                    ],
                    "text": f"Care Transfer: {referral.referral_type}",
                }
            ],
            "priority": priority_map.get(str(referral.priority).upper(), "routine"),
            "code": {
                "text": f"Referral to higher facility: {referral.clinical_summary or referral.reason}",
            },
            "subject": {
                "reference": f"Patient/{referral.patient_id}",
            },
            "encounter": {
                "reference": f"Encounter/{referral.encounter_id}",
            },
            "requester": {
                "reference": f"Practitioner/{referral.referring_provider_id}",
            },
            "performer": [
                {
                    "reference": f"Organization/{referral.receiving_facility_id}",
                }
            ],
            "reasonCode": [
                {
                    "text": referral.reason,
                }
            ],
        }

        return res
