CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.quality_check_registry (
    check_key BIGSERIAL PRIMARY KEY,
    check_code VARCHAR(100) UNIQUE NOT NULL,
    check_name VARCHAR(255) NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- 'COMPLETENESS', 'VALIDITY', 'INTEGRITY', 'DUPLICATE', 'FRESHNESS', 'VOLUME', 'SCHEMA', 'ANOMALY', 'RECONCILIATION'
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'INFO', 'WARNING', 'CRITICAL'
    threshold_config JSONB,
    source_table VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quality_reg_code ON analytics.quality_check_registry(check_code);
