-- Access and Distribution Metrics
SELECT
    COUNT(DISTINCT e.patient_key) AS unique_patients_served,
    COUNT(DISTINCT e.facility_key) AS facilities_serving_patients,
    COUNT(DISTINCT e.patient_key)::DECIMAL / NULLIF(COUNT(DISTINCT e.facility_key), 0) AS patients_served_per_facility,
    COALESCE(AVG(a.wait_minutes), 0.0) AS overall_avg_wait_minutes
FROM analytics.fact_encounter e
LEFT JOIN analytics.fact_appointment a ON e.patient_key = a.patient_key AND e.facility_key = a.facility_key;
