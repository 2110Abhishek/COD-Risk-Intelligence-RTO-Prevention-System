import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.entities import Order, PaymentAttempt, SystemConfiguration
from app.schemas.schemas import CreateMockPaymentRequest, MockPaymentActionRequest
from app.services.workflow_service import WorkflowService
from app.api.routes.configuration import load_active_config_from_file

router = APIRouter(prefix="/payments", tags=["Payment Simulation"])


@router.post("/create-mock")
def create_mock_payment_link(payload: CreateMockPaymentRequest, db: Session = Depends(get_db)):
    """
    Generates a simulated prepaid payment link with configured ₹15 discount.
    """
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    cfg = load_active_config_from_file()
    discount_amount = float(cfg.get("prepaid_offer", {}).get("discount_amount", 15.0))
    original_val = float(order.order_value)
    payable_val = max(0.0, original_val - discount_amount)

    ref = f"MOCK_TXN_{order.order_id}_{uuid.uuid4().hex[:8].upper()}"

    attempt = PaymentAttempt(
        order_id=order.order_id,
        original_amount=original_val,
        discount_amount=discount_amount,
        payable_amount=payable_val,
        payment_status="PENDING",
        transaction_reference=ref
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="PAYMENT_PENDING",
        event_type="PREPAID_PAYMENT_INITIATED",
        metadata={"transaction_reference": ref, "payable_amount": payable_val}
    )

    return {
        "status": "CREATED",
        "order_id": order.order_id,
        "transaction_reference": ref,
        "original_amount": original_val,
        "discount_amount": discount_amount,
        "payable_amount": payable_val,
        "payment_link": f"https://pay.blissbloomly.com/mock-pay/{order.order_id}?ref={ref}"
    }


@router.post("/mock-success")
def simulate_payment_success(payload: MockPaymentActionRequest, db: Session = Depends(get_db)):
    """
    Simulates successful prepaid payment:
    - Marks payment SUCCESSFUL
    - Updates order payment_method to PREPAID
    - Releases order for dispatch (SHIP_APPROVED)
    """
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    attempt = db.query(PaymentAttempt).filter(
        PaymentAttempt.order_id == payload.order_id,
        PaymentAttempt.payment_status == "PENDING"
    ).order_by(desc(PaymentAttempt.created_at)).first()

    if not attempt:
        # Create one on the fly if user clicks success directly
        attempt = PaymentAttempt(
            order_id=order.order_id,
            original_amount=order.order_value,
            discount_amount=15.0,
            payable_amount=max(0.0, order.order_value - 15.0),
            payment_status="PENDING",
            transaction_reference=f"MOCK_TXN_{order.order_id}_{uuid.uuid4().hex[:8].upper()}"
        )
        db.add(attempt)

    attempt.payment_status = "SUCCESSFUL"
    order.payment_method = "PREPAID"
    db.add(attempt)
    db.add(order)
    db.commit()

    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="PAYMENT_SUCCESSFUL",
        event_type="PREPAID_PAYMENT_CONFIRMED",
        metadata={"txn_ref": attempt.transaction_reference}
    )
    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="SHIP_APPROVED",
        event_type="SHIPMENT_RELEASED_PREPAID_ORDER"
    )

    return {
        "status": "SUCCESSFUL",
        "order_id": order.order_id,
        "payment_method": "PREPAID",
        "workflow_status": "SHIP_APPROVED",
        "transaction_reference": attempt.transaction_reference,
        "message": f"Prepaid payment of ₹{attempt.payable_amount:,.0f} verified. Order approved for shipment."
    }


@router.post("/mock-failure")
def simulate_payment_failure(payload: MockPaymentActionRequest, db: Session = Depends(get_db)):
    """
    Simulates failed payment attempt:
    - Retains original COD order
    - Leaves payment status FAILED
    - Does NOT release shipment
    """
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    attempt = db.query(PaymentAttempt).filter(
        PaymentAttempt.order_id == payload.order_id
    ).order_by(desc(PaymentAttempt.created_at)).first()

    if attempt:
        attempt.payment_status = "FAILED"
        db.add(attempt)
        db.commit()

    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="AWAITING_CONFIRMATION",
        event_type="PAYMENT_FAILED_REVERTED_TO_COD",
        metadata={"reverted_payment_method": "COD"}
    )

    return {
        "status": "FAILED",
        "order_id": order.order_id,
        "payment_method": "COD",
        "workflow_status": "AWAITING_CONFIRMATION",
        "message": "Payment failed. Order retained as Cash on Delivery awaiting confirmation."
    }
