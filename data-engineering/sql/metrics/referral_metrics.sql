-- Referral Metrics Calculation
SELECT
    COUNT(*) AS referral_volume,
    COUNT(*) FILTER (WHERE is_completed = TRUE) AS completed_referrals,
    COUNT(*) FILTER (WHERE is_completed = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) AS referral_completion_rate,
    COUNT(*) FILTER (WHERE is_completed = FALSE) AS pending_referrals,
    COUNT(*) FILTER (WHERE is_completed = FALSE)::DECIMAL / NULLIF(COUNT(*), 0) AS referral_pending_rate,
    COALESCE(AVG(completion_days) FILTER (WHERE is_completed = TRUE), 0.0) AS avg_referral_completion_days,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_days) FILTER (WHERE is_completed = TRUE), 0.0) AS median_referral_completion_days
FROM analytics.fact_referral;
