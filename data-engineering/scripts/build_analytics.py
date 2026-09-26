import sys
import time
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analytics.builder import build_analytics_model

def main():
    print("=" * 80)
    print("HEALTHCARE PLATFORM -- DIMENSIONAL / ANALYTICAL DATA MODEL")
    print("=" * 80)
    print("\nExecuting DDL and populating Star Schema in PostgreSQL 'analytics' schema...\n")
    
    start_time = time.time()
    try:
        summary = build_analytics_model()
        duration = time.time() - start_time
        
        print("-" * 80)
        print(f"{'Analytical Table':<30} {'Type':<15} {'Rows Populated':<15}")
        print("-" * 80)
        
        for tbl, count in summary.items():
            t_type = "DIMENSION" if tbl.startswith("dim_") else "FACT"
            print(f"{tbl:<30} {t_type:<15} {count:<15,}")
            
        print("-" * 80)
        print(f"\n[OK] Analytics Star Schema built in {duration:.2f} seconds.")
        print("[OK] Target Schema: PostgreSQL 'analytics.*'")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Analytics build failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
