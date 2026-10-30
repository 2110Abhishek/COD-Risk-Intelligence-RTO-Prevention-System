from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.api.routes.configuration import load_active_config_from_file

router = APIRouter(prefix="/dashboard", tags=["Founder Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    date_filter: Optional[str] = Query("yesterday", description="Filter period: today, yesterday, last_7_days, last_30_days, all"),
    db: Session = Depends(get_db)
):
    """
    Returns single-screen overview of COD order decisions, RTO savings, cancellation opportunity losses, and net financial impact.
    """
    cfg = load_active_config_from_file()
    return DashboardService.get_dashboard_summary(db=db, config=cfg, date_filter=date_filter)


@router.get("/financial-impact")
def get_financial_impact_breakdown(db: Session = Depends(get_db)):
    """Returns granular financial component breakdown with explicit formulas and assumptions."""
    cfg = load_active_config_from_file()
    summary = DashboardService.get_dashboard_summary(db=db, config=cfg)
    return summary["financial_impact"]


@router.get("/decision-distribution")
def get_decision_distribution(db: Session = Depends(get_db)):
    """Returns order counts across all four decision categories."""
    cfg = load_active_config_from_file()
    summary = DashboardService.get_dashboard_summary(db=db, config=cfg)
    return summary["bucket_counts"]


@router.get("/trends")
def get_historical_trends(db: Session = Depends(get_db)):
    """Returns daily time-series of orders, RTO rates, and COD volume."""
    return DashboardService.get_trends(db)
