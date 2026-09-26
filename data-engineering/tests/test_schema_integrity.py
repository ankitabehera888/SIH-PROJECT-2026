from src.profiling.profiler import DatabaseProfiler

REQUIRED_TABLES = [
    "alembic_version",
    "appointments",
    "consents",
    "consultation_participants",
    "consultations",
    "diagnostic_order_items",
    "diagnostic_orders",
    "diagnostic_results",
    "diagnostic_tests",
    "encounters",
    "facilities",
    "interoperability_audits",
    "medications",
    "notification_preferences",
    "notifications",
    "patient_identifiers",
    "patients",
    "prescription_items",
    "prescriptions",
    "queue_entries",
    "referrals",
    "system_checks",
    "users",
    "vitals",
]

def test_all_tables_exist():
    """Verify that all 24 operational tables are present in PostgreSQL."""
    profiler = DatabaseProfiler()
    tables = profiler.get_table_names()
    for req in REQUIRED_TABLES:
        assert req in tables, f"Missing expected operational table: {req}"

def test_table_row_counts_non_empty():
    """Assert that core demographic and clinical tables contain data."""
    profiler = DatabaseProfiler()
    df_counts = profiler.profile_row_counts()
    count_dict = dict(zip(df_counts["table_name"], df_counts["row_count"]))
    
    assert count_dict.get("patients", 0) > 0, "Patients table is empty"
    assert count_dict.get("encounters", 0) > 0, "Encounters table is empty"
    assert count_dict.get("appointments", 0) > 0, "Appointments table is empty"
    assert count_dict.get("vitals", 0) > 0, "Vitals table is empty"

def test_referential_integrity_zero_orphans():
    """Assert zero orphan records across all parent-child relationships."""
    profiler = DatabaseProfiler()
    df_orphans = profiler.check_orphan_records()
    failing = df_orphans[df_orphans["status"] == "FAIL"]
    assert len(failing) == 0, f"Found orphan records in relationships:\n{failing}"
