from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException
from app.repositories.analytics.dashboard_repository import DashboardRepository
from app.schemas.analytics.dashboard import (
    AppointmentSummaryResponse,
    AppointmentTrendsResponse,
    ReferralSummaryResponse,
    ReferralAgingResponse,
    CohortSummaryResponse,
    DashboardOverviewResponse,
)
from app.schemas.analytics.facility import FacilityAnalyticsResponse, GeographyAnalyticsResponse
from app.services.analytics.cache import get_cached_json, set_cached_json

class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_appointment_summary(self) -> AppointmentSummaryResponse:
        cache_key = "analytics:dashboard:appointment_summary"
        cached = get_cached_json(cache_key)
        if cached:
            return AppointmentSummaryResponse(**cached)
        res = self.repo.get_appointment_summary()
        set_cached_json(cache_key, res, ttl_seconds=300)
        return AppointmentSummaryResponse(**res)

    def get_appointment_trends(self) -> AppointmentTrendsResponse:
        cache_key = "analytics:dashboard:appointment_trends"
        cached = get_cached_json(cache_key)
        if cached:
            return AppointmentTrendsResponse(**cached)
        res = {"data": self.repo.get_appointment_trends()}
        set_cached_json(cache_key, res, ttl_seconds=300)
        return AppointmentTrendsResponse(**res)

    def get_referral_summary(self) -> ReferralSummaryResponse:
        cache_key = "analytics:dashboard:referral_summary"
        cached = get_cached_json(cache_key)
        if cached:
            return ReferralSummaryResponse(**cached)
        res = self.repo.get_referral_summary()
        set_cached_json(cache_key, res, ttl_seconds=300)
        return ReferralSummaryResponse(**res)

    def get_referral_aging(self) -> ReferralAgingResponse:
        cache_key = "analytics:dashboard:referral_aging"
        cached = get_cached_json(cache_key)
        if cached:
            return ReferralAgingResponse(**cached)
        res = {"buckets": self.repo.get_referral_aging()}
        set_cached_json(cache_key, res, ttl_seconds=300)
        return ReferralAgingResponse(**res)

    def get_cohort_summary(self) -> CohortSummaryResponse:
        cache_key = "analytics:dashboard:cohort_summary"
        cached = get_cached_json(cache_key)
        if cached:
            return CohortSummaryResponse(**cached)
        res = {"data": self.repo.get_cohort_summary()}
        set_cached_json(cache_key, res, ttl_seconds=300)
        return CohortSummaryResponse(**res)

    def get_facility_analytics(self, page: int = 1, page_size: int = 20) -> FacilityAnalyticsResponse:
        if page < 1:
            raise BadRequestException("page must be greater than or equal to 1")
        if page_size < 1 or page_size > 100:
            raise BadRequestException("page_size must be between 1 and 100")

        cache_key = f"analytics:dashboard:facilities:{page}:{page_size}"
        cached = get_cached_json(cache_key)
        if cached:
            return FacilityAnalyticsResponse(**cached)

        total, data = self.repo.get_facility_analytics(page=page, page_size=page_size)
        res = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": data,
        }
        set_cached_json(cache_key, res, ttl_seconds=300)
        return FacilityAnalyticsResponse(**res)

    def get_geography_analytics(self, page: int = 1, page_size: int = 20) -> GeographyAnalyticsResponse:
        if page < 1:
            raise BadRequestException("page must be greater than or equal to 1")
        if page_size < 1 or page_size > 100:
            raise BadRequestException("page_size must be between 1 and 100")

        cache_key = f"analytics:dashboard:geography:{page}:{page_size}"
        cached = get_cached_json(cache_key)
        if cached:
            return GeographyAnalyticsResponse(**cached)

        total, data = self.repo.get_geography_analytics(page=page, page_size=page_size)
        res = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": data,
        }
        set_cached_json(cache_key, res, ttl_seconds=300)
        return GeographyAnalyticsResponse(**res)

    def get_dashboard_overview(self) -> DashboardOverviewResponse:
        cache_key = "analytics:dashboard:overview"
        cached = get_cached_json(cache_key)
        if cached:
            return DashboardOverviewResponse(**cached)
        res = self.repo.get_dashboard_overview()
        set_cached_json(cache_key, res, ttl_seconds=300)
        return DashboardOverviewResponse(**res)
