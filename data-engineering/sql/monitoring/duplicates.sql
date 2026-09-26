-- Duplicate Growth Quality Check Query
SELECT
    'duplicate_patients' AS check_target,
    COUNT(*) AS duplicate_count
FROM (
    SELECT patient_id, COUNT(*)
    FROM analytics.dim_patient
    WHERE is_current = TRUE
    GROUP BY patient_id
    HAVING COUNT(*) > 1
) sub
UNION ALL
SELECT
    'duplicate_encounters' AS check_target,
    COUNT(*) AS duplicate_count
FROM (
    SELECT encounter_id, COUNT(*)
    FROM analytics.fact_encounter
    GROUP BY encounter_id
    HAVING COUNT(*) > 1
) sub
UNION ALL
SELECT
    'duplicate_appointments' AS check_target,
    COUNT(*) AS duplicate_count
FROM (
    SELECT appointment_id, COUNT(*)
    FROM analytics.fact_appointment
    GROUP BY appointment_id
    HAVING COUNT(*) > 1
) sub
UNION ALL
SELECT
    'duplicate_referrals' AS check_target,
    COUNT(*) AS duplicate_count
FROM (
    SELECT referral_id, COUNT(*)
    FROM analytics.fact_referral
    GROUP BY referral_id
    HAVING COUNT(*) > 1
) sub;
