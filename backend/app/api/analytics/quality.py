from typing import Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.core.roles import UserRole
from app.db.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/quality",
    tags=["Data Quality Monitoring (Admin Only)"],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)

class QualityCheckSummary(BaseModel):
    total: int
    passed: int
    warnings: int
    critical: int

class QualitySummaryResponse(BaseModel):
    quality_score: float
    status: str
    checks: QualityCheckSummary

class QualityAlertItem(BaseModel):
    alert_code: str
    severity: str
    status: str
    message: str
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

class QualityAlertsResponse(BaseModel):
    data: List[QualityAlertItem]

@router.get("/summary", response_model=QualitySummaryResponse, summary="Get Platform Quality Summary")
def get_quality_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Returns continuous data quality score and check status for the platform."""
    # Query latest quality check results
    query = text("""
        WITH latest_run AS (
            SELECT pipeline_run_id
            FROM analytics.quality_check_results
            ORDER BY execution_time DESC
            LIMIT 1
        )
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status = 'PASS') AS passed,
            COUNT(*) FILTER (WHERE status = 'WARNING') AS warnings,
            COUNT(*) FILTER (WHERE status IN ('FAIL', 'ERROR') AND severity = 'CRITICAL') AS critical
        FROM analytics.quality_check_results
        WHERE pipeline_run_id = (SELECT pipeline_run_id FROM latest_run);
    """)
    r = db.execute(query).fetchone()
    if not r or r[0] == 0:
        return QualitySummaryResponse(
            quality_score=100.0,
            status="HEALTHY",
            checks=QualityCheckSummary(total=0, passed=0, warnings=0, critical=0),
        )

    total = r[0]
    passed = r[1]
    warnings = r[2]
    critical = r[3]
    score = round((passed / total) * 100.0, 1)

    if critical > 0:
        status = "CRITICAL"
    elif warnings > 2:
        status = "DEGRADED"
    elif warnings > 0:
        status = "WARNING"
    else:
        status = "HEALTHY"

    return QualitySummaryResponse(
        quality_score=score,
        status=status,
        checks=QualityCheckSummary(total=total, passed=passed, warnings=warnings, critical=critical),
    )

@router.get("/alerts", response_model=QualityAlertsResponse, summary="Get Quality Alerts")
def get_quality_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Lists recent quality alerts across operational and analytical datasets."""
    query = text("""
        SELECT
            alert_code,
            severity,
            status,
            message,
            TO_CHAR(created_at, 'YYYY-MM-DD"T"HH24:MI:SS') AS created_at,
            TO_CHAR(resolved_at, 'YYYY-MM-DD"T"HH24:MI:SS') AS resolved_at
        FROM analytics.quality_alerts
        ORDER BY created_at DESC
        LIMIT 50;
    """)
    rows = db.execute(query).fetchall()
    return QualityAlertsResponse(
        data=[
            QualityAlertItem(
                alert_code=r[0],
                severity=r[1],
                status=r[2],
                message=r[3],
                created_at=r[4],
                resolved_at=r[5],
            )
            for r in rows
        ]
    )
