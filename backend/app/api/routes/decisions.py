from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.schemas.schemas import EvaluateOrderRequest, EvaluateOrderResponse, DecisionRead
from app.models.entities import OrderDecision, SystemConfiguration
from app.services.decision_service import DecisionService
from app.api.routes.configuration import load_active_config_from_file

router = APIRouter(prefix="/decisions", tags=["Decision Engine"])


def get_current_policy(db: Session) -> dict:
    db_config = db.query(SystemConfiguration).filter(SystemConfiguration.configuration_key == "active_policy").first()
    if db_config:
        return db_config.configuration_value
    return load_active_config_from_file()


@router.post("/evaluate", response_model=EvaluateOrderResponse)
def evaluate_order(payload: EvaluateOrderRequest, db: Session = Depends(get_db)):
    """
    Evaluates an incoming COD order.
    Returns calibrated probability, recommended action, reason codes, plain-English explanation, and financial estimates.
    """
    config = get_current_policy(db)
    order_dict = payload.model_dump()
    result = DecisionService.evaluate_order(db=db, order_dict=order_dict, config=config)
    return result


@router.get("/{order_id}")
def get_order_decision(order_id: str, db: Session = Depends(get_db)):
    """Retrieves the latest decision and financial estimate for an order."""
    dec = db.query(OrderDecision).filter(OrderDecision.order_id == order_id).order_by(desc(OrderDecision.created_at)).first()
    if not dec:
        raise HTTPException(status_code=404, detail=f"No decision found for order '{order_id}'")
    return {
        "id": dec.id,
        "order_id": dec.order_id,
        "action": dec.action,
        "operational_status": dec.operational_status,
        "reason_codes": dec.reason_codes,
        "explanation": dec.explanation,
        "financial_estimate": dec.financial_estimate,
        "rule_version": dec.rule_version,
        "is_override": dec.is_override,
        "override_reason": dec.override_reason,
        "created_at": dec.created_at.isoformat() if dec.created_at else None,
    }


@router.get("")
def list_decisions(
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieves recent decision records for audit and logs."""
    query = db.query(OrderDecision)
    if action:
        query = query.filter(OrderDecision.action == action)
    decisions = query.order_by(desc(OrderDecision.created_at)).limit(limit).all()
    return [
        {
            "id": d.id,
            "order_id": d.order_id,
            "action": d.action,
            "operational_status": d.operational_status,
            "reason_codes": d.reason_codes,
            "explanation": d.explanation,
            "rule_version": d.rule_version,
            "is_override": d.is_override,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in decisions
    ]
