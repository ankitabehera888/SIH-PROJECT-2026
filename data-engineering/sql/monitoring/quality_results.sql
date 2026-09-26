CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.quality_check_results (
    result_key BIGSERIAL PRIMARY KEY,
    check_key BIGINT REFERENCES analytics.quality_check_registry(check_key) ON DELETE CASCADE,
    check_code VARCHAR(100) NOT NULL,
    pipeline_run_id VARCHAR(100) NOT NULL,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    observed_value NUMERIC,
    expected_value NUMERIC,
    threshold_value NUMERIC,
    status VARCHAR(20) NOT NULL, -- 'PASS', 'WARNING', 'FAIL', 'ERROR'
    severity VARCHAR(20) NOT NULL, -- 'INFO', 'WARNING', 'CRITICAL'
    message TEXT,
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_quality_res_code ON analytics.quality_check_results(check_code);
CREATE INDEX IF NOT EXISTS idx_quality_res_run ON analytics.quality_check_results(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_quality_res_status ON analytics.quality_check_results(status);
