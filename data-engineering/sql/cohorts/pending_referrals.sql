-- Cohort 5: Pending Referrals v1.0
-- Inclusion: Patients with active unresolved care transfers (is_completed = FALSE)
WITH unresolved_referrals AS (
    SELECT
        r.patient_key,
        d.full_date AS index_date,
        r.completion_days,
        ROW_NUMBER() OVER (PARTITION BY r.patient_key ORDER BY d.full_date DESC) as rn
    FROM analytics.fact_referral r
    JOIN analytics.dim_date d ON r.created_date_key = d.date_key
    WHERE r.patient_key IS NOT NULL
      AND r.is_completed = FALSE
)
SELECT
    patient_key,
    index_date,
    index_date AS observation_start,
    index_date + INTERVAL '60 days' AS observation_end,
    'eligible' AS eligibility_status,
    25.0 AS risk_score
FROM unresolved_referrals
WHERE rn = 1;
