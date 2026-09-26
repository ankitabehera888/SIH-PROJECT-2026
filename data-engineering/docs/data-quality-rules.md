# Data Quality Rules & Business Invariants

This document establishes the foundational data quality rules enforced in the data engineering layer.

---

## 1. Domain Entity Invariants

### Patient Demographics
- **DQ-PAT-01**: `patient.id` must be a valid, unique UUID (Primary Key).
- **DQ-PAT-02**: `date_of_birth` cannot be in the future ($\text{DOB} \le \text{CURRENT\_DATE}$).
- **DQ-PAT-03**: `first_name` and `last_name` cannot be empty or whitespace only.
- **DQ-PAT-04**: `phone` must adhere to E.164 format or standard 10-digit Indian mobile format (`+91` / `9XXXXXXXXX`).
- **DQ-PAT-05**: `is_active` must be a non-null boolean.

### Clinical Encounters
- **DQ-ENC-01**: `encounter.id` must be a valid, unique UUID.
- **DQ-ENC-02**: `patient_id` must reference a valid, non-deleted patient.
- **DQ-ENC-03**: `provider_id` must reference a user with role `DOCTOR` or `ADMIN`.
- **DQ-ENC-04**: `facility_id` must reference an active `facilities.id`.
- **DQ-ENC-05**: If `status = 'COMPLETED'`, `ended_at` must be populated.

### Vitals & Physiological Observations
- **DQ-VIT-01**: `encounter_id` must reference an existing encounter.
- **DQ-VIT-02**: Blood pressure values must be physiologically plausible:
  - $40 \le \text{systolic\_bp} \le 300\text{ mmHg}$
  - $30 \le \text{diastolic\_bp} \le 200\text{ mmHg}$
  - $\text{systolic\_bp} > \text{diastolic\_bp}$
- **DQ-VIT-03**: Oxygen Saturation: $50.0\% \le \text{spo2} \le 100.0\%$.
- **DQ-VIT-04**: Heart Rate: $30 \le \text{heart\_rate} \le 250\text{ bpm}$.
- **DQ-VIT-05**: Body Temperature: $30.0^\circ\text{C} \le \text{temperature} \le 45.0^\circ\text{C}$.
- **DQ-VIT-06**: Respiratory Rate: $6 \le \text{respiratory\_rate} \le 60\text{ bpm}$.

### Prescriptions & Medications
- **DQ-RX-01**: `prescription_items.medication_id` must reference an active medication in `medications`.
- **DQ-RX-02**: `quantity` must be a positive integer ($> 0$).
- **DQ-RX-03**: `duration` must be a positive integer ($> 0$).
- **DQ-RX-04**: Prescribing provider must be the encounter physician or authorized delegate.

---

## 2. Temporal Consistency Rules

Healthcare event ordering is strictly causal. Any chronological violation indicates a systemic data entry or clock synchronization defect:

| Rule ID | Table / Domain | Temporal Invariant | Failure Classification |
|---|---|---|---|
| **DQ-TIME-01** | All Tables | `created_at <= updated_at` | Critical Record Corruption |
| **DQ-TIME-02** | `appointments` | `appointment_date >= created_at::date` | Historical backdating / booking anomaly |
| **DQ-TIME-03** | `encounters` | `started_at <= ended_at` | Critical Chronological Inversion |
| **DQ-TIME-04** | `queue_entries` | `called_at >= created_at` (check-in) | Queue logic error |
| **DQ-TIME-05** | `queue_entries` | `started_at >= called_at` | Queue logic error |
| **DQ-TIME-06** | `queue_entries` | `completed_at >= started_at` | Queue duration error |
| **DQ-TIME-07** | `diagnostic_results` | `verified_at >= diagnostic_orders.ordered_at` | Result precedes order |
| **DQ-TIME-08** | `referrals` | `completed_at >= created_at` | Referral lifecycle error |
| **DQ-TIME-09** | `consents` | `valid_from < valid_until` | Invalid consent period |

---

## 3. Referential Integrity Rules (Zero-Orphan Policy)

Every foreign key must reference an intact parent entity:

```
vitals.encounter_id              -> encounters.id            (Orphans = 0)
prescriptions.encounter_id       -> encounters.id            (Orphans = 0)
prescription_items.prescription  -> prescriptions.id         (Orphans = 0)
diagnostic_orders.encounter_id   -> encounters.id            (Orphans = 0)
diagnostic_results.order_item_id -> diagnostic_order_items.id(Orphans = 0)
referrals.encounter_id           -> encounters.id            (Orphans = 0)
consultations.appointment_id     -> appointments.id          (Orphans = 0)
queue_entries.appointment_id     -> appointments.id          (Orphans = 0)
patient_identifiers.patient_id   -> patients.id              (Orphans = 0)
```
