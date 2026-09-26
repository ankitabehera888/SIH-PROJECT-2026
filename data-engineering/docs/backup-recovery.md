# Backup & Recovery Policy

## 1. Objectives & Targets
- **Recovery Point Objective (RPO)**: $\le 15\text{ minutes}$.
- **Recovery Time Objective (RTO)**: $\le 60\text{ minutes}$.

---

## 2. Backup Schedule & Automation
- **Daily Full Logical Backup**: Executed via `scripts/backup_database.ps1` at 01:00 UTC.
- **Cryptographic Verification**: Every backup produces a SHA-256 hash stored alongside the dump file in `.sha256`.
- **Integrity Validation**: Automated restore test via `scripts/restore_database.ps1` restoring to an isolated database (`healthcare_restore_test`) and matching row counts.

---

## 3. Retention Policy
- **Daily Backups**: Retained for 30 days.
- **Weekly Backups**: Retained for 12 weeks.
- **Monthly Backups**: Retained for 7 years (compliance / legal requirement).
