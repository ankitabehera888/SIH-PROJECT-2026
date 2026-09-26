"""Healthcare Platform — Metrics & KPIs Module."""

from .definitions import METRIC_CATALOG, MetricDefinition
from .registry import sync_metric_registry
from .validation import validate_metric_calculation
from .aggregations import compute_facility_aggregations, compute_geography_aggregations
from .versioning import get_metric_lineage_metadata, DEFAULT_METRIC_VERSION
from .calculator import calculate_all_metrics

__all__ = [
    "METRIC_CATALOG",
    "MetricDefinition",
    "sync_metric_registry",
    "validate_metric_calculation",
    "compute_facility_aggregations",
    "compute_geography_aggregations",
    "get_metric_lineage_metadata",
    "DEFAULT_METRIC_VERSION",
    "calculate_all_metrics",
]
