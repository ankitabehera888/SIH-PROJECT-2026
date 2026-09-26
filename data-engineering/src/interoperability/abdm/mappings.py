from datetime import datetime, timezone
from typing import Dict, List

def build_fhir_resource_registry_entry(
    resource_type: str,
    internal_entity_type: str,
    internal_entity_id: str,
    fhir_resource_id: str,
    pipeline_run_id: str,
    version: int = 1
) -> Dict:
    """Builds an entry for analytics.fhir_resource_registry."""
    return {
        "resource_type": resource_type,
        "internal_entity_type": internal_entity_type,
        "internal_entity_id": str(internal_entity_id),
        "fhir_resource_id": fhir_resource_id,
        "version": version,
        "status": "active",
        "generated_at": datetime.now(timezone.utc),
        "pipeline_run_id": str(pipeline_run_id),
    }
