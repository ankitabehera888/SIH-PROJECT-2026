CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.quality_alerts (
    alert_key BIGSERIAL PRIMARY KEY,
    check_key BIGINT REFERENCES analytics.quality_check_registry(check_key) ON DELETE CASCADE,
    result_key BIGINT REFERENCES analytics.quality_check_results(result_key) ON DELETE SET NULL,
    pipeline_run_id VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'INFO', 'WARNING', 'CRITICAL'
    alert_code VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'OPEN', -- 'OPEN', 'ACKNOWLEDGED', 'RESOLVED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_quality_alt_code ON analytics.quality_alerts(alert_code);
CREATE INDEX IF NOT EXISTS idx_quality_alt_status ON analytics.quality_alerts(status);
