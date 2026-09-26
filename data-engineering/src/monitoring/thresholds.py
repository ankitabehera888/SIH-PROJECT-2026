from pathlib import Path
from typing import Dict, List
import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "configs" / "monitoring_rules.yaml"

def load_monitoring_rules() -> List[Dict]:
    """Loads and parses declarative quality monitoring rules from YAML config."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Monitoring configuration not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])
