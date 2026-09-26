import sys
from pathlib import Path

# Add data-engineering directory to sys.path so 'src' is always importable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
