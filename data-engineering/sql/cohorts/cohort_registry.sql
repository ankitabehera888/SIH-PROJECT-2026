CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.cohort_registry (
    cohort_key BIGSERIAL PRIMARY KEY,
    cohort_name VARCHAR(64) NOT NULL,
    cohort_version VARCHAR(32) NOT NULL,
    description TEXT,
    definition_criteria TEXT,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cohort_name, cohort_version)
);

CREATE INDEX IF NOT EXISTS idx_cohort_reg_name ON analytics.cohort_registry(cohort_name);
