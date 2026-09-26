-- Cohort 2: Essential Hypertension v1.0
-- Inclusion: Documented hypertension diagnosis OR elevated blood pressure (SBP >= 140 or DBP >= 90)
WITH hypertension_encounters AS (
    SELECT
        e.patient_key,
        d.full_date AS index_date,
        ROW_NUMBER() OVER (PARTITION BY e.patient_key ORDER BY d.full_date ASC) as rn
    FROM analytics.fact_encounter e
    JOIN analytics.dim_date d ON e.date_key = d.date_key
    WHERE e.patient_key IS NOT NULL
      AND (
          EXISTS (
              SELECT 1 FROM encounters enc 
              WHERE enc.id::text = e.encounter_id 
                AND (enc.chief_complaint ILIKE '%hypertension%' OR enc.clinical_notes ILIKE '%hypertension%')
          )
          OR EXISTS (
              SELECT 1 FROM analytics.fact_vital v
              WHERE v.encounter_key = e.encounter_key
                AND (v.systolic_bp >= 140.0 OR v.diastolic_bp >= 90.0)
          )
      )
)
SELECT
    patient_key,
    index_date,
    index_date AS observation_start,
    index_date + INTERVAL '365 days' AS observation_end,
    'eligible' AS eligibility_status,
    20.0 AS risk_score
FROM hypertension_encounters
WHERE rn = 1;
