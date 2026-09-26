-- Cohort 3: High-Risk Clinical Cohort v1.0
-- Definition: Multi-factor weighted clinical risk score >= 30.0
WITH patient_scores AS (
    SELECT
        p.patient_key,
        CURRENT_DATE AS index_date,
        (
            -- +20 for chronic conditions (hypertension/cardiac)
            CASE WHEN EXISTS (
                SELECT 1 FROM analytics.fact_encounter e
                JOIN encounters enc ON enc.id::text = e.encounter_id
                WHERE e.patient_key = p.patient_key
                  AND (enc.chief_complaint ILIKE '%hypertension%' OR enc.chief_complaint ILIKE '%chest%')
            ) THEN 20.0 ELSE 0.0 END
            +
            -- +15 for pending unresolved referrals
            CASE WHEN EXISTS (
                SELECT 1 FROM analytics.fact_referral r
                WHERE r.patient_key = p.patient_key AND r.is_completed = FALSE
            ) THEN 15.0 ELSE 0.0 END
            +
            -- +10 for abnormal vitals (elevated BP or low SpO2)
            CASE WHEN EXISTS (
                SELECT 1 FROM analytics.fact_vital v
                WHERE v.patient_key = p.patient_key
                  AND (v.systolic_bp >= 140.0 OR v.diastolic_bp >= 90.0 OR v.spo2 < 95.0)
            ) THEN 10.0 ELSE 0.0 END
            +
            -- +10 for frequent encounters (>= 2 encounters)
            CASE WHEN (
                SELECT COUNT(*) FROM analytics.fact_encounter e2
                WHERE e2.patient_key = p.patient_key
            ) >= 2 THEN 10.0 ELSE 0.0 END
        ) AS risk_score
    FROM analytics.dim_patient p
    WHERE p.is_current = TRUE
)
SELECT
    patient_key,
    index_date,
    index_date AS observation_start,
    index_date + INTERVAL '180 days' AS observation_end,
    'eligible' AS eligibility_status,
    risk_score
FROM patient_scores
WHERE risk_score >= 30.0;
