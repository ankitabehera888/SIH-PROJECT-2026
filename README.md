# 🏥 Sahaay – Enterprise Healthcare Interoperability & Care Management Platform

![Sahaay Healthcare Platform](https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1200&q=80)

**Sahaay** is a unified, enterprise-grade healthcare platform designed to bridge the gap between primary healthcare centers (PHCs), regional referral hospitals, community health workers (ASHAs), doctors, and patients. Built with **FastAPI**, **React**, **TypeScript**, **FHIR R4**, and **ABDM (Ayushman Bharat Digital Mission)** compliance.

---

## ✨ Features & Capabilities (38/38 Implemented)

### 🩺 Clinical Workflows & Care Continuity
- **Multi-Role Dashboards:** Role-scoped operational views for Doctors, Patients, Community Health Workers (ASHAs), and Facility Admins.
- **Clinical Encounters & Vitals:** Full encounter lifecycle (creation, update, completion, locking) with time-series observation vitals (BP, HR, SpO2, Temp, RR).
- **Prescriptions & Pharmacy Dispensing:** Multi-item prescriptions, active medication tracking, refill management, and pharmacy dispensing statuses (`Active`, `Completed`, `Discontinued`).
- **Diagnostics & Lab Results:** Diagnostic order placement, per-item lab/imaging result verification, and PDF report uploads.
- **Referrals & Care Transfers:** Intra-facility and inter-facility referral outbox/inbox with status tracking (`Submitted`, `Accepted`, `Scheduled`, `Completed`).
- **Clinical Follow-ups Tracking:** Follow-up appointment scheduling, status tracking (`Upcoming`, `Missed`, `Completed`), rescheduling, and in-app/SMS patient reminders.

### 💬 Real-Time Communication & Telehealth
- **Multi-User Messaging & Chat:** Direct chat threads between patients, doctors, and health workers, backed by real-time **Socket.IO** event broadcasts and unread badges.
- **Teleconsultation (WebRTC):** Automated WebRTC video session provisioning with **Daily.co** token generation and attendance logs.
- **AI Symptom Assistant & Voice Bot:** AI-powered symptom analysis, Whisper voice transcription, text-to-speech synthesis, and downloadable PDF symptom reports.

### 🌐 Standards, Interoperability & Analytics
- **FHIR R4 Standard Support:** Export longitudinal patient bundles (Patient, Practitioner, Organization, Encounter, Observation, MedicationRequest, ServiceRequest, DiagnosticReport).
- **ABDM Digital Health Integration:** ABHA identifier linking, consent artefact management, and simulated ABDM OTP authentication.
- **Healthcare Analytics Engine:** Executive KPIs, time-series metrics, referral turnaround aging, facility throughput, and personal patient adherence analytics.
- **Facility Stock Inventory:** Real-time stock tracking with automated reorder alerts (`Available`, `Low Stock`, `Out of Stock`).
- **Billing & Invoicing:** Patient service invoicing, balance due calculation, and multi-channel payment processing (`Cash`, `Card`, `UPI`, `Insurance`).

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) |
| **Database & ORM** | PostgreSQL / SQLite + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) |
| **Real-Time Events** | [Socket.IO](https://python-socketio.readthedocs.io/) |
| **Async Worker Queue** | [Celery](https://docs.celeryq.dev/) + Redis |
| **Frontend Framework** | [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Vite](https://vitejs.dev/) |
| **Styling & Motion** | Tailwind CSS + Framer Motion |
| **Standards & APIs** | FHIR R4, ABDM Gateway APIs, Daily.co WebRTC |

---

## ⚙️ Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+

---

### 1. ⚙️ Running the Backend Server

Open a terminal in the project root:

```bash
cd backend

# Create & activate Python virtual environment
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

> 🌐 **Backend API:** `http://127.0.0.1:8000`  
> 📄 **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`

---

### 2. 💻 Running the Frontend Web App

Open a second terminal in the project root:

```bash
# Navigate to project directory
cd shaay

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```

> 🌐 **Frontend Application:** `http://localhost:5173`

---

## 🔐 System Roles (RBAC)

| Role | Key Capabilities |
|---|---|
| **DOCTOR** | Conduct encounters, write prescriptions, order diagnostics, accept referrals, hold video consultations, view doctor dashboard |
| **NURSE** | Record vitals, manage facility queues, check in patients, update stock inventory |
| **PATIENT** | Book appointments, view longitudinal record, check active medicines, track care journey, analyze personal adherence |
| **WORKER** | Community health worker (ASHA) field patient registration, community screening, follow-up alerts, chat |
| **ADMIN** | System administration, facility management, platform analytics, billing, user role assignments |

---

## 📄 License & Attribution

Developed by **Ankita Behera** ([ankitabehera888](https://github.com/ankitabehera888)).  
Released under the [MIT License](LICENSE).
