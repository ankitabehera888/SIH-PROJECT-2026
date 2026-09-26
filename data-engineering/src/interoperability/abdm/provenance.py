from datetime import datetime, timezone
from typing import Dict, List

def create_fhir_provenance_record(
    resource_type: str,
    fhir_resource_id: str,
    source_table: str,
    source_record_id: str,
    pipeline_run_id: str,
    mapping_version: str = "1.0"
) -> Dict:
    """Constructs a provenance audit record for an exported FHIR resource."""
    return {
        "resource_type": resource_type,
        "fhir_resource_id": fhir_resource_id,
        "source_table": source_table,
        "source_record_id": str(source_record_id),
        "pipeline_run_id": str(pipeline_run_id),
        "mapping_version": mapping_version,
        "generated_at": datetime.now(timezone.utc),
    }
