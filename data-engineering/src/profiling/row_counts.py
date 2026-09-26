from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import inspect, text
from src.database import engine

def profile_row_counts(engine_instance=None) -> pd.DataFrame:
    """Collects row count, column count, PK, FK count, and temporal bounds for all tables."""
    eng = engine_instance or engine
    inspector = inspect(eng)
    table_names = sorted(inspector.get_table_names(schema="public"))
    
    date_columns = {
        "appointments": "appointment_date",
        "encounters": "started_at",
        "vitals": "recorded_at",
        "prescriptions": "prescribed_at",
        "diagnostic_orders": "ordered_at",
        "referrals": "created_at",
        "consultations": "created_at",
        "notifications": "created_at",
        "patients": "created_at",
        "users": "created_at",
        "facilities": "created_at",
        "queue_entries": "created_at",
    }
    
    results = []
    with eng.connect() as conn:
        for table in table_names:
            columns = inspector.get_columns(table, schema="public")
            pk_constraint = inspector.get_pk_constraint(table, schema="public")
            pks = pk_constraint.get("constrained_columns", [])
            fks = inspector.get_foreign_keys(table, schema="public")
            
            # Row count
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            
            # Earliest & Latest records
            earliest, latest = "N/A", "N/A"
            date_col = date_columns.get(table)
            if date_col and any(c["name"] == date_col for c in columns):
                try:
                    res = conn.execute(text(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table}")).fetchone()
                    if res and res[0] is not None:
                        earliest = str(res[0])
                        latest = str(res[1])
                except Exception:
                    pass
            elif any(c["name"] == "created_at" for c in columns):
                try:
                    res = conn.execute(text(f"SELECT MIN(created_at), MAX(created_at) FROM {table}")).fetchone()
                    if res and res[0] is not None:
                        earliest = str(res[0])
                        latest = str(res[1])
                except Exception:
                    pass
            
            results.append({
                "Table": table,
                "Rows": row_count,
                "Columns": len(columns),
                "Primary_Key": ", ".join(pks) if pks else "None",
                "Foreign_Keys": len(fks),
                "Earliest_Record": earliest,
                "Latest_Record": latest,
            })
            
    df = pd.DataFrame(results).sort_values(by="Rows", ascending=False).reset_index(drop=True)
    return df
