-- Cohort 4: Missed Appointments / No-Shows v1.0
-- Inclusion: Patients with cancelled or no-show appointment statuses
WITH missed_appts AS (
    SELECT
        a.patient_key,
        d.full_date AS index_date,
        ROW_NUMBER() OVER (PARTITION BY a.patient_key ORDER BY d.full_date DESC) as rn
    FROM analytics.fact_appointment a
    JOIN analytics.dim_date d ON a.date_key = d.date_key
    WHERE a.patient_key IS NOT NULL
      AND (a.is_cancelled = TRUE OR a.is_no_show = TRUE OR a.appointment_status IN ('cancelled', 'no_show'))
)
SELECT
    patient_key,
    index_date,
    index_date AS observation_start,
    index_date + INTERVAL '90 days' AS observation_end,
    'eligible' AS eligibility_status,
    15.0 AS risk_score
FROM missed_appts
WHERE rn = 1;
