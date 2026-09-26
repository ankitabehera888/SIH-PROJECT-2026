-- Clinical Biometric Boundary Validation Query
SELECT
    'invalid_systolic_bp' AS check_target,
    COUNT(*) AS invalid_count
FROM analytics.fact_vital
WHERE systolic_bp IS NOT NULL AND (systolic_bp < 50.0 OR systolic_bp > 260.0)
UNION ALL
SELECT
    'invalid_diastolic_bp' AS check_target,
    COUNT(*) AS invalid_count
FROM analytics.fact_vital
WHERE diastolic_bp IS NOT NULL AND (diastolic_bp < 30.0 OR diastolic_bp > 160.0)
UNION ALL
SELECT
    'invalid_heart_rate' AS check_target,
    COUNT(*) AS invalid_count
FROM analytics.fact_vital
WHERE heart_rate IS NOT NULL AND (heart_rate < 30.0 OR heart_rate > 250.0)
UNION ALL
SELECT
    'invalid_spo2' AS check_target,
    COUNT(*) AS invalid_count
FROM analytics.fact_vital
WHERE spo2 IS NOT NULL AND (spo2 < 50.0 OR spo2 > 100.0);
