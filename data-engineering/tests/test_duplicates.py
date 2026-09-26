from src.profiling.duplicates import detect_duplicates

def test_duplicate_detection_runs():
    """Assert that duplicate detection evaluates all major clinical domains."""
    df_dups = detect_duplicates()
    assert not df_dups.empty
    domains = df_dups["Domain"].unique().tolist()
    assert "Patients" in domains
    assert "Appointments" in domains
    assert "Prescriptions" in domains
    assert "Diagnostics" in domains

def test_no_double_booked_appointments():
    """Assert that no active appointments share the same patient, provider, and time slot."""
    df_dups = detect_duplicates()
    appt_dup = df_dups[df_dups["Check_Type"] == "Double-Booked Appointment Slot"].iloc[0]
    assert appt_dup["Duplicate_Groups"] == 0, f"Found double-booked appointments: {appt_dup}"

def test_no_duplicate_prescription_items():
    """Assert that no prescription has duplicate medication order items."""
    df_dups = detect_duplicates()
    rx_dup = df_dups[df_dups["Check_Type"] == "Duplicate Medication in Same Prescription"].iloc[0]
    assert rx_dup["Duplicate_Groups"] == 0, f"Found duplicate prescription items: {rx_dup}"
