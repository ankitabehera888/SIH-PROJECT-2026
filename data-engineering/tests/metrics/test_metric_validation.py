from src.metrics.validation import validate_metric_calculation
from src.metrics.calculator import calculate_all_metrics

def test_rate_calculation_valid():
    """Verify rate validation succeeds for standard valid numbers."""
    is_val, err = validate_metric_calculation("test_rate", "RATE", 80.0, 100.0, 0.80)
    assert is_val
    assert err is None

def test_zero_denominator_returns_null_not_zero():
    """Verify zero denominator requires metric_value to be None (NULL), never 0.0."""
    # When denominator is 0.0, metric_value must be None
    is_val_null, _ = validate_metric_calculation("test_rate", "RATE", 0.0, 0.0, None)
    assert is_val_null
    
    # If someone tries to pass 0.0 instead of None, it must be flagged
    is_val_zero, err = validate_metric_calculation("test_rate", "RATE", 0.0, 0.0, 0.0)
    assert not is_val_zero
    assert "Zero denominator" in err

def test_numerator_exceeds_denominator_fails():
    """Verify validation error when numerator exceeds denominator for a rate."""
    is_val, err = validate_metric_calculation("test_rate", "RATE", 120.0, 100.0, 1.20)
    assert not is_val
    assert "out of bounds" in err or "exceeds" in err

def test_negative_duration_fails():
    """Verify validation error for negative duration or count."""
    is_val, err = validate_metric_calculation("test_duration", "DURATION", None, None, -5.0)
    assert not is_val
    assert "negative" in err

def test_metrics_calculator_reproducibility():
    """Verify that running calculate_all_metrics twice produces identical results."""
    res1 = calculate_all_metrics(run_id="run_test_1")
    res2 = calculate_all_metrics(run_id="run_test_2")
    
    vals1 = {r["metric_code"]: r["metric_value"] for r in res1["summary"]}
    vals2 = {r["metric_code"]: r["metric_value"] for r in res2["summary"]}
    
    assert vals1 == vals2, f"Discrepancy in metric calculation runs: {vals1} vs {vals2}"
