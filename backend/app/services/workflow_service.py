from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import Order, OrderEvent, AuditLog


VALID_TRANSITIONS: Dict[str, set[str]] = {
    "RECEIVED": {"VALIDATING", "EVALUATED", "SHIP_APPROVED", "AWAITING_CONFIRMATION", "PREPAID_OFFERED", "HOLD"},
    "VALIDATING": {"EVALUATED", "HOLD"},
    "EVALUATED": {"SHIP_APPROVED", "AWAITING_CONFIRMATION", "PREPAID_OFFERED", "HOLD"},
    "AWAITING_CONFIRMATION": {"CONFIRMED", "CUSTOMER_DECLINED", "CONFIRMATION_TIMEOUT", "HOLD", "PAYMENT_PENDING", "PAYMENT_SUCCESSFUL"},
    "CONFIRMED": {"SHIP_APPROVED"},
    "PREPAID_OFFERED": {"PAYMENT_PENDING", "PAYMENT_SUCCESSFUL", "HOLD", "AWAITING_CONFIRMATION", "CONFIRMED", "CUSTOMER_DECLINED", "CONFIRMATION_TIMEOUT"},
    "PAYMENT_PENDING": {"PAYMENT_SUCCESSFUL", "HOLD", "AWAITING_CONFIRMATION", "CUSTOMER_DECLINED"},
    "PAYMENT_SUCCESSFUL": {"SHIP_APPROVED"},
    "CONFIRMATION_TIMEOUT": {"HOLD", "MANUAL_REVIEW"},
    "CUSTOMER_DECLINED": {"CANCELLED"},
    "HOLD": {"MANUAL_REVIEW", "SHIP_APPROVED", "CANCELLED", "AWAITING_CONFIRMATION", "CONFIRMED"},
    "MANUAL_REVIEW": {"SHIP_APPROVED", "CANCELLED", "HOLD", "AWAITING_CONFIRMATION"},
    "SHIP_APPROVED": {"DISPATCHED", "HOLD", "PAYMENT_PENDING", "PAYMENT_SUCCESSFUL", "AWAITING_CONFIRMATION", "CONFIRMED", "CUSTOMER_DECLINED", "CONFIRMATION_TIMEOUT"},
    "DISPATCHED": {"DELIVERED", "RTO"},
    "CANCELLED": set(),
    "DELIVERED": set(),
    "RTO": set(),
}


class WorkflowService:
    @staticmethod
    def transition_state(
        db: Session,
        order: Order,
        new_status: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        actor: str = "SYSTEM",
        override_reason: Optional[str] = None
    ) -> Order:
        """
        Server-side state machine enforcement.
        Rejects invalid transitions and logs an immutable order event.
        """
        current_status = order.workflow_status or "RECEIVED"
        
        # Allow idempotent same-state events (e.g. re-evaluating)
        if current_status != new_status:
            allowed = VALID_TRANSITIONS.get(current_status, set())
            # Super-admin/manual override/eval engine can transition without being blocked by previous simulator state
            if new_status not in allowed and actor not in ("EVALUATION_ENGINE", "OPERATIONS_MANAGER", "SYSTEM_OVERRIDE"):
                raise ValueError(
                    f"Invalid state transition from '{current_status}' to '{new_status}'. Allowed transitions: {sorted(allowed)}"
                )

        # Update order state
        order.workflow_status = new_status
        db.add(order)

        # Append OrderEvent
        event = OrderEvent(
            order_id=order.order_id,
            event_type=event_type,
            previous_status=current_status,
            new_status=new_status,
            metadata_json=metadata or {}
        )
        db.add(event)

        # If override, record audit log
        if override_reason:
            audit = AuditLog(
                actor=actor,
                action=f"STATE_TRANSITION_{event_type}",
                entity_type="ORDER",
                entity_id=order.order_id,
                previous_value={"status": current_status},
                new_value={"status": new_status},
                reason=override_reason
            )
            db.add(audit)

        db.commit()
        db.refresh(order)
        return order
