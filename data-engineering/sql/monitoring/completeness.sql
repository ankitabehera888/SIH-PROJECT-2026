-- Completeness Quality Check Query
SELECT
    'dim_patient_key' AS check_target,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE patient_key IS NULL) AS null_rows,
    ROUND(COUNT(*) FILTER (WHERE patient_key IS NULL)::numeric / NULLIF(COUNT(*), 0), 4) AS null_rate
FROM analytics.dim_patient
UNION ALL
SELECT
    'fact_encounter_key' AS check_target,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE encounter_key IS NULL) AS null_rows,
    ROUND(COUNT(*) FILTER (WHERE encounter_key IS NULL)::numeric / NULLIF(COUNT(*), 0), 4) AS null_rate
FROM analytics.fact_encounter
UNION ALL
SELECT
    'fact_appointment_key' AS check_target,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE appointment_key IS NULL) AS null_rows,
    ROUND(COUNT(*) FILTER (WHERE appointment_key IS NULL)::numeric / NULLIF(COUNT(*), 0), 4) AS null_rate
FROM analytics.fact_appointment
UNION ALL
SELECT
    'fact_referral_key' AS check_target,
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE referral_key IS NULL) AS null_rows,
    ROUND(COUNT(*) FILTER (WHERE referral_key IS NULL)::numeric / NULLIF(COUNT(*), 0), 4) AS null_rate
FROM analytics.fact_referral;
