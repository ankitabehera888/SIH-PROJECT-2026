CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_facility (
    facility_key BIGSERIAL PRIMARY KEY,
    facility_id VARCHAR(64) NOT NULL UNIQUE, -- Business UUID
    facility_name VARCHAR(128) NOT NULL,
    facility_code VARCHAR(32) NOT NULL,
    facility_tier VARCHAR(32),               -- e.g. PHC, CHC, District Hospital
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_dim_facility_id ON analytics.dim_facility(facility_id);
