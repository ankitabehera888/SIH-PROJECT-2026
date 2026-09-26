import sys
from pathlib import Path

# Add data-engineering root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.runner import run_pipeline

def main():
    ctx = run_pipeline()
    if ctx.status == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
