# PII / PHI Classification & Data Access Governance

Healthcare information systems require strict data segregation to comply with the Digital Personal Data Protection Act (DPDPA), HIPAA, and ABDM data privacy guidelines.

---

## 1. Field Classification Matrix

### Category A: Direct Identifiers (High Risk)
Data elements that directly identify a single individual without secondary information.

| Field Name | Table | Classification | Storage Protection |
|---|---|---|---|
| `first_name`, `last_name` | `patients` | PII | Tokenized / Masked in analytics |
| `phone` | `patients` | PII | Masked (e.g. `+91 98****1234`) |
| `email` | `patients` | PII | Hashed / Suppressed in reporting |
| `address` | `patients` | PII | Generalized to District/State |
| `value` (ABHA Number) | `patient_identifiers` | PII / National ID | Hashed / Never exported in cleartext |
| `value` (ABHA Address) | `patient_identifiers` | PII / National ID | Hashed / Never exported in cleartext |

### Category B: Indirect / Quasi-Identifiers (Re-identification Risk)
Data elements that do not identify a person alone, but can uniquely identify individuals when combined with external datasets (k-anonymity risk).

| Field Name | Table | Re-identification Vector | De-identification Recommendation |
|---|---|---|---|
| `date_of_birth` | `patients` | Combined with Gender & District | Convert to 5-year Age Groups or Age at encounter |
| `gender` | `patients` | Demographic profiling | Retain for clinical cohorts |
| `facility_id` | multiple | Location attribution | Aggregate to District tier for broad analytics |
| `appointment_date`, `started_at` | multiple | Timeline matching | Shift dates by random patient offset or bin by week/month |

### Category C: Protected Health Information (PHI — Sensitive Clinical)
Data elements revealing clinical diagnosis, physiological observations, and treatments.

| Field Name | Table | Clinical Sensitivity | Handling Rule |
|---|---|---|---|
| `chief_complaint`, `clinical_notes` | `encounters` | Sensitive Free-Text PHI | Excluded from public analytics; NLP de-identification required |
| `systolic_bp`, `diastolic_bp`, `spo2`| `vitals` | Physiological Metrics | Numerical analysis permitted; isolate from direct IDs |
| `result_value`, `abnormal_flag` | `diagnostic_results`| Clinical Lab Finding | Numerical/categorical analysis permitted; anonymized |
| `medication_id`, `instructions` | `prescription_items`| Treatment Regimen | Retain generic ATC codes; strip doctor narrative notes |
| `reason`, `clinical_summary` | `referrals` | Transfer Clinical PHI | Categorical referral classification only |

---

## 2. 4-Tier Data Access Matrix

```
┌───────────────────────────────────────────────────────────────┐
│               TIER 1: Operational Backend                     │
│  - Full read/write access to all tables                       │
│  - Directly serves doctors, nurses, patients, and admins      │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│              TIER 2: Data Engineering Environment             │
│  - Read-Only operational access for profiling & ELT           │
│  - Operates inside secure VPC / Docker network                │
│  - Strictly prohibited from exporting cleartext raw PII       │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│             TIER 3: Analytical De-identified Warehouse        │
│  - Pseudonymized surrogate keys (`patient_key`, `encounter_key`)│
│  - Suppressed direct identifiers (No names, phone, email)     │
│  - Date-shifted / aggregated timestamps                       │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│              TIER 4: Public / KPI Dashboards                  │
│  - Strictly aggregated cohorts (min group size k >= 5)        │
│  - Facility-level and District-level aggregates only          │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Data Protection Rules for Developers

1. **Zero Patient Data in Git**: No CSV dumps, SQL exports, or notebook outputs containing patient rows may be committed to version control.
2. **Local Profiling Isolation**: Profiling scripts must run in-memory and print summary statistics (row counts, null percentages, distribution medians) without persisting raw patient lists.
3. **Synthetic Data for Development**: Any offline demonstration datasets must be synthetically generated using tools like `Faker` rather than copied from production.
