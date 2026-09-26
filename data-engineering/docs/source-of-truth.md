# Source of Truth & Derived Data Specification

## 1. Domain Authoritative Entities

In a complex healthcare platform, distinct tables may capture overlapping information. The following table identifies the authoritative **Source of Truth** for each domain:

| Domain | Authoritative Table | Justification |
|---|---|---|
| **Patient Identity & Demographics** | `patients` | Primary registration record containing legal name, DOB, and primary contact. |
| **National / ABDM Identifiers** | `patient_identifiers` | Authoritative source for 14-digit ABHA Number, ABHA Address (`@abdm`), and verification status. |
| **Health Consent** | `consents` | Authoritative record of patient data sharing grants, purposes, and revocations. |
| **Scheduled Availability & Booking**| `appointments` | Authoritative record of scheduled clinic capacity, provider slot, and intended appointment date. |
| **Operational OPD Queue** | `queue_entries` | Authoritative for physical/virtual waiting room sequence, triage token, and live queue status. |
| **Clinical Encounter (Visit Session)**| `encounters` | Authoritative for visit duration, attending physician, and encounter completion state. |
| **Physiological Observations** | `vitals` | Point-in-time clinical measurements (BP, SpO2, Heart Rate, Temperature, BMI factors). |
| **Prescription Instructions** | `prescriptions` + `prescription_items` | Authoritative prescription orders, structured frequency, dosage, and duration. |
| **Medication Nomenclature** | `medications` | Authoritative drug catalog, generic brand names, and strengths. |
| **Diagnostic Test Request** | `diagnostic_orders` + `items` | Doctor order intent, priority, and lab routing. |
| **Diagnostic Findings** | `diagnostic_results` | Authoritative laboratory/radiology values, reference ranges, and abnormal flags. |
| **Inter-Facility Referrals** | `referrals` | Transfer of care requests between primary health centres and tertiary hospitals. |
| **Teleconsultation Session State** | `consultations` | Real-time meeting state, Daily.co private room metadata, and overall session lifecycle. |
| **Teleconsultation Attendance** | `consultation_participants` | Authoritative for individual participant joined/left timestamps and exact duration. |

---

## 2. Authoritative vs. Derived Data Decisions

### Decision 1: Patient Age vs. Date of Birth
- **Problem**: Storing an integer `age` field causes data drift as time progresses.
- **Rule**: `patients.date_of_birth` is the **sole source of truth**.
- **Transformation Decision**: Downstream analytical models must derive age dynamically:
  $$\text{age} = \lfloor \frac{\text{event\_date} - \text{date\_of\_birth}}{365.25} \rfloor$$
  At the time of an encounter, the patient's age at visit is calculated relative to `encounters.started_at`.

### Decision 2: Queue Wait Time vs. Appointment Time
- **Problem**: Calculating patient waiting time as `started_at - appointments.start_time` produces inaccurate results (patients arrive late or early).
- **Rule**: `queue_entries.created_at` (check-in time) to `queue_entries.started_at` (doctor called and started consultation) is the **authoritative wait time**.
- **Transformation Decision**:
  $$\text{wait\_duration} = \text{queue\_entries.started\_at} - \text{queue\_entries.created\_at}$$

### Decision 3: Teleconsultation Duration
- **Problem**: `consultations.actual_end - consultations.actual_start` represents the total room lifespan, not individual doctor-patient face-to-face time.
- **Rule**: `consultation_participants.duration_seconds` is the **authoritative participant presence record**.
- **Transformation Decision**: Clinical teleconsultation duration is the overlapping interval between the `PROVIDER` and `PATIENT` participant records.

### Decision 4: Encounter Status vs. Lock Status
- **Problem**: Once an encounter reaches `COMPLETED`, its clinical notes and attached items are locked to maintain medicolegal integrity.
- **Rule**: `encounters.status = 'COMPLETED'` with `ended_at IS NOT NULL` defines the final authoritative clinical state. Any vitals or prescriptions linked to open encounters (`IN_PROGRESS`) are considered preliminary until the encounter is completed.
