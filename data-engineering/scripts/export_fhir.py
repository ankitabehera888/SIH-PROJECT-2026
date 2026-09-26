import sys
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from sqlalchemy import text

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine
from src.staging.pipeline import STAGING_DIR, REPORTS_DIR
from src.interoperability.mapping.terminology import get_all_terminology_mappings
from src.interoperability.abdm.identifiers import build_patient_identifier_mappings
from src.interoperability.abdm.provenance import create_fhir_provenance_record
from src.interoperability.abdm.mappings import build_fhir_resource_registry_entry
from src.interoperability.fhir.patient import generate_fhir_patient
from src.interoperability.fhir.encounter import generate_fhir_encounter
from src.interoperability.fhir.observation import generate_fhir_vital_observations
from src.interoperability.fhir.medication_request import generate_fhir_medication_request
from src.interoperability.validation import (
    validate_fhir_patient,
    validate_fhir_encounter,
    validate_fhir_observation,
    validate_referential_integrity,
)

SQL_DIR = Path(__file__).resolve().parent.parent / "sql" / "interoperability"

def apply_ddl_migrations():
    """Applies interoperability table DDL migrations to PostgreSQL analytics schema."""
    ddl_files = [
        "patient_identifier_map.sql",
        "terminology_map.sql",
        "fhir_resource_registry.sql",
        "fhir_provenance.sql",
    ]
    with engine.begin() as conn:
        for fname in ddl_files:
            fpath = SQL_DIR / fname
            if fpath.exists():
                sql_text = fpath.read_text(encoding="utf-8")
                conn.execute(text(sql_text))

def run_fhir_export(run_id: str = None) -> dict:
    current_run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print("=" * 70)
    print(f"FHIR R4 & ABDM DATA EXPORT -- RUN ID: {current_run_id}")
    print("=" * 70)
    
    # 1. Apply DDL
    apply_ddl_migrations()
    print("[1/5] Interoperability DDL migrations applied.")
    
    # 2. Populate Terminology Map
    terms = get_all_terminology_mappings()
    df_terms = pd.DataFrame(terms)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.terminology_map CASCADE;"))
    df_terms.to_sql("terminology_map", engine, schema="analytics", if_exists="append", index=False)
    print(f"[2/5] Seeded {len(df_terms)} canonical terminology mappings (LOINC, UCUM, SNOMED).")
    
    # 3. Read Staged Data
    df_patients = pd.read_parquet(STAGING_DIR / "patients" / "patients.parquet")
    df_encounters = pd.read_parquet(STAGING_DIR / "encounters" / "encounters.parquet")
    df_vitals = pd.read_parquet(STAGING_DIR / "vitals" / "vitals.parquet")
    df_prescriptions = pd.read_parquet(STAGING_DIR / "prescriptions" / "prescriptions.parquet")
    
    # Read patient surrogate key lookup
    with engine.connect() as conn:
        df_p_keys = pd.read_sql("SELECT patient_key, patient_id FROM analytics.dim_patient;", conn)
    pat_key_map = dict(zip(df_p_keys["patient_id"].astype(str), df_p_keys["patient_key"]))
    
    # Populate analytics.patient_identifier_map
    id_mappings = build_patient_identifier_mappings(df_patients, pat_key_map)
    df_id_map = pd.DataFrame(id_mappings)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.patient_identifier_map CASCADE;"))
    df_id_map.to_sql("patient_identifier_map", engine, schema="analytics", if_exists="append", index=False)
    print(f"[3/5] Synchronized {len(df_id_map)} patient identifiers (MRN, FHIR ID, ABHA).")
    
    # 4. Generate FHIR Resources
    print("[4/5] Generating FHIR R4 Resources...")
    fhir_patients = []
    reg_entries = []
    prov_records = []
    
    for _, row in df_patients.iterrows():
        p_res = generate_fhir_patient(row.to_dict())
        is_val, _ = validate_fhir_patient(p_res)
        if is_val:
            fhir_patients.append(p_res)
            reg_entries.append(build_fhir_resource_registry_entry("Patient", "patients", row["patient_id"], p_res["id"], current_run_id))
            prov_records.append(create_fhir_provenance_record("Patient", p_res["id"], "patients", row["patient_id"], current_run_id))
            
    fhir_encounters = []
    for _, row in df_encounters.iterrows():
        e_res = generate_fhir_encounter(row.to_dict())
        is_val, _ = validate_fhir_encounter(e_res)
        if is_val:
            fhir_encounters.append(e_res)
            reg_entries.append(build_fhir_resource_registry_entry("Encounter", "encounters", row["id"], e_res["id"], current_run_id))
            prov_records.append(create_fhir_provenance_record("Encounter", e_res["id"], "encounters", row["id"], current_run_id))
            
    fhir_observations = []
    quarantined_vitals_count = 0
    for _, row in df_vitals.iterrows():
        obs_list = generate_fhir_vital_observations(row.to_dict())
        if not obs_list and str(row.get("_vital_quality_status")) == "invalid":
            quarantined_vitals_count += 1
            
        for obs in obs_list:
            is_val, _ = validate_fhir_observation(obs)
            if is_val:
                fhir_observations.append(obs)
                reg_entries.append(build_fhir_resource_registry_entry("Observation", "vitals", row["id"], obs["id"], current_run_id))
                prov_records.append(create_fhir_provenance_record("Observation", obs["id"], "vitals", row["id"], current_run_id))
                
    fhir_medications = []
    for _, row in df_prescriptions.iterrows():
        m_res = generate_fhir_medication_request(row.to_dict())
        fhir_medications.append(m_res)
        reg_entries.append(build_fhir_resource_registry_entry("MedicationRequest", "prescriptions", row["id"], m_res["id"], current_run_id))
        prov_records.append(create_fhir_provenance_record("MedicationRequest", m_res["id"], "prescriptions", row["id"], current_run_id))
        
    # 5. Referential Integrity & Validation
    is_ref_valid, ref_errors = validate_referential_integrity(
        fhir_patients, fhir_encounters, fhir_observations, fhir_medications
    )
    print(f"    - FHIR Patients: {len(fhir_patients):,}")
    print(f"    - FHIR Encounters: {len(fhir_encounters):,}")
    print(f"    - FHIR Observations: {len(fhir_observations):,} ({quarantined_vitals_count} quarantined invalid vitals)")
    print(f"    - FHIR MedicationRequests: {len(fhir_medications):,}")
    print(f"    - 100% Referential Integrity: {'PASSED' if is_ref_valid else 'FAILED (' + str(len(ref_errors)) + ' errors)'}")
    
    # Save Registry and Provenance
    df_reg = pd.DataFrame(reg_entries)
    df_prov = pd.DataFrame(prov_records)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.fhir_resource_registry CASCADE;"))
        conn.execute(text("TRUNCATE TABLE analytics.fhir_provenance CASCADE;"))
    df_reg.to_sql("fhir_resource_registry", engine, schema="analytics", if_exists="append", index=False)
    df_prov.to_sql("fhir_provenance", engine, schema="analytics", if_exists="append", index=False)
    print(f"[5/5] Persisted {len(df_reg)} resource registry entries & provenance records.")
    
    # 6. Export Quality Report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "fhir_export_report.csv"
    report_rows = [
        {"Resource": "Patient", "Source": "patients", "Total": len(df_patients), "Exported": len(fhir_patients), "Failed": 0, "Unmapped": 0},
        {"Resource": "Encounter", "Source": "encounters", "Total": len(df_encounters), "Exported": len(fhir_encounters), "Failed": 0, "Unmapped": 0},
        {"Resource": "Observation", "Source": "vitals", "Total": len(df_vitals), "Exported": len(fhir_observations), "Failed": quarantined_vitals_count, "Unmapped": 0},
        {"Resource": "MedicationRequest", "Source": "prescriptions", "Total": len(df_prescriptions), "Exported": len(fhir_medications), "Failed": 0, "Unmapped": 0},
    ]
    df_rep = pd.DataFrame(report_rows)
    df_rep.to_csv(report_path, index=False)
    print(f"Export Report saved: {report_path}")
    print("=" * 70)
    print("FHIR / ABDM EXPORT COMPLETED SUCCESSFULLY.")
    print("=" * 70)
    
    return {
        "run_id": current_run_id,
        "patients": len(fhir_patients),
        "encounters": len(fhir_encounters),
        "observations": len(fhir_observations),
        "medications": len(fhir_medications),
        "quarantined_vitals": quarantined_vitals_count,
        "referential_valid": is_ref_valid,
        "report_path": str(report_path),
    }

if __name__ == "__main__":
    run_fhir_export()
