from typing import Dict, List, Optional
import pandas as pd
from src.database import engine
from src.profiling.null_analysis import analyze_nulls
from src.profiling.duplicates import detect_duplicates
from src.profiling.integrity import check_referential_integrity
from src.profiling.temporal import check_temporal_integrity
from src.profiling.validation import get_validation_summary

WEIGHTS = {
    "completeness": 0.25,
    "consistency": 0.25,
    "validity": 0.20,
    "integrity": 0.20,
    "timeliness": 0.10,
}

CORE_CLINICAL_TABLES = [
    "patients",
    "appointments",
    "encounters",
    "vitals",
    "prescriptions",
    "prescription_items",
    "diagnostic_orders",
    "diagnostic_results",
    "referrals",
    "consultations",
    "queue_entries",
    "facilities",
]

def calculate_quality_scores(engine_instance=None) -> Dict:
    """Calculates multidimensional data quality scores for operational tables and the entire platform."""
    eng = engine_instance or engine
    
    # 1. Run underlying profiling engines
    df_nulls = analyze_nulls(tables=CORE_CLINICAL_TABLES, engine_instance=eng)
    df_dups = detect_duplicates(engine_instance=eng)
    df_integrity = check_referential_integrity(engine_instance=eng)
    df_temporal = check_temporal_integrity(engine_instance=eng)
    df_valid = get_validation_summary(engine_instance=eng)
    
    table_scores = []
    
    # Precompute global integrity & duplicate deductions
    total_orphans = int(df_integrity["Invalid_Orphan_Records"].sum())
    total_dups = int(df_dups["Total_Excess_Records"].sum())
    
    for tbl in CORE_CLINICAL_TABLES:
        # Completeness (25%): Based on mandatory and critical null violations
        tbl_nulls = df_nulls[df_nulls["Table"] == tbl]
        if not tbl_nulls.empty:
            crit_violations = len(tbl_nulls[tbl_nulls["Status"].isin(["CRITICAL_PK_NULL", "MANDATORY_VIOLATION"])])
            avg_null_pct = float(tbl_nulls["Null_Percentage"].mean())
            completeness_score = max(0.0, 100.0 - (crit_violations * 25.0) - (avg_null_pct * 0.2))
        else:
            completeness_score = 100.0
            
        # Consistency (25%): Deduct if duplicate business keys exist in this domain
        dom_dups = df_dups[df_dups["Domain"].str.lower() == tbl.lower()]
        dup_excess = int(dom_dups["Total_Excess_Records"].sum()) if not dom_dups.empty else 0
        consistency_score = max(50.0, 100.0 - (dup_excess * 1.5))
        
        # Validity (20%): Vital bounds check for vitals table; 100% baseline for others
        if tbl == "vitals" and not df_valid.empty:
            avg_validity = float(df_valid["Validity_Percentage"].mean())
            validity_score = avg_validity
        else:
            validity_score = 100.0
            
        # Integrity (20%): Anti-join check for this table
        tbl_orphans = df_integrity[df_integrity["Child_Table"] == tbl]
        tbl_orphan_cnt = int(tbl_orphans["Invalid_Orphan_Records"].sum()) if not tbl_orphans.empty else 0
        integrity_score = 100.0 if tbl_orphan_cnt == 0 else max(0.0, 100.0 - (tbl_orphan_cnt * 10.0))
        
        # Timeliness / Temporal (10%): Check temporal violations
        tbl_temporal = df_temporal[df_temporal["Table"] == tbl]
        temp_viols = int(tbl_temporal["Violations_Count"].sum()) if not tbl_temporal.empty else 0
        timeliness_score = 100.0 if temp_viols == 0 else max(0.0, 100.0 - (temp_viols * 5.0))
        
        # Composite Weighted Score
        overall = (
            completeness_score * WEIGHTS["completeness"]
            + consistency_score * WEIGHTS["consistency"]
            + validity_score * WEIGHTS["validity"]
            + integrity_score * WEIGHTS["integrity"]
            + timeliness_score * WEIGHTS["timeliness"]
        )
        overall = round(overall, 1)
        
        # Letter Grade Assignment
        if overall >= 90:
            grade = "A (Excellent)"
        elif overall >= 80:
            grade = "B (Good)"
        elif overall >= 70:
            grade = "C (Acceptable)"
        else:
            grade = "D (Action Required)"
            
        table_scores.append({
            "Table": tbl,
            "Completeness_Score": round(completeness_score, 1),
            "Consistency_Score": round(consistency_score, 1),
            "Validity_Score": round(validity_score, 1),
            "Integrity_Score": round(integrity_score, 1),
            "Timeliness_Score": round(timeliness_score, 1),
            "Overall_Score": overall,
            "Grade": grade,
        })
        
    df_scores = pd.DataFrame(table_scores).sort_values(by="Overall_Score", ascending=False).reset_index(drop=True)
    platform_score = round(float(df_scores["Overall_Score"].mean()), 1)
    
    return {
        "platform_score": platform_score,
        "table_scores_df": df_scores,
        "weights": WEIGHTS,
    }
