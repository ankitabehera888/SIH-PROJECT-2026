CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fact_appointment (
    appointment_key BIGSERIAL PRIMARY KEY,
    appointment_id VARCHAR(64) NOT NULL UNIQUE,
    date_key INT REFERENCES analytics.dim_date(date_key),
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    provider_key BIGINT REFERENCES analytics.dim_provider(provider_key),
    facility_key BIGINT REFERENCES analytics.dim_facility(facility_key),
    appointment_status VARCHAR(32) NOT NULL,
    wait_minutes NUMERIC(8, 2),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,
    is_no_show BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_fact_appt_patient ON analytics.fact_appointment(patient_key);
CREATE INDEX IF NOT EXISTS idx_fact_appt_facility ON analytics.fact_appointment(facility_key);
CREATE INDEX IF NOT EXISTS idx_fact_appt_date ON analytics.fact_appointment(date_key);
