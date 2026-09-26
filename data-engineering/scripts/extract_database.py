import argparse
import sys
import time
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extraction.snapshot import extract_all_snapshots

def main():
    parser = argparse.ArgumentParser(description="Extract all operational PostgreSQL tables into the RAW data layer.")
    parser.add_argument("--date", default=None, help="Snapshot date in YYYY-MM-DD format (default: today UTC)")
    args = parser.parse_args()

    print("=" * 80)
    print("HEALTHCARE PLATFORM -- COMPLETE DATABASE EXTRACTION (RAW LAYER)")
    print("=" * 80)
    print("\nExtracting database tables to immutable Parquet snapshots...\n")
    
    start_time = time.time()
    result = extract_all_snapshots(snapshot_date=args.date)
    duration = time.time() - start_time
    
    print("-" * 80)
    print(f"{'Table':<30} {'Rows':<12} {'Size (KB)':<12} {'Status':<15} {'Reconciliation'}")
    print("-" * 80)
    
    for meta in result["successful_tables"]:
        size_kb = round(meta["file_size_bytes"] / 1024.0, 1)
        print(f"{meta['source_table']:<30} {meta['extracted_row_count']:<12,} {size_kb:<12} [OK] {meta['status']:<10} {meta['reconciliation_status']}")
        
    for fail in result["failed_tables"]:
        print(f"{fail['table']:<30} {'N/A':<12} {'N/A':<12} [FAIL] {fail['error'][:25]}")
        
    print("-" * 80)
    print(f"\nExtraction completed in {duration:.2f} seconds.")
    print(f"Total Tables Processed: {result['successful_count']} / {result['total_attempted']}")
    print(f"Manifest Generated at:  {result['manifest_path']}")
    print("=" * 80)
    
    if result["failed_count"] > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
