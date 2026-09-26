# Canonical Terminology Mapping Specification

## 1. Overview
This specification details the standardized coding crosswalks implemented in `analytics.terminology_map`.

---

## 2. Terminology Preservation Principle
$$\text{Raw Source Code / Display} \longrightarrow \text{Target Canonical Code / Display}$$
Source values are never overwritten or discarded; the crosswalk stores both the source code and the standard concept to guarantee clinical auditability.

---

## 3. Supported Terminology Systems

| Domain | Standard System | Target System URI |
|---|---|---|
| Vital Signs | LOINC | `http://loinc.org` |
| Clinical Units | UCUM | `http://unitsofmeasure.org` |
| Diagnoses / Conditions | SNOMED CT / ICD-10 | `http://snomed.info/sct` / `http://hl7.org/fhir/sid/icd-10` |
| Encounter Statuses | FHIR ValueSet | `http://hl7.org/fhir/encounter-status` |

---

## 4. Handling Unmapped Codes
If an internal term cannot be deterministically mapped to an approved standard code:
- `mapping_status` is explicitly set to `'unmapped'`.
- The source term is preserved.
- No dummy or arbitrary target codes are invented.
