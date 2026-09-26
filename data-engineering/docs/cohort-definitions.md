# Clinical Cohort Definitions Specification

## 1. Executive Summary
This document specifies the clinical, mathematical, and temporal criteria governing reproducible cohort generation within the Healthcare Data Engineering platform.

---

## 2. Cohort Data Architecture

```text
               analytics.cohort_registry
              (cohort_key, name, version)
                          │
                          │ 1 : N
                          ▼
              analytics.cohort_membership
    (membership_key, cohort_key, patient_key, index_date,
     observation_start, observation_end, risk_score, run_id)
```

- **Uniqueness Constraint**: `UNIQUE (cohort_key, patient_key, index_date)`.
- **Surrogate Keys**: Cohorts link exclusively to synthetic surrogate keys (`patient_key`). No patient names, phone numbers, or cleartext PHI are stored.

---

## 3. Detailed Cohort Specifications

### 3.1 Cohort 1: Diabetes Mellitus (`v1.0`)
- **Purpose**: Cohort for monitoring glycemic control, chronic diabetes care pathways, and medication adherence.
- **Inclusion Criteria**:
  - Documented diagnosis/complaint of diabetes in clinical encounters (`chief_complaint` or `clinical_notes` matching `diabet%`).
  - OR prescribed anti-diabetic medication (`metformin`, `glimepiride`, `insulin`).
- **Exclusion Criteria**: Unverified or inactive patient records.
- **Index Date**: Earliest documented diabetes diagnosis encounter date or prescription date.
- **Observation Window**: Index Date to Index Date + 365 days.
- **Risk Score**: 20.0 base.

---

### 3.2 Cohort 2: Essential Hypertension (`v1.0`)
- **Purpose**: Identify patients with documented or measured hypertension for cardiovascular risk management.
- **Inclusion Criteria**:
  - Documented clinical diagnosis/complaint of hypertension (`chief_complaint ILIKE '%hypertension%'`).
  - OR validated elevated blood pressure readings ($\text{Systolic BP} \ge 140\text{ mmHg}$ or $\text{Diastolic BP} \ge 90\text{ mmHg}$).
- **Exclusion Criteria**: Vitals marked as invalid (`_vital_quality_status = 'invalid'`).
- **Index Date**: Earliest documented hypertension encounter date or elevated BP observation date.
- **Observation Window**: Index Date to Index Date + 365 days.
- **Risk Score**: 20.0 base.

---

### 3.3 Cohort 3: High-Risk Clinical Cohort (`v1.0`)
- **Purpose**: Stratified clinical risk triage identifying patients requiring multidisciplinary care coordination.
- **Scoring Formula**:
  $$\text{Risk Score} = \sum (\text{Chronic Condition: } 20) + (\text{Pending Referral: } 15) + (\text{Abnormal Vitals: } 10) + (\ge 2\text{ Encounters: } 10)$$
- **Inclusion Criteria**: Composite risk score $\ge 30.0$.
- **Exclusion Criteria**: Inactive patient records.
- **Index Date**: Date of risk evaluation (`CURRENT_DATE`).
- **Observation Window**: Index Date to Index Date + 180 days.

---

### 3.4 Cohort 4: Missed Appointments (`v1.0`)
- **Purpose**: Identify care continuity drop-offs, scheduling adherence gaps, and clinic capacity utilization issues.
- **Inclusion Criteria**:
  - Appointments marked as cancelled (`is_cancelled = TRUE` or `appointment_status = 'cancelled'`).
  - OR recorded no-shows (`is_no_show = TRUE` or `appointment_status = 'no_show'`).
- **Exclusion Criteria**: Future scheduled appointments.
- **Index Date**: Scheduled date of the most recent missed appointment.
- **Observation Window**: Index Date to Index Date + 90 days.
- **Risk Score**: 15.0 base.

---

### 3.5 Cohort 5: Pending Referrals (`v1.0`)
- **Purpose**: Track unresolved care transfers, eliminate specialist referral backlogs, and prevent patient loss to follow-up.
- **Inclusion Criteria**: Unresolved referrals (`is_completed = FALSE`).
- **Exclusion Criteria**: Completed or cancelled care transfers.
- **Index Date**: Referral creation date.
- **Observation Window**: Index Date to Index Date + 60 days.
- **Risk Score**: 25.0 base.

---

### 3.6 Cohort 6: Chronic Disease Follow-up Gap (`v1.0`)
- **Purpose**: Identify chronic patients overdue for clinical review and monitor care intervals.
- **Inclusion Criteria**: Patients with documented chronic condition (Hypertension, Cardiac, or Diabetes).
- **Index Date**: Most recent clinical consultation date.
- **Observation Window**: Index Date to Index Date + 180 days (`followup_days: 180`).
- **Eligibility Status**:
  - `'overdue'`: If $\text{Elapsed Days} \ge 180\text{ days}$.
  - `'eligible'`: If within active follow-up cycle ($< 180\text{ days}$).
- **Risk Score**: 30.0 base.
