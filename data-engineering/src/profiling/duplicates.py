from typing import List, Optional
import pandas as pd
from sqlalchemy import text
from src.database import engine

def detect_duplicates(engine_instance=None) -> pd.DataFrame:
    """Detects duplicate business keys and potential identity overlaps."""
    eng = engine_instance or engine
    results = []
    
    with eng.connect() as conn:
        # 1. Patient Identifiers: System + Value duplicates
        q_pi = text("""
            SELECT system, value, COUNT(*) as cnt
            FROM patient_identifiers
            WHERE value IS NOT NULL AND value != ''
            GROUP BY system, value
            HAVING COUNT(*) > 1
        """)
        pi_dups = conn.execute(q_pi).fetchall()
        results.append({
            "Domain": "Patients",
            "Check_Type": "National / ABHA Identifier Duplicate",
            "Duplicate_Groups": len(pi_dups),
            "Total_Excess_Records": sum(r[2] - 1 for r in pi_dups),
            "Details": f"{len(pi_dups)} duplicate ABHA/national ID values found",
            "Severity": "HIGH" if len(pi_dups) > 0 else "NONE",
        })
        
        # 2. Patient Phone Duplicates
        q_phone = text("""
            SELECT phone, COUNT(*) as cnt
            FROM patients
            WHERE phone IS NOT NULL AND phone != ''
            GROUP BY phone
            HAVING COUNT(*) > 1
        """)
        phone_dups = conn.execute(q_phone).fetchall()
        results.append({
            "Domain": "Patients",
            "Check_Type": "Duplicate Phone Numbers",
            "Duplicate_Groups": len(phone_dups),
            "Total_Excess_Records": sum(r[1] - 1 for r in phone_dups),
            "Details": f"{len(phone_dups)} phone numbers shared across multiple patient records (e.g. family accounts)",
            "Severity": "MEDIUM" if len(phone_dups) > 0 else "NONE",
        })
        
        # 3. Patient Email Duplicates
        q_email = text("""
            SELECT email, COUNT(*) as cnt
            FROM patients
            WHERE email IS NOT NULL AND email != ''
            GROUP BY email
            HAVING COUNT(*) > 1
        """)
        email_dups = conn.execute(q_email).fetchall()
        results.append({
            "Domain": "Patients",
            "Check_Type": "Duplicate Email Addresses",
            "Duplicate_Groups": len(email_dups),
            "Total_Excess_Records": sum(r[1] - 1 for r in email_dups),
            "Details": f"{len(email_dups)} email addresses shared across multiple patient records",
            "Severity": "LOW" if len(email_dups) > 0 else "NONE",
        })
        
        # 4. Appointment Schedule Overlap
        q_appt = text("""
            SELECT patient_id, provider_id, appointment_date, start_time, COUNT(*) as cnt
            FROM appointments
            WHERE status != 'CANCELLED'
            GROUP BY patient_id, provider_id, appointment_date, start_time
            HAVING COUNT(*) > 1
        """)
        appt_dups = conn.execute(q_appt).fetchall()
        results.append({
            "Domain": "Appointments",
            "Check_Type": "Double-Booked Appointment Slot",
            "Duplicate_Groups": len(appt_dups),
            "Total_Excess_Records": sum(r[4] - 1 for r in appt_dups),
            "Details": f"{len(appt_dups)} double-booked appointment slots for same patient, provider and time",
            "Severity": "HIGH" if len(appt_dups) > 0 else "NONE",
        })
        
        # 5. Duplicate Medication in Same Prescription
        q_rx = text("""
            SELECT prescription_id, medication_id, COUNT(*) as cnt
            FROM prescription_items
            GROUP BY prescription_id, medication_id
            HAVING COUNT(*) > 1
        """)
        rx_dups = conn.execute(q_rx).fetchall()
        results.append({
            "Domain": "Prescriptions",
            "Check_Type": "Duplicate Medication in Same Prescription",
            "Duplicate_Groups": len(rx_dups),
            "Total_Excess_Records": sum(r[2] - 1 for r in rx_dups),
            "Details": f"{len(rx_dups)} prescriptions containing duplicate lines for the same drug",
            "Severity": "MEDIUM" if len(rx_dups) > 0 else "NONE",
        })
        
        # 6. Duplicate Diagnostic Test in Same Order
        q_diag = text("""
            SELECT diagnostic_order_id, diagnostic_test_id, COUNT(*) as cnt
            FROM diagnostic_order_items
            GROUP BY diagnostic_order_id, diagnostic_test_id
            HAVING COUNT(*) > 1
        """)
        diag_dups = conn.execute(q_diag).fetchall()
        results.append({
            "Domain": "Diagnostics",
            "Check_Type": "Duplicate Test in Same Diagnostic Order",
            "Duplicate_Groups": len(diag_dups),
            "Total_Excess_Records": sum(r[2] - 1 for r in diag_dups),
            "Details": f"{len(diag_dups)} orders containing duplicate test line items",
            "Severity": "MEDIUM" if len(diag_dups) > 0 else "NONE",
        })

    df = pd.DataFrame(results)
    return df
