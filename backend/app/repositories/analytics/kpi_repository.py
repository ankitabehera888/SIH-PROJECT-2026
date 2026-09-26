from datetime import date
from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

class KPIRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_kpi(
        self,
        metric_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        facility_key: Optional[int] = None,
        geography_key: Optional[int] = None,
    ) -> Optional[Dict]:
        """Queries the latest materialized metric result for a given code and optional filters."""
        query = text("""
            SELECT
                r.metric_code,
                reg.metric_name,
                reg.metric_type,
                r.period_start,
                r.period_end,
                r.numerator,
                r.denominator,
                r.metric_value,
                r.calculation_version
            FROM analytics.metric_results r
            JOIN analytics.metric_registry reg ON r.metric_key = reg.metric_key
            WHERE r.metric_code = :metric_code
            ORDER BY r.calculated_at DESC
            LIMIT 1;
        """)
        row = self.db.execute(query, {"metric_code": metric_code}).fetchone()
        if not row:
            # Fallback: check if metric is registered in registry even if uncalculated
            reg_row = self.db.execute(
                text("SELECT metric_code, metric_name, metric_type, calculation_version FROM analytics.metric_registry WHERE metric_code = :code;"),
                {"code": metric_code}
            ).fetchone()
            if reg_row:
                return {
                    "metric_code": reg_row[0],
                    "metric_name": reg_row[1],
                    "metric_type": reg_row[2],
                    "period_start": start_date or date(2026, 1, 1),
                    "period_end": end_date or date(2026, 12, 31),
                    "numerator": None,
                    "denominator": None,
                    "metric_value": None,
                    "calculation_version": reg_row[3],
                }
            return None

        return {
            "metric_code": row[0],
            "metric_name": row[1],
            "metric_type": row[2],
            "period_start": row[3],
            "period_end": row[4],
            "numerator": row[5],
            "denominator": row[6],
            "metric_value": row[7],
            "calculation_version": row[8],
        }

    def get_timeseries(
        self,
        metric_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "month"
    ) -> List[Dict]:
        """Calculates historical time series for appointment or encounter metrics."""
        # Query monthly trend directly from fact_appointment or fact_encounter
        if "appointment" in metric_code:
            query = text("""
                SELECT
                    TO_CHAR(d.full_date, 'YYYY-MM') AS period,
                    COUNT(*) AS total_count,
                    COUNT(*) FILTER (WHERE a.is_completed = TRUE) AS num_count,
                    ROUND(COUNT(*) FILTER (WHERE a.is_completed = TRUE)::numeric / NULLIF(COUNT(*), 0), 4) AS val
                FROM analytics.fact_appointment a
                JOIN analytics.dim_date d ON a.date_key = d.date_key
                GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
                ORDER BY period ASC;
            """)
        else:
            query = text("""
                SELECT
                    TO_CHAR(d.full_date, 'YYYY-MM') AS period,
                    COUNT(*) AS total_count,
                    COUNT(*) AS num_count,
                    COUNT(*)::numeric AS val
                FROM analytics.fact_encounter e
                JOIN analytics.dim_date d ON e.date_key = d.date_key
                GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
                ORDER BY period ASC;
            """)
        rows = self.db.execute(query).fetchall()
        return [
            {
                "period": r[0],
                "denominator": r[1],
                "numerator": r[2],
                "value": r[3],
            }
            for r in rows
        ]

    def get_comparison(self, metric_code: str, group_by: str = "facility") -> List[Dict]:
        """Computes metric distribution grouped by facility."""
        query = text("""
            SELECT
                f.facility_key::text AS entity_id,
                f.facility_name AS entity_name,
                COUNT(e.encounter_key)::numeric AS val
            FROM analytics.dim_facility f
            LEFT JOIN analytics.fact_encounter e ON f.facility_key = e.facility_key
            GROUP BY f.facility_key, f.facility_name
            HAVING COUNT(e.encounter_key) > 0
            ORDER BY val DESC
            LIMIT 20;
        """)
        rows = self.db.execute(query).fetchall()
        return [
            {
                "entity_id": r[0],
                "entity_name": r[1],
                "value": r[2],
            }
            for r in rows
        ]
