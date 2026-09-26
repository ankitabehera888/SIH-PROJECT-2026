# Production Observability & Alerting Specification

## 1. Metrics Stack
- **Prometheus**: Scrapes metrics every 15s across:
  - `fastapi_backend` (:8000/metrics)
  - `postgres_database` (:9187)
  - `redis_cache` (:9121)
  - `airflow_scheduler` (:8080)
- **Grafana**: Operational dashboards visualizing Quality Score, Pipeline Duration, Request Rates, and Database Connections.

---

## 2. Alert Escalation Matrix

| Trigger | Condition | Severity | Action |
|---|---|---|---|
| Quality Gate Blocked | Critical Quality Check Failed | `CRITICAL` | Block publication, alert Slack/PagerDuty |
| Database Unreachable | PostgreSQL ping failed | `CRITICAL` | Page On-Call DBA, initiate failover |
| Ingestion Lag | Freshness hours $> 48\text{h}$ | `WARNING` | Notify data engineering team |
| Storage Exhaustion | Disk usage $> 85\%$ | `WARNING` | Trigger log/backup cleanup policy |
