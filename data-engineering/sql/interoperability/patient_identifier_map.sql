CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.patient_identifier_map (
    mapping_key BIGSERIAL PRIMARY KEY,
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    internal_patient_id VARCHAR(64) NOT NULL,
    identifier_system VARCHAR(128) NOT NULL, -- e.g. 'https://healthid.abdm.gov.in', 'hospital_mrn', 'fhir_id'
    identifier_value VARCHAR(128) NOT NULL,
    identifier_type VARCHAR(32) NOT NULL,    -- 'ABHA_NUMBER', 'MRN', 'FHIR_ID'
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_pat_id_map_internal ON analytics.patient_identifier_map(internal_patient_id);
CREATE INDEX IF NOT EXISTS idx_pat_id_map_value ON analytics.patient_identifier_map(identifier_system, identifier_value);
