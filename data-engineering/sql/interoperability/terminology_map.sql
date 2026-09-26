CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.terminology_map (
    mapping_key BIGSERIAL PRIMARY KEY,
    domain VARCHAR(64) NOT NULL,             -- 'vitals', 'conditions', 'medications', 'status'
    source_system VARCHAR(64) NOT NULL,      -- 'internal_db'
    source_code VARCHAR(128) NOT NULL,
    source_display VARCHAR(255),
    target_system VARCHAR(128) NOT NULL,     -- 'http://loinc.org', 'http://snomed.info/sct', 'http://unitsofmeasure.org'
    target_code VARCHAR(128) NOT NULL,
    target_display VARCHAR(255),
    mapping_status VARCHAR(32) NOT NULL DEFAULT 'mapped', -- 'mapped', 'unmapped', 'deprecated'
    mapping_version VARCHAR(32) DEFAULT '1.0'
);

CREATE INDEX IF NOT EXISTS idx_term_map_lookup ON analytics.terminology_map(domain, source_code);
