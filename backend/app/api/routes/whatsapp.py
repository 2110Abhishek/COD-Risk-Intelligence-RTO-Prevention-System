import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Order, CustomerInteraction
from app.schemas.schemas import WhatsAppSendRequest, WhatsAppReplyRequest, WhatsAppTimeoutRequest
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Simulator"])

YES_TERMS = {"yes", "y", "haan", "haa", "ha", "confirm", "confirmed", "send", "ok", "pls send"}
NO_TERMS = {"no", "n", "nahi", "cancel", "cancelled", "stop", "dont send", "don't send"}


@router.post("/send")
def send_mock_message(payload: WhatsAppSendRequest, db: Session = Depends(get_db)):
    """Generates an outbound mock WhatsApp message."""
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    brand = "Bliss Bloomly Haircare"
    if payload.template_type == "PREPAID_NUDGE":
        msg = (
            f"Hi {order.customer_name}! 👋\n\n"
            f"Your order #{order.order_id} is almost ready!\n"
            f"Save ₹15 instantly by paying online:\n"
            f"https://pay.blissbloomly.com/mock-pay/{order.order_id}\n\n"
            f"Or continue with COD if you prefer."
        )
    else:
        msg = (
            f"Hi {order.customer_name}! 👋\n\n"
            f"Thank you for ordering from {brand}.\n"
            f"Your order #{order.order_id} worth ₹{order.order_value:,.0f} is ready for dispatch.\n\n"
            f"Please confirm your order by replying YES.\n"
            f"Reply NO if you don't wish to continue."
        )

    interaction = CustomerInteraction(
        order_id=payload.order_id,
        channel="WHATSAPP",
        direction="OUTBOUND",
        template_key=payload.template_type,
        message=msg,
        delivery_status="DELIVERED"
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "status": "SENT",
        "message_id": interaction.id,
        "message": msg,
        "created_at": interaction.created_at.isoformat()
    }


@router.post("/reply")
def simulate_customer_reply(payload: WhatsAppReplyRequest, db: Session = Depends(get_db)):
    """
    Simulates an incoming WhatsApp reply from the customer.
    Deterministic parsing:
    - YES -> Confirms order and approves shipment
    - NO -> Customer declined, stops shipment
    - Ambiguous -> Requests clarification, holds dispatch
    """
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    clean_text = re.sub(r"[^\w\s]", "", payload.reply_text.lower()).strip()

    # 1. Record incoming message
    incoming = CustomerInteraction(
        order_id=order.order_id,
        channel="WHATSAPP",
        direction="INBOUND",
        message=payload.reply_text,
        delivery_status="RECEIVED"
    )
    db.add(incoming)
    db.commit()

    # 2. Classify response
    is_yes = clean_text in YES_TERMS or any(t in clean_text.split() for t in YES_TERMS)
    is_no = clean_text in NO_TERMS or any(t in clean_text.split() for t in NO_TERMS)

    if is_yes and not is_no:
        incoming.response_type = "YES"
        db.add(incoming)

        # Transition state
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status="CONFIRMED",
            event_type="CUSTOMER_REPLIED_YES",
            metadata={"reply": payload.reply_text}
        )
        # Release to SHIP_APPROVED
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status="SHIP_APPROVED",
            event_type="SHIPMENT_RELEASED_ON_CONFIRMATION"
        )

        reply_bot = "Thank you! Your order has been confirmed and is being packed for dispatch. 🚚"
        bot_msg = CustomerInteraction(
            order_id=order.order_id,
            channel="WHATSAPP",
            direction="OUTBOUND",
            template_key="CONFIRMATION_SUCCESS",
            message=reply_bot,
            delivery_status="DELIVERED"
        )
        db.add(bot_msg)
        db.commit()

        return {
            "classification": "YES",
            "workflow_status": "SHIP_APPROVED",
            "bot_reply": reply_bot,
            "order_id": order.order_id,
        }

    elif is_no:
        incoming.response_type = "NO"
        db.add(incoming)

        # Transition state
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status="CUSTOMER_DECLINED",
            event_type="CUSTOMER_REPLIED_NO",
            metadata={"reply": payload.reply_text}
        )
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status="CANCELLED",
            event_type="CANCELLED_ON_CUSTOMER_DECLINE"
        )

        reply_bot = "We have cancelled your order as requested. No charges will apply. Hope to serve you again! 🙏"
        bot_msg = CustomerInteraction(
            order_id=order.order_id,
            channel="WHATSAPP",
            direction="OUTBOUND",
            template_key="CANCELLATION_CONFIRMED",
            message=reply_bot,
            delivery_status="DELIVERED"
        )
        db.add(bot_msg)
        db.commit()

        return {
            "classification": "NO",
            "workflow_status": "CANCELLED",
            "bot_reply": reply_bot,
            "order_id": order.order_id,
        }

    else:
        # Ambiguous reply - DO NOT release shipment!
        incoming.response_type = "AMBIGUOUS"
        db.add(incoming)

        reply_bot = "We didn't quite catch that. Please reply YES to confirm your delivery or NO if you wish to cancel."
        bot_msg = CustomerInteraction(
            order_id=order.order_id,
            channel="WHATSAPP",
            direction="OUTBOUND",
            template_key="CLARIFICATION_PROMPT",
            message=reply_bot,
            delivery_status="DELIVERED"
        )
        db.add(bot_msg)
        db.commit()

        return {
            "classification": "AMBIGUOUS",
            "workflow_status": order.workflow_status,
            "bot_reply": reply_bot,
            "order_id": order.order_id,
        }


@router.post("/timeout")
def simulate_confirmation_timeout(payload: WhatsAppTimeoutRequest, db: Session = Depends(get_db)):
    """
    Simulates 24-hour expiration of confirmation window.
    Transitions order to HOLD and routes to operations queue.
    """
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{payload.order_id}' not found")

    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="CONFIRMATION_TIMEOUT",
        event_type="CONFIRMATION_WINDOW_EXPIRED"
    )
    WorkflowService.transition_state(
        db=db,
        order=order,
        new_status="HOLD",
        event_type="HELD_AWAITING_MANUAL_REVIEW"
    )

    return {
        "status": "TIMEOUT_APPLIED",
        "order_id": order.order_id,
        "workflow_status": "HOLD",
        "message": "24-hour confirmation window expired. Order placed on HOLD for operations review."
    }


@router.get("/conversations/{order_id}")
def get_conversation_history(order_id: str, db: Session = Depends(get_db)):
    """Retrieves all WhatsApp messages for the specified order."""
    interactions = db.query(CustomerInteraction).filter(
        CustomerInteraction.order_id == order_id
    ).order_by(CustomerInteraction.created_at).all()

    return [
        {
            "id": i.id,
            "order_id": i.order_id,
            "channel": i.channel,
            "direction": i.direction,
            "template_key": i.template_key,
            "message": i.message,
            "response_type": i.response_type,
            "delivery_status": i.delivery_status,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in interactions
    ]
