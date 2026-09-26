CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_provider (
    provider_key BIGSERIAL PRIMARY KEY,
    provider_id INT NOT NULL UNIQUE,         -- Business User/Provider ID
    role VARCHAR(32) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_dim_provider_id ON analytics.dim_provider(provider_id);
