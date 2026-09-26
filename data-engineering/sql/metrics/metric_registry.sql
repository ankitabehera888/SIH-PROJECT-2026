CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.metric_registry (
    metric_key BIGSERIAL PRIMARY KEY,
    metric_code VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'COUNT', 'RATE', 'AVERAGE', 'MEDIAN', 'DURATION', 'AGING'
    numerator_definition TEXT,
    denominator_definition TEXT,
    population_definition TEXT,
    exclusion_definition TEXT,
    time_basis VARCHAR(100),
    grain VARCHAR(100),
    source_tables TEXT,
    calculation_version VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metric_reg_code ON analytics.metric_registry(metric_code);
