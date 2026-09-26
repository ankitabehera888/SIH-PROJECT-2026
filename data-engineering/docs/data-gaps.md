# Data Gap Analysis & Analytical Metric Feasibility

This document identifies the gap between high-level healthcare analytical objectives (e.g. travel time reduction, waiting time analysis, referral completion) and the operational fields currently captured in PostgreSQL.

---

## 1. Healthcare Analytical Goals vs. Operational Schema

| Analytical Metric | Required Fields | Current Schema Status | Gap Analysis & Recommendation |
|---|---|---|---|
| **1. Outpatient Waiting Time** | `check_in_time`, `called_time`, `consultation_start_time` | **Available** (`queue_entries.created_at`, `called_at`, `started_at`) | **No Gap**: Full OPD waiting duration is computable directly from `queue_entries`. |
| **2. Patient Travel Time Saved** | `patient_home_coordinates` / `pincode`, `referral_hospital_location`, `teleconsultation_flag` | **Partial Gap** | `patients.address` is stored as free-text without latitude/longitude coordinates or structured PIN code. Teleconsultation flag exists (`consultations`).<br>**Recommendation**: Add structured `pincode` or geocoded centroids to `patients` and `facilities`. |
| **3. Referral Completion Rate** | `referral_created_at`, `referral_completed_at`, `referral_status`, `destination_facility_id` | **Available** (`referrals.created_at`, `updated_at`, `status = 'COMPLETED'`) | **Minor Gap**: Recommend adding an explicit `completed_at` timestamp rather than relying on `updated_at`. |
| **4. Diagnostic Turnaround Time (TAT)** | `ordered_at`, `sample_collected_at`, `verified_at` | **Partial Gap** | `diagnostic_orders.ordered_at` and `diagnostic_results.verified_at` are present. Intermediate `sample_collected_at` or `specimen_received_at` is not tracked.<br>**Recommendation**: Compute overall Order-to-Result TAT; add specimen timestamps if lab tracking is required. |
| **5. Teleconsultation Duration & Quality** | `consultation_start`, `consultation_end`, `participant_attendance`, `network_quality` | **Available** (`consultations.actual_start`, `actual_end`, `consultation_participants.duration_seconds`) | **Minor Gap**: Participant video duration is accurately tracked. WebRTC packet loss/jitter metrics are not stored. |
| **6. Medicine Stockout & Availability** | `prescribed_medication_id`, `dispensed_flag`, `dispensed_at`, `inventory_level` | **Major Gap** | `prescriptions` records what was ordered. A dedicated pharmacy dispensing / stock inventory table (`pharmacy_dispensations` or `inventory_stock`) does not yet exist.<br>**Recommendation**: Introduce a `dispensations` or `inventory_transactions` operational table in subsequent backend iterations. |
| **7. Antenatal / Maternal Cohort Follow-up** | `pregnancy_flag` / `gestational_age`, `scheduled_visit_date`, `completed_encounter_date` | **Partial Gap** | `encounters.chief_complaint` and `notes` contain maternal indicators in unstructured text. Longitudinal encounter history exists.<br>**Recommendation**: Add structured encounter classification tags (e.g. `ANC_VISIT_1`, `ANC_VISIT_2`, `IMMUNIZATION`) for cohort extraction. |
| **8. Chronic Disease Control (HTN / DM)** | Sequential `systolic_bp`, `diastolic_bp`, `fasting_glucose`, `hba1c` over 3+ months | **Available** (`vitals` with timestamps, `diagnostic_results` with LOINC test codes) | **No Gap**: Full longitudinal blood pressure panels and lab results are recorded per encounter. |

---

## 2. Summary of Recommendations for Backend Team

1. **Add Structured Geolocation / Pincode**: Add `pincode` (VARCHAR 6) to `patients` and `facilities` tables to calculate travel distance saved through local PHC visits and teleconsultation.
2. **Explicit Lifecycle Timestamps**: Add `completed_at` to `referrals` to differentiate between general record edits and actual clinical intake at receiving facilities.
3. **Pharmacy Dispensation Tracking**: Create an operational table capturing when prescription items are fulfilled vs. out-of-stock.
