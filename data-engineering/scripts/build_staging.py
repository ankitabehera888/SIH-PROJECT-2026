import sys
import time
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.staging.pipeline import run_staging_pipeline

def main():
    print("=" * 80)
    print("HEALTHCARE PLATFORM -- STAGING, CLEANING & STANDARDIZATION")
    print("=" * 80)
    print("\nReading RAW Parquet snapshots and building STAGING layer...\n")
    
    start_time = time.time()
    try:
        result = run_staging_pipeline()
        duration = time.time() - start_time
        
        df_rep = result["report_df"]
        print("-" * 80)
        print(f"{'Table':<18} {'Input':<8} {'Output':<8} {'Valid':<8} {'Invalid':<9} {'Duplicates':<12} {'Orphans':<8}")
        print("-" * 80)
        
        for _, r in df_rep.iterrows():
            print(f"{r['Table']:<18} {r['Input_Rows']:<8} {r['Output_Rows']:<8} {r['Valid_Rows']:<8} {r['Invalid_Rows']:<9} {r['Duplicates_Flagged']:<12} {r['Orphans_Flagged']:<8}")
            
        print("-" * 80)
        print(f"\n[OK] Staging completed in {duration:.2f} seconds.")
        print(f"[OK] Quality Report Generated: {result['report_path']}")
        print(f"[OK] Staging Outputs Saved to: data/staging/<table_name>/<table_name>.parquet")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Staging pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
