CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fact_prescription (
    prescription_key BIGSERIAL PRIMARY KEY,
    prescription_item_id VARCHAR(64) NOT NULL UNIQUE,
    prescription_id VARCHAR(64) NOT NULL,
    date_key INT REFERENCES analytics.dim_date(date_key),
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    encounter_key BIGINT REFERENCES analytics.fact_encounter(encounter_key),
    medication_id VARCHAR(64),
    quantity NUMERIC(8, 2) DEFAULT 1,
    duration_days INT DEFAULT 5,
    prescription_status VARCHAR(32) NOT NULL DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_fact_rx_patient ON analytics.fact_prescription(patient_key);
CREATE INDEX IF NOT EXISTS idx_fact_rx_encounter ON analytics.fact_prescription(encounter_key);
CREATE INDEX IF NOT EXISTS idx_fact_rx_date ON analytics.fact_prescription(date_key);
