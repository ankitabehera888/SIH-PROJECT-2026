from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from sqlalchemy import create_engine, text

from src.database import engine as default_engine
from src.analytics.dimensions.date import build_dim_date
from src.analytics.dimensions.patient import build_dim_patient
from src.analytics.dimensions.provider import build_dim_provider
from src.analytics.dimensions.facility import build_dim_facility
from src.analytics.dimensions.geography import build_dim_geography
from src.analytics.facts.appointments import build_fact_appointment
from src.analytics.facts.encounters import build_fact_encounter
from src.analytics.facts.referrals import build_fact_referral
from src.analytics.facts.prescriptions import build_fact_prescription
from src.analytics.facts.vitals import build_fact_vital
from src.staging.pipeline import STAGING_DIR, RAW_DIR

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SQL_DIR = BASE_DIR / "sql"

def run_ddl_scripts(engine_instance=None):
    """Executes all DDL files in sql/dimensions and sql/facts."""
    engine = engine_instance or default_engine
    
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics;"))
        
        # Dimensions DDL
        dim_files = sorted((SQL_DIR / "dimensions").glob("*.sql"))
        for f in dim_files:
            sql = f.read_text(encoding="utf-8")
            conn.execute(text(sql))
            
        # Facts DDL
        fact_files = sorted((SQL_DIR / "facts").glob("*.sql"))
        for f in fact_files:
            sql = f.read_text(encoding="utf-8")
            conn.execute(text(sql))

def build_analytics_model(engine_instance=None) -> Dict:
    """
    Orchestrates the creation and population of the Analytics Star Schema in PostgreSQL.
    Populates 5 Dimension tables and 5 Fact tables from standardized staging data.
    """
    engine = engine_instance or default_engine
    
    # 1. Execute DDL migrations
    run_ddl_scripts(engine)
    
    # 2. Read Staging Parquet files
    df_staged_patients = pd.read_parquet(STAGING_DIR / "patients" / "patients.parquet")
    df_staged_appointments = pd.read_parquet(STAGING_DIR / "appointments" / "appointments.parquet")
    df_staged_encounters = pd.read_parquet(STAGING_DIR / "encounters" / "encounters.parquet")
    df_staged_vitals = pd.read_parquet(STAGING_DIR / "vitals" / "vitals.parquet")
    df_staged_prescriptions = pd.read_parquet(STAGING_DIR / "prescriptions" / "prescriptions.parquet")
    df_staged_referrals = pd.read_parquet(STAGING_DIR / "referrals" / "referrals.parquet")
    df_staged_facilities = pd.read_parquet(STAGING_DIR / "facilities" / "facilities.parquet")
    
    # Read raw users and prescription items if available
    users_raw_file = sorted((RAW_DIR / "users").glob("snapshot_*.parquet"))
    df_raw_users = pd.read_parquet(users_raw_file[-1]) if users_raw_file else pd.DataFrame()
    
    rx_items_raw = sorted((RAW_DIR / "prescription_items").glob("snapshot_*.parquet"))
    df_raw_rx_items = pd.read_parquet(rx_items_raw[-1]) if rx_items_raw else None
    
    # 3. Build and Populate Dimensions
    # dim_date
    df_dim_date = build_dim_date(2020, 2030)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.dim_date CASCADE;"))
    df_dim_date.to_sql("dim_date", engine, schema="analytics", if_exists="append", index=False)
    
    # dim_patient
    df_dim_patient = build_dim_patient(df_staged_patients)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.dim_patient CASCADE;"))
    df_dim_patient.to_sql("dim_patient", engine, schema="analytics", if_exists="append", index=False)
    
    # dim_provider
    df_dim_provider = build_dim_provider(df_raw_users)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.dim_provider CASCADE;"))
    df_dim_provider.to_sql("dim_provider", engine, schema="analytics", if_exists="append", index=False)
    
    # dim_facility
    df_dim_facility = build_dim_facility(df_staged_facilities)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.dim_facility CASCADE;"))
    df_dim_facility.to_sql("dim_facility", engine, schema="analytics", if_exists="append", index=False)
    
    # dim_geography
    df_dim_geography = build_dim_geography()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.dim_geography CASCADE;"))
    df_dim_geography.to_sql("dim_geography", engine, schema="analytics", if_exists="append", index=False)
    
    # 4. Fetch Surrogate Key Lookups
    with engine.connect() as conn:
        df_p_keys = pd.read_sql("SELECT patient_key, patient_id FROM analytics.dim_patient;", conn)
        df_f_keys = pd.read_sql("SELECT facility_key, facility_id FROM analytics.dim_facility;", conn)
        df_pr_keys = pd.read_sql("SELECT provider_key, provider_id FROM analytics.dim_provider;", conn)
        df_d_keys = pd.read_sql("SELECT date_key, CAST(full_date AS TEXT) as dt FROM analytics.dim_date;", conn)
        
    patient_map = dict(zip(df_p_keys["patient_id"].astype(str), df_p_keys["patient_key"]))
    facility_map = dict(zip(df_f_keys["facility_id"].astype(str), df_f_keys["facility_key"]))
    provider_map = dict(zip(df_pr_keys["provider_id"].astype(int), df_pr_keys["provider_key"]))
    date_map = dict(zip(df_d_keys["dt"].astype(str), df_d_keys["date_key"]))
    
    # 5. Build and Populate Fact Tables
    # Clean fact tables first
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE analytics.fact_prescription CASCADE;"))
        conn.execute(text("TRUNCATE TABLE analytics.fact_vital CASCADE;"))
        conn.execute(text("TRUNCATE TABLE analytics.fact_encounter CASCADE;"))
        conn.execute(text("TRUNCATE TABLE analytics.fact_appointment CASCADE;"))
        conn.execute(text("TRUNCATE TABLE analytics.fact_referral CASCADE;"))
        
    # fact_appointment
    df_fact_appt = build_fact_appointment(
        df_staged_appointments, patient_map, facility_map, provider_map, date_map
    )
    df_fact_appt.to_sql("fact_appointment", engine, schema="analytics", if_exists="append", index=False)
    
    # fact_encounter
    df_fact_enc = build_fact_encounter(
        df_staged_encounters, patient_map, facility_map, provider_map, date_map,
        df_vitals=df_staged_vitals, df_prescriptions=df_staged_prescriptions
    )
    df_fact_enc.to_sql("fact_encounter", engine, schema="analytics", if_exists="append", index=False)
    
    # Fetch encounter surrogate keys
    with engine.connect() as conn:
        df_enc_keys = pd.read_sql("SELECT encounter_key, encounter_id FROM analytics.fact_encounter;", conn)
    encounter_map = dict(zip(df_enc_keys["encounter_id"].astype(str), df_enc_keys["encounter_key"]))
    
    # fact_referral
    df_fact_ref = build_fact_referral(
        df_staged_referrals, patient_map, facility_map, date_map
    )
    df_fact_ref.to_sql("fact_referral", engine, schema="analytics", if_exists="append", index=False)
    
    # fact_prescription
    df_fact_rx = build_fact_prescription(
        df_staged_prescriptions, df_raw_rx_items, patient_map, encounter_map, date_map
    )
    df_fact_rx.to_sql("fact_prescription", engine, schema="analytics", if_exists="append", index=False)
    
    # fact_vital
    df_fact_vit = build_fact_vital(
        df_staged_vitals, patient_map, encounter_map, date_map
    )
    df_fact_vit.to_sql("fact_vital", engine, schema="analytics", if_exists="append", index=False)
    
    # 6. Return Table Volumes
    summary = {
        "dim_date": len(df_dim_date),
        "dim_patient": len(df_dim_patient),
        "dim_provider": len(df_dim_provider),
        "dim_facility": len(df_dim_facility),
        "dim_geography": len(df_dim_geography),
        "fact_appointment": len(df_fact_appt),
        "fact_encounter": len(df_fact_enc),
        "fact_referral": len(df_fact_ref),
        "fact_prescription": len(df_fact_rx),
        "fact_vital": len(df_fact_vit),
    }
    return summary
