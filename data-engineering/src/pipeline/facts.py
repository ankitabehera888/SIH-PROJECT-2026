import logging
from typing import Dict
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.analytics.facts.appointments import build_fact_appointment
from src.analytics.facts.encounters import build_fact_encounter
from src.analytics.facts.referrals import build_fact_referral
from src.analytics.facts.prescriptions import build_fact_prescription
from src.analytics.facts.vitals import build_fact_vital
from src.pipeline.context import PipelineContext
from src.staging.pipeline import STAGING_DIR, RAW_DIR

def execute_facts_loading(
    context: PipelineContext,
    logger: logging.Logger,
    engine_instance=None
) -> Dict:
    """
    Step 5: Loads fact tables into PostgreSQL 'analytics' schema.
    Guarantees idempotency on business keys (appointment_id, encounter_id, referral_id, etc.).
    """
    logger.info("Starting Step 5: Fact Tables Loading...")
    engine = engine_instance or default_engine
    
    try:
        # 1. Fetch surrogate key lookup maps from active dimensions
        with engine.connect() as conn:
            df_p = pd.read_sql("SELECT patient_key, patient_id FROM analytics.dim_patient;", conn)
            df_f = pd.read_sql("SELECT facility_key, facility_id FROM analytics.dim_facility;", conn)
            df_pr = pd.read_sql("SELECT provider_key, provider_id FROM analytics.dim_provider;", conn)
            df_d = pd.read_sql("SELECT date_key, CAST(full_date AS TEXT) as dt FROM analytics.dim_date;", conn)
            
        patient_map = dict(zip(df_p["patient_id"].astype(str), df_p["patient_key"]))
        facility_map = dict(zip(df_f["facility_id"].astype(str), df_f["facility_key"]))
        provider_map = dict(zip(df_pr["provider_id"].astype(int), df_pr["provider_key"]))
        date_map = dict(zip(df_d["dt"].astype(str), df_d["date_key"]))
        
        # 2. Read staged data
        df_staged_appts = pd.read_parquet(STAGING_DIR / "appointments" / "appointments.parquet")
        df_staged_encs = pd.read_parquet(STAGING_DIR / "encounters" / "encounters.parquet")
        df_staged_refs = pd.read_parquet(STAGING_DIR / "referrals" / "referrals.parquet")
        df_staged_vits = pd.read_parquet(STAGING_DIR / "vitals" / "vitals.parquet")
        df_staged_rxs = pd.read_parquet(STAGING_DIR / "prescriptions" / "prescriptions.parquet")
        
        rx_items_raw = sorted((RAW_DIR / "prescription_items").glob("snapshot_*.parquet"))
        df_raw_rx_items = pd.read_parquet(rx_items_raw[-1]) if rx_items_raw else None
        
        # 3. Clean and Populate Facts Idempotently
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE analytics.fact_prescription CASCADE;"))
            conn.execute(text("TRUNCATE TABLE analytics.fact_vital CASCADE;"))
            conn.execute(text("TRUNCATE TABLE analytics.fact_encounter CASCADE;"))
            conn.execute(text("TRUNCATE TABLE analytics.fact_appointment CASCADE;"))
            conn.execute(text("TRUNCATE TABLE analytics.fact_referral CASCADE;"))
            
        # fact_appointment
        df_fact_appt = build_fact_appointment(df_staged_appts, patient_map, facility_map, provider_map, date_map)
        df_fact_appt.to_sql("fact_appointment", engine, schema="analytics", if_exists="append", index=False)
        logger.info(f"Loaded fact_appointment: {len(df_fact_appt):,} rows.")
        
        # fact_encounter
        df_fact_enc = build_fact_encounter(
            df_staged_encs, patient_map, facility_map, provider_map, date_map,
            df_vitals=df_staged_vits, df_prescriptions=df_staged_rxs
        )
        df_fact_enc.to_sql("fact_encounter", engine, schema="analytics", if_exists="append", index=False)
        logger.info(f"Loaded fact_encounter: {len(df_fact_enc):,} rows.")
        
        # Fetch encounter surrogate keys
        with engine.connect() as conn:
            df_enc_keys = pd.read_sql("SELECT encounter_key, encounter_id FROM analytics.fact_encounter;", conn)
        encounter_map = dict(zip(df_enc_keys["encounter_id"].astype(str), df_enc_keys["encounter_key"]))
        
        # fact_referral
        df_fact_ref = build_fact_referral(df_staged_refs, patient_map, facility_map, date_map)
        df_fact_ref.to_sql("fact_referral", engine, schema="analytics", if_exists="append", index=False)
        logger.info(f"Loaded fact_referral: {len(df_fact_ref):,} rows.")
        
        # fact_prescription
        df_fact_rx = build_fact_prescription(df_staged_rxs, df_raw_rx_items, patient_map, encounter_map, date_map)
        df_fact_rx.to_sql("fact_prescription", engine, schema="analytics", if_exists="append", index=False)
        logger.info(f"Loaded fact_prescription: {len(df_fact_rx):,} rows.")
        
        # fact_vital
        df_fact_vit = build_fact_vital(df_staged_vits, patient_map, encounter_map, date_map)
        df_fact_vit.to_sql("fact_vital", engine, schema="analytics", if_exists="append", index=False)
        logger.info(f"Loaded fact_vital: {len(df_fact_vit):,} rows.")
        
        fact_summary = {
            "fact_appointment": len(df_fact_appt),
            "fact_encounter": len(df_fact_enc),
            "fact_referral": len(df_fact_ref),
            "fact_prescription": len(df_fact_rx),
            "fact_vital": len(df_fact_vit),
        }
        context.record_step("facts", "success", fact_summary)
        logger.info("Step 5 completed successfully. All facts loaded.")
        return fact_summary
    except Exception as e:
        logger.error(f"Step 5 Facts loading failed: {e}")
        context.record_error("facts", str(e))
        raise
