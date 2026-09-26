# FHIR R4 & ABDM Clinical Mapping Matrix

This document defines the canonical bidirectional mapping between the **Healthcare Platform API** internal domain models and the **HL7 FHIR R4 (Release 4.0.1)** and **ABDM (Ayushman Bharat Digital Mission)** clinical artifact profiles.

---

## 1. Domain Resource Mapping Overview

| Internal Domain Entity | FHIR R4 Resource | ABDM Milestone / Profile | Purpose |
|---|---|---|---|
| `Patient` | `Patient` | ABDM Patient Profile | Master demographic and identity representation |
| `PatientIdentifier` | `Identifier` | ABHA ID / ABHA Address | 14-digit ABHA (`14-XXXX-XXXX-XXXX`) & PHR address |
| `User` (`DOCTOR`/`NURSE`) | `Practitioner` | ABDM Practitioner | Licensed healthcare professional credentials |
| `Facility` | `Organization` | ABDM Health Facility | PHC, Sub-centre, CHC, Rural/District Hospital |
| `Appointment` | `Appointment` | FHIR Appointment | Scheduled or teleconsultation booking |
| `Encounter` | `Encounter` | ABDM OP/IP Encounter | Clinical care delivery encounter interaction |
| `Vital` | `Observation` | ABDM Vital Signs Profile | Physiological measurements (LOINC-coded) |
| `Medication` | `Medication` | FHIR Medication | Generic / branded drug catalog representation |
| `PrescriptionItem` | `MedicationRequest` | ABDM Prescription | Clinician instructions, dosage, route, frequency |
| `DiagnosticOrder` | `ServiceRequest` | ABDM Diagnostic Request | Laboratory, pathology, or radiology order |
| `DiagnosticResult` | `DiagnosticReport` + `Observation` | ABDM Diagnostic Report | Investigation findings, values, and normal ranges |
| `Referral` | `ServiceRequest` | ABDM Care Transfer | Facility-to-facility patient referral |
| `Longitudinal Record` | `Bundle` (type: `collection`/`document`) | ABDM Health Document Record | Consolidated longitudinal clinical exchange |

---

## 2. Standardized Vocabularies & Coding Systems

### 2.1 Physiological Vital Signs (LOINC & UCUM)

| Measurement | LOINC Code | LOINC Display | Standard UCUM Unit | Structure |
|---|---|---|---|---|
| **Blood Pressure Panel** | `85354-9` | Blood pressure panel with all children optional | `mm[Hg]` | Structured Multi-component Observation |
| ↳ *Systolic BP* | `8480-6` | Systolic blood pressure | `mm[Hg]` | Component 1 |
| ↳ *Diastolic BP* | `8462-4` | Diastolic blood pressure | `mm[Hg]` | Component 2 |
| **Heart Rate** | `8867-4` | Heart rate | `/min` | Single valueQuantity |
| **Body Temperature** | `8310-5` | Body temperature | `Cel` | Single valueQuantity |
| **Respiratory Rate** | `9279-1` | Respiratory rate | `/min` | Single valueQuantity |
| **Oxygen Saturation (SpO2)** | `2708-6` | Oxygen saturation in Arterial blood | `%` | Single valueQuantity |
| **Body Weight** | `29463-7` | Body weight | `kg` | Single valueQuantity |
| **Body Height** | `8302-2` | Body height | `cm` | Single valueQuantity |

### 2.2 Identifier Systems (ABDM / National Registries)

| Identifier Type | URI / System | Format / Value Pattern |
|---|---|---|
| **ABHA Number** | `https://healthid.abdm.gov.in` | `14-XXXX-XXXX-XXXX` (14 digits) |
| **ABHA Address (PHR)** | `https://ndhm.in/phr` | `<username>@abdm` or `<username>@sbx` |
| **Internal Patient Number** | `https://healthcare.gov.in/patient-number` | `PAT-YYYYMMDD-XXXX` |
| **HPR (Healthcare Professional ID)**| `https://hpr.abdm.gov.in` | Practitioner National ID |
| **HFR (Health Facility Registry)** | `https://facility.abdm.gov.in` | Facility National Code |

---

## 3. Field-Level Mapping Specifications

### 3.1 Patient $\rightarrow$ FHIR `Patient`
```json
{
  "resourceType": "Patient",
  "id": "<patient.id>",
  "identifier": [
    {
      "system": "https://healthcare.gov.in/patient-number",
      "value": "<patient.patient_number>",
      "use": "usual"
    },
    {
      "system": "https://healthid.abdm.gov.in",
      "value": "<patient_identifier.value>",
      "use": "official"
    }
  ],
  "active": true,
  "name": [
    {
      "use": "official",
      "text": "Anita Sharma",
      "family": "<patient.last_name>",
      "given": ["<patient.first_name>", "<patient.middle_name>"]
    }
  ],
  "telecom": [
    { "system": "phone", "value": "<patient.phone>", "use": "mobile" },
    { "system": "email", "value": "<patient.email>", "use": "home" }
  ],
  "gender": "female",
  "birthDate": "1994-06-15",
  "address": [
    {
      "use": "home",
      "text": "<patient.address>"
    }
  ]
}
```

### 3.2 Encounter $\rightarrow$ FHIR `Encounter`
```json
{
  "resourceType": "Encounter",
  "id": "<encounter.id>",
  "status": "finished",
  "class": {
    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    "code": "AMB",
    "display": "ambulatory"
  },
  "subject": {
    "reference": "Patient/<encounter.patient_id>"
  },
  "participant": [
    {
      "individual": {
        "reference": "Practitioner/<encounter.provider_id>"
      }
    }
  ],
  "period": {
    "start": "<encounter.started_at>",
    "end": "<encounter.ended_at>"
  },
  "serviceProvider": {
    "reference": "Organization/<encounter.facility_id>"
  }
}
```

### 3.3 Prescription Item $\rightarrow$ FHIR `MedicationRequest`
```json
{
  "resourceType": "MedicationRequest",
  "id": "<prescription_item.id>",
  "status": "active",
  "intent": "order",
  "medicationReference": {
    "reference": "Medication/<medication.id>",
    "display": "Amoxicillin 500mg Capsule"
  },
  "subject": {
    "reference": "Patient/<patient.id>"
  },
  "encounter": {
    "reference": "Encounter/<encounter.id>"
  },
  "dosageInstruction": [
    {
      "text": "1 capsule 3 times daily for 5 days after food",
      "timing": {
        "repeat": {
          "frequency": 3,
          "period": 1,
          "periodUnit": "d"
        }
      },
      "route": {
        "coding": [
          { "system": "http://snomed.info/sct", "code": "260548002", "display": "Oral" }
        ]
      }
    }
  ],
  "dispenseRequest": {
    "quantity": {
      "value": 15,
      "unit": "Capsule"
    },
    "expectedSupplyDuration": {
      "value": 5,
      "unit": "days",
      "system": "http://unitsofmeasure.org",
      "code": "d"
    }
  }
}
```

---

## 4. Consent Architecture (ABDM Model)

All data exchanged via FHIR bundles is gated by patient consent:
- `Consent.status`: `REQUESTED` $\rightarrow$ `GRANTED` $\rightarrow$ `EXPIRED` or `REVOKED`.
- `Consent.scope`: Restricted to permissible clinical domains (`VITALS`, `PRESCRIPTIONS`, `DIAGNOSTICS`, or `ALL`).
- Requests lacking active valid consent will be blocked with **`403 Forbidden`**.
