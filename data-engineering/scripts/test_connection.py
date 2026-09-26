import sys
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import test_db_connection

def main():
    print("Testing PostgreSQL connectivity for Data Engineering...")
    try:
        info = test_db_connection()
        print("\nDatabase connection successful!")
        print("-" * 50)
        print(f"Database: {info['database']}")
        print(f"User:     {info['user']}")
        print(f"Version:  {info['version']}")
        print("-" * 50)
        sys.exit(0)
    except Exception as e:
        print(f"\nDatabase connection failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
