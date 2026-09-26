from datetime import date
from decimal import Decimal
from typing import Dict, List, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_appointment_summary(self) -> Dict:
        """Retrieves aggregated appointment performance metrics."""
        query = text("""
            SELECT
                COUNT(*) AS volume,
                COUNT(*) FILTER (WHERE is_completed = TRUE) AS completed,
                ROUND(COUNT(*) FILTER (WHERE is_completed = TRUE)::numeric / NULLIF(COUNT(*), 0), 4) AS completion_rate,
                COUNT(*) FILTER (WHERE is_cancelled = TRUE) AS cancelled,
                ROUND(COUNT(*) FILTER (WHERE is_cancelled = TRUE)::numeric / NULLIF(COUNT(*), 0), 4) AS cancellation_rate,
                COUNT(*) FILTER (WHERE is_no_show = TRUE) AS no_show,
                ROUND(COUNT(*) FILTER (WHERE is_no_show = TRUE)::numeric / NULLIF(COUNT(*), 0), 4) AS no_show_rate,
                COALESCE(ROUND(AVG(wait_minutes)::numeric, 2), 0.0) AS avg_wait,
                COALESCE(ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY wait_minutes)::numeric, 2), 0.0) AS med_wait
            FROM analytics.fact_appointment;
        """)
        r = self.db.execute(query).fetchone()
        return {
            "appointment_volume": r[0],
            "completed_appointments": r[1],
            "completion_rate": r[2],
            "cancelled_appointments": r[3],
            "cancellation_rate": r[4],
            "no_show_appointments": r[5],
            "no_show_rate": r[6],
            "average_wait_minutes": r[7],
            "median_wait_minutes": r[8],
        }

    def get_appointment_trends(self) -> List[Dict]:
        """Retrieves monthly appointment trend volumes."""
        query = text("""
            SELECT
                TO_CHAR(d.full_date, 'YYYY-MM') AS period,
                COUNT(*) AS appointments,
                COUNT(*) FILTER (WHERE a.is_completed = TRUE) AS completed,
                COUNT(*) FILTER (WHERE a.is_cancelled = TRUE) AS cancelled,
                COUNT(*) FILTER (WHERE a.is_no_show = TRUE) AS no_show
            FROM analytics.fact_appointment a
            JOIN analytics.dim_date d ON a.date_key = d.date_key
            GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
            ORDER BY period ASC;
        """)
        rows = self.db.execute(query).fetchall()
        return [
            {
                "period": r[0],
                "appointments": r[1],
                "completed": r[2],
                "cancelled": r[3],
                "no_show": r[4],
            }
            for r in rows
        ]

    def get_referral_summary(self) -> Dict:
        """Retrieves aggregated referral performance metrics."""
        query = text("""
            SELECT
                COUNT(*) AS volume,
                COUNT(*) FILTER (WHERE is_completed = TRUE) AS completed,
                ROUND(COUNT(*) FILTER (WHERE is_completed = TRUE)::numeric / NULLIF(COUNT(*), 0), 4) AS completion_rate,
                COUNT(*) FILTER (WHERE is_completed = FALSE) AS pending,
                ROUND(COUNT(*) FILTER (WHERE is_completed = FALSE)::numeric / NULLIF(COUNT(*), 0), 4) AS pending_rate,
                COALESCE(ROUND(AVG(completion_days) FILTER (WHERE is_completed = TRUE)::numeric, 2), 0.0) AS avg_days
            FROM analytics.fact_referral;
        """)
        r = self.db.execute(query).fetchone()
        return {
            "referral_volume": r[0],
            "completed_referrals": r[1],
            "completion_rate": r[2],
            "pending_referrals": r[3],
            "pending_rate": r[4],
            "average_completion_days": r[5],
        }

    def get_referral_aging(self) -> List[Dict]:
        """Categorizes pending referrals into operational aging buckets."""
        query = text("""
            WITH referral_ages AS (
                SELECT
                    (CURRENT_DATE - d.full_date) AS age_days
                FROM analytics.fact_referral r
                JOIN analytics.dim_date d ON r.created_date_key = d.date_key
                WHERE r.is_completed = FALSE
            )
            SELECT
                CASE
                    WHEN age_days <= 2 THEN '0-2 days'
                    WHEN age_days <= 7 THEN '3-7 days'
                    WHEN age_days <= 14 THEN '8-14 days'
                    WHEN age_days <= 30 THEN '15-30 days'
                    ELSE '31+ days'
                END AS bucket,
                COUNT(*) AS count
            FROM referral_ages
            GROUP BY 1
            ORDER BY 1;
        """)
        rows = self.db.execute(query).fetchall()
        # Ensure canonical 5 buckets exist
        buckets_map = {r[0]: r[1] for r in rows}
        canonical_buckets = ["0-2 days", "3-7 days", "8-14 days", "15-30 days", "31+ days"]
        return [{"bucket": b, "count": buckets_map.get(b, 0)} for b in canonical_buckets]

    def get_cohort_summary(self) -> List[Dict]:
        """Retrieves high-level cohort population and risk distribution from analytics.cohort_registry."""
        query = text("""
            SELECT
                r.cohort_name,
                r.cohort_version,
                COUNT(m.membership_key) AS eligible_patients,
                COALESCE(ROUND(AVG(m.risk_score)::numeric, 1), 0.0) AS avg_risk,
                r.description
            FROM analytics.cohort_registry r
            LEFT JOIN analytics.cohort_membership m ON r.cohort_key = m.cohort_key
            GROUP BY r.cohort_name, r.cohort_version, r.description
            ORDER BY eligible_patients DESC;
        """)
        rows = self.db.execute(query).fetchall()
        return [
            {
                "cohort_name": r[0].replace("_", " ").title(),
                "cohort_version": r[1],
                "eligible_patients": r[2],
                "risk_score_avg": r[3],
                "active_criteria": r[4],
            }
            for r in rows
        ]

    def get_facility_analytics(self, page: int = 1, page_size: int = 20) -> Tuple[int, List[Dict]]:
        """Retrieves paginated facility analytics comparison."""
        offset = (page - 1) * page_size
        count_query = text("SELECT COUNT(DISTINCT facility_key) FROM analytics.dim_facility WHERE is_active = TRUE;")
        total = self.db.execute(count_query).scalar() or 0

        query = text("""
            SELECT
                f.facility_key,
                f.facility_name,
                COUNT(e.encounter_key) AS encounter_volume,
                COUNT(DISTINCT e.patient_key) AS patients_served,
                COALESCE(ROUND(AVG(a.wait_minutes)::numeric, 1), 15.0) AS average_wait_minutes
            FROM analytics.dim_facility f
            LEFT JOIN analytics.fact_encounter e ON f.facility_key = e.facility_key
            LEFT JOIN analytics.fact_appointment a ON f.facility_key = a.facility_key
            WHERE f.is_active = TRUE
            GROUP BY f.facility_key, f.facility_name
            ORDER BY encounter_volume DESC, f.facility_name ASC
            LIMIT :limit OFFSET :offset;
        """)
        rows = self.db.execute(query, {"limit": page_size, "offset": offset}).fetchall()
        data = [
            {
                "facility_key": r[0],
                "facility_name": r[1],
                "encounter_volume": r[2],
                "patients_served": r[3],
                "average_wait_minutes": r[4],
            }
            for r in rows
        ]
        return total, data

    def get_geography_analytics(self, page: int = 1, page_size: int = 20) -> Tuple[int, List[Dict]]:
        """Retrieves paginated district geography analytics."""
        offset = (page - 1) * page_size
        count_query = text("SELECT COUNT(*) FROM analytics.dim_geography;")
        total = self.db.execute(count_query).scalar() or 0

        query = text("""
            SELECT
                g.geography_key,
                g.district AS district_name,
                COUNT(e.encounter_key) AS encounter_volume
            FROM analytics.dim_geography g
            LEFT JOIN analytics.fact_encounter e ON 1=1
            GROUP BY g.geography_key, g.district
            ORDER BY g.district ASC
            LIMIT :limit OFFSET :offset;
        """)
        rows = self.db.execute(query, {"limit": page_size, "offset": offset}).fetchall()
        data = [
            {
                "geography_key": r[0],
                "district_name": r[1],
                "encounter_volume": r[2],
            }
            for r in rows
        ]
        return total, data

    def get_dashboard_overview(self) -> Dict:
        """Consolidates key metrics into a single high-performance overview payload."""
        # Query results from materialized table analytics.metric_results
        query = text("""
            SELECT metric_code, metric_value
            FROM analytics.metric_results;
        """)
        rows = self.db.execute(query).fetchall()
        vals = {r[0]: r[1] for r in rows}

        return {
            "period": {
                "start": date(2026, 1, 1),
                "end": date(2026, 12, 31),
            },
            "appointments": {
                "volume": vals.get("appointment_volume"),
                "completion_rate": vals.get("appointment_completion_rate"),
                "no_show_rate": vals.get("appointment_no_show_rate"),
                "cancellation_rate": vals.get("appointment_cancellation_rate"),
            },
            "encounters": {
                "volume": vals.get("encounter_volume"),
                "average_wait_minutes": vals.get("average_wait_minutes"),
                "median_wait_minutes": vals.get("median_wait_minutes"),
            },
            "referrals": {
                "volume": vals.get("referral_volume"),
                "completion_rate": vals.get("referral_completion_rate"),
                "pending_rate": vals.get("referral_pending_rate"),
            },
            "chronic_care": {
                "hypertension_followup_rate": vals.get("hypertension_followup_rate"),
                "chronic_followup_adherence": vals.get("chronic_followup_adherence"),
            },
            "access": {
                "unique_patients_served": vals.get("unique_patients_served"),
                "patients_served_per_facility": vals.get("patients_served_per_facility"),
            },
        }
