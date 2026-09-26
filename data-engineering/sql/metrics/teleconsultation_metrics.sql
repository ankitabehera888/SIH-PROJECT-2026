-- Teleconsultation Metrics
SELECT
    COUNT(*) FILTER (WHERE encounter_type = 'teleconsultation') AS teleconsultation_volume,
    COUNT(*) FILTER (WHERE encounter_type = 'teleconsultation' AND encounter_status = 'completed') AS completed_teleconsultations,
    COUNT(*) FILTER (WHERE encounter_type = 'teleconsultation' AND encounter_status = 'completed')::DECIMAL / NULLIF(COUNT(*) FILTER (WHERE encounter_type = 'teleconsultation'), 0) AS teleconsultation_completion_rate,
    COALESCE(AVG(duration_minutes) FILTER (WHERE encounter_type = 'teleconsultation'), 0.0) AS avg_teleconsultation_duration
FROM analytics.fact_encounter;
