-- Chronic Disease Care & Follow-up Metrics
WITH htn_cohort AS (
    SELECT DISTINCT m.patient_key
    FROM analytics.cohort_membership m
    JOIN analytics.cohort_registry r ON m.cohort_key = r.cohort_key
    WHERE r.cohort_name = 'hypertension'
),
chronic_cohort AS (
    SELECT DISTINCT m.patient_key
    FROM analytics.cohort_membership m
    JOIN analytics.cohort_registry r ON m.cohort_key = r.cohort_key
    WHERE r.cohort_name = 'chronic_followup'
)
SELECT
    (SELECT COUNT(*) FROM htn_cohort) AS total_hypertension_patients,
    (
        SELECT COUNT(DISTINCT h.patient_key)
        FROM htn_cohort h
        JOIN analytics.fact_encounter e ON e.patient_key = h.patient_key
    ) AS htn_patients_with_encounter,
    (
        SELECT COUNT(DISTINCT h.patient_key)::DECIMAL / NULLIF((SELECT COUNT(*) FROM htn_cohort), 0)
        FROM htn_cohort h
        JOIN analytics.fact_encounter e ON e.patient_key = h.patient_key
    ) AS hypertension_followup_rate,
    (SELECT COUNT(*) FROM chronic_cohort) AS total_chronic_patients,
    (
        SELECT COUNT(DISTINCT c.patient_key)
        FROM chronic_cohort c
        JOIN analytics.fact_encounter e ON e.patient_key = c.patient_key
    ) AS chronic_patients_with_encounter,
    (
        SELECT COUNT(DISTINCT c.patient_key)::DECIMAL / NULLIF((SELECT COUNT(*) FROM chronic_cohort), 0)
        FROM chronic_cohort c
        JOIN analytics.fact_encounter e ON e.patient_key = c.patient_key
    ) AS chronic_followup_adherence;
