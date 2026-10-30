from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import OrderCreate, OrderRead, ManualOverrideRequest
from app.models.entities import Order
from app.services.order_service import OrderService
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderRead)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """Creates or ingests an incoming order."""
    existing = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if existing:
        return existing

    order = Order(
        order_id=payload.order_id,
        order_datetime=payload.order_datetime,
        customer_name=payload.customer_name,
        phone=payload.phone,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        order_value=payload.order_value,
        items=payload.items,
        num_items=payload.num_items,
        customer_prior_orders=payload.customer_prior_orders,
        customer_prior_rto=payload.customer_prior_rto,
        utm_source=payload.utm_source,
        courier=payload.courier,
        payment_method=payload.payment_method,
        workflow_status="RECEIVED"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("")
def list_orders(
    search: Optional[str] = Query(None, description="Search by Order ID, Customer Name, Phone, City"),
    action: Optional[str] = Query(None, description="Filter by decision action"),
    risk_band: Optional[str] = Query(None, description="Filter by risk band (LOW, MODERATE, ELEVATED, HIGH)"),
    workflow_status: Optional[str] = Query(None, description="Filter by operational status"),
    date_filter: Optional[str] = Query(None, description="Filter by date range (today, yesterday, last_7_days, last_30_days, all)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    courier: Optional[str] = Query(None, description="Filter by courier"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Returns paginated orders with privacy-masked customer phones and latest decision metrics."""
    return OrderService.get_orders(
        db=db,
        search=search,
        action=action,
        risk_band=risk_band,
        workflow_status=workflow_status,
        date_filter=date_filter,
        state=state,
        courier=courier,
        page=page,
        page_size=page_size
    )


@router.get("/{order_id}")
def get_order_details(order_id: str, db: Session = Depends(get_db)):
    """Returns complete details of an order including prediction, decision, events, and interactions."""
    detail = OrderService.get_order_detail(db, order_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return detail


@router.post("/{order_id}/override")
def manual_override_order(
    order_id: str,
    payload: ManualOverrideRequest,
    db: Session = Depends(get_db)
):
    """Allows operations to manually approve, hold, or cancel an order with reason audit."""
    try:
        res = OrderService.override_order_decision(
            db=db,
            order_id=order_id,
            new_action=payload.action,
            reason=payload.reason
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
