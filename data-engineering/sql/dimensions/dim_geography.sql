CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_geography (
    geography_key BIGSERIAL PRIMARY KEY,
    district VARCHAR(64) NOT NULL,
    state VARCHAR(64) NOT NULL,
    country VARCHAR(32) DEFAULT 'India',
    rural_urban VARCHAR(16) DEFAULT 'rural'
);

CREATE INDEX IF NOT EXISTS idx_dim_geo_district ON analytics.dim_geography(district, state);
