# Data Dictionary — Operational Database

This data dictionary outlines the schema of the live PostgreSQL transactional database (`healthcare_dev`).

---

## 1. Core Demographics & Identity

### `patients`
Authoritative store of patient demographic records.

| Column | Type | Nullable | Description | Sensitive (PHI/PII) |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No (Pseudonymous) |
| `first_name` | VARCHAR(100) | No | Patient legal given name | Yes (Direct Identifier) |
| `last_name` | VARCHAR(100) | No | Patient legal surname | Yes (Direct Identifier) |
| `date_of_birth` | DATE | No | Date of birth for age calculation | Yes (Indirect Identifier) |
| `gender` | VARCHAR(20) | No | Biological/administrative gender | No |
| `phone` | VARCHAR(20) | No | Primary mobile phone number | Yes (Direct Identifier) |
| `email` | VARCHAR(255) | Yes | Contact email address | Yes (Direct Identifier) |
| `address` | TEXT | Yes | Residential residential address | Yes (Direct Identifier) |
| `is_active` | BOOLEAN | No | Soft-deletion flag | No |
| `created_at` | TIMESTAMPTZ | No | Record creation timestamp | No |
| `updated_at` | TIMESTAMPTZ | No | Last update timestamp | No |

### `patient_identifiers`
External identity mappings (ABHA number, ABHA address, National ID).

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `patient_id` | UUID | No | Foreign key to `patients.id` | No |
| `system` | VARCHAR(255) | No | Identifying authority URI | No |
| `value` | VARCHAR(255) | No | External identifier string (e.g. 14-digit ABHA) | Yes (Direct Identifier) |
| `identifier_type` | VARCHAR(50) | No | Type category (e.g., ABHA_NUMBER) | No |
| `is_verified` | BOOLEAN | No | Verification status flag | No |
| `created_at` | TIMESTAMPTZ | No | Linkage timestamp | No |

### `consents`
ABDM patient consent artefacts and access permissions.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `patient_id` | UUID | No | Foreign key to `patients.id` | No |
| `purpose` | VARCHAR(50) | No | Clinical / analytical purpose code | No |
| `scope` | VARCHAR(50) | No | Granular scope (ALL, ENCOUNTER, etc.) | No |
| `status` | VARCHAR(50) | No | Lifecycle status (GRANTED, REVOKED) | No |
| `valid_from` | TIMESTAMPTZ | No | Consent start validity | No |
| `valid_until` | TIMESTAMPTZ | No | Expiration timestamp | No |

---

## 2. Scheduling & Clinical Queue

### `appointments`
Provider schedules and patient booking slots.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `patient_id` | UUID | No | Foreign key to `patients.id` | No |
| `provider_id` | INTEGER | No | Foreign key to `users.id` (Doctor) | No |
| `facility_id` | UUID | No | Foreign key to `facilities.id` | No |
| `appointment_date`| DATE | No | Scheduled appointment date | No |
| `start_time` | TIME | No | Scheduled slot start | No |
| `end_time` | TIME | No | Scheduled slot end | No |
| `status` | VARCHAR(50) | No | Status (BOOKED, CHECKED_IN, COMPLETED) | No |
| `reason` | TEXT | Yes | Reason for consultation | Yes (Clinical Context) |

### `queue_entries`
Real-time outpatient department (OPD) queue entries.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `appointment_id` | UUID | No | Foreign key to `appointments.id` | No |
| `facility_id` | UUID | No | Foreign key to `facilities.id` | No |
| `token_number` | INTEGER | No | Daily sequential queue token | No |
| `priority` | VARCHAR(20) | No | Triage priority (NORMAL, EMERGENCY) | No |
| `status` | VARCHAR(50) | No | Queue status (WAITING, CALLED, IN_CONSULTATION)| No |
| `called_at` | TIMESTAMPTZ | Yes | Timestamp when doctor called token | No |
| `started_at` | TIMESTAMPTZ | Yes | Timestamp when consultation started | No |
| `completed_at` | TIMESTAMPTZ | Yes | Timestamp when consultation closed | No |

---

## 3. Clinical Encounters & Physiological Vitals

### `encounters`
Clinical visit sessions and consultations.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `patient_id` | UUID | No | Foreign key to `patients.id` | No |
| `provider_id` | INTEGER | No | Foreign key to `users.id` | No |
| `facility_id` | UUID | No | Foreign key to `facilities.id` | No |
| `appointment_id` | UUID | Yes | Foreign key to `appointments.id` | No |
| `encounter_type` | VARCHAR(50) | No | Encounter classification (OUTPATIENT, etc.)| No |
| `status` | VARCHAR(50) | No | Encounter state (IN_PROGRESS, COMPLETED) | No |
| `chief_complaint`| TEXT | Yes | Presenting symptoms and complaints | Yes (Clinical PHI) |
| `clinical_notes` | TEXT | Yes | Doctor's diagnostic progress notes | Yes (Clinical PHI) |
| `started_at` | TIMESTAMPTZ | No | Clinical encounter start | No |
| `ended_at` | TIMESTAMPTZ | Yes | Clinical encounter completion | No |

### `vitals`
Physiological point-in-time clinical observations.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `encounter_id` | UUID | No | Foreign key to `encounters.id` | No |
| `systolic_bp` | INTEGER | Yes | Systolic Blood Pressure (mmHg) | Yes (Clinical PHI) |
| `diastolic_bp` | INTEGER | Yes | Diastolic Blood Pressure (mmHg) | Yes (Clinical PHI) |
| `heart_rate` | INTEGER | Yes | Pulse rate (bpm) | Yes (Clinical PHI) |
| `temperature` | NUMERIC(4,1)| Yes | Body temperature (°C) | Yes (Clinical PHI) |
| `spo2` | NUMERIC(4,1)| Yes | Blood oxygen saturation percentage | Yes (Clinical PHI) |
| `respiratory_rate`| INTEGER | Yes | Breaths per minute | Yes (Clinical PHI) |
| `weight` | NUMERIC(5,2)| Yes | Body mass in kg | Yes (Clinical PHI) |
| `height` | NUMERIC(5,2)| Yes | Stature in cm | Yes (Clinical PHI) |
| `recorded_at` | TIMESTAMPTZ | No | Observation recording timestamp | No |

---

## 4. Pharmacy & Medications

### `medications`
Pharmaceutical drug catalog.

| Column | Type | Nullable | Description | Sensitive |
|---|---|---|---|---|
| `id` | UUID | No | Primary key | No |
| `name` | VARCHAR(255) | No | Commercial/trade name | No |
| `generic_name` | VARCHAR(255) | No | Active pharmaceutical ingredient (INN) | No |
| `strength` | VARCHAR(50) | No | Dosage strength (e.g. 500mg) | No |
| `dosage_form` | VARCHAR(50) | No | Form (TABLET, SYRUP, INJECTION) | No |
| `route` | VARCHAR(50) | No | Route of administration (ORAL, IV) | No |
| `is_active` | BOOLEAN | No | Catalog availability flag | No |

### `prescriptions` & `prescription_items`
Structured physician prescription orders and items.

| Table | Key Column | Description |
|---|---|---|
| `prescriptions` | `id`, `encounter_id`, `prescriber_id`, `prescribed_at`, `status` | Parent prescription record |
| `prescription_items` | `id`, `prescription_id`, `medication_id`, `dosage`, `frequency`, `duration`, `duration_unit`, `quantity`, `instructions` | Specific dosage instructions |

---

## 5. Diagnostics & Lab Results

| Table | Key Columns | Description |
|---|---|---|
| `diagnostic_tests` | `id`, `name`, `code`, `category` (LABORATORY, RADIOLOGY) | Test catalog definition |
| `diagnostic_orders`| `id`, `encounter_id`, `priority`, `ordered_at`, `status` | Doctor lab order request |
| `diagnostic_order_items` | `id`, `order_id`, `diagnostic_test_id` | Individual test in order |
| `diagnostic_results` | `id`, `order_item_id`, `result_value`, `unit`, `reference_range`, `abnormal_flag`, `result_status`, `verified_at` | Quantitative/qualitative findings |

---

## 6. Referrals & Telemedicine

| Table | Key Columns | Description |
|---|---|---|
| `referrals` | `id`, `encounter_id`, `referring_facility_id`, `receiving_facility_id`, `status`, `referral_type`, `priority`, `reason`, `clinical_summary` | Patient transfer between PHC and Hospital |
| `consultations` | `id`, `appointment_id`, `room_name`, `room_url`, `status`, `actual_start`, `actual_end` | Daily WebRTC teleconsultation session |
| `consultation_participants` | `id`, `consultation_id`, `user_id`, `role`, `joined_at`, `left_at`, `duration_seconds` | Attendance audit log |

---

## 7. Operational Administration & Auditing

| Table | Description |
|---|---|
| `users` | Doctors, Nurses, Staff, Admins, Patients (Argon2 hashes, roles, active flags) |
| `facilities` | Hospitals, Primary Health Centres, Clinics (facility codes, tiers) |
| `notifications` & `preferences` | In-app, SMS, and email notification events and delivery receipts |
| `interoperability_audits` | Read and export audit log for ABDM / FHIR compliance |
| `system_checks` | Application health and database liveness probes |
| `alembic_version` | Database migration version tracking |
