from datetime import datetime, timezone
from typing import Dict

DEFAULT_METRIC_VERSION = "1.0.0"

def get_metric_lineage_metadata(metric_code: str, run_id: str, version: str = DEFAULT_METRIC_VERSION) -> Dict:
    """Builds audit lineage metadata for a metric calculation run."""
    return {
        "metric_code": metric_code,
        "calculation_version": version,
        "pipeline_run_id": str(run_id),
        "calculated_at": datetime.now(timezone.utc).isoformat(),
    }
