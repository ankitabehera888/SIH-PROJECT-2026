from typing import Any, Dict, List, Tuple


class FHIRValidationError(Exception):
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []


class FHIRValidator:
    """Validates structural and semantic compliance of FHIR R4 resources."""

    VALID_RESOURCE_TYPES = {
        "Patient",
        "Practitioner",
        "Organization",
        "Appointment",
        "Encounter",
        "Observation",
        "Medication",
        "MedicationRequest",
        "ServiceRequest",
        "DiagnosticReport",
        "Bundle",
    }

    @classmethod
    def validate_resource(cls, resource: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not isinstance(resource, dict):
            return False, ["Resource must be a JSON object"]

        res_type = resource.get("resourceType")
        if not res_type:
            errors.append("Missing required field 'resourceType'")
            return False, errors

        if res_type not in cls.VALID_RESOURCE_TYPES:
            errors.append(f"Unsupported or unrecognized FHIR resourceType '{res_type}'")

        if not resource.get("id"):
            errors.append(f"Resource '{res_type}' must contain a unique 'id'")

        # Resource-specific structural validations
        if res_type == "Patient":
            if "gender" in resource and resource["gender"] not in ("male", "female", "other", "unknown"):
                errors.append(f"Invalid Patient gender '{resource['gender']}'")
            if "name" in resource and not isinstance(resource["name"], list):
                errors.append("Patient 'name' must be an array")

        elif res_type == "Observation":
            if not resource.get("status"):
                errors.append("Observation must specify 'status'")
            if not resource.get("code"):
                errors.append("Observation must specify 'code'")
            if not resource.get("subject"):
                errors.append("Observation must specify 'subject'")
            if not any(k in resource for k in ("valueQuantity", "valueString", "component")):
                errors.append("Observation must have 'valueQuantity', 'valueString', or 'component'")

        elif res_type == "Encounter":
            if not resource.get("status"):
                errors.append("Encounter must specify 'status'")
            if not resource.get("class"):
                errors.append("Encounter must specify 'class'")
            if not resource.get("subject"):
                errors.append("Encounter must specify 'subject'")

        elif res_type == "MedicationRequest":
            if not resource.get("status"):
                errors.append("MedicationRequest must specify 'status'")
            if not resource.get("intent"):
                errors.append("MedicationRequest must specify 'intent'")
            if not resource.get("subject"):
                errors.append("MedicationRequest must specify 'subject'")

        elif res_type == "DiagnosticReport":
            if not resource.get("status"):
                errors.append("DiagnosticReport must specify 'status'")
            if not resource.get("code"):
                errors.append("DiagnosticReport must specify 'code'")
            if not resource.get("subject"):
                errors.append("DiagnosticReport must specify 'subject'")

        elif res_type == "Bundle":
            if not resource.get("type"):
                errors.append("Bundle must specify 'type'")
            entries = resource.get("entry", [])
            if not isinstance(entries, list):
                errors.append("Bundle 'entry' must be an array")
            else:
                for idx, entry in enumerate(entries):
                    inner_res = entry.get("resource")
                    if not inner_res:
                        errors.append(f"Bundle entry[{idx}] missing 'resource'")
                    else:
                        is_valid, inner_errs = cls.validate_resource(inner_res)
                        if not is_valid:
                            errors.extend([f"Bundle entry[{idx}] ({inner_res.get('resourceType', 'Unknown')}): {e}" for e in inner_errs])

        return len(errors) == 0, errors

    @classmethod
    def assert_valid(cls, resource: Dict[str, Any]):
        is_valid, errors = cls.validate_resource(resource)
        if not is_valid:
            raise FHIRValidationError(f"FHIR validation failed for {resource.get('resourceType')}", errors=errors)
