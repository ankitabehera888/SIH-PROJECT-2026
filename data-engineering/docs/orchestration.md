# Pipeline Orchestration & Scheduling Specification

## 1. Executive Summary
Phase 11 operationalizes the end-to-end healthcare data engineering roadmap using **Apache Airflow**, turning decoupled manual pipeline scripts into an automated, dependency-aware, scheduled, and idempotent production workflow.

---

## 2. Target Orchestration Architecture

```text
                         SCHEDULE
                            │
                            ▼
                    ┌───────────────┐
                    │    AIRFLOW    │
                    │  ORCHESTRATOR │
                    └───────┬───────┘
                            │
                            ▼
                       EXTRACTION
                            │
                            ▼
                           RAW
                            │
                            ▼
                      RAW QUALITY
                            │
                            ▼
                        STAGING
                            │
                            ▼
                     ANALYTICAL DB
                            │
                            ▼
                        COHORTS
                            │
                            ▼
                          KPIs
                            │
                            ▼
                    DATA QUALITY
                            │
                    ┌───────┴───────┐
                    ▼               ▼
                   PASS           BLOCK
                    │               │
                    ▼               ▼
                 PUBLISH          ALERT
                    │
                    ▼
               ANALYTICS API
                    │
                    ▼
                FRONTEND
```

---

## 3. Production DAG Catalog

### 3.1 `healthcare_data_pipeline`
- **Schedule**: `0 2 * * *` (Daily at 02:00 IST)
- **Catchup**: `False`
- **Max Active Runs**: 1
- **Task Hierarchy**:
  $$\text{extract} \to \text{raw\_validation} \to \text{staging} \to \text{load\_dimensions} \to \text{load\_facts} \to \text{build\_cohorts} \to \text{build\_metrics} \to \text{quality\_monitoring} \to \text{publish}$$
- **Quality Gate Integration**: If `quality_monitoring` detects any `CRITICAL` quality failures, the Quality Gate blocks execution and skips `publish`.

### 3.2 `quality_monitoring`
- **Schedule**: `0 */6 * * *` (Every 6 hours)
- **Purpose**: Evaluates data freshness, volume deviations, and biometric bounds independently of the main ETL schedule.
- **Task Hierarchy**:
  $$\text{check\_freshness} \to \text{anomaly\_detection} \to \text{quality\_suite}$$

### 3.3 `backfill_pipeline`
- **Schedule**: `None` (Manual / external trigger only)
- **Purpose**: Reprocesses historical cohort memberships and KPIs for specified historical date windows (`start_date`, `end_date`) idempotently.
- **Task Hierarchy**:
  $$\text{validate\_parameters} \to \text{recompute\_cohorts} \to \text{recompute\_metrics}$$

---

## 4. Retries, Timeouts, and Error Classification

| Task | Execution Timeout | Retries | Retry Delay | Failure Classification |
|---|---|---|---|---|
| `extract` | 30 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `raw_validation` | 15 minutes | 1 | 2 minutes | `DATA_FAILURE` |
| `staging` | 30 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `load_dimensions` | 30 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `load_facts` | 45 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `build_cohorts` | 30 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `build_metrics` | 20 minutes | 2 | 5 minutes | `TRANSIENT_FAILURE` |
| `quality_monitoring` | 15 minutes | 1 | 2 minutes | `QUALITY_GATE_BLOCK` |
| `publish` | 10 minutes | 2 | 2 minutes | `OPERATIONAL_FAILURE` |

---

## 5. Pipeline State Tracking

All executions are recorded in PostgreSQL:
- **`analytics.pipeline_runs`**:
  - `run_id` (Primary Key, e.g. `20260902_020000`)
  - `dag_id`, `execution_date`, `start_time`, `end_time`, `status`
  - Records extracted, staged, loaded, and quality score.
- **`analytics.pipeline_task_runs`**:
  - `task_run_key`, `run_id`, `task_name`, `start_time`, `end_time`
  - `rows_processed`, `status`, `error_message`.

---

## 6. Operational Incident Runbook

1. **Airflow Service Inspection**:
   ```powershell
   docker ps --filter "name=healthcare_airflow"
   ```
2. **Task Failure Triage**:
   - Inspect Airflow task logs or query `analytics.pipeline_task_runs`.
   - Distinguish transient connection hiccups (auto-retried) from clinical data quality blocks.
3. **Quality Gate Block Recovery**:
   - Inspect `analytics.quality_check_results` where `status = 'FAIL'`.
   - Address data or schema drift root cause in staging/pipeline.
   - Trigger DAG retry or rerun `scripts/run_quality_monitor.py`.
