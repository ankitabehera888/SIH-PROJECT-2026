from typing import Any, Dict, List
from app.models.diagnostic_result import DiagnosticResult
from app.models.vital import Vital


class ObservationFHIRMapper:
    """Maps internal Vital measurements and DiagnosticResults into standard LOINC FHIR R4 Observations."""

    @staticmethod
    def from_vital(vital: Vital) -> List[Dict[str, Any]]:
        """Converts a multi-measurement Vital record into a list of standardized FHIR Observations."""
        observations: List[Dict[str, Any]] = []
        effective_time = vital.recorded_at.isoformat() if vital.recorded_at else None

        base_meta = {
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ]
                }
            ],
            "subject": {"reference": f"Patient/{vital.patient_id}"},
            "encounter": {"reference": f"Encounter/{vital.encounter_id}"},
            "effectiveDateTime": effective_time,
        }

        # 1. Blood Pressure Panel (Structured Multi-component)
        if vital.systolic_bp is not None or vital.diastolic_bp is not None:
            bp_components = []
            if vital.systolic_bp is not None:
                bp_components.append({
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": vital.systolic_bp,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                })
            if vital.diastolic_bp is not None:
                bp_components.append({
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": vital.diastolic_bp,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                })

            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-bp",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "85354-9",
                            "display": "Blood pressure panel with all children optional",
                        }
                    ],
                    "text": "Blood Pressure",
                },
                "component": bp_components,
            })

        # 2. Heart Rate
        if vital.heart_rate is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-hr",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate",
                        }
                    ],
                    "text": "Heart Rate",
                },
                "valueQuantity": {
                    "value": vital.heart_rate,
                    "unit": "beats/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min",
                },
            })

        # 3. Body Temperature
        if vital.temperature is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-temp",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8310-5",
                            "display": "Body temperature",
                        }
                    ],
                    "text": "Body Temperature",
                },
                "valueQuantity": {
                    "value": vital.temperature,
                    "unit": "Celsius",
                    "system": "http://unitsofmeasure.org",
                    "code": "Cel",
                },
            })

        # 4. Respiratory Rate
        if vital.respiratory_rate is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-rr",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "9279-1",
                            "display": "Respiratory rate",
                        }
                    ],
                    "text": "Respiratory Rate",
                },
                "valueQuantity": {
                    "value": vital.respiratory_rate,
                    "unit": "breaths/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min",
                },
            })

        # 5. Oxygen Saturation (SpO2)
        spo2_val = getattr(vital, "spo2", getattr(vital, "oxygen_saturation", None))
        if spo2_val is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-spo2",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "2708-6",
                            "display": "Oxygen saturation in Arterial blood",
                        }
                    ],
                    "text": "Oxygen Saturation",
                },
                "valueQuantity": {
                    "value": spo2_val,
                    "unit": "%",
                    "system": "http://unitsofmeasure.org",
                    "code": "%",
                },
            })

        # 6. Weight
        if vital.weight is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-wt",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "29463-7",
                            "display": "Body weight",
                        }
                    ],
                    "text": "Body Weight",
                },
                "valueQuantity": {
                    "value": vital.weight,
                    "unit": "kg",
                    "system": "http://unitsofmeasure.org",
                    "code": "kg",
                },
            })

        # 7. Height
        if vital.height is not None:
            observations.append({
                "resourceType": "Observation",
                "id": f"{vital.id}-ht",
                **base_meta,
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8302-2",
                            "display": "Body height",
                        }
                    ],
                    "text": "Body Height",
                },
                "valueQuantity": {
                    "value": vital.height,
                    "unit": "cm",
                    "system": "http://unitsofmeasure.org",
                    "code": "cm",
                },
            })

        return observations

    @staticmethod
    def from_diagnostic_result(result: DiagnosticResult, test_name: str = "Diagnostic Test") -> Dict[str, Any]:
        """Converts a diagnostic result into an Observation."""
        effective_time = result.performed_at.isoformat() if result.performed_at else None

        obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": str(result.id),
            "status": "final" if result.result_status == "FINAL" else "preliminary",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "text": test_name,
            },
            "subject": {"reference": f"Patient/{result.patient_id}"},
            "effectiveDateTime": effective_time,
        }

        # Try to parse numerical value if possible, else string
        try:
            val_float = float(result.result_value)
            obs["valueQuantity"] = {
                "value": val_float,
                "unit": result.unit or "",
            }
        except (ValueError, TypeError):
            obs["valueString"] = result.result_value

        if result.reference_range:
            obs["referenceRange"] = [
                {
                    "text": result.reference_range,
                }
            ]

        if result.abnormal_flag:
            obs["interpretation"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "A",
                            "display": "Abnormal",
                        }
                    ]
                }
            ]

        return obs
