from typing import Dict, List, Tuple

def calculate_quality_score(check_results: List[Dict]) -> Tuple[float, str, int, int]:
    """
    Computes a weighted quality score (0.0 - 100.0) across all evaluated checks.
    
    CRITICAL RULE:
    Critical failures override the score. If any CRITICAL check fails,
    the status is immediately 'CRITICAL' / 'BLOCKED'.
    """
    if not check_results:
        return 100.0, "HEALTHY", 0, 0

    total_checks = len(check_results)
    passed_checks = sum(1 for c in check_results if c["status"] == "PASS")
    warnings = sum(1 for c in check_results if c["status"] == "WARNING")
    critical_failures = sum(1 for c in check_results if c["status"] in ("FAIL", "ERROR") and c["severity"] == "CRITICAL")

    # Base pass percentage
    base_score = round((passed_checks / total_checks) * 100.0, 1)

    # Status Determination with Critical Failure Override
    if critical_failures > 0:
        overall_status = "CRITICAL"
    elif warnings > 2:
        overall_status = "DEGRADED"
    elif warnings > 0:
        overall_status = "WARNING"
    else:
        overall_status = "HEALTHY"

    return base_score, overall_status, warnings, critical_failures
