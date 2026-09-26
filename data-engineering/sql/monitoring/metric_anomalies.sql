-- Metric & KPI Boundary Anomaly Query
SELECT
    metric_code,
    metric_value,
    CASE
        WHEN metric_code LIKE '%rate' AND (metric_value < 0.0 OR metric_value > 1.0) THEN 'RATE_OUT_OF_BOUNDS'
        WHEN metric_code LIKE '%volume' AND metric_value < 0.0 THEN 'NEGATIVE_VOLUME'
        WHEN metric_code LIKE '%duration' AND metric_value < 0.0 THEN 'NEGATIVE_DURATION'
        ELSE 'NORMAL'
    END AS anomaly_status
FROM analytics.metric_results
WHERE metric_value IS NOT NULL;
