CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.cohort_membership (
    membership_key BIGSERIAL PRIMARY KEY,
    cohort_key BIGINT REFERENCES analytics.cohort_registry(cohort_key) ON DELETE CASCADE,
    patient_key BIGINT REFERENCES analytics.dim_patient(patient_key) ON DELETE CASCADE,
    index_date DATE NOT NULL,
    observation_start DATE NOT NULL,
    observation_end DATE NOT NULL,
    eligibility_status VARCHAR(32) NOT NULL DEFAULT 'eligible', -- 'eligible', 'flagged', 'review'
    risk_score NUMERIC(6, 2) DEFAULT 0.0,
    pipeline_run_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cohort_key, patient_key, index_date)
);

CREATE INDEX IF NOT EXISTS idx_cohort_mem_patient ON analytics.cohort_membership(patient_key);
CREATE INDEX IF NOT EXISTS idx_cohort_mem_cohort ON analytics.cohort_membership(cohort_key);
CREATE INDEX IF NOT EXISTS idx_cohort_mem_index_date ON analytics.cohort_membership(index_date);
