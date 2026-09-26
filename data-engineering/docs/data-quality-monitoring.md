# Continuous Data Quality Monitoring & Alerting Specification

## 1. Executive Summary
Phase 10 turns the manual data profiling and verification framework from Phase 1 into a continuous, automated production monitoring system governing data health across operational, staging, and analytical schemas.

---

## 2. Quality Monitoring Architecture

```text
                 DATA PIPELINES
                       │
                       ▼
              QUALITY CHECKS
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
     Completeness  Integrity    Freshness
          │            │            │
          └────────────┼────────────┘
                       ↓
                QUALITY ENGINE
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       quality_results       quality_alerts
             │                   │
             └─────────┬─────────┘
                       ↓
                  QUALITY GATE
                       │
              ┌────────┴────────┐
              ↓                 ↓
            PASS             FAILURE
              ↓                 ↓
         Publish KPI       Block/Alert
```

---

## 3. Core Monitoring Dimensions

| Check Type | Purpose | Frequency | Severity |
|---|---|---|---|
| **`COMPLETENESS`** | Detects null spikes in surrogate and business keys | Per Pipeline Run | `CRITICAL` |
| **`INTEGRITY`** | Enforces zero orphan foreign keys across dimensional facts | Per Pipeline Run | `CRITICAL` |
| **`DUPLICATE`** | Detects duplicate natural keys in dimensions and facts | Per Pipeline Run | `CRITICAL` |
| **`FRESHNESS`** | Measures ingestion latency in hours against operational tables | Hourly / Batch | `WARNING` |
| **`VOLUME`** | Detects abnormal drops or unexpected row-count fluctuations | Per Pipeline Run | `WARNING` / `CRITICAL` |
| **`VALIDITY`** | Validates biometric physiological bounds (heart rate, BP, SpO2) | Per Pipeline Run | `WARNING` |
| **`SCHEMA`** | Detects schema drift (added/removed columns, type changes) | Per Pipeline Run | `CRITICAL` |
| **`ANOMALY`** | Detects out-of-bounds KPI rates ($< 0$ or $> 1$) and durations | Post-KPI Run | `WARNING` |

---

## 4. Severity & Health Scoring Model

### 4.1 Scoring Formula
$$\text{Quality Score} = \left( \frac{\text{Passed Checks}}{\text{Total Checks}} \right) \times 100$$

### 4.2 Critical Failure Override
Even if the numeric score is $98\%$, any `CRITICAL` failure (e.g. orphan records or schema drift) **immediately overrides** the platform status to:
$$\text{Platform Status} = \mathbf{CRITICAL} \quad \Longrightarrow \quad \text{Quality Gate} = \mathbf{BLOCKED}$$

### 4.3 Health Statuses
- **`HEALTHY`**: 0 Critical failures, 0 Warnings, Score $\ge 98\%$.
- **`WARNING`**: 0 Critical failures, 1–2 Warnings.
- **`DEGRADED`**: 0 Critical failures, $> 2$ Warnings.
- **`CRITICAL`**: $\ge 1$ Critical failures. Downstream publication is blocked.

---

## 5. Alert Lifecycle & Deduplication
- **Lifecycle**: `OPEN` $\longrightarrow$ `ACKNOWLEDGED` $\longrightarrow$ `RESOLVED`.
- **Deduplication**: If a check fails on consecutive pipeline runs, the existing `OPEN` alert is updated rather than creating duplicate alerts.
- **Auto-Resolution**: When a failing check returns to `PASS` on subsequent runs, the alert status is automatically updated to `RESOLVED` with `resolved_at = CURRENT_TIMESTAMP`.

---

## 6. Operational Incident Runbook

When an alert with `CRITICAL` severity triggers:
1. **Immediate Action**: Quality Gate blocks downstream KPI and analytical publication.
2. **Diagnosis**: Review `reports/quality_monitoring_summary.csv` and `analytics.quality_check_results` to inspect observed vs expected values.
3. **Traceability**: Identify whether the error originated in raw ingestion, staging standardization, or fact extraction.
4. **Correction**: Fix the pipeline code or source mapping. Re-run staging and ETL stages.
5. **Validation**: Execute `python scripts/run_quality_monitor.py`. Verify check passes and alert transitions to `RESOLVED`.
