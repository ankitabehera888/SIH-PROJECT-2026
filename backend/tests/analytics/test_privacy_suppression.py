from datetime import date
from unittest.mock import MagicMock
from app.services.analytics.kpi_service import KPIService, MIN_AGGREGATE_COUNT

def test_privacy_suppression_under_threshold():
    """Verify that when a KPI denominator is under MIN_AGGREGATE_COUNT (10), it is suppressed."""
    mock_db = MagicMock()
    service = KPIService(mock_db)
    
    # Mock repository return with denominator = 5 (< 10)
    service.repo.get_kpi = MagicMock(return_value={
        "metric_code": "rare_disease_rate",
        "metric_name": "Rare Disease Rate",
        "metric_type": "RATE",
        "period_start": date(2026, 1, 1),
        "period_end": date(2026, 12, 31),
        "numerator": 2.0,
        "denominator": 5.0,  # Below threshold
        "metric_value": 0.4,
        "calculation_version": "1.0.0",
    })
    
    resp = service.get_kpi("rare_disease_rate")
    assert resp.suppressed is True
    assert resp.suppression_reason == "small_population"
    assert resp.value is None
    assert resp.denominator == 5.0

def test_privacy_non_suppression_above_threshold():
    """Verify that when a KPI denominator is >= MIN_AGGREGATE_COUNT (10), it is not suppressed."""
    mock_db = MagicMock()
    service = KPIService(mock_db)
    
    service.repo.get_kpi = MagicMock(return_value={
        "metric_code": "common_disease_rate",
        "metric_name": "Common Disease Rate",
        "metric_type": "RATE",
        "period_start": date(2026, 1, 1),
        "period_end": date(2026, 12, 31),
        "numerator": 20.0,
        "denominator": 100.0,  # Well above threshold
        "metric_value": 0.2,
        "calculation_version": "1.0.0",
    })
    
    resp = service.get_kpi("common_disease_rate")
    assert resp.suppressed is False
    assert resp.suppression_reason is None
    assert float(resp.value) == 0.2
