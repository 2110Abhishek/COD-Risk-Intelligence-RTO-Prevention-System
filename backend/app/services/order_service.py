from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.models.entities import Order, OrderDecision, RiskPrediction, CustomerInteraction, PaymentAttempt, OrderEvent, AuditLog
from app.utils.phone import mask_phone_number
from app.services.workflow_service import WorkflowService


class OrderService:
    @staticmethod
    def get_orders(
        db: Session,
        search: Optional[str] = None,
        action: Optional[str] = None,
        risk_band: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_filter: Optional[str] = None,
        state: Optional[str] = None,
        courier: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieves paginated and filtered orders with masked phone numbers.
        """
        from datetime import datetime
        query = db.query(Order)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Order.order_id.ilike(s),
                    Order.customer_name.ilike(s),
                    Order.phone.ilike(s),
                    Order.city.ilike(s),
                )
            )

        if workflow_status:
            query = query.filter(Order.workflow_status == workflow_status)
        if state:
            query = query.filter(Order.state.ilike(f"%{state}%"))
        if courier:
            query = query.filter(Order.courier.ilike(f"%{courier}%"))

        if date_filter and date_filter != "all":
            now = datetime.utcnow()
            if date_filter == "today":
                query = query.filter(Order.order_datetime >= datetime(now.year, now.month, now.day, 0, 0, 0))
            elif date_filter == "yesterday":
                query = query.filter(Order.order_datetime >= datetime(2026, 9, 30, 0, 0, 0), Order.order_datetime <= datetime(2026, 9, 30, 23, 59, 59))
            elif date_filter == "last_7_days":
                query = query.filter(Order.order_datetime >= datetime(2026, 9, 24, 0, 0, 0), Order.order_datetime <= datetime(2026, 9, 30, 23, 59, 59))
            elif date_filter == "last_30_days":
                query = query.filter(Order.order_datetime >= datetime(2026, 9, 1, 0, 0, 0), Order.order_datetime <= datetime(2026, 9, 30, 23, 59, 59))

        total = query.count()
        orders = query.order_by(desc(Order.order_datetime)).offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for o in orders:
            # Latest decision
            dec = db.query(OrderDecision).filter(OrderDecision.order_id == o.order_id).order_by(desc(OrderDecision.created_at)).first()
            # Latest prediction
            pred = db.query(RiskPrediction).filter(RiskPrediction.order_id == o.order_id).order_by(desc(RiskPrediction.created_at)).first()

            if action and (not dec or dec.action != action):
                continue
            if risk_band and (not pred or pred.risk_band != risk_band):
                continue

            items.append({
                "id": o.id,
                "order_id": o.order_id,
                "customer_name": o.customer_name,
                "phone_masked": mask_phone_number(o.phone),
                "address": o.address,
                "city": o.city,
                "state": o.state,
                "pincode": o.pincode,
                "order_value": o.order_value,
                "payment_method": o.payment_method,
                "workflow_status": o.workflow_status,
                "final_status": o.final_status,
                "order_datetime": o.order_datetime.isoformat() if o.order_datetime else None,
                "decision": dec.action if dec else "PENDING",
                "risk_band": pred.risk_band if pred else "UNKNOWN",
                "rto_probability": pred.rto_probability if pred else None,
                "explanation": dec.explanation if dec else None,
            })

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
            "orders": items,
        }

    @staticmethod
    def get_order_detail(db: Session, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves complete order detail with predictions, decisions,
        interactions, payment history, and audit timeline.
        """
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return None

        dec = db.query(OrderDecision).filter(OrderDecision.order_id == order_id).order_by(desc(OrderDecision.created_at)).first()
        pred = db.query(RiskPrediction).filter(RiskPrediction.order_id == order_id).order_by(desc(RiskPrediction.created_at)).first()
        interactions = db.query(CustomerInteraction).filter(CustomerInteraction.order_id == order_id).order_by(CustomerInteraction.created_at).all()
        payments = db.query(PaymentAttempt).filter(PaymentAttempt.order_id == order_id).order_by(PaymentAttempt.created_at).all()
        events = db.query(OrderEvent).filter(OrderEvent.order_id == order_id).order_by(OrderEvent.created_at).all()

        return {
            "order": {
                "id": order.id,
                "order_id": order.order_id,
                "customer_name": order.customer_name,
                "phone": mask_phone_number(order.phone),
                "raw_phone_authorized": order.phone,
                "address": order.address,
                "city": order.city,
                "state": order.state,
                "pincode": order.pincode,
                "order_value": order.order_value,
                "items": order.items,
                "num_items": order.num_items,
                "customer_prior_orders": order.customer_prior_orders,
                "customer_prior_rto": order.customer_prior_rto,
                "utm_source": order.utm_source,
                "courier": order.courier,
                "payment_method": order.payment_method,
                "workflow_status": order.workflow_status,
                "final_status": order.final_status,
                "order_datetime": order.order_datetime.isoformat() if order.order_datetime else None,
            },
            "latest_decision": {
                "action": dec.action if dec else None,
                "operational_status": dec.operational_status if dec else None,
                "reason_codes": dec.reason_codes if dec else [],
                "explanation": dec.explanation if dec else None,
                "financial_estimate": dec.financial_estimate if dec else {},
                "rule_version": dec.rule_version if dec else None,
                "is_override": dec.is_override if dec else False,
                "override_reason": dec.override_reason if dec else None,
                "created_at": dec.created_at.isoformat() if dec else None,
            } if dec else None,
            "latest_prediction": {
                "rto_probability": pred.rto_probability if pred else None,
                "risk_band": pred.risk_band if pred else None,
                "model_version": pred.model_version if pred else None,
                "feature_snapshot": pred.feature_snapshot if pred else {},
                "created_at": pred.created_at.isoformat() if pred else None,
            } if pred else None,
            "interactions": [
                {
                    "id": i.id,
                    "channel": i.channel,
                    "direction": i.direction,
                    "template_key": i.template_key,
                    "message": i.message,
                    "response_type": i.response_type,
                    "delivery_status": i.delivery_status,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in interactions
            ],
            "payments": [
                {
                    "id": p.id,
                    "original_amount": p.original_amount,
                    "discount_amount": p.discount_amount,
                    "payable_amount": p.payable_amount,
                    "payment_status": p.payment_status,
                    "transaction_reference": p.transaction_reference,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in payments
            ],
            "timeline": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "previous_status": e.previous_status,
                    "new_status": e.new_status,
                    "metadata": e.metadata_json,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in events
            ]
        }

    @staticmethod
    def override_order_decision(
        db: Session,
        order_id: str,
        new_action: str,
        reason: str,
        actor: str = "OPERATIONS_MANAGER"
    ) -> Dict[str, Any]:
        """
        Allows an authorized user to override an order decision (e.g. approve ship, hold, or cancel).
        Enforces audit trail and server-side state transitions.
        """
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError(f"Order #{order_id} not found")

        # Map action to target status
        target_status_map = {
            "SHIP_APPROVED": "SHIP_APPROVED",
            "HOLD": "HOLD",
            "CANCELLED": "CANCELLED",
        }
        target_status = target_status_map.get(new_action)
        if not target_status:
            raise ValueError(f"Invalid override action '{new_action}'. Must be SHIP_APPROVED, HOLD, or CANCELLED")

        # Transition state
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status=target_status,
            event_type=f"MANUAL_OVERRIDE_{new_action}",
            metadata={"override_reason": reason, "actor": actor},
            actor=actor,
            override_reason=reason
        )

        # Mark latest decision as overridden
        dec = db.query(OrderDecision).filter(OrderDecision.order_id == order_id).order_by(desc(OrderDecision.created_at)).first()
        if dec:
            dec.is_override = True
            dec.override_reason = reason
            dec.operational_status = target_status
            db.add(dec)
            db.commit()

        return {"status": "SUCCESS", "order_id": order_id, "new_status": target_status, "reason": reason}
