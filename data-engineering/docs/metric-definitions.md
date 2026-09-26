# Healthcare Metrics & KPIs Specification

## 1. Executive Summary
This document specifies the authoritative metric catalog, mathematical formulations, denominators, and validation rules governing healthcare indicators in the data engineering platform.

---

## 2. Core Governance Principles

### 2.1 Controlled Vocabulary of Metric Types
- **`COUNT`**: Quantitative integer volume of discrete clinical or operational events.
- **`RATE`**: Proportion bounded strictly between `0.0` and `1.0` ($\text{numerator} \le \text{denominator}$).
- **`AVERAGE`**: Arithmetic mean of continuous clinical metrics (e.g. wait time, duration).
- **`MEDIAN`**: 50th percentile rank resistant to extreme outliers.
- **`DURATION`**: Elapsed time intervals (minutes or days).
- **`AGING`**: Discrete buckets for elapsed delay tracking.

### 2.2 Explicit Denominators & Zero Handling
- Every rate metric has an explicitly declared numerator and denominator.
- **Zero-Denominator Rule**: When $\text{denominator} = 0$, the metric value is strictly returned as `NULL`, **never** coerced to `0%`.

---

## 3. Authoritative Metric Catalog

### 3.1 Appointment Metrics
| Metric Code | Type | Numerator | Denominator | Grain | Source Table |
|---|---|---|---|---|---|
| `appointment_volume` | `COUNT` | Count of appointments | N/A | Reporting period | `fact_appointment` |
| `appointment_completion_rate` | `RATE` | Appointments with `is_completed = TRUE` | Total eligible appointments | Reporting period | `fact_appointment` |
| `appointment_cancellation_rate` | `RATE` | Appointments with `is_cancelled = TRUE` | Total scheduled appointments | Reporting period | `fact_appointment` |
| `appointment_no_show_rate` | `RATE` | Appointments with `is_no_show = TRUE` | Total scheduled appointments | Reporting period | `fact_appointment` |
| `average_wait_minutes` | `AVERAGE` | Sum of `wait_minutes` | Count of eligible encounters | Reporting period | `fact_appointment` |
| `median_wait_minutes` | `MEDIAN` | 50th percentile of `wait_minutes` | N/A | Reporting period | `fact_appointment` |

---

### 3.2 Clinical Encounter Metrics
| Metric Code | Type | Numerator | Denominator | Grain | Source Table |
|---|---|---|---|---|---|
| `encounter_volume` | `COUNT` | Count of clinical encounters | N/A | Reporting period | `fact_encounter` |
| `average_consultation_duration` | `AVERAGE` | Sum of `duration_minutes` | Encounters with valid duration | Reporting period | `fact_encounter` |
| `encounters_per_facility` | `AVERAGE` | Total encounter volume | Distinct active facilities | Facility | `fact_encounter` |
| `encounters_per_provider` | `AVERAGE` | Total encounter volume | Distinct clinical providers | Provider | `fact_encounter` |

---

### 3.3 Care Transfer & Referral Metrics
| Metric Code | Type | Numerator | Denominator | Grain | Source Table |
|---|---|---|---|---|---|
| `referral_volume` | `COUNT` | Count of initiated referrals | N/A | Reporting period | `fact_referral` |
| `referral_completion_rate` | `RATE` | Referrals with `is_completed = TRUE` | Total initiated referrals | Reporting period | `fact_referral` |
| `referral_pending_rate` | `RATE` | Referrals with `is_completed = FALSE` | Total initiated referrals | Reporting period | `fact_referral` |
| `avg_referral_completion_days` | `DURATION` | Sum of `completion_days` | Count of completed referrals | Reporting period | `fact_referral` |

---

### 3.4 Chronic Care & Continuity Metrics
| Metric Code | Type | Numerator | Denominator | Grain | Source Table |
|---|---|---|---|---|---|
| `hypertension_followup_rate` | `RATE` | Hypertension cohort patients with encounter | Total hypertension cohort patients | Cohort | `cohort_membership`, `fact_encounter` |
| `chronic_followup_adherence` | `RATE` | Chronic cohort patients with consultation | Total chronic cohort patients | Cohort | `cohort_membership`, `fact_encounter` |

---

### 3.5 Healthcare Access & Distribution Metrics
| Metric Code | Type | Numerator | Denominator | Grain | Source Table |
|---|---|---|---|---|---|
| `unique_patients_served` | `COUNT` | Distinct `patient_key` | N/A | Reporting period | `fact_encounter` |
| `patients_served_per_facility` | `AVERAGE` | Distinct `patient_key` | Distinct `facility_key` | Facility | `fact_encounter` |

---

## 4. Double-Counting Prevention
- In queries combining encounters and child observations or prescriptions, aggregation is performed prior to joins (or using `COUNT(DISTINCT ...)`), ensuring 1:N fan-out does not distort volume metrics.
