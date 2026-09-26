CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.fact_referral (
    referral_key BIGSERIAL PRIMARY KEY,
    referral_id VARCHAR(64) NOT NULL UNIQUE,
    created_date_key INT REFERENCES analytics.dim_date(date_key),
    completed_date_key INT REFERENCES analytics.dim_date(date_key),
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key),
    referring_facility_key BIGINT REFERENCES analytics.dim_facility(facility_key),
    receiving_facility_key BIGINT REFERENCES analytics.dim_facility(facility_key),
    referral_status VARCHAR(32) NOT NULL,
    priority VARCHAR(16) DEFAULT 'routine',
    completion_days NUMERIC(8, 2),
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_fact_ref_patient ON analytics.fact_referral(patient_key);
CREATE INDEX IF NOT EXISTS idx_fact_ref_ref_fac ON analytics.fact_referral(referring_facility_key);
CREATE INDEX IF NOT EXISTS idx_fact_ref_rec_fac ON analytics.fact_referral(receiving_facility_key);
CREATE INDEX IF NOT EXISTS idx_fact_ref_created_date ON analytics.fact_referral(created_date_key);
