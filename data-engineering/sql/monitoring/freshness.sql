-- Freshness & Ingestion Lag Query
SELECT
    'fact_encounter' AS table_name,
    MAX(d.full_date) AS latest_record_date,
    ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(d.full_date)::timestamp)) / 3600.0, 1) AS freshness_hours
FROM analytics.fact_encounter e
JOIN analytics.dim_date d ON e.date_key = d.date_key
UNION ALL
SELECT
    'fact_appointment' AS table_name,
    MAX(d.full_date) AS latest_record_date,
    ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(d.full_date)::timestamp)) / 3600.0, 1) AS freshness_hours
FROM analytics.fact_appointment a
JOIN analytics.dim_date d ON a.date_key = d.date_key
UNION ALL
SELECT
    'fact_referral' AS table_name,
    MAX(d.full_date) AS latest_record_date,
    ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(d.full_date)::timestamp)) / 3600.0, 1) AS freshness_hours
FROM analytics.fact_referral r
JOIN analytics.dim_date d ON r.created_date_key = d.date_key;
