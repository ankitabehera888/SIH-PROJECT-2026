-- Clinical Encounter Metrics Calculation
SELECT
    COUNT(*) AS encounter_volume,
    COALESCE(AVG(duration_minutes), 0.0) AS average_consultation_duration,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_minutes), 0.0) AS median_consultation_duration,
    COUNT(DISTINCT facility_key) AS active_facilities_count,
    COUNT(*)::DECIMAL / NULLIF(COUNT(DISTINCT facility_key), 0) AS encounters_per_facility,
    COUNT(DISTINCT provider_key) AS active_providers_count,
    COUNT(*)::DECIMAL / NULLIF(COUNT(DISTINCT provider_key), 0) AS encounters_per_provider
FROM analytics.fact_encounter;
