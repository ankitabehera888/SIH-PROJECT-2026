from typing import Optional, Tuple

def validate_metric_calculation(
    metric_code: str,
    metric_type: str,
    numerator: Optional[float],
    denominator: Optional[float],
    metric_value: Optional[float]
) -> Tuple[bool, Optional[str]]:
    """
    Applies mathematical and healthcare integrity checks to calculated KPI values.
    
    Rules:
    - Zero denominator -> metric_value MUST be None (NULL), never 0.0.
    - RATE: 0.0 <= metric_value <= 1.0.
    - RATE: numerator <= denominator.
    - COUNT, AVERAGE, MEDIAN, DURATION: metric_value >= 0.0.
    """
    # 1. Zero Denominator
    if denominator is not None and denominator == 0.0:
        if metric_value is not None:
            return False, f"Zero denominator for '{metric_code}' must produce NULL, not {metric_value}"
        return True, None
        
    if metric_value is None:
        return True, None
        
    # 2. Rate validation
    if metric_type == "RATE":
        if not (0.0 <= metric_value <= 1.0):
            return False, f"Rate metric '{metric_code}' value {metric_value} is out of bounds [0.0, 1.0]"
        if numerator is not None and denominator is not None and numerator > denominator:
            return False, f"Rate metric '{metric_code}' numerator ({numerator}) exceeds denominator ({denominator})"
            
    # 3. Non-negative validation for Counts & Durations
    if metric_type in ("COUNT", "AVERAGE", "MEDIAN", "DURATION"):
        if metric_value < 0.0:
            return False, f"Metric '{metric_code}' produced negative value: {metric_value}"
            
    return True, None
