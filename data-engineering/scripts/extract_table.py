import argparse
import sys
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extraction.snapshot import extract_snapshot

def main():
    parser = argparse.ArgumentParser(description="Extract an operational PostgreSQL table to raw Parquet.")
    parser.add_argument("table", nargs="?", default="patients", help="Name of the table to extract (default: patients)")
    parser.add_argument("--date", default=None, help="Snapshot date tag in YYYY-MM-DD format (default: today UTC)")
    args = parser.parse_args()

    table_name = args.table
    print("=" * 80)
    print(f"HEALTHCARE PLATFORM -- RAW EXTRACTION: {table_name}")
    print("=" * 80)
    
    try:
        print(f"\n[1/3] Extracting table '{table_name}' from PostgreSQL...")
        meta = extract_snapshot(table_name=table_name, snapshot_date=args.date)
        
        print(f"[2/3] Writing raw snapshot...")
        print(f"  [OK] Parquet Path: {meta['file_path']}")
        print(f"  [OK] File Size:    {meta['file_size_bytes']:,} bytes")
        print(f"  [OK] Dimensions:   {meta['extracted_row_count']:,} rows x {meta['column_count']} columns")
        
        print(f"[3/3] Reconciliation & Checksum...")
        print(f"  [OK] Reconciliation: Source ({meta['source_row_count']}) == Raw Parquet ({meta['extracted_row_count']}) [{meta['reconciliation_status']}]")
        print(f"  [OK] SHA-256:        {meta['sha256']}")
        print(f"  [OK] Schema Hash:    {meta['schema_hash']}")
        print("\n" + "=" * 80)
        print("EXTRACTION SUCCESSFUL")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
