# Healthcare Platform API - Backend

Enterprise-ready FastAPI backend foundation supporting Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, and Phase 10.

## Architecture

```
                                          Postman / Frontend
                                                  │
                                                  ▼
                                            FastAPI /api/v1
                                                  │
      ┌───────────────────┬───────────────────────┼───────────────────────────────┬───────────────────────────────┬───────────────────────────────┬───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
      │                   │                       │                               │                               │                               │                               │                               │                               │
    Auth               Health                  Patients                 Appointments & Queues            Encounters & Vitals                  Referrals              Prescriptions & Diagnostics            Notifications                  Teleconsultations
      │                                           │                               │                               │                               │                               │                               │                               │
      ▼                                           ▼                               ▼                               ▼                               ▼                               ▼                               ▼                               ▼
 Auth Service                              Patient Service               Appointment Service              Encounter Service               Referral Service               Prescription Service            Notification Service            Consultation Service
      │                                           │                               │                               ├── Vital Service               │                               ├── Medication Service          │                               ├── DailyService
      ▼                                           ▼                               ├── Queue Service               │                               ▼                               ├── Diagnostic Service          ▼                               │ (WebRTC Rooms & Tokens)
 User Repository                           Patient Repository                     │                               ▼                       Referral Repository                     ▼                       Notification Repo                       ▼
      │                                           │                               ▼                       Encounter & Vital Repos                 │                       Prescription, Diagnostic Repos          │                       Consultation Repository
      └───────────────────┬───────────────────────┴─────────────────────── Appointment & Queue Repos               │                               │                               │                               │                               │
                          │                                                                                       │                               │                               │                               │                               │
                          └───────────────────────────────────────┬───────────────────────────────────────────────┴───────────────────────────────┴───────────────────────────────┴───────────────────────────────┼───────────────────────────────┘
                                                                  │                                                                                                                                               │
                                                                  ▼                                                                                                                                               ▼
                                                   Longitudinal Health Record Service                                                                                                                       Redis (Broker)
                                                   (Chronological Clinical Timeline)                                                                                                                              │
                                                                  │                                                                                                                                               ▼
                                                                  ▼                                                                                                                                        Celery Worker
                                                             SQLAlchemy 2.0                                                                                                                      ┌────────────────┼────────────────┐
                                                                  │                                                                                                                              ▼                ▼                ▼
                                                                  ▼                                                                                                                         Mock / SES       Mock / Twilio     In-App / DB
                                                             PostgreSQL 16 (Docker)                                                                                                           (Email)            (SMS)          (Database)
```

## Tech Stack
- **Python**: 3.11+ (running 3.14)
- **Framework**: FastAPI + Uvicorn
- **Teleconsultation & WebRTC Real-Time Media (Daily.co)**:
  - Strict architectural separation: Video/audio media transport is handled by Daily.co WebRTC infrastructure, while FastAPI controls session provisioning, authorization, state transitions, and attendance audit logs.
  - Private WebRTC rooms (`privacy: "private"`) dynamically created per consultation with strict time-to-live expiration.
  - Cryptographically signed meeting tokens generated per participant role (`PATIENT`, `PROVIDER`, `HEALTH_WORKER`).
  - Strict resource authorization: Patients can only obtain tokens for their own teleconsultation (`403 Forbidden` on cross-patient attempts); doctors can only join assigned sessions.
  - Assisted Teleconsultation workflow: Rural health workers (`NURSE` / `HEALTH_WORKER`) can enter sessions to assist rural patients with diagnostics, document presentation, and translation.
  - Granular attendance tracking: `joined_at`, `left_at`, `duration_seconds`, connection states (`CONNECTED`, `DISCONNECTED`, `RECONNECTING`), and reconnection attempts counter.
  - Webhook callback processing (`/api/v1/webhooks/daily`) for room lifecycle sync (`meeting.started` ➔ `IN_PROGRESS`, `meeting.ended` ➔ `COMPLETED`).
  - Seamless clinical transition: Concluded consultations link directly to the clinical `Encounter` record without duplicate creation.
- **Asynchronous Task Processing & Notifications**:
  - Celery 5.6 distributed task queue with Redis 7 message broker
  - Dedicated background workers with retry logic (exponential backoff: `2 ** retries`, max retries: 3)
  - Strict idempotency protection (`idempotency_key` preventing redundant SMS/Email transmissions)
  - Multi-channel notification delivery: In-App, Email (Mock / AWS SES), SMS (Mock / Twilio)
  - Granular user communication preferences (channel and notification category toggles)
  - PHI-safe notification templates (no sensitive diagnoses or test values exposed via SMS)
  - Periodic task runner (Celery Beat) for automated upcoming appointment reminders and follow-up alerts
- **Longitudinal Patient Health Records**:
  - Unified multi-domain health record assembly without denormalized data duplication
  - Consolidated queries across encounters, vitals, prescriptions, diagnostic orders & results, referrals, and appointments
  - Chronological clinical timeline stream (`APPOINTMENT`, `ENCOUNTER`, `VITAL`, `PRESCRIPTION`, `DIAGNOSTIC_ORDER`, `DIAGNOSTIC_RESULT`, `REFERRAL`)
  - Flexible event filtering by `event_type`, date range (`from_date`, `to_date`), and pagination (`page`, `page_size`)
  - Strict resource-level access control (patient self-service portal access; cross-patient blocked with `403 Forbidden`)
- **Prescriptions & Formulary Medications**:
  - Clear architectural separation: Reusable Drug Formulary (`Medication`) vs Patient-specific Line Item Instructions (`PrescriptionItem`)
  - Strict lifecycle state transitions: `DRAFT` ➔ `ISSUED` ➔ `COMPLETED` (or `CANCELLED`)
  - Medication catalog validation: Inactive medications blocked (`MEDICATION_INACTIVE` 400)
  - Longitudinal patient prescription history with full audit provenance
- **Diagnostic Orders & Verified Laboratory Results**:
  - Investigation Catalog (`DiagnosticTest`): Standard codes (CBC, Blood Glucose, Renal profile)
  - Clinical Order Tracking (`DiagnosticOrder`): Priority triage (`ROUTINE`, `URGENT`, `STAT`)
  - Observation Results (`DiagnosticResult`): Multi-type values (numeric, qualitative, textual), units, reference ranges, abnormal flags, and verifier audit provenance
- **Referral Management (Multi-Tier Care Coordination)**:
  - Multi-tier patient transfers: Sub-centre ➔ PHC ➔ Rural Hospital ➔ District Hospital ➔ Specialist Centre
  - Facility-to-facility isolation: Self-referrals blocked (`REFERRAL_FACILITY_IDENTICAL` 400)
  - Strict lifecycle state transitions: `DRAFT` ➔ `SENT` ➔ `ACCEPTED` ➔ `SCHEDULED` ➔ `COMPLETED` (or `REJECTED` / `CANCELLED`)
  - Facility Outbox (`/facilities/{id}/referrals/outgoing`) and Inbox (`/facilities/{id}/referrals/incoming`)
  - Structured outcomes on completion (`outcome_status`, `outcome_notes`, `follow_up_required`, `follow_up_date`)
- **Clinical Encounters & Observation Vitals**:
  - Clear domain separation: Appointment (planned care) vs Encounter (delivered clinical reality)
  - 1-to-1 appointment-to-encounter linkage with duplicate creation prevention (`409 Conflict`)
  - Strict forward state transitions: `SCHEDULED` ➔ `IN_PROGRESS` ➔ `COMPLETED`
  - Immutability lock on completion: completed clinical encounters reject direct modifications (`400 Bad Request`)
  - Multiple observation vitals snapshots per encounter (time-series monitoring during visits)
  - Explicit clinical unit standards: Temperature (°C), Heart Rate (bpm), RR (breaths/min), BP (mmHg), SpO2 (%), Weight (kg), Height (cm)
  - Physiological plausibility validation envelopes
- **Appointments & Triage Queues**:
  - Overlap time-conflict detection (`409 Conflict`)
  - Strict forward state machines (`SCHEDULED` ➔ `WAITING` ➔ `IN_CONSULTATION` ➔ `COMPLETED`)
  - Facility-scoped daily sequential queue numbering (`Q001`, `Q002`)
  - Priority triage ordering (`URGENT` ➔ `HIGH` ➔ `NORMAL` ➔ FIFO arrival)
  - Granular timestamps for operational waiting-time analytics
- **Patient Registry**: Dual ID (Internal UUID + Human `PAT-YYYY-XXXXXX`), soft deactivation, duplicate detection, optional user portal linking
- **Authentication**: PyJWT + Argon2id (`pwdlib`) + OAuth2 Bearer
- **Authorization**: Role-Based Access Control (RBAC) & Resource-Level Ownership
- **Database & Cache**: PostgreSQL 16 + Redis 7 (Docker Compose)
- **ORM & Migrations**: SQLAlchemy 2.0 + Alembic + psycopg 3
- **Testing**: pytest + httpx (106 automated tests passing)

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                  # App factory, CORS, structured logging, error handlers
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Central API v1 router
│   │       ├── auth.py          # Authentication (/register, /login, /refresh, /me)
│   │       ├── facilities.py    # Facility directory (/facilities)
│   │       ├── patients.py      # Patient management (/patients, /search, /{id})
│   │       ├── patient_records.py # Longitudinal health record & timeline (/patients/{id}/record, /timeline)
│   │       ├── appointments.py  # Appointments (/appointments, /check-in, /reschedule, /cancel, /encounter)
│   │       ├── consultations.py # Teleconsultation API (/consultations, /join, /end, /cancel, /participants)
│   │       ├── webhooks.py      # Daily.co WebRTC callbacks (/webhooks/daily)
│   │       ├── queues.py        # Facility queues (/queues/{facility_id}, /call-next, /start, /complete)
│   │       ├── encounters.py    # Clinical encounters & vitals (/encounters, /vitals, /referral)
│   │       ├── referrals.py     # Referral lifecycle & facility inboxes (/referrals, /accept, /reject, /schedule, /complete)
│   │       ├── medications.py   # Drug formulary catalog (/medications)
│   │       ├── prescriptions.py # Clinical prescriptions (/encounters/{id}/prescriptions, /prescriptions/{id}/cancel)
│   │       ├── diagnostic_tests.py # Lab test catalog (/diagnostic-tests)
│   │       ├── diagnostics.py   # Investigation orders & lab results (/diagnostic-orders, /diagnostic-order-items/{id}/result)
│   │       ├── notifications.py # Notification feed, unread count, preferences (/notifications)
│   │       ├── test_rbac.py     # Role-guarded test endpoints
│   │       ├── health.py        # Health checks (/health, /database, /redis)
│   │       └── system_check.py  # Infrastructure verification checks
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings (DB, Redis, Celery, Daily, JWT)
│   │   ├── celery_app.py        # Celery application instance & broker configuration
│   │   ├── roles.py             # UserRole enum (PATIENT, DOCTOR, NURSE, ADMIN)
│   │   ├── security.py          # Argon2 hashing & JWT creation/decoding
│   │   ├── dependencies.py      # get_current_user and require_role guards
│   │   ├── logging.py           # Structured request logging middleware (PHI-safe)
│   │   └── exceptions.py        # Standardized error envelopes & handlers
│   ├── db/
│   │   ├── base.py              # SQLAlchemy 2.0 DeclarativeBase
│   │   └── session.py           # Engine, SessionLocal, get_db dependency
│   ├── integrations/            # External provider adapters
│   │   ├── daily.py             # DailyService (WebRTC room creation, tokens, webhooks)
│   │   ├── email.py             # BaseEmailProvider, MockEmailProvider, SESEmailProvider
│   │   └── sms.py               # BaseSMSProvider, MockSMSProvider, TwilioSMSProvider
│   ├── models/
│   │   ├── user.py              # User model (with facility_id)
│   │   ├── patient.py           # Patient model (with user_id)
│   │   ├── facility.py          # Facility model
│   │   ├── appointment.py       # Appointment model (state machine, audit)
│   │   ├── consultation.py      # Teleconsultation session model
│   │   ├── consultation_participant.py # Participant attendance & connection tracking model
│   │   ├── queue.py             # QueueEntry model (priority, timestamps)
│   │   ├── encounter.py         # Clinical Encounter model (completion audit, notes)
│   │   ├── vital.py             # Vitals observation model (BP, HR, SpO2, Temp, RR)
│   │   ├── referral.py          # Referral model (incoming/outgoing, state machine, outcome)
│   │   ├── medication.py        # Reusable drug formulary model
│   │   ├── prescription.py      # Prescription header model
│   │   ├── prescription_item.py # Prescription line item instructions model
│   │   ├── diagnostic_test.py   # Diagnostic test catalog model
│   │   ├── diagnostic_order.py  # Diagnostic order model
│   │   ├── diagnostic_order_item.py # Order item model
│   │   ├── diagnostic_result.py # Verified lab result observation model
│   │   ├── notification.py      # Multi-channel notification delivery model
│   │   ├── notification_preference.py # User communication preferences model
│   │   └── system_check.py      # SystemCheck model
│   ├── schemas/
│   │   ├── auth.py              # Auth request & response schemas
│   │   ├── patient.py           # Patient schemas (with user_id)
│   │   ├── patient_record.py    # Longitudinal record, timeline event, and summary schemas
│   │   ├── facility.py          # Facility schemas
│   │   ├── appointment.py       # Appointment schemas
│   │   ├── consultation.py      # Teleconsultation, meeting token, and participant schemas
│   │   ├── queue.py             # Queue schemas
│   │   ├── encounter.py         # Encounter schemas
│   │   ├── vital.py             # Vital observation schemas with validation
│   │   ├── referral.py          # Referral schemas with outcomes
│   │   ├── medication.py        # Formulary drug schemas
│   │   ├── prescription.py      # Prescription & item schemas
│   │   ├── diagnostic.py        # Diagnostic test, order, item, and result schemas
│   │   └── notification.py      # Notification, unread count, and preference schemas
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── patient_repository.py
│   │   ├── facility_repository.py
│   │   ├── appointment_repository.py
│   │   ├── consultation_repository.py
│   │   ├── queue_repository.py
│   │   ├── encounter_repository.py
│   │   ├── vital_repository.py
│   │   ├── referral_repository.py
│   │   ├── medication_repository.py
│   │   ├── prescription_repository.py
│   │   ├── diagnostic_test_repository.py
│   │   ├── diagnostic_repository.py
│   │   └── notification_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── patient_record_service.py
│   │   ├── facility_service.py
│   │   ├── appointment_service.py
│   │   ├── consultation_service.py
│   │   ├── queue_service.py
│   │   ├── encounter_service.py
│   │   ├── vital_service.py
│   │   ├── referral_service.py
│   │   ├── medication_service.py
│   │   ├── prescription_service.py
│   │   ├── diagnostic_service.py
│   │   └── notification_service.py
│   └── tasks/
│       ├── test_tasks.py        # Pipeline test tasks
│       ├── notification_tasks.py# Async notification delivery with retry & idempotency
│       └── periodic_tasks.py    # Scheduled reminder jobs (Celery Beat)
├── migrations/                  # Alembic migrations directory
├── tests/                       # Automated pytest test suites (106 tests)
│   ├── test_auth.py             # Auth & RBAC test suite (13 tests)
│   ├── test_patients.py         # Patient registry test suite (11 tests)
│   ├── test_patient_records.py  # Longitudinal records & clinical timeline tests (9 tests)
│   ├── test_appointments.py     # Appointment lifecycle & conflict tests (7 tests)
│   ├── test_consultations.py    # Teleconsultation sessions & join tests (8 tests)
│   ├── test_consultation_participants.py # Attendance, assisted calls, and reconnect tests (3 tests)
│   ├── test_daily_integration.py# Daily.co WebRTC adapter & webhook tests (2 tests)
│   ├── test_queue.py            # Facility queue & priority triage tests (5 tests)
│   ├── test_encounters.py       # Clinical encounter creation & lock tests (6 tests)
│   ├── test_vitals.py           # Observation vitals & range validation tests (4 tests)
│   ├── test_referrals.py        # Care transfer referrals lifecycle tests (8 tests)
│   ├── test_prescriptions.py    # Prescriptions & formulary tests (6 tests)
│   ├── test_diagnostics.py      # Diagnostic orders & lab results tests (6 tests)
│   ├── test_tasks.py            # Celery task execution, retry, and idempotency tests (5 tests)
│   ├── test_notifications.py    # Notification API, preferences, and security tests (6 tests)
│   ├── test_health.py           # Health endpoint tests (4 tests)
│   └── test_system_check.py     # System verification tests (3 tests)
├── .env                         # Local runtime secrets (untracked)
├── .env.example                 # Environment configuration template
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml           # Local development containers
└── requirements.txt             # Frozen dependency manifest
```

---

## Teleconsultation API (v1)

| Method | Endpoint | Required Role | Description |
|---|---|---|---|
| `POST` | `/api/v1/appointments/{appointment_id}/consultation` | Doctor / Nurse / Admin | Provisions a private Daily.co room and consultation record for a scheduled appointment |
| `GET` | `/api/v1/consultations/{id}` | Patient / Assigned Doctor | Retrieves session metadata, room information, and participant attendance log |
| `GET` | `/api/v1/consultations` | Authenticated | Lists teleconsultation sessions associated with the user |
| `POST` | `/api/v1/consultations/{id}/join` | Patient / Assigned Doctor / Nurse | Authenticates participant, transitions state machine, and generates cryptographic Daily meeting token |
| `POST` | `/api/v1/consultations/{id}/end` | Assigned Doctor / Admin | Concludes session, closes private room, logs duration, and links clinical encounter |
| `POST` | `/api/v1/consultations/{id}/cancel` | Participant / Staff | Cancels scheduled consultation session |
| `GET` | `/api/v1/consultations/{id}/participants` | Participant / Staff | Retrieves detailed attendance timeline, connection states, and durations |
| `POST` | `/api/v1/webhooks/daily` | Webhook / Daily.co | Webhook listener for real-time room events (`meeting.started`, `meeting.ended`) |

---

## Quickstart

### 1. Start Infrastructure (Docker)
```powershell
docker compose up -d
docker compose ps
```

### 2. Activate Python Virtual Environment
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

### 3. Run Database Migrations
```powershell
alembic upgrade head
```

### 4. Start Development Server & Celery Worker
```powershell
# Terminal 1: FastAPI
uvicorn app.main:app --reload

# Terminal 2: Celery Worker (Windows solo pool)
celery -A app.core.celery_app.celery_app worker -P solo --loglevel=info
```

### 5. Run Automated Tests
```powershell
pytest -v
```
