-- Cohort 6: Chronic Follow-Up Gap v1.0
-- Definition: Patients with chronic conditions whose last visit was >= 180 days ago
WITH chronic_patients AS (
    SELECT DISTINCT
        e.patient_key,
        MAX(d.full_date) AS last_visit_date
    FROM analytics.fact_encounter e
    JOIN analytics.dim_date d ON e.date_key = d.date_key
    JOIN encounters enc ON enc.id::text = e.encounter_id
    WHERE e.patient_key IS NOT NULL
      AND (enc.chief_complaint ILIKE '%hypertension%' OR enc.chief_complaint ILIKE '%chest%')
    GROUP BY e.patient_key
)
SELECT
    patient_key,
    last_visit_date AS index_date,
    last_visit_date AS observation_start,
    last_visit_date + INTERVAL '180 days' AS observation_end,
    CASE 
        WHEN (CURRENT_DATE - last_visit_date) >= 180 THEN 'overdue' 
        ELSE 'eligible' 
    END AS eligibility_status,
    30.0 AS risk_score
FROM chronic_patients;
