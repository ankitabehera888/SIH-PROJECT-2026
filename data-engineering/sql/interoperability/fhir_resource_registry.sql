CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fhir_resource_registry (
    resource_key BIGSERIAL PRIMARY KEY,
    resource_type VARCHAR(64) NOT NULL,      -- 'Patient', 'Encounter', 'Observation', 'MedicationRequest'
    internal_entity_type VARCHAR(64) NOT NULL,
    internal_entity_id VARCHAR(64) NOT NULL,
    fhir_resource_id VARCHAR(128) NOT NULL UNIQUE,
    version INT DEFAULT 1,
    status VARCHAR(32) DEFAULT 'active',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id VARCHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fhir_reg_internal ON analytics.fhir_resource_registry(internal_entity_type, internal_entity_id);
CREATE INDEX IF NOT EXISTS idx_fhir_reg_resource_id ON analytics.fhir_resource_registry(fhir_resource_id);
