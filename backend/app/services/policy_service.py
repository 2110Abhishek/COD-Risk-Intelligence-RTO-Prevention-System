from typing import Dict, Any, List, Tuple
from app.services.financial_service import FinancialService
from app.utils.address import check_placeholder_name, assess_address_structure
from app.utils.phone import is_valid_indian_mobile


class PolicyService:
    @staticmethod
    def evaluate_policy(
        order_data: Dict[str, Any],
        rto_probability: float,
        config: Dict[str, Any],
        llm_assessment: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Deterministic decision policy engine.
        Maps ML probability, deterministic evidence, and configuration into:
        - action: SHIP_AS_IS, SHIP_AFTER_CONFIRMATION, NUDGE_TO_PREPAID, HOLD_CANCEL
        - operational_status: SHIP_APPROVED, AWAITING_CONFIRMATION, PREPAID_OFFERED, HOLD
        - reason_codes: List[str]
        - explanation: str
        """
        reason_codes: List[str] = []
        rule_version = config.get("policy_version", "1.0")
        thresholds = config.get("risk_thresholds", {
            "ship_as_is_max": 0.20,
            "confirmation_max": 0.40,
            "prepaid_max": 0.65,
            "hold_min": 0.65
        })
        protection = config.get("customer_protection", {
            "protect_first_time_customers": True,
            "manual_review_before_cancellation": True,
            "geography_alone_can_cancel": False,
            "llm_alone_can_cancel": False
        })
        prepaid_cfg = config.get("prepaid_offer", {"enabled": True, "discount_amount": 15.0})

        order_val = float(order_data.get("order_value", 0))
        cust_name = str(order_data.get("customer_name", ""))
        phone = str(order_data.get("phone", ""))
        address = str(order_data.get("address", ""))
        prior_orders = int(order_data.get("customer_prior_orders", 0))
        prior_rto = int(order_data.get("customer_prior_rto", 0))
        payment_method = str(order_data.get("payment_method", "COD")).upper()

        # Check 1: Non-COD orders
        if payment_method != "COD":
            reason_codes.append("PREPAID_ORDER")
            explanation = "This order is prepaid and already secured against COD refusal risk."
            fin_est = FinancialService.evaluate_order_intervention(order_val, rto_probability, "SHIP_AS_IS", config)
            return {
                "action": "SHIP_AS_IS",
                "operational_status": "SHIP_APPROVED",
                "risk_band": "LOW",
                "reason_codes": reason_codes,
                "explanation": explanation,
                "financial_estimate": fin_est,
                "rule_version": rule_version,
            }

        # Check 2: Deterministic Data Quality & Blockers
        name_check = check_placeholder_name(cust_name)
        addr_check = assess_address_structure(address)
        phone_valid = is_valid_indian_mobile(phone)

        if not phone_valid:
            reason_codes.append("INVALID_PHONE_FORMAT")
        if name_check["is_suspicious"]:
            reason_codes.append("SUSPICIOUS_CUSTOMER_NAME")
        if not addr_check["is_usable"]:
            reason_codes.append("INSUFFICIENT_ADDRESS")
        elif addr_check["has_landmark"]:
            reason_codes.append("USABLE_ADDRESS_WITH_LANDMARK")

        # Check customer history
        is_first_time = prior_orders == 0
        if is_first_time:
            reason_codes.append("FIRST_TIME_CUSTOMER")
        elif prior_rto > 0:
            reason_codes.append(f"PREVIOUS_RTO_HISTORY_{prior_rto}")
        else:
            reason_codes.append("REPEAT_DELIVERED_CUSTOMER")

        # Check LLM insights if available
        if llm_assessment and llm_assessment.get("status") == "COMPLETED":
            if llm_assessment.get("name_quality") == "SUSPICIOUS":
                reason_codes.append("LLM_FLAGGED_SUSPICIOUS_NAME")
            if llm_assessment.get("address_quality") in ("INSUFFICIENT", "NEEDS_CLARIFICATION"):
                reason_codes.append("LLM_FLAGGED_AMBIGUOUS_ADDRESS")

        # Determine Risk Band
        ship_as_is_max = thresholds.get("ship_as_is_max", 0.20)
        confirm_max = thresholds.get("confirmation_max", 0.40)
        prepaid_max = thresholds.get("prepaid_max", 0.65)

        if rto_probability < ship_as_is_max:
            risk_band = "LOW"
        elif rto_probability < confirm_max:
            risk_band = "MODERATE"
        elif rto_probability < prepaid_max:
            risk_band = "ELEVATED"
        else:
            risk_band = "HIGH"

        reason_codes.append(f"RISK_BAND_{risk_band}")

        # Check for Hard Blocker
        if not phone_valid or not addr_check["is_usable"] or name_check["is_suspicious"]:
            action = "HOLD_CANCEL"
            operational_status = "HOLD"
            explanation = "Order placed on hold due to data quality issues (invalid contact or unusable address description). Requires manual review."
            fin_est = FinancialService.evaluate_order_intervention(order_val, rto_probability, action, config)
            return {
                "action": action,
                "operational_status": operational_status,
                "risk_band": risk_band,
                "reason_codes": reason_codes,
                "explanation": explanation,
                "financial_estimate": fin_est,
                "rule_version": rule_version,
            }

        # Safe customer protection override: First-time customers are never cancelled
        if risk_band == "LOW":
            action = "SHIP_AS_IS"
            operational_status = "SHIP_APPROVED"
            explanation = "Predicted RTO probability is low. Delivery address is valid and usable for dispatch."

        elif risk_band == "MODERATE":
            action = "SHIP_AFTER_CONFIRMATION"
            operational_status = "AWAITING_CONFIRMATION"
            if is_first_time:
                explanation = "Moderate RTO probability for a first-time customer. WhatsApp confirmation requested to verify delivery intent."
            else:
                explanation = "Moderate RTO probability detected. Confirmation requested via WhatsApp before dispatch."

        elif risk_band == "ELEVATED":
            if prepaid_cfg.get("enabled", True):
                action = "NUDGE_TO_PREPAID"
                operational_status = "PREPAID_OFFERED"
                disc = prepaid_cfg.get("discount_amount", 15.0)
                explanation = f"Elevated delivery risk detected. Nudge sent offering ₹{disc} discount to convert order to prepaid."
            else:
                action = "SHIP_AFTER_CONFIRMATION"
                operational_status = "AWAITING_CONFIRMATION"
                explanation = "Elevated risk detected and prepaid offer is disabled; routed to customer confirmation."

        else:  # HIGH
            action = "HOLD_CANCEL"
            operational_status = "HOLD"
            explanation = "High predicted RTO risk. Order placed on hold for operations manual review."

        fin_est = FinancialService.evaluate_order_intervention(order_val, rto_probability, action, config)

        return {
            "action": action,
            "operational_status": operational_status,
            "risk_band": risk_band,
            "reason_codes": reason_codes,
            "explanation": explanation,
            "financial_estimate": fin_est,
            "rule_version": rule_version,
        }
