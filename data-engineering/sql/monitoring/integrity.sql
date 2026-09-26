-- Referential Integrity Monitoring Query
SELECT
    'orphan_vitals' AS check_target,
    COUNT(*) AS orphan_count
FROM analytics.fact_vital v
LEFT JOIN analytics.fact_encounter e ON v.encounter_key = e.encounter_key
WHERE e.encounter_key IS NULL
UNION ALL
SELECT
    'orphan_prescriptions' AS check_target,
    COUNT(*) AS orphan_count
FROM analytics.fact_prescription p
LEFT JOIN analytics.fact_encounter e ON p.encounter_key = e.encounter_key
WHERE e.encounter_key IS NULL
UNION ALL
SELECT
    'orphan_encounters_patient' AS check_target,
    COUNT(*) AS orphan_count
FROM analytics.fact_encounter e
LEFT JOIN analytics.dim_patient p ON e.patient_key = p.patient_key
WHERE p.patient_key IS NULL
UNION ALL
SELECT
    'orphan_appointments_patient' AS check_target,
    COUNT(*) AS orphan_count
FROM analytics.fact_appointment a
LEFT JOIN analytics.dim_patient p ON a.patient_key = p.patient_key
WHERE p.patient_key IS NULL
UNION ALL
SELECT
    'orphan_referrals_patient' AS check_target,
    COUNT(*) AS orphan_count
FROM analytics.fact_referral r
LEFT JOIN analytics.dim_patient p ON r.patient_key = p.patient_key
WHERE p.patient_key IS NULL;
