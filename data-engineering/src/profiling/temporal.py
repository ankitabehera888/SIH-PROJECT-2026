from typing import List
import pandas as pd
from sqlalchemy import text
from src.database import engine

def check_temporal_integrity(engine_instance=None) -> pd.DataFrame:
    """Evaluates causal chronology and temporal validity across clinical workflows."""
    eng = engine_instance or engine
    
    temporal_checks = [
        (
            "encounters",
            "Encounter End >= Encounter Start",
            "SELECT COUNT(*) FROM encounters WHERE ended_at IS NOT NULL",
            "SELECT COUNT(*) FROM encounters WHERE ended_at IS NOT NULL AND ended_at < started_at",
            "Encounter ended before it started"
        ),
        (
            "appointments",
            "Appointment Date >= Booking Date",
            "SELECT COUNT(*) FROM appointments",
            "SELECT COUNT(*) FROM appointments WHERE appointment_date < created_at::date",
            "Appointment booked in the past relative to creation"
        ),
        (
            "queue_entries",
            "Queue Consultation Start >= Queue Check-in",
            "SELECT COUNT(*) FROM queue_entries WHERE consultation_started_at IS NOT NULL",
            "SELECT COUNT(*) FROM queue_entries WHERE consultation_started_at IS NOT NULL AND consultation_started_at < checked_in_at",
            "Queue consultation started before patient checked in"
        ),
        (
            "queue_entries",
            "Queue Completed >= Queue Started",
            "SELECT COUNT(*) FROM queue_entries WHERE completed_at IS NOT NULL AND consultation_started_at IS NOT NULL",
            "SELECT COUNT(*) FROM queue_entries WHERE completed_at IS NOT NULL AND consultation_started_at IS NOT NULL AND completed_at < consultation_started_at",
            "Queue consultation completed before it started"
        ),
        (
            "consultations",
            "Teleconsultation Room End >= Room Start",
            "SELECT COUNT(*) FROM consultations WHERE actual_end IS NOT NULL AND actual_start IS NOT NULL",
            "SELECT COUNT(*) FROM consultations WHERE actual_end IS NOT NULL AND actual_start IS NOT NULL AND actual_end < actual_start",
            "Teleconsultation room ended before it began"
        ),
        (
            "consents",
            "Consent Valid Until > Valid From",
            "SELECT COUNT(*) FROM consents",
            "SELECT COUNT(*) FROM consents WHERE valid_until <= valid_from",
            "Consent expiration precedes validity start"
        ),
        (
            "diagnostic_results",
            "Lab Verification Time >= Order Time",
            "SELECT COUNT(*) FROM diagnostic_results r JOIN diagnostic_order_items i ON r.diagnostic_order_item_id = i.id JOIN diagnostic_orders o ON i.diagnostic_order_id = o.id WHERE r.verified_at IS NOT NULL",
            "SELECT COUNT(*) FROM diagnostic_results r JOIN diagnostic_order_items i ON r.diagnostic_order_item_id = i.id JOIN diagnostic_orders o ON i.diagnostic_order_id = o.id WHERE r.verified_at IS NOT NULL AND r.verified_at < o.ordered_at",
            "Lab result verified before the doctor ordered the test"
        ),
        (
            "patients",
            "Patient DOB <= Current Date",
            "SELECT COUNT(*) FROM patients",
            "SELECT COUNT(*) FROM patients WHERE date_of_birth > CURRENT_DATE",
            "Patient date of birth in future"
        ),
    ]
    
    records = []
    with eng.connect() as conn:
        for table, rule_name, total_q, viol_q, desc in temporal_checks:
            try:
                total_evaluated = conn.execute(text(total_q)).scalar()
                violations = conn.execute(text(viol_q)).scalar()
                viol_pct = round((violations / total_evaluated * 100) if total_evaluated > 0 else 0.0, 2)
                
                records.append({
                    "Table": table,
                    "Temporal_Rule": rule_name,
                    "Description": desc,
                    "Evaluated_Records": total_evaluated,
                    "Violations_Count": violations,
                    "Violation_Percentage": viol_pct,
                    "Status": "PASS" if violations == 0 else "FAIL",
                })
            except Exception as e:
                records.append({
                    "Table": table,
                    "Temporal_Rule": rule_name,
                    "Description": f"Query Error: {e}",
                    "Evaluated_Records": 0,
                    "Violations_Count": 0,
                    "Violation_Percentage": 0.0,
                    "Status": "ERROR",
                })
                
    df = pd.DataFrame(records)
    return df
