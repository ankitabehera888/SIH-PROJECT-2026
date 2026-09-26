CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fhir_provenance (
    provenance_key BIGSERIAL PRIMARY KEY,
    resource_type VARCHAR(64) NOT NULL,
    fhir_resource_id VARCHAR(128) NOT NULL,
    source_table VARCHAR(64) NOT NULL,
    source_record_id VARCHAR(64) NOT NULL,
    pipeline_run_id VARCHAR(64) NOT NULL,
    mapping_version VARCHAR(32) DEFAULT '1.0',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_prov_resource ON analytics.fhir_provenance(fhir_resource_id);
CREATE INDEX IF NOT EXISTS idx_fhir_prov_run ON analytics.fhir_provenance(pipeline_run_id);
