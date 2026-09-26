"""Healthcare Platform — FHIR R4 & ABDM Interoperability Module."""

from .mapping.terminology import get_vital_terminology, get_all_terminology_mappings
from .abdm.identifiers import build_patient_identifier_mappings
from .abdm.provenance import create_fhir_provenance_record
from .fhir.patient import generate_fhir_patient
from .fhir.encounter import generate_fhir_encounter
from .fhir.observation import generate_fhir_vital_observations
from .fhir.medication_request import generate_fhir_medication_request
from .fhir.diagnostic_report import generate_fhir_diagnostic_report
from .validation import (
    validate_fhir_patient,
    validate_fhir_encounter,
    validate_fhir_observation,
    validate_referential_integrity,
)

__all__ = [
    "get_vital_terminology",
    "get_all_terminology_mappings",
    "build_patient_identifier_mappings",
    "create_fhir_provenance_record",
    "generate_fhir_patient",
    "generate_fhir_encounter",
    "generate_fhir_vital_observations",
    "generate_fhir_medication_request",
    "generate_fhir_diagnostic_report",
    "validate_fhir_patient",
    "validate_fhir_encounter",
    "validate_fhir_observation",
    "validate_referential_integrity",
]
