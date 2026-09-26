-- Cohort 1: Diabetes Mellitus v1.0
-- Inclusion: Documented diagnosis of diabetes OR anti-diabetic medication prescription
WITH qualifying_patients AS (
    SELECT DISTINCT
        e.patient_key,
        d.full_date AS index_date,
        ROW_NUMBER() OVER (PARTITION BY e.patient_key ORDER BY d.full_date ASC) as rn
    FROM analytics.fact_encounter e
    JOIN analytics.dim_date d ON e.date_key = d.date_key
    WHERE e.patient_key IS NOT NULL
      AND (
          -- Diagnosis evidence
          EXISTS (
              SELECT 1 FROM encounters enc 
              WHERE enc.id::text = e.encounter_id 
                AND (enc.chief_complaint ILIKE '%diabet%' OR enc.clinical_notes ILIKE '%diabet%')
          )
          -- Medication evidence
          OR EXISTS (
              SELECT 1 FROM analytics.fact_prescription rx
              WHERE rx.encounter_key = e.encounter_key
                AND rx.medication_id ILIKE '%metformin%'
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
FROM qualifying_patients
WHERE rn = 1;
