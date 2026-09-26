# Phase 0 — Comprehensive Data Quality Report

**Date of Profiling**: September 2026  
**Source System**: PostgreSQL 16 (`healthcare_dev` container)  
**Environment**: Local Data Engineering (Read-Only)  

---

## 1. Executive Summary

This report documents the baseline data quality, completeness, and referential integrity of the operational healthcare database. Across all 24 relational tables examined, the database exhibits high structural integrity with **zero orphan records** across all primary foreign key hierarchies.

---

## 2. Table Row Counts (Operational Inventory)

| Category | Table Name | Live Row Count | Primary Key | Description |
|---|---|---|---|---|
| **Core Identity** | `users` | 2,394 | `id` (INT) | Doctors, Nurses, Admins, Patients |
| **Core Identity** | `facilities` | 839 | `id` (UUID) | PHCs, Community Health Centres, District Hospitals |
| **Demographics** | `patients` | 833 | `id` (UUID) | Clinical patient records |
| **Interoperability**| `patient_identifiers` | 15 | `id` (UUID) | ABHA Numbers and external IDs |
| **Interoperability**| `consents` | 11 | `id` (UUID) | ABDM consent artefacts |
| **Scheduling** | `appointments` | 637 | `id` (UUID) | Scheduled booking slots |
| **Scheduling** | `queue_entries` | 78 | `id` (UUID) | Operational OPD tokens |
| **Clinical Session**| `encounters` | 371 | `id` (UUID) | Doctor clinical consultations |
| **Observations** | `vitals` | 112 | `id` (UUID) | LOINC Blood Pressure, SpO2, Heart Rate |
| **Pharmacy** | `medications` | 135 | `id` (UUID) | Drug catalog |
| **Pharmacy** | `prescriptions` | 110 | `id` (UUID) | Prescription orders |
| **Pharmacy** | `prescription_items` | 110 | `id` (UUID) | Structured items per prescription |
| **Diagnostics** | `diagnostic_tests` | 128 | `id` (UUID) | Laboratory/radiology catalog |
| **Diagnostics** | `diagnostic_orders` | 119 | `id` (UUID) | Lab order requests |
| **Diagnostics** | `diagnostic_order_items`| 119 | `id` (UUID) | Individual tests ordered |
| **Diagnostics** | `diagnostic_results` | 85 | `id` (UUID) | Verified lab findings |
| **Continuity** | `referrals` | 139 | `id` (UUID) | Care transfers between facilities |
| **Telemedicine** | `consultations` | 129 | `id` (UUID) | Daily.co WebRTC sessions |
| **Telemedicine** | `consultation_participants`| 86 | `id` (UUID) | Attendance logs |
| **Messaging** | `notifications` | 117 | `id` (UUID) | Multi-channel notifications |
| **Messaging** | `notification_preferences` | 90 | `id` (UUID) | User delivery preferences |
| **Audit & Ops** | `interoperability_audits` | 64 | `id` (UUID) | FHIR & ABDM audit trail |
| **Audit & Ops** | `system_checks` | 22 | `id` (UUID) | Database health probes |
| **Migration** | `alembic_version` | 1 | `version_num` | Migration pointer (`ac7c0676af36`) |

---

## 3. Referential Integrity Evaluation

All 14 parent-child foreign key relationships were verified using anti-join queries (`LEFT JOIN ... WHERE parent.id IS NULL`).

| Child Table | Foreign Key | Parent Table | Orphan Rows | Status |
|---|---|---|---|---|
| `vitals` | `encounter_id` | `encounters` | **0** | **PASS** |
| `encounters` | `patient_id` | `patients` | **0** | **PASS** |
| `appointments` | `patient_id` | `patients` | **0** | **PASS** |
| `prescriptions` | `encounter_id` | `encounters` | **0** | **PASS** |
| `prescription_items` | `prescription_id` | `prescriptions` | **0** | **PASS** |
| `diagnostic_orders` | `encounter_id` | `encounters` | **0** | **PASS** |
| `diagnostic_order_items` | `order_id` | `diagnostic_orders` | **0** | **PASS** |
| `diagnostic_results` | `order_item_id` | `diagnostic_order_items` | **0** | **PASS** |
| `referrals` | `encounter_id` | `encounters` | **0** | **PASS** |
| `consultations` | `appointment_id` | `appointments` | **0** | **PASS** |
| `consultation_participants` | `consultation_id` | `consultations` | **0** | **PASS** |
| `queue_entries` | `appointment_id` | `appointments` | **0** | **PASS** |
| `patient_identifiers` | `patient_id` | `patients` | **0** | **PASS** |
| `consents` | `patient_id` | `patients` | **0** | **PASS** |

**Conclusion**: Foreign key enforcement at the PostgreSQL database level is 100% sound. No data corruption or orphan records exist.

---

## 4. Null & Completeness Analysis

- **`patients`**: 0% null on mandatory fields (`id`, `first_name`, `last_name`, `date_of_birth`, `gender`, `phone`). `email` and `address` have controlled optionality (~8-12% nulls), representing rural patients without email access.
- **`encounters`**: 100% populated `patient_id`, `provider_id`, `facility_id`, `started_at`. `clinical_notes` is null only on early-stage encounters (`IN_PROGRESS`).
- **`vitals`**: Individual vital signs (`spo2`, `temperature`, `heart_rate`) allow independent recording (a nurse may take blood pressure without taking temperature), which aligns with standard clinical workflow.
- **`diagnostic_results`**: Results correctly populate `verified_at`, `result_value`, and `unit` whenever `result_status = 'FINAL'`.

---

## 5. Temporal Consistency Analysis

- `created_at <= updated_at` evaluated to true across 100% of rows.
- No appointment has a `start_time > end_time`.
- Consultation participants duration matches `left_at - joined_at`.
- All clinical events fall within the current production year (2026).

---

## 6. Phase 0 Recommendations for Future ELT / Analytics

1. **Implement Incremental Change Extraction**: In Phase 1, extract operational data based on `updated_at >= :last_extracted_timestamp` to optimize network payload.
2. **De-identification Before Staging**: Replace `patient_id` with salted hash `patient_key` in the analytical presentation layer to protect confidentiality.
3. **Structured PIN Codes**: Coordinate with the backend team to add postal codes (`pincode`) to support geographical catchment area analysis and distance-traveled reduction metrics.
