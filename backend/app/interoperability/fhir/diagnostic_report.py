from typing import Any, Dict, List, Optional
from app.models.diagnostic_order import DiagnosticOrder
from app.models.diagnostic_result import DiagnosticResult


class DiagnosticReportFHIRMapper:
    """Maps internal DiagnosticOrder + DiagnosticResults into FHIR R4 DiagnosticReport."""

    @staticmethod
    def to_fhir(
        order: DiagnosticOrder,
        results: Optional[List[DiagnosticResult]] = None,
        test_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        has_results = bool(results)
        fhir_status = "final" if (order.status == "COMPLETED" or has_results) else "preliminary"
        if order.status == "CANCELLED":
            fhir_status = "cancelled"

        report_title = ", ".join(test_names) if test_names else "Diagnostic Investigation Report"

        result_references = []
        conclusions = []
        if results:
            for r in results:
                result_references.append({
                    "reference": f"Observation/{r.id}",
                    "display": f"Result: {r.result_value} {r.unit or ''}".strip(),
                })
                if r.abnormal_flag:
                    conclusions.append(f"Abnormal finding in result ({r.result_value} {r.unit or ''})")

        conclusion_text = order.notes or (" ; ".join(conclusions) if conclusions else "Investigation within normal limits.")

        res: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": str(order.id),
            "status": fhir_status,
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                            "code": "LAB",
                            "display": "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "text": report_title,
            },
            "subject": {
                "reference": f"Patient/{order.patient_id}",
            },
            "encounter": {
                "reference": f"Encounter/{order.encounter_id}",
            },
            "effectiveDateTime": (order.ordered_at if getattr(order, "ordered_at", None) else getattr(order, "order_date", None)).isoformat() if (getattr(order, "ordered_at", None) or getattr(order, "order_date", None)) else None,
            "conclusion": conclusion_text,
        }

        if result_references:
            res["result"] = result_references

        return res
