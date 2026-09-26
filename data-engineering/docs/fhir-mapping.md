# FHIR R4 Mapping Specification

## 1. Executive Summary
This document specifies the semantic transformations between internal transactional healthcare models and HL7 FHIR Release 4 (R4) resource representations.

## 2. Core Separation Principle
$$\text{Internal System UUID (\texttt{patient\_id})} \neq \text{FHIR Resource ID (\texttt{Patient/pat-...})} \neq \text{ABDM ABHA ID}$$

Internal primary keys are never exposed directly as public FHIR IDs without domain namespacing.

## 3. Entity-to-Resource Crosswalk

| Operational / Staging Entity | Target FHIR Resource | Cardinality | Primary Business Key |
|---|---|---|---|
| `staging.patients` | `Patient` | 1 : 1 | `patient_id` |
| `staging.encounters` | `Encounter` | 1 : 1 | `id` |
| `staging.vitals` | `Observation` | 1 : N (per measurement) | `id` + `metric_type` |
| `staging.prescriptions` | `MedicationRequest` | 1 : 1 | `id` |
| `staging.diagnostics` | `DiagnosticReport` | 1 : 1 | `id` |

---

## 4. Resource Mapping Details

### 4.1 Patient Resource
- **FHIR Resource**: `Patient`
- **ID Format**: `pat-{patient_id}`
- **Identifiers**:
  - Usual identifier: `https://hospital.org/mrn` = `source_patient_id`
  - Official identifier: `https://healthid.abdm.gov.in` = `abha_id`
- **Demographics**:
  - `gender`: mapped to `male` | `female` | `other` | `unknown`
  - `birthDate`: `YYYY-MM-DD`

### 4.2 Encounter Resource
- **FHIR Resource**: `Encounter`
- **ID Format**: `enc-{encounter_id}`
- **Class**: `AMB` (Ambulatory / Outpatient Clinic)
- **Status**: `finished` (completed), `in-progress` (active), `planned` (scheduled)
- **Subject**: `Reference(Patient/pat-{patient_id})`
- **Period**: `start` (UTC timestamp), `end` (UTC timestamp)

### 4.3 Vital Signs (Observation Resource)
- **FHIR Resource**: `Observation`
- **Category**: `vital-signs` (`http://terminology.hl7.org/CodeSystem/observation-category`)
- **Coding**: Standard LOINC codes
- **Value**: Standard UCUM units
- **Subject**: `Reference(Patient/pat-{patient_id})`
- **Encounter**: `Reference(Encounter/enc-{encounter_id})`

#### Vital Code Crosswalk:
| Internal Metric | LOINC Code | LOINC Display | UCUM Unit | Display Unit |
|---|---|---|---|---|
| `systolic_bp` | `8480-6` | Systolic blood pressure | `mm[Hg]` | `mmHg` |
| `diastolic_bp` | `8462-4` | Diastolic blood pressure | `mm[Hg]` | `mmHg` |
| `heart_rate` | `8867-4` | Heart rate | `/min` | `bpm` |
| `temperature` | `8310-5` | Body temperature | `Cel` | `°C` |
| `spo2` | `2708-6` | Oxygen saturation in Arterial blood | `%` | `%` |
| `respiratory_rate` | `9279-1` | Respiratory rate | `/min` | `breaths/min` |

> [!CAUTION]
> **Data Quality Quarantine Rule**: Any record flagged with `_vital_quality_status = 'invalid'` is strictly omitted from FHIR Observation export. Corrupted clinical data is never exported as valid observations.

### 4.4 MedicationRequest Resource
- **FHIR Resource**: `MedicationRequest`
- **ID Format**: `medrx-{prescription_id}`
- **Status**: `active` | `completed` | `cancelled`
- **Intent**: `order`
- **Subject**: `Reference(Patient/pat-{patient_id})`
- **Encounter**: `Reference(Encounter/enc-{encounter_id})`
