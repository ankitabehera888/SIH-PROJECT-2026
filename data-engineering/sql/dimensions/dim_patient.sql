CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_patient (
    patient_key BIGSERIAL PRIMARY KEY,
    patient_id VARCHAR(64) NOT NULL,        -- Business UUID
    source_patient_id VARCHAR(64),          -- Facility Patient Number
    abha_id VARCHAR(64),                    -- National ABDM Identifier
    gender VARCHAR(16) NOT NULL,
    date_of_birth DATE,
    age_band VARCHAR(20),                   -- e.g. "0-5", "6-17", "18-35", "36-60", "60+"
    blood_group VARCHAR(10),
    district VARCHAR(64),
    state VARCHAR(64),
    source_system VARCHAR(32) DEFAULT 'healthcare_dev',
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP WITH TIME ZONE,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_dim_patient_id ON analytics.dim_patient(patient_id);
CREATE INDEX IF NOT EXISTS idx_dim_patient_is_current ON analytics.dim_patient(is_current);
