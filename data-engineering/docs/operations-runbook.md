# Production Operations Runbook

## 1. Routine Operational Checklist

### Daily (08:00 IST)
- [ ] Verify `healthcare_data_pipeline` status in Airflow UI (`http://localhost:8080`).
- [ ] Check latest data quality score: `GET /api/v1/analytics/quality/summary`.
- [ ] Confirm 0 critical quality alerts: `GET /api/v1/analytics/quality/alerts`.
- [ ] Verify backup generated and checksum verified: `infrastructure/postgres/backup/`.

### Weekly
- [ ] Review average daily pipeline run duration in Grafana.
- [ ] Check PostgreSQL disk utilization (`< 75%`).
- [ ] Run test restore drill: `powershell -File scripts/restore_database.ps1`.

### Monthly
- [ ] Run full disaster recovery drill: `powershell -File scripts/disaster_recovery_test.ps1`.
- [ ] Review slow queries using `pg_stat_statements`.
- [ ] Audit least-privilege role access and rotate service account passwords.

---

## 2. On-Call Incident Response Matrix

```text
Incident Detected
       │
       ▼
Classify Severity
(INFO / WARNING / CRITICAL)
       │
  ┌────┴────┐
  ▼         ▼
WARNING  CRITICAL
  │         │
  │         ├─ Block Downstream Publication
  │         ├─ Engage Lead Engineer
  │         └─ Follow Scenario Playbook
  │         │
  └────┬────┘
       ▼
Remediate Root Cause
       │
       ▼
Run Quality Verification (scripts/run_quality_monitor.py)
       │
       ▼
Publish Datasets & Resolve Alert
```
