CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.metric_results (
    metric_result_key BIGSERIAL PRIMARY KEY,
    metric_key BIGINT REFERENCES analytics.metric_registry(metric_key) ON DELETE CASCADE,
    metric_code VARCHAR(100) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    facility_key BIGINT,
    geography_key BIGINT,
    numerator NUMERIC,
    denominator NUMERIC,
    metric_value NUMERIC,
    calculation_version VARCHAR(50) NOT NULL,
    pipeline_run_id VARCHAR(100) NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metric_res_code ON analytics.metric_results(metric_code);
CREATE INDEX IF NOT EXISTS idx_metric_res_period ON analytics.metric_results(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_metric_res_facility ON analytics.metric_results(facility_key);
