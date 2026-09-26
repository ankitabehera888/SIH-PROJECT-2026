CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.pipeline_runs (
    run_id VARCHAR(100) PRIMARY KEY,
    dag_id VARCHAR(255) NOT NULL,
    execution_date TIMESTAMP WITH TIME ZONE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(30) NOT NULL, -- 'RUNNING', 'SUCCESS', 'WARNING', 'BLOCKED', 'FAILED'
    records_extracted BIGINT DEFAULT 0,
    records_staged BIGINT DEFAULT 0,
    records_loaded BIGINT DEFAULT 0,
    quality_score NUMERIC,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pipe_runs_dag ON analytics.pipeline_runs(dag_id);
CREATE INDEX IF NOT EXISTS idx_pipe_runs_status ON analytics.pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipe_runs_exec_date ON analytics.pipeline_runs(execution_date);
