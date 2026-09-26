from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException, NotFoundException
from app.repositories.analytics.kpi_repository import KPIRepository
from app.schemas.analytics.kpi import KPIResponse, KPITimeSeriesResponse, KPIComparisonResponse
from app.services.analytics.cache import get_cached_json, set_cached_json

MIN_AGGREGATE_COUNT = 10
ALLOWED_INTERVALS = {"day", "week", "month", "quarter"}

class KPIService:
    def __init__(self, db: Session):
        self.repo = KPIRepository(db)

    def get_kpi(
        self,
        metric_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        facility_id: Optional[int] = None,
        geography_id: Optional[int] = None,
    ) -> KPIResponse:
        """Retrieves and privacy-validates a single healthcare KPI."""
        if start_date and end_date and start_date > end_date:
            raise BadRequestException("start_date cannot be greater than end_date")

        cache_key = f"analytics:kpi:{metric_code}:{start_date}:{end_date}:{facility_id}:{geography_id}"
        cached = get_cached_json(cache_key)
        if cached:
            return KPIResponse(**cached)

        data = self.repo.get_kpi(
            metric_code=metric_code,
            start_date=start_date,
            end_date=end_date,
            facility_key=facility_id,
            geography_key=geography_id,
        )
        if not data:
            raise NotFoundException(f"Metric '{metric_code}' is not registered or found")

        # Small population privacy suppression check
        suppressed = False
        suppression_reason = None
        val = data["metric_value"]
        den = data["denominator"]

        if den is not None and 0 < den < MIN_AGGREGATE_COUNT:
            suppressed = True
            suppression_reason = "small_population"
            val = None

        resp_dict = {
            "metric_code": data["metric_code"],
            "metric_name": data["metric_name"],
            "metric_type": data["metric_type"],
            "period_start": data["period_start"],
            "period_end": data["period_end"],
            "numerator": data["numerator"],
            "denominator": den,
            "value": val,
            "calculation_version": data["calculation_version"],
            "suppressed": suppressed,
            "suppression_reason": suppression_reason,
        }
        set_cached_json(cache_key, resp_dict, ttl_seconds=300)
        return KPIResponse(**resp_dict)

    def get_timeseries(
        self,
        metric_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "month"
    ) -> KPITimeSeriesResponse:
        """Generates historical time series for the requested metric."""
        if interval not in ALLOWED_INTERVALS:
            raise BadRequestException(f"Invalid interval '{interval}'. Allowed intervals: {ALLOWED_INTERVALS}")
        if start_date and end_date and start_date > end_date:
            raise BadRequestException("start_date cannot be greater than end_date")

        cache_key = f"analytics:timeseries:{metric_code}:{interval}:{start_date}:{end_date}"
        cached = get_cached_json(cache_key)
        if cached:
            return KPITimeSeriesResponse(**cached)

        data = self.repo.get_timeseries(
            metric_code=metric_code,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        resp_dict = {
            "metric_code": metric_code,
            "interval": interval,
            "data": data,
        }
        set_cached_json(cache_key, resp_dict, ttl_seconds=300)
        return KPITimeSeriesResponse(**resp_dict)

    def get_comparison(self, metric_code: str, group_by: str = "facility") -> KPIComparisonResponse:
        """Compares metric distributions across facilities."""
        if group_by not in ("facility", "geography"):
            raise BadRequestException("group_by must be either 'facility' or 'geography'")

        cache_key = f"analytics:compare:{metric_code}:{group_by}"
        cached = get_cached_json(cache_key)
        if cached:
            return KPIComparisonResponse(**cached)

        data = self.repo.get_comparison(metric_code=metric_code, group_by=group_by)
        resp_dict = {
            "metric_code": metric_code,
            "group_by": group_by,
            "data": data,
        }
        set_cached_json(cache_key, resp_dict, ttl_seconds=300)
        return KPIComparisonResponse(**resp_dict)
