CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fact_encounter (
    encounter_key BIGSERIAL PRIMARY KEY,
    encounter_id VARCHAR(64) NOT NULL UNIQUE,
    date_key INT REFERENCES analytics.dim_date(date_key),
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    provider_key BIGINT REFERENCES analytics.dim_provider(provider_key),
    facility_key BIGINT REFERENCES analytics.dim_facility(facility_key),
    encounter_type VARCHAR(32) NOT NULL DEFAULT 'outpatient',
    encounter_status VARCHAR(32) NOT NULL,
    duration_minutes NUMERIC(8, 2),
    diagnosis_count INT DEFAULT 0,
    prescription_count INT DEFAULT 0,
    has_vitals BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_fact_enc_patient ON analytics.fact_encounter(patient_key);
CREATE INDEX IF NOT EXISTS idx_fact_enc_provider ON analytics.fact_encounter(provider_key);
CREATE INDEX IF NOT EXISTS idx_fact_enc_facility ON analytics.fact_encounter(facility_key);
CREATE INDEX IF NOT EXISTS idx_fact_enc_date ON analytics.fact_encounter(date_key);
