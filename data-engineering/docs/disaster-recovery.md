# Disaster Recovery Runbook & Procedure

## 1. Scenario Playbooks

### Scenario A: Primary PostgreSQL Failure / Corruption
1. **Detect**: Health monitor fires alert `PostgreSQL Unreachable`.
2. **Contain**: Halt Airflow pipelines and FastAPI writes (switch API to read-only maintenance mode).
3. **Recover**:
   - Locate latest verified backup in `infrastructure/postgres/backup/` with valid `.sha256`.
   - Execute `powershell -File scripts/restore_database.ps1 -BackupFilePath <path>`.
4. **Validate**:
   - Verify table counts match previous extraction manifests.
   - Run `python scripts/run_quality_monitor.py` to confirm 0 critical failures.
5. **Resume**: Restart FastAPI and Airflow schedulers.

### Scenario B: Airflow Scheduler Crash
1. PostgreSQL data remains completely intact.
2. Restart container: `powershell -File scripts/start_airflow.ps1`.
3. Airflow scheduler auto-recovers from `airflow_db` DAG run states.

### Scenario C: Redis Failure
1. Redis contains ephemeral response caches only; zero authoritative healthcare data is stored in Redis.
2. Restart Redis; FastAPI gracefully falls back to PostgreSQL until cache warm-up completes.
