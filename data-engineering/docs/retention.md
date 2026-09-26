# Data Lifecycle & Retention Policy

## 1. Storage Tiers & Retention Durations

| Layer | Storage Media | Retention Duration | Disposal Policy |
|---|---|---|---|
| **`RAW` (Snapshots)** | Parquet in Object Storage (S3) | 90 days | Automated lifecycle transition to Glacier |
| **`STAGING`** | PostgreSQL Temporary Schema | 14 days | Truncated / Vacuumed post-ETL |
| **`ANALYTICS`** | PostgreSQL Dimensional Model | Permanent / 10+ Years | Retained for longitudinal clinical reporting |
| **`METRICS` & `COHORTS`**| PostgreSQL Analytical Tables | Permanent | Versioned tracking with run lineage |
| **Application Logs** | Container stdout / Logstash | 30 days | Rotated and archived |
| **Database Backups** | Encrypted S3 Bucket | 30d daily, 12w weekly, 7y monthly | Automated deletion of expired dumps |
