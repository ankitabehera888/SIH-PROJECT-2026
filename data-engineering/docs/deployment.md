# Production Deployment Specification

## 1. Deployment Workflow & Gating
Production deployments follow a strict automated progression:

```text
Developer Branch
      │
      ▼
Pull Request & Automated CI
(Pytest, Linting, Alembic Check)
      │
      ▼
Docker Image Build & Security Scan
      │
      ▼
Staging Deployment & Smoke Tests
      │
      ▼
Readiness Gate Check
(scripts/deployment_check.ps1)
      │
      ▼
Production Release
```

---

## 2. Environment Configurations
- `.env.development`: Local development with verbosity.
- `.env.staging`: Staging with mock integrations and test database.
- `.env.production`: Hardened production secrets externalized from Git. Template provided in `.env.example`.

---

## 3. Database Migration Strategy
- Managed via Alembic migrations.
- Zero breaking changes: Add columns first, deploy code, backfill data, and deprecate old columns in staged releases.
- Never drop columns in the same deployment release.
