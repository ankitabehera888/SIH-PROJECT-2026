from typing import List, Tuple
import pandas as pd
from sqlalchemy import text
from src.database import engine

def check_referential_integrity(engine_instance=None) -> pd.DataFrame:
    """Validates referential integrity across all operational foreign keys."""
    eng = engine_instance or engine
    
    relationships: List[Tuple[str, str, str, str, str]] = [
        ("vitals -> encounters", "vitals", "encounter_id", "encounters", "id"),
        ("vitals -> patients", "vitals", "patient_id", "patients", "id"),
        ("encounters -> patients", "encounters", "patient_id", "patients", "id"),
        ("encounters -> facilities", "encounters", "facility_id", "facilities", "id"),
        ("encounters -> appointments", "encounters", "appointment_id", "appointments", "id"),
        ("appointments -> patients", "appointments", "patient_id", "patients", "id"),
        ("appointments -> facilities", "appointments", "facility_id", "facilities", "id"),
        ("prescriptions -> encounters", "prescriptions", "encounter_id", "encounters", "id"),
        ("prescriptions -> patients", "prescriptions", "patient_id", "patients", "id"),
        ("prescription_items -> prescriptions", "prescription_items", "prescription_id", "prescriptions", "id"),
        ("prescription_items -> medications", "prescription_items", "medication_id", "medications", "id"),
        ("diagnostic_orders -> encounters", "diagnostic_orders", "encounter_id", "encounters", "id"),
        ("diagnostic_orders -> patients", "diagnostic_orders", "patient_id", "patients", "id"),
        ("diagnostic_order_items -> diagnostic_orders", "diagnostic_order_items", "diagnostic_order_id", "diagnostic_orders", "id"),
        ("diagnostic_order_items -> diagnostic_tests", "diagnostic_order_items", "diagnostic_test_id", "diagnostic_tests", "id"),
        ("diagnostic_results -> diagnostic_order_items", "diagnostic_results", "diagnostic_order_item_id", "diagnostic_order_items", "id"),
        ("referrals -> encounters", "referrals", "encounter_id", "encounters", "id"),
        ("referrals -> patients", "referrals", "patient_id", "patients", "id"),
        ("consultations -> appointments", "consultations", "appointment_id", "appointments", "id"),
        ("consultation_participants -> consultations", "consultation_participants", "consultation_id", "consultations", "id"),
        ("queue_entries -> appointments", "queue_entries", "appointment_id", "appointments", "id"),
        ("patient_identifiers -> patients", "patient_identifiers", "patient_id", "patients", "id"),
        ("consents -> patients", "consents", "patient_id", "patients", "id"),
        ("notifications -> patients", "notifications", "patient_id", "patients", "id"),
    ]
    
    records = []
    with eng.connect() as conn:
        for rel_name, child_tbl, fk_col, parent_tbl, pk_col in relationships:
            total_child = conn.execute(text(f"SELECT COUNT(*) FROM {child_tbl}")).scalar()
            
            # Anti-join query
            query = text(f"""
                SELECT COUNT(*) 
                FROM {child_tbl} c 
                LEFT JOIN {parent_tbl} p ON c.{fk_col} = p.{pk_col}
                WHERE c.{fk_col} IS NOT NULL AND p.{pk_col} IS NULL
            """)
            orphan_count = conn.execute(query).scalar()
            
            records.append({
                "Relationship": rel_name,
                "Child_Table": child_tbl,
                "Foreign_Key": fk_col,
                "Parent_Table": parent_tbl,
                "Total_Child_Records": total_child,
                "Invalid_Orphan_Records": orphan_count,
                "Status": "PASS" if orphan_count == 0 else "FAIL",
            })
            
    df = pd.DataFrame(records)
    return df
