import sys
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.profiling.profiler import DatabaseProfiler

def main():
    print("=" * 80)
    print("HEALTHCARE PLATFORM — DATA PROFILING & QUALITY REPORT")
    print("=" * 80)
    
    profiler = DatabaseProfiler()
    
    print("\n1. Operational Table Row Counts:")
    print("-" * 50)
    df_counts = profiler.profile_row_counts()
    print(df_counts.to_string(index=False))
    
    print("\n\n2. Clinical Event Date Ranges:")
    print("-" * 80)
    df_dates = profiler.profile_date_ranges()
    print(df_dates.to_string(index=False))
    
    print("\n\n3. Referential Integrity (Orphan Record Check):")
    print("-" * 80)
    df_orphans = profiler.check_orphan_records()
    print(df_orphans.to_string(index=False))
    
    print("\n\n4. Column Profiling Sample (Patients Table):")
    print("-" * 80)
    df_patients = profiler.profile_table_columns("patients")
    print(df_patients.to_string(index=False))

    print("\n\n5. Column Profiling Sample (Encounters Table):")
    print("-" * 80)
    df_encounters = profiler.profile_table_columns("encounters")
    print(df_encounters.to_string(index=False))

    print("\n\n6. Column Profiling Sample (Vitals Table):")
    print("-" * 80)
    df_vitals = profiler.profile_table_columns("vitals")
    print(df_vitals.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("Profiling Complete.")

if __name__ == "__main__":
    main()
