# Data Quality Summary Report

**Date of Profiling**: September 2026  
**Environment**: Local Data Engineering (`healthcare_dev` PostgreSQL 16)  
**Tables Profiled**: 24  
**Platform Overall Data Quality Score**: **97.9 / 100**

---

## 1. Executive Quality Scorecard

| Table | Completeness (25%) | Consistency (25%) | Validity (20%) | Integrity (20%) | Timeliness (10%) | Overall Score | Grade |
|---|---|---|---|---|---|---|---|
| `prescription_items` | 97.9% | 100.0% | 100.0% | 100.0% | 100.0% | **99.5** | A (Excellent) |
| `diagnostic_results` | 97.7% | 100.0% | 100.0% | 100.0% | 100.0% | **99.4** | A (Excellent) |
| `consultations` | 97.5% | 100.0% | 100.0% | 100.0% | 100.0% | **99.4** | A (Excellent) |
| `encounters` | 97.2% | 100.0% | 100.0% | 100.0% | 100.0% | **99.3** | A (Excellent) |
| `facilities` | 96.7% | 100.0% | 100.0% | 100.0% | 100.0% | **99.2** | A (Excellent) |
| `queue_entries` | 96.6% | 100.0% | 100.0% | 100.0% | 100.0% | **99.2** | A (Excellent) |
| `prescriptions` | 96.3% | 100.0% | 100.0% | 100.0% | 100.0% | **99.1** | A (Excellent) |
| `appointments` | 95.3% | 100.0% | 100.0% | 100.0% | 100.0% | **98.8** | A (Excellent) |
| `diagnostic_orders` | 94.8% | 100.0% | 100.0% | 100.0% | 100.0% | **98.7** | A (Excellent) |
| `vitals` | 94.6% | 100.0% | 100.0% | 100.0% | 100.0% | **98.6** | A (Excellent) |
| `referrals` | 89.5% | 100.0% | 100.0% | 100.0% | 100.0% | **97.4** | A (Excellent) |
| `patients` | 92.9% | 50.0% | 100.0% | 100.0% | 100.0% | **85.7** | B (Good) |

---

## 2. Key Findings & Issues Log

- **Referential Integrity**: **0 orphan records** found across all 24 foreign key relationships (100% integrity maintained by PostgreSQL schema constraints).
- **Temporal Consistency**: **0 chronological violations** detected. Clinical workflows strictly adhere to causal timelines.
- **Clinical Bounds Validation**: **0 physiologically impossible vital signs** detected across all blood pressure, heart rate, temperature, SpO2, and respiratory observations.
- **Duplicate Entities**: Identified **4 duplicate groupings**:
  - **Patients**: 4 phone numbers shared across multiple patient records (e.g. family accounts) (65 excess records)
- **Statistical Outliers**: Flagged **45 statistical outliers** using IQR analysis for manual operational review.

---

## 3. Operational Table Inventory

| Table | Live Rows | Columns | Primary Key | Foreign Keys | Earliest Record | Latest Record |
|---|---|---|---|---|---|---|
| `users` | 2,394 | 8 | `id` | 1 | 2026-09-01 07:47:15 | 2026-09-01 19:27:58 |
| `facilities` | 839 | 9 | `id` | 0 | 2026-09-01 10:30:21 | 2026-09-01 19:28:00 |
| `patients` | 833 | 18 | `id` | 3 | 2026-09-01 09:18:25 | 2026-09-01 19:28:00 |
| `appointments` | 637 | 18 | `id` | 6 | 2026-09-01 | 2026-09-10 |
| `encounters` | 371 | 15 | `id` | 6 | 2026-09-01 10:46:06 | 2026-09-01 19:28:00 |
| `referrals` | 139 | 36 | `id` | 13 | 2026-09-01 11:12:29 | 2026-09-01 19:28:02 |
| `medications` | 135 | 10 | `id` | 0 | 2026-09-01 11:32:35 | 2026-09-01 19:28:01 |
| `consultations` | 129 | 18 | `id` | 7 | 2026-09-01 15:47:18 | 2026-09-01 19:28:02 |
| `diagnostic_tests` | 128 | 9 | `id` | 0 | 2026-09-01 11:32:17 | 2026-09-01 19:28:01 |
| `diagnostic_order_items` | 119 | 7 | `id` | 2 | N/A | N/A |
| `diagnostic_orders` | 119 | 14 | `id` | 5 | 2026-09-01 11:32:18 | 2026-09-01 19:28:01 |
| `notifications` | 117 | 21 | `id` | 2 | 2026-09-01 12:59:24 | 2026-09-01 16:52:30 |
| `vitals` | 112 | 14 | `id` | 3 | 2026-09-01 10:46:17 | 2026-09-01 19:28:01 |
| `prescription_items` | 110 | 11 | `id` | 2 | N/A | N/A |
| `prescriptions` | 110 | 17 | `id` | 8 | 2026-09-01 11:32:36 | 2026-09-01 19:28:01 |
| `notification_preferences` | 90 | 13 | `id` | 1 | 2026-09-01 12:59:24 | 2026-09-01 16:52:31 |
| `consultation_participants` | 86 | 11 | `id` | 2 | 2026-09-01 15:47:22 | 2026-09-01 19:28:03 |
| `diagnostic_results` | 85 | 16 | `id` | 5 | 2026-09-01 11:32:21 | 2026-09-01 19:28:01 |
| `queue_entries` | 78 | 13 | `id` | 3 | 2026-09-01 10:30:31 | 2026-09-01 19:28:00 |
| `interoperability_audits` | 64 | 10 | `id` | 2 | N/A | N/A |
| `system_checks` | 22 | 4 | `id` | 0 | 2026-09-01 07:17:55 | 2026-09-01 16:52:30 |
| `patient_identifiers` | 15 | 9 | `id` | 1 | 2026-09-01 16:45:15 | 2026-09-01 19:28:03 |
| `consents` | 11 | 13 | `id` | 2 | 2026-09-01 16:45:15 | 2026-09-01 19:28:03 |
| `alembic_version` | 1 | 1 | `version_num` | 0 | N/A | N/A |

---

## 4. Clinical Vitals Validation Details

| Vital Sign | Expected Normal Range | Total Measurements | Valid | Invalid | Validity % | Status |
|---|---|---|---|---|---|---|
| Systolic Blood Pressure | 60 - 260 mmHg | 112 | 112 | 0 | 100.0% | PASS |
| Diastolic Blood Pressure | 30 - 180 mmHg | 112 | 112 | 0 | 100.0% | PASS |
| Heart Rate | 25 - 240 bpm | 112 | 112 | 0 | 100.0% | PASS |
| Body Temperature | 30.0 - 45.0 °C | 28 | 28 | 0 | 100.0% | PASS |
| Oxygen Saturation | 50.0 - 100.0 % | 76 | 76 | 0 | 100.0% | PASS |
| Respiratory Rate | 6 - 60 breaths/min | 87 | 87 | 0 | 100.0% | PASS |

---

## 5. Statistical Outliers (Operational Distributions)

| Metric | Total Evaluated | Median | Mean ± Std | IQR [Lower, Upper] | Outliers (IQR) | Max Observed | Status |
|---|---|---|---|---|---|---|---|
| OPD Waiting Duration | 17 | 0.0 Minutes | 0.0 ± 0.0 | [0.0, 0.0] | 17 | 0.0 Minutes | REVIEW_NEEDED |
| Teleconsultation Duration | 0 | 0.0 Minutes | 0.0 ± 0.0 | [0.0, 0.0] | 0 | 0.0 Minutes | INSUFFICIENT_DATA |
| Appointment Booking Lead Time | 637 | 0.0 Days | 1.02 ± 1.68 | [-3.0, 5.0] | 28 | 9.0 Days | REVIEW_NEEDED |
| Prescription Items Density | 110 | 1.0 Items | 1.0 ± 0.0 | [1.0, 1.0] | 0 | 1.0 Items | NORMAL |

---

## 6. Recommendations for Staging & Analytics Pipelines

1. **Family Account Disambiguation**: Shared patient phone numbers indicate family member registration under a single mobile device. The ETL staging pipeline should assign distinct surrogate keys (`patient_key`) while clustering shared phone accounts for household-level analytics.
2. **Handle Sparse Demographics**: Email and home addresses have high optionality (~80-95% null) reflecting rural and semi-urban catchment demographics. Staging pipelines must substitute explicit categorical indicators (e.g. `'NOT_PROVIDED'`) rather than dropping sparse rows.
3. **Outlier Quarantine**: In future ELT ingestion, flag operational outliers with an `is_outlier` boolean column to permit analysts to toggle sensitive aggregations (e.g. median vs. trimmed mean).
