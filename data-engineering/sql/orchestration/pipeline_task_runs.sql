CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.pipeline_task_runs (
    task_run_key BIGSERIAL PRIMARY KEY,
    run_id VARCHAR(100) NOT NULL REFERENCES analytics.pipeline_runs(run_id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(30) NOT NULL, -- 'RUNNING', 'SUCCESS', 'WARNING', 'BLOCKED', 'FAILED', 'SKIPPED'
    rows_processed BIGINT DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_pipe_task_run_id ON analytics.pipeline_task_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_pipe_task_name ON analytics.pipeline_task_runs(task_name);
CREATE INDEX IF NOT EXISTS idx_pipe_task_status ON analytics.pipeline_task_runs(status);
