from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import inspect, text
from src.database import engine

class DatabaseProfiler:
    """Performs deep data profiling and statistical quality assessment on the operational database."""

    def __init__(self):
        self.engine = engine
        self.inspector = inspect(self.engine)

    def get_table_names(self) -> List[str]:
        """Return all tables in the public schema."""
        return sorted(self.inspector.get_table_names(schema="public"))

    def profile_row_counts(self) -> pd.DataFrame:
        """Calculate exact row counts across all operational tables."""
        tables = self.get_table_names()
        results = []
        with self.engine.connect() as conn:
            for table in tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                results.append({"table_name": table, "row_count": count})
        df = pd.DataFrame(results).sort_values(by="row_count", ascending=False).reset_index(drop=True)
        return df

    def profile_table_columns(self, table_name: str) -> pd.DataFrame:
        """Calculate column-level statistics: data type, null count, null percentage, unique values."""
        df_table = pd.read_sql_table(table_name, con=self.engine)
        total_rows = len(df_table)
        col_profiles = []

        for col in df_table.columns:
            null_count = int(df_table[col].isna().sum())
            null_pct = round((null_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
            unique_count = int(df_table[col].nunique(dropna=True))
            dtype = str(df_table[col].dtype)

            col_profiles.append({
                "column_name": col,
                "data_type": dtype,
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_count": unique_count,
            })

        return pd.DataFrame(col_profiles)

    def profile_date_ranges(self) -> pd.DataFrame:
        """Find minimum and maximum dates across major clinical event tables."""
        date_queries = {
            "appointments": "appointment_date",
            "encounters": "started_at",
            "vitals": "recorded_at",
            "prescriptions": "prescribed_at",
            "diagnostic_orders": "ordered_at",
            "referrals": "created_at",
            "consultations": "created_at",
            "notifications": "created_at",
        }
        records = []
        with self.engine.connect() as conn:
            for table, col in date_queries.items():
                try:
                    res = conn.execute(text(f"SELECT MIN({col}), MAX({col}) FROM {table}")).fetchone()
                    records.append({
                        "table_name": table,
                        "date_column": col,
                        "min_date": str(res[0]) if res[0] is not None else "N/A",
                        "max_date": str(res[1]) if res[1] is not None else "N/A",
                    })
                except Exception as e:
                    records.append({
                        "table_name": table,
                        "date_column": col,
                        "min_date": "Error",
                        "max_date": str(e),
                    })
        return pd.DataFrame(records)

    def check_orphan_records(self) -> pd.DataFrame:
        """Inspect referential integrity for orphan records."""
        checks = [
            ("vitals", "encounter_id", "encounters", "id"),
            ("encounters", "patient_id", "patients", "id"),
            ("appointments", "patient_id", "patients", "id"),
            ("prescriptions", "encounter_id", "encounters", "id"),
            ("prescription_items", "prescription_id", "prescriptions", "id"),
            ("diagnostic_orders", "encounter_id", "encounters", "id"),
            ("diagnostic_order_items", "diagnostic_order_id", "diagnostic_orders", "id"),
            ("diagnostic_results", "diagnostic_order_item_id", "diagnostic_order_items", "id"),
            ("referrals", "encounter_id", "encounters", "id"),
            ("consultations", "appointment_id", "appointments", "id"),
            ("consultation_participants", "consultation_id", "consultations", "id"),
            ("queue_entries", "appointment_id", "appointments", "id"),
            ("patient_identifiers", "patient_id", "patients", "id"),
            ("consents", "patient_id", "patients", "id"),
        ]
        results = []
        with self.engine.connect() as conn:
            for child_table, child_col, parent_table, parent_col in checks:
                query = text(f"""
                    SELECT COUNT(*) 
                    FROM {child_table} c 
                    LEFT JOIN {parent_table} p ON c.{child_col} = p.{parent_col}
                    WHERE c.{child_col} IS NOT NULL AND p.{parent_col} IS NULL
                """)
                orphan_count = conn.execute(query).scalar()
                results.append({
                    "child_table": child_table,
                    "foreign_key": child_col,
                    "parent_table": parent_table,
                    "orphan_count": orphan_count,
                    "status": "PASS" if orphan_count == 0 else "FAIL",
                })
        return pd.DataFrame(results)
