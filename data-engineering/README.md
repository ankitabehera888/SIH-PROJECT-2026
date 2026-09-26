# Healthcare Platform — Data Engineering & Records

This repository module contains the **Data Engineering & Records** pipeline for the Healthcare Platform. It bridges operational PostgreSQL clinical transaction data with analytical datasets, clinical quality metrics, population health cohorts, and administrative dashboards.

---

## 1. Directory Structure

```text
data-engineering/
│
├── README.md                           # Documentation and setup guide
├── requirements.txt                    # Python package dependencies
├── .gitignore                          # Strict data and credential exclusion
├── .env                                # Local credentials (NEVER committed)
│
├── docs/                               # Data contracts and architecture specifications
│   ├── data-architecture.md            # Multi-layer ELT design and ERD
│   ├── data-dictionary.md              # Detailed schema dictionary for all 24 tables
│   ├── data-quality-rules.md           # Business, temporal, and referential rules
│   ├── pii-classification.md           # 4-tier data access and PII/PHI matrix
│   ├── source-of-truth.md              # Domain authoritative source definitions
│   ├── data-gaps.md                    # Gap analysis for targeted healthcare metrics
│   └── phase-0-data-quality-report.md  # Comprehensive quality baseline report
│
├── notebooks/                          # Exploratory analysis and profiling
│   └── 01_database_profiling.ipynb     # Interactive Jupyter profiling notebook
│
├── scripts/                            # Operational CLI utilities
│   ├── test_connection.py              # PostgreSQL connectivity probe
│   ├── inspect_database.py             # Schema and foreign key inspection tool
│   └── profile_tables.py               # Statistical profiling runner
│
├── src/                                # Core data engineering library
│   ├── __init__.py
│   ├── config.py                       # Configuration & environment variables
│   ├── database.py                     # SQLAlchemy read-only engine provider
│   └── profiling/
│       ├── __init__.py
│       └── profiler.py                 # Automated table and column profiler
│
└── tests/                              # Automated test suite
    ├── __init__.py
    ├── test_connection.py              # Connectivity test
    └── test_schema_integrity.py        # Schema & referential integrity test
```

---

## 2. Quickstart & Setup

### Prerequisites
- Python 3.11+
- Docker running `healthcare_postgres` on port `5432`

### Setup Instructions

1. **Activate the Virtual Environment**:
   ```powershell
   cd data-engineering
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify Database Connectivity**:
   ```powershell
   python scripts/test_connection.py
   ```

3. **Run Schema Inspection**:
   ```powershell
   python scripts/inspect_database.py
   ```

4. **Run Data Profiling**:
   ```powershell
   python scripts/profile_tables.py
   ```

5. **Launch Jupyter Profiling Notebook**:
   ```powershell
   jupyter notebook notebooks/01_database_profiling.ipynb
   ```

6. **Execute Automated Tests**:
   ```powershell
   pytest -v tests/
   ```

---

## 3. Data Protection Policy

> [!CAUTION]
> **Strict Patient Privacy Guarantee**:
> - Never commit `.env` or database credentials to version control.
> - Never commit raw patient exports, CSVs, Excel files, or Parquet datasets to Git.
> - Direct identifiers (`first_name`, `last_name`, `phone`, `email`, `address`, `ABHA`) must be tokenized or masked before entering downstream staging or analytical layers.
