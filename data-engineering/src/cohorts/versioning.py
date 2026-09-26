from datetime import datetime, timezone
from typing import Dict

def get_cohort_lineage_metadata(cohort_name: str, cohort_version: str, run_id: str) -> Dict:
    """Constructs lineage metadata for a cohort generation execution."""
    return {
        "cohort_name": cohort_name,
        "cohort_version": cohort_version,
        "pipeline_run_id": str(run_id),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_data_layer": "analytics_star_schema",
    }
