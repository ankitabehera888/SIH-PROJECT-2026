# Production Security & Least-Privilege Specification

## 1. Network Perimeter & Access Isolation
- **Reverse Proxy**: Nginx terminates TLS (HTTPS) on port 443 with security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`).
- **Private Database Network**: PostgreSQL (5432), Redis (6379), and Airflow internal databases are isolated inside the Docker network and not exposed to the public internet.

---

## 2. Least-Privilege Database Roles
Role definitions implemented in `infrastructure/postgres/init/01_roles.sql`:
- **`app_user`**: Full DML on operational clinical tables (`public` schema). No administrative or cross-database privileges.
- **`etl_user`**: Full DML and schema manipulation on `analytics` and staging schemas.
- **`analytics_user`**: Strict `SELECT` privileges only on `analytics` schema tables. No access to unmasked patient tables.
- **`readonly_user`**: Audit and read-only extraction role.

---

## 3. Data Protection & PHI Redaction
- Zero patient PHI (names, phone numbers, addresses, ABHA, clinical notes) is logged in application, Airflow, or data quality logs.
- Surrogate keys (`patient_key`, `encounter_key`, `run_id`) are used exclusively in analytical facts and audit traces.
