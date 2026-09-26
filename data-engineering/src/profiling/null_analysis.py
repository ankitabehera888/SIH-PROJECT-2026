from typing import List, Optional
import pandas as pd
from sqlalchemy import inspect
from src.database import engine

def analyze_nulls(tables: Optional[List[str]] = None, engine_instance=None) -> pd.DataFrame:
    """Calculates column-level null counts, null percentages, and data quality classification."""
    eng = engine_instance or engine
    inspector = inspect(eng)
    all_tables = sorted(inspector.get_table_names(schema="public"))
    target_tables = [t for t in all_tables if t in tables] if tables else all_tables
    
    rows = []
    for table_name in target_tables:
        columns_meta = {c["name"]: c for c in inspector.get_columns(table_name, schema="public")}
        pk_meta = inspector.get_pk_constraint(table_name, schema="public").get("constrained_columns", [])
        
        df_table = pd.read_sql_table(table_name, con=eng)
        total_rows = len(df_table)
        
        for col_name in df_table.columns:
            null_count = int(df_table[col_name].isna().sum())
            null_pct = round((null_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
            is_nullable = columns_meta[col_name]["nullable"] if col_name in columns_meta else True
            is_pk = col_name in pk_meta
            
            # Data quality status classification
            if is_pk and null_count > 0:
                status = "CRITICAL_PK_NULL"
            elif not is_nullable and null_count > 0:
                status = "MANDATORY_VIOLATION"
            elif null_pct == 0.0:
                status = "COMPLETE"
            elif null_pct > 80.0:
                status = "SPARSE_OPTIONAL"
            else:
                status = "NORMAL_OPTIONAL"
                
            rows.append({
                "Table": table_name,
                "Column": col_name,
                "Data_Type": str(df_table[col_name].dtype),
                "Nullable_In_Schema": is_nullable,
                "Is_Primary_Key": is_pk,
                "Null_Count": null_count,
                "Total_Rows": total_rows,
                "Null_Percentage": null_pct,
                "Status": status,
            })
            
    df = pd.DataFrame(rows).sort_values(by=["Table", "Null_Percentage"], ascending=[True, False]).reset_index(drop=True)
    return df
