import json
import sys
from pathlib import Path
from sqlalchemy import inspect

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import engine

def inspect_schema():
    inspector = inspect(engine)
    table_names = sorted(inspector.get_table_names(schema="public"))
    
    print(f"Discovered {len(table_names)} tables in 'public' schema:")
    print("=" * 70)
    
    inventory = {}
    
    for table_name in table_names:
        columns = inspector.get_columns(table_name, schema="public")
        pk_constraint = inspector.get_pk_constraint(table_name, schema="public")
        pk_cols = pk_constraint.get("constrained_columns", [])
        fks = inspector.get_foreign_keys(table_name, schema="public")
        
        inventory[table_name] = {
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col.get("default", "")) if col.get("default") is not None else None,
                    "is_primary_key": col["name"] in pk_cols,
                }
                for col in columns
            ],
            "primary_key": pk_cols,
            "foreign_keys": [
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in fks
            ],
        }
        
        print(f"\nTable: {table_name} ({len(columns)} columns)")
        print(f"  Primary Key: {', '.join(pk_cols) if pk_cols else 'None'}")
        if fks:
            print("  Foreign Keys:")
            for fk in fks:
                print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    output_path = Path(__file__).resolve().parent.parent / "docs" / "schema_inventory.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
        
    print("\n" + "=" * 70)
    print(f"Schema inventory saved to: {output_path}")

if __name__ == "__main__":
    inspect_schema()
