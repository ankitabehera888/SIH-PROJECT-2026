-- Table Volume Monitoring Query
SELECT
    'dim_patient' AS table_name,
    COUNT(*) AS current_row_count
FROM analytics.dim_patient
UNION ALL
SELECT
    'fact_encounter' AS table_name,
    COUNT(*) AS current_row_count
FROM analytics.fact_encounter
UNION ALL
SELECT
    'fact_appointment' AS table_name,
    COUNT(*) AS current_row_count
FROM analytics.fact_appointment
UNION ALL
SELECT
    'fact_referral' AS table_name,
    COUNT(*) AS current_row_count
FROM analytics.fact_referral
UNION ALL
SELECT
    'fact_vital' AS table_name,
    COUNT(*) AS current_row_count
FROM analytics.fact_vital;
