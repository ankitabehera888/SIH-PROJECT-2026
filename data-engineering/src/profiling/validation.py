from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import text
from src.database import engine

# Clinical physiological threshold bounds
CLINICAL_BOUNDS = {
    "systolic_bp": {"min": 60, "max": 260, "unit": "mmHg", "label": "Systolic Blood Pressure"},
    "diastolic_bp": {"min": 30, "max": 180, "unit": "mmHg", "label": "Diastolic Blood Pressure"},
    "heart_rate": {"min": 25, "max": 240, "unit": "bpm", "label": "Heart Rate"},
    "temperature": {"min": 30.0, "max": 45.0, "unit": "°C", "label": "Body Temperature"},
    "spo2": {"min": 50.0, "max": 100.0, "unit": "%", "label": "Oxygen Saturation"},
    "respiratory_rate": {"min": 6, "max": 60, "unit": "breaths/min", "label": "Respiratory Rate"},
}

def validate_clinical_values(engine_instance=None) -> pd.DataFrame:
    """Validates physiological vitals against established medical plausibility thresholds."""
    eng = engine_instance or engine
    violations = []
    
    with eng.connect() as conn:
        # 1. Check each physiological boundary
        for field, bound in CLINICAL_BOUNDS.items():
            query = text(f"""
                SELECT id, patient_id, encounter_id, {field}, recorded_at
                FROM vitals
                WHERE {field} IS NOT NULL 
                  AND ({field} < :min_val OR {field} > :max_val)
            """)
            rows = conn.execute(query, {"min_val": bound["min"], "max_val": bound["max"]}).fetchall()
            for r in rows:
                violations.append({
                    "Record_ID": str(r[0]),
                    "Patient_ID": str(r[1]),
                    "Encounter_ID": str(r[2]),
                    "Metric": bound["label"],
                    "Field": field,
                    "Value": float(r[3]),
                    "Unit": bound["unit"],
                    "Expected_Range": f"{bound['min']} - {bound['max']} {bound['unit']}",
                    "Recorded_At": str(r[4]),
                    "Validation_Status": "INVALID",
                    "Severity": "CRITICAL"
                })
                
        # 2. Check systolic > diastolic condition
        bp_logic_q = text("""
            SELECT id, patient_id, encounter_id, systolic_bp, diastolic_bp, recorded_at
            FROM vitals
            WHERE systolic_bp IS NOT NULL AND diastolic_bp IS NOT NULL
              AND systolic_bp <= diastolic_bp
        """)
        bp_rows = conn.execute(bp_logic_q).fetchall()
        for r in bp_rows:
            violations.append({
                "Record_ID": str(r[0]),
                "Patient_ID": str(r[1]),
                "Encounter_ID": str(r[2]),
                "Metric": "Blood Pressure Ratio",
                "Field": "systolic_vs_diastolic",
                "Value": f"Sys: {r[3]}, Dia: {r[4]}",
                "Unit": "mmHg",
                "Expected_Range": "Systolic > Diastolic",
                "Recorded_At": str(r[5]),
                "Validation_Status": "INVALID",
                "Severity": "CRITICAL"
            })
            
    if not violations:
        # Return empty structured dataframe
        return pd.DataFrame(columns=[
            "Record_ID", "Patient_ID", "Encounter_ID", "Metric", "Field",
            "Value", "Unit", "Expected_Range", "Recorded_At", "Validation_Status", "Severity"
        ])
        
    df = pd.DataFrame(violations)
    return df

def get_validation_summary(engine_instance=None) -> pd.DataFrame:
    """Provides an aggregated summary of valid vs. invalid measurements per vital type."""
    eng = engine_instance or engine
    summary_list = []
    
    with eng.connect() as conn:
        for field, bound in CLINICAL_BOUNDS.items():
            tot_q = text(f"SELECT COUNT(*) FROM vitals WHERE {field} IS NOT NULL")
            inv_q = text(f"""
                SELECT COUNT(*) FROM vitals 
                WHERE {field} IS NOT NULL AND ({field} < :min_val OR {field} > :max_val)
            """)
            
            total = conn.execute(tot_q).scalar()
            invalid = conn.execute(inv_q, {"min_val": bound["min"], "max_val": bound["max"]}).scalar()
            valid = total - invalid
            valid_pct = round((valid / total * 100) if total > 0 else 100.0, 2)
            
            summary_list.append({
                "Vital_Sign": bound["label"],
                "Expected_Range": f"{bound['min']} - {bound['max']} {bound['unit']}",
                "Total_Measurements": total,
                "Valid_Count": valid,
                "Invalid_Count": invalid,
                "Validity_Percentage": valid_pct,
                "Status": "PASS" if invalid == 0 else "FAIL",
            })
            
    return pd.DataFrame(summary_list)
