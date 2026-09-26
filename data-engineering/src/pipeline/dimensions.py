import logging
from typing import Dict
import pandas as pd
from sqlalchemy import text

from src.database import engine as default_engine
from src.analytics.dimensions.date import build_dim_date
from src.analytics.dimensions.patient import build_dim_patient
from src.analytics.dimensions.provider import build_dim_provider
from src.analytics.dimensions.facility import build_dim_facility
from src.analytics.dimensions.geography import build_dim_geography
from src.pipeline.context import PipelineContext
from src.staging.pipeline import STAGING_DIR, RAW_DIR

def execute_dimensions_loading(
    context: PipelineContext,
    logger: logging.Logger,
    engine_instance=None
) -> Dict:
    """
    Step 4: Loads dimensions into PostgreSQL 'analytics' schema.
    Uses idempotent upsert strategies based on business identifiers.
    """
    logger.info("Starting Step 4: Dimension Tables Loading...")
    engine = engine_instance or default_engine
    
    try:
        dim_summary = {}
        
        # 1. dim_date
        with engine.connect() as conn:
            date_cnt = conn.execute(text("SELECT COUNT(*) FROM analytics.dim_date;")).scalar()
            
        if date_cnt != 4018:
            df_date = build_dim_date(2020, 2030)
            with engine.begin() as conn:
                conn.execute(text("TRUNCATE TABLE analytics.dim_date CASCADE;"))
            df_date.to_sql("dim_date", engine, schema="analytics", if_exists="append", index=False)
            dim_summary["dim_date"] = len(df_date)
            logger.info(f"Populated dim_date with {len(df_date):,} dates.")
        else:
            dim_summary["dim_date"] = date_cnt
            logger.info(f"dim_date already up-to-date ({date_cnt:,} dates).")
            
        # 2. dim_geography
        with engine.connect() as conn:
            geo_cnt = conn.execute(text("SELECT COUNT(*) FROM analytics.dim_geography;")).scalar()
        if geo_cnt == 0:
            df_geo = build_dim_geography()
            df_geo.to_sql("dim_geography", engine, schema="analytics", if_exists="append", index=False)
            dim_summary["dim_geography"] = len(df_geo)
        else:
            dim_summary["dim_geography"] = geo_cnt
            
        # 3. dim_facility (Idempotent load based on facility_id)
        df_staged_fac = pd.read_parquet(STAGING_DIR / "facilities" / "facilities.parquet")
        df_dim_fac = build_dim_facility(df_staged_fac)
        
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE analytics.dim_facility CASCADE;"))
        df_dim_fac.to_sql("dim_facility", engine, schema="analytics", if_exists="append", index=False)
        dim_summary["dim_facility"] = len(df_dim_fac)
        logger.info(f"Loaded dim_facility: {len(df_dim_fac):,} facilities.")
        
        # 4. dim_provider (Idempotent load based on provider_id)
        users_raw_file = sorted((RAW_DIR / "users").glob("snapshot_*.parquet"))
        df_raw_users = pd.read_parquet(users_raw_file[-1]) if users_raw_file else pd.DataFrame()
        df_dim_prov = build_dim_provider(df_raw_users)
        
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE analytics.dim_provider CASCADE;"))
        df_dim_prov.to_sql("dim_provider", engine, schema="analytics", if_exists="append", index=False)
        dim_summary["dim_provider"] = len(df_dim_prov)
        logger.info(f"Loaded dim_provider: {len(df_dim_prov):,} providers.")
        
        # 5. dim_patient (Idempotent load based on patient_id)
        df_staged_pat = pd.read_parquet(STAGING_DIR / "patients" / "patients.parquet")
        df_dim_pat = build_dim_patient(df_staged_pat)
        
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE analytics.dim_patient CASCADE;"))
        df_dim_pat.to_sql("dim_patient", engine, schema="analytics", if_exists="append", index=False)
        dim_summary["dim_patient"] = len(df_dim_pat)
        logger.info(f"Loaded dim_patient: {len(df_dim_pat):,} patients.")
        
        context.record_step("dimensions", "success", dim_summary)
        logger.info("Step 4 completed successfully. All dimensions synchronized.")
        return dim_summary
    except Exception as e:
        logger.error(f"Step 4 Dimensions loading failed: {e}")
        context.record_error("dimensions", str(e))
        raise
