# Production Data Platform Architecture Specification

## 1. Overview
This document specifies the target architecture for the production-grade healthcare data platform, spanning operational transactions, raw ingestion, staging standardization, analytical star schemas, clinical cohorts, KPIs, analytics APIs, automated quality monitoring, and Airflow orchestration.

---

## 2. End-to-End System Topology

```text
                         USERS
                           │
                           ▼
                    Frontend / APIs
                           │
                           ▼
                  Nginx Reverse Proxy
                    (TLS / HTTPS)
                           │
                           ▼
                     FastAPI Backend
                 (/health/live, /ready)
                           │
             ┌─────────────┴─────────────┐
             ↓                           ↓
       Operational DB              Analytics APIs
             │                           │
             └─────────────┬─────────────┘
                           ↓
                    DATA PLATFORM
                           │
                  ┌────────┴────────┐
                  ↓                 ↓
              Airflow            Redis
                  │
                  ▼
             ETL / ELT
                  │
       ┌──────────┼───────────┐
       ↓          ↓           ↓
      RAW      STAGING     ANALYTICS
                             │
                  ┌──────────┼──────────┐
                  ↓          ↓          ↓
               Cohorts      KPIs     Quality
                  │          │          │
                  └──────────┼──────────┘
                             ↓
                       Monitoring
                             │
                             ▼
                    Backup / Recovery
```

---

## 3. High Availability & Resource Boundaries
- **Container Resource Allocation**:
  - FastAPI: 1.0 CPU, 1GB RAM.
  - Airflow Scheduler & Webserver: 1.5 CPU, 2GB RAM.
  - PostgreSQL: 2.0 CPU, 4GB RAM.
  - Redis: 0.5 CPU, 512MB RAM (`maxmemory-policy allkeys-lru`).
- **Separation of Metadata**:
  - `healthcare_dev`: Operational + analytical schemas.
  - `airflow_db`: Dedicated Airflow metadata database.
