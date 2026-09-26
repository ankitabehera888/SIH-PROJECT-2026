CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fact_vital (
    vital_key BIGSERIAL PRIMARY KEY,
    vital_id VARCHAR(64) NOT NULL UNIQUE,
    date_key INT REFERENCES analytics.dim_date(date_key),
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    encounter_key BIGINT REFERENCES analytics.fact_encounter(encounter_key),
    systolic_bp NUMERIC(6, 1),
    diastolic_bp NUMERIC(6, 1),
    heart_rate NUMERIC(6, 1),
    temperature NUMERIC(6, 2),
    spo2 NUMERIC(5, 2),
    respiratory_rate NUMERIC(5, 1),
    quality_status VARCHAR(32) NOT NULL DEFAULT 'valid'
);

CREATE INDEX IF NOT EXISTS idx_fact_vital_patient ON analytics.fact_vital(patient_key);
CREATE INDEX IF NOT EXISTS idx_fact_vital_encounter ON analytics.fact_vital(encounter_key);
CREATE INDEX IF NOT EXISTS idx_fact_vital_date ON analytics.fact_vital(date_key);
