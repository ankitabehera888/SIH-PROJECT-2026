from src.interoperability.abdm.provenance import create_fhir_provenance_record

def test_create_fhir_provenance_record():
    """Verify provenance record contains lineage metadata, pipeline run ID, and timestamps."""
    record = create_fhir_provenance_record(
        resource_type="Observation",
        fhir_resource_id="obs-1234",
        source_table="vitals",
        source_record_id="vit-5678",
        pipeline_run_id="20260902_033000",
        mapping_version="1.0"
    )
    
    assert record["resource_type"] == "Observation"
    assert record["fhir_resource_id"] == "obs-1234"
    assert record["source_table"] == "vitals"
    assert record["source_record_id"] == "vit-5678"
    assert record["pipeline_run_id"] == "20260902_033000"
    assert record["mapping_version"] == "1.0"
    assert record["generated_at"] is not None
