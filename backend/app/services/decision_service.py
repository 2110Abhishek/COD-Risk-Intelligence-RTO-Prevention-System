import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Order, RiskPrediction, OrderDecision, CustomerInteraction
from app.ml.predict import predict_rto_risk
from app.llm.validator import LLMValidatorService
from app.services.policy_service import PolicyService
from app.services.workflow_service import WorkflowService
from app.services.customer_history_service import CustomerHistoryService
from app.core.settings import settings


class DecisionService:
    @staticmethod
    def evaluate_order(
        db: Session,
        order_dict: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Full 10-step decision pipeline:
        1. Validate & fetch/store order
        2. Retrieve point-in-time customer history
        3. Score ML RTO probability
        4. Run LLM/deterministic address validation
        5. Apply business policy rules
        6. Compute financial intervention economics
        7. Persist prediction and decision records
        8. Initialize workflow state & automated mock messaging
        9. Return explainable result
        """
        order_id = order_dict["order_id"]
        order = db.query(Order).filter(Order.order_id == order_id).first()

        # If order not in DB, create it
        if not order:
            order = Order(
                order_id=order_id,
                order_datetime=order_dict.get("order_datetime") or datetime.utcnow(),
                customer_name=order_dict["customer_name"],
                phone=order_dict["phone"],
                address=order_dict["address"],
                city=order_dict.get("city"),
                state=order_dict.get("state"),
                pincode=order_dict.get("pincode"),
                order_value=float(order_dict["order_value"]),
                items=order_dict.get("items"),
                num_items=int(order_dict.get("num_items", 1)),
                customer_prior_orders=int(order_dict.get("customer_prior_orders", 0)),
                customer_prior_rto=int(order_dict.get("customer_prior_rto", 0)),
                utm_source=order_dict.get("utm_source"),
                courier=order_dict.get("courier"),
                payment_method=order_dict.get("payment_method", "COD"),
                workflow_status="RECEIVED"
            )
            db.add(order)
            db.commit()
            db.refresh(order)

        # 1. Point-in-time customer history
        history = CustomerHistoryService.get_point_in_time_customer_history(
            db, order.phone, current_order_id=order.order_id, as_of_datetime=order.order_datetime
        )
        if not history["is_first_time"]:
            order_dict["customer_prior_orders"] = history["prior_orders"]
            order_dict["customer_prior_rto"] = history["prior_rto"]

        # 2. Score with ML
        rto_prob, model_ver, features = predict_rto_risk(order_dict)

        # 3. Persist Prediction
        prediction = RiskPrediction(
            order_id=order_id,
            rto_probability=rto_prob,
            risk_band="MODERATE",  # will update after policy
            model_version=model_ver,
            feature_snapshot=features
        )
        db.add(prediction)

        # 4. LLM / Deterministic Address Assessment
        llm_res = LLMValidatorService.validate(
            customer_name=order.customer_name,
            address=order.address,
            city=order.city or "",
            state=order.state or "",
            config=config
        )

        # 5. Apply Policy Rules
        policy_res = PolicyService.evaluate_policy(
            order_data=order_dict,
            rto_probability=rto_prob,
            config=config,
            llm_assessment=llm_res
        )

        risk_band = policy_res["risk_band"]
        prediction.risk_band = risk_band
        action = policy_res["action"]
        operational_status = policy_res["operational_status"]
        reasons = policy_res["reason_codes"]
        explanation = policy_res["explanation"]
        fin_estimate = policy_res["financial_estimate"]
        rule_ver = policy_res["rule_version"]

        # 6. Persist Decision
        decision = OrderDecision(
            order_id=order_id,
            action=action,
            operational_status=operational_status,
            reason_codes=reasons,
            explanation=explanation,
            financial_estimate=fin_estimate,
            rule_version=rule_ver
        )
        db.add(decision)
        db.commit()

        # 7. Workflow Transition & Automated Mock Message trigger
        WorkflowService.transition_state(
            db=db,
            order=order,
            new_status=operational_status,
            event_type=f"EVALUATE_{action}",
            metadata={"probability": rto_prob, "reasons": reasons},
            actor="EVALUATION_ENGINE"
        )

        # Send initial WhatsApp mock message if needed
        brand_name = "Bliss Bloomly Haircare"
        if action == "SHIP_AFTER_CONFIRMATION":
            msg_text = (
                f"Hi {order.customer_name}! 👋\n\n"
                f"Thank you for ordering from {brand_name}.\n"
                f"Your order #{order.order_id} worth ₹{order.order_value:,.0f} is ready for dispatch.\n\n"
                f"Please confirm your order by replying YES.\n"
                f"Reply NO if you don't wish to continue.\n\n"
                f"Thank you!"
            )
            interaction = CustomerInteraction(
                order_id=order_id,
                channel="WHATSAPP",
                direction="OUTBOUND",
                template_key="CONFIRMATION_REQUEST",
                message=msg_text,
                delivery_status="DELIVERED"
            )
            db.add(interaction)
            db.commit()

        elif action == "NUDGE_TO_PREPAID":
            disc = config.get("prepaid_offer", {}).get("discount_amount", 15.0)
            pay_amt = max(0.0, order.order_value - disc)
            msg_text = (
                f"Hi {order.customer_name}! 👋\n\n"
                f"Your order #{order.order_id} is almost ready!\n"
                f"You can get ₹{disc:.0f} OFF by choosing prepaid payment.\n\n"
                f"Order Value: ₹{order.order_value:,.0f}\n"
                f"Prepaid Amount: ₹{pay_amt:,.0f}\n\n"
                f"Complete your payment using the secure link below:\n"
                f"https://pay.blissbloomly.com/mock-pay/{order.order_id}\n\n"
                f"You can also continue with COD if you prefer."
            )
            interaction = CustomerInteraction(
                order_id=order_id,
                channel="WHATSAPP",
                direction="OUTBOUND",
                template_key="PREPAID_NUDGE",
                message=msg_text,
                delivery_status="DELIVERED"
            )
            db.add(interaction)
            db.commit()

        return {
            "order_id": order_id,
            "rto_probability": rto_prob,
            "risk_band": risk_band,
            "action": action,
            "operational_status": operational_status,
            "reason_codes": reasons,
            "explanation": explanation,
            "financial_estimate": fin_estimate,
            "model_version": model_ver,
            "rule_version": rule_ver,
            "llm_status": llm_res.get("status", "SKIPPED"),
            "decision_timestamp": datetime.utcnow()
        }
