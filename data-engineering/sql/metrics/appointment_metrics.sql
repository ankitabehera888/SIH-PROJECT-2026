-- Appointment Metrics Calculation
SELECT
    COUNT(*) AS appointment_volume,
    COUNT(*) FILTER (WHERE is_completed = TRUE) AS completed_appointments,
    COUNT(*) FILTER (WHERE is_completed = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) AS appointment_completion_rate,
    COUNT(*) FILTER (WHERE is_cancelled = TRUE) AS cancelled_appointments,
    COUNT(*) FILTER (WHERE is_cancelled = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) AS appointment_cancellation_rate,
    COUNT(*) FILTER (WHERE is_no_show = TRUE) AS no_show_appointments,
    COUNT(*) FILTER (WHERE is_no_show = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) AS appointment_no_show_rate,
    COALESCE(AVG(wait_minutes), 0.0) AS average_wait_minutes,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY wait_minutes), 0.0) AS median_wait_minutes
FROM analytics.fact_appointment;
