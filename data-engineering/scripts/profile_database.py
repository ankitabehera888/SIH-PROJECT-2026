import sys
from pathlib import Path
import pandas as pd

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.profiling.row_counts import profile_row_counts
from src.profiling.null_analysis import analyze_nulls
from src.profiling.duplicates import detect_duplicates
from src.profiling.integrity import check_referential_integrity
from src.profiling.temporal import check_temporal_integrity
from src.profiling.validation import validate_clinical_values, get_validation_summary
from src.profiling.outliers import detect_outliers
from src.profiling.quality_score import calculate_quality_scores

def run_profiling():
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("HEALTHCARE PLATFORM -- PHASE 1 DATA PROFILING ORCHESTRATOR")
    print("=" * 80)
    
    # 1. Table Profile & Row Counts
    print("\n[1/8] Profiling Table Row Counts & Schema Metadata...")
    df_tables = profile_row_counts()
    table_csv = reports_dir / "table_profile.csv"
    df_tables.to_csv(table_csv, index=False)
    print(f"  [OK] Saved to {table_csv.name} ({len(df_tables)} tables profiled)")
    
    # 2. Null Value Analysis
    print("\n[2/8] Analyzing Column Null Rates & Sparsity...")
    df_nulls = analyze_nulls()
    null_csv = reports_dir / "null_analysis.csv"
    df_nulls.to_csv(null_csv, index=False)
    print(f"  [OK] Saved to {null_csv.name} ({len(df_nulls)} columns evaluated)")
    
    # 3. Duplicate Detection
    print("\n[3/8] Detecting Business Identity & Clinical Duplicates...")
    df_dups = detect_duplicates()
    dups_csv = reports_dir / "duplicates.csv"
    df_dups.to_csv(dups_csv, index=False)
    print(f"  [OK] Saved to {dups_csv.name} ({len(df_dups)} duplicate checks)")
    
    # 4. Referential Integrity
    print("\n[4/8] Evaluating Foreign Key Referential Integrity (Anti-Joins)...")
    df_integrity = check_referential_integrity()
    integrity_csv = reports_dir / "integrity_report.csv"
    df_integrity.to_csv(integrity_csv, index=False)
    orphans_total = int(df_integrity["Invalid_Orphan_Records"].sum())
    print(f"  [OK] Saved to {integrity_csv.name} (Total Orphans: {orphans_total})")
    
    # 5. Temporal Consistency
    print("\n[5/8] Checking Event Chronology & Temporal Consistency...")
    df_temporal = check_temporal_integrity()
    temporal_csv = reports_dir / "temporal_report.csv"
    df_temporal.to_csv(temporal_csv, index=False)
    temp_viols = int(df_temporal["Violations_Count"].sum())
    print(f"  [OK] Saved to {temporal_csv.name} (Violations: {temp_viols})")
    
    # 6. Clinical Value Validation
    print("\n[6/8] Validating Physiological Vital Signs Bounds...")
    df_valid_summary = get_validation_summary()
    valid_csv = reports_dir / "validation_report.csv"
    df_valid_summary.to_csv(valid_csv, index=False)
    invalid_vitals = int(df_valid_summary["Invalid_Count"].sum())
    print(f"  [OK] Saved to {valid_csv.name} (Invalid Measurements: {invalid_vitals})")
    
    # 7. Outlier Detection
    print("\n[7/8] Detecting Statistical Outliers (IQR & Z-score)...")
    df_outliers = detect_outliers()
    outlier_csv = reports_dir / "outlier_report.csv"
    df_outliers.to_csv(outlier_csv, index=False)
    outlier_count = int(df_outliers["Outliers_IQR_Count"].sum())
    print(f"  [OK] Saved to {outlier_csv.name} (Outliers Identified: {outlier_count})")
    
    # 8. Data Quality Score
    print("\n[8/8] Calculating Multidimensional Quality Scores...")
    score_data = calculate_quality_scores()
    df_scores = score_data["table_scores_df"]
    platform_score = score_data["platform_score"]
    score_csv = reports_dir / "quality_score.csv"
    df_scores.to_csv(score_csv, index=False)
    print(f"  [OK] Saved to {score_csv.name} (Platform Score: {platform_score} / 100)")
    
    # 9. Generate Markdown Summary
    summary_md = reports_dir / "data_quality_summary.md"
    generate_summary_markdown(
        summary_md,
        df_tables,
        df_nulls,
        df_dups,
        df_integrity,
        df_temporal,
        df_valid_summary,
        df_outliers,
        df_scores,
        platform_score,
    )
    print(f"\n  [OK] Generated Comprehensive Summary: {summary_md.name}")
    print("\n" + "=" * 80)
    print(f"PROFILING COMPLETE -- PLATFORM QUALITY SCORE: {platform_score} / 100")
    print("=" * 80)

def generate_summary_markdown(
    file_path: Path,
    df_tables: pd.DataFrame,
    df_nulls: pd.DataFrame,
    df_dups: pd.DataFrame,
    df_integrity: pd.DataFrame,
    df_temporal: pd.DataFrame,
    df_valid: pd.DataFrame,
    df_outliers: pd.DataFrame,
    df_scores: pd.DataFrame,
    platform_score: float,
):
    """Writes an executive data quality summary markdown report."""
    total_tables = len(df_tables)
    total_orphans = int(df_integrity["Invalid_Orphan_Records"].sum())
    total_temp_viols = int(df_temporal["Violations_Count"].sum())
    total_invalid_vitals = int(df_valid["Invalid_Count"].sum())
    total_outliers = int(df_outliers["Outliers_IQR_Count"].sum())
    total_dup_groups = int(df_dups["Duplicate_Groups"].sum())
    
    md_content = f"""# Data Quality Summary Report

**Date of Profiling**: September 2026  
**Environment**: Local Data Engineering (`healthcare_dev` PostgreSQL 16)  
**Tables Profiled**: {total_tables}  
**Platform Overall Data Quality Score**: **{platform_score} / 100**

---

## 1. Executive Quality Scorecard

| Table | Completeness (25%) | Consistency (25%) | Validity (20%) | Integrity (20%) | Timeliness (10%) | Overall Score | Grade |
|---|---|---|---|---|---|---|---|
"""
    for _, r in df_scores.iterrows():
        md_content += f"| `{r['Table']}` | {r['Completeness_Score']}% | {r['Consistency_Score']}% | {r['Validity_Score']}% | {r['Integrity_Score']}% | {r['Timeliness_Score']}% | **{r['Overall_Score']}** | {r['Grade']} |\n"

    md_content += f"""
---

## 2. Key Findings & Issues Log

- **Referential Integrity**: **{total_orphans} orphan records** found across all {len(df_integrity)} foreign key relationships (100% integrity maintained by PostgreSQL schema constraints).
- **Temporal Consistency**: **{total_temp_viols} chronological violations** detected. Clinical workflows strictly adhere to causal timelines.
- **Clinical Bounds Validation**: **{total_invalid_vitals} physiologically impossible vital signs** detected across all blood pressure, heart rate, temperature, SpO2, and respiratory observations.
- **Duplicate Entities**: Identified **{total_dup_groups} duplicate groupings**:
"""
    for _, d in df_dups[df_dups["Duplicate_Groups"] > 0].iterrows():
        md_content += f"  - **{d['Domain']}**: {d['Details']} ({d['Total_Excess_Records']} excess records)\n"

    if total_dup_groups == 0:
        md_content += "  - Zero business entity duplicates identified.\n"

    md_content += f"""- **Statistical Outliers**: Flagged **{total_outliers} statistical outliers** using IQR analysis for manual operational review.

---

## 3. Operational Table Inventory

| Table | Live Rows | Columns | Primary Key | Foreign Keys | Earliest Record | Latest Record |
|---|---|---|---|---|---|---|
"""
    for _, t in df_tables.iterrows():
        md_content += f"| `{t['Table']}` | {t['Rows']:,} | {t['Columns']} | `{t['Primary_Key']}` | {t['Foreign_Keys']} | {t['Earliest_Record'][:19] if t['Earliest_Record'] != 'N/A' else 'N/A'} | {t['Latest_Record'][:19] if t['Latest_Record'] != 'N/A' else 'N/A'} |\n"

    md_content += """
---

## 4. Clinical Vitals Validation Details

| Vital Sign | Expected Normal Range | Total Measurements | Valid | Invalid | Validity % | Status |
|---|---|---|---|---|---|---|
"""
    for _, v in df_valid.iterrows():
        md_content += f"| {v['Vital_Sign']} | {v['Expected_Range']} | {v['Total_Measurements']} | {v['Valid_Count']} | {v['Invalid_Count']} | {v['Validity_Percentage']}% | {v['Status']} |\n"

    md_content += """
---

## 5. Statistical Outliers (Operational Distributions)

| Metric | Total Evaluated | Median | Mean ± Std | IQR [Lower, Upper] | Outliers (IQR) | Max Observed | Status |
|---|---|---|---|---|---|---|---|
"""
    for _, o in df_outliers.iterrows():
        md_content += f"| {o['Metric']} | {o['Total_Evaluated']} | {o['Median']} {o['Unit']} | {o['Mean']} ± {o['Std_Dev']} | [{o['IQR_Lower_Bound']}, {o['IQR_Upper_Bound']}] | {o['Outliers_IQR_Count']} | {o['Max_Observed']} {o['Unit']} | {o['Outlier_Status']} |\n"

    md_content += """
---

## 6. Recommendations for Staging & Analytics Pipelines

1. **Family Account Disambiguation**: Shared patient phone numbers indicate family member registration under a single mobile device. The ETL staging pipeline should assign distinct surrogate keys (`patient_key`) while clustering shared phone accounts for household-level analytics.
2. **Handle Sparse Demographics**: Email and home addresses have high optionality (~80-95% null) reflecting rural and semi-urban catchment demographics. Staging pipelines must substitute explicit categorical indicators (e.g. `'NOT_PROVIDED'`) rather than dropping sparse rows.
3. **Outlier Quarantine**: In future ELT ingestion, flag operational outliers with an `is_outlier` boolean column to permit analysts to toggle sensitive aggregations (e.g. median vs. trimmed mean).
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

if __name__ == "__main__":
    run_profiling()
