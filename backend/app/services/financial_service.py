from typing import Dict, Any, Optional
from app.core.settings import settings


class FinancialService:
    @staticmethod
    def calculate_expected_damage_cost(
        product_cost: float = settings.product_cost,
        damage_probability: float = settings.damage_probability
    ) -> float:
        """Expected damage cost = Product cost * Damage probability."""
        return round(product_cost * damage_probability, 2)

    @staticmethod
    def calculate_expected_rto_cost(
        forward_shipping: float = settings.forward_shipping_cost,
        return_shipping: float = settings.return_shipping_cost,
        packaging: float = settings.packaging_cost,
        expected_damage: Optional[float] = None,
        product_cost: float = settings.product_cost,
        damage_probability: float = settings.damage_probability
    ) -> float:
        """Expected RTO cost = Forward shipping + Return shipping + Packaging + Expected damage cost."""
        if expected_damage is None:
            expected_damage = FinancialService.calculate_expected_damage_cost(product_cost, damage_probability)
        return round(forward_shipping + return_shipping + packaging + expected_damage, 2)

    @staticmethod
    def calculate_delivered_gross_contribution(
        order_value: float = settings.aov_reference,
        gross_margin: float = settings.gross_margin
    ) -> float:
        """Gross contribution per delivered order = Order value * Gross margin."""
        return round(order_value * gross_margin, 2)

    @staticmethod
    def evaluate_order_intervention(
        order_value: float,
        rto_probability: float,
        action: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates expected financial metrics for an individual order intervention.
        Distinguishes estimated counterfactual savings from realised cash outcomes.
        """
        cfg_fin = config.get("financials", {}) if config else {}
        cfg_prepaid = config.get("prepaid_offer", {}) if config else {}
        cfg_assumptions = config.get("intervention_assumptions", {}) if config else {}

        fwd = cfg_fin.get("forward_shipping", settings.forward_shipping_cost)
        ret = cfg_fin.get("return_shipping", settings.return_shipping_cost)
        pkg = cfg_fin.get("packaging_handling", settings.packaging_cost)
        prod_cost = cfg_fin.get("product_cost", settings.product_cost)
        dmg_prob = cfg_fin.get("damage_probability", settings.damage_probability)
        gm = cfg_fin.get("gross_margin", settings.gross_margin)
        discount_amt = cfg_prepaid.get("discount_amount", settings.prepaid_discount_amount)
        prepaid_rto_rate = cfg_assumptions.get("prepaid_rto_rate", 0.04)
        confirm_eff = cfg_assumptions.get("confirmation_effectiveness", 0.70)

        rto_cost = FinancialService.calculate_expected_rto_cost(
            forward_shipping=fwd,
            return_shipping=ret,
            packaging=pkg,
            product_cost=prod_cost,
            damage_probability=dmg_prob
        )
        gross_contrib = FinancialService.calculate_delivered_gross_contribution(order_value, gm)

        expected_rto_cost_without = round(rto_probability * rto_cost, 2)

        avoided_rto_cost = 0.0
        applied_discount = 0.0
        intervention_cost = 0.0
        net_expected_benefit = 0.0
        assumptions = ["Baseline RTO cost = forward + return + packaging + expected damage"]

        if action == "SHIP_AS_IS":
            avoided_rto_cost = 0.0
            net_expected_benefit = 0.0
            assumptions.append("Low predicted risk; no intervention needed")

        elif action == "SHIP_AFTER_CONFIRMATION":
            # Confirmation filters uncommitted customers
            avoided_rto_cost = round(rto_probability * confirm_eff * rto_cost, 2)
            intervention_cost = 0.0  # Simulated WhatsApp msg
            net_expected_benefit = round(avoided_rto_cost - intervention_cost, 2)
            assumptions.append(f"Estimated confirmation effectiveness: {int(confirm_eff * 100)}%")

        elif action == "NUDGE_TO_PREPAID":
            # Converting to prepaid reduces RTO risk from COD baseline to prepaid baseline
            avoided_diff = max(0.0, rto_probability - prepaid_rto_rate)
            avoided_rto_cost = round(avoided_diff * rto_cost, 2)
            applied_discount = discount_amt
            net_expected_benefit = round(avoided_rto_cost - applied_discount, 2)
            assumptions.append(f"Assumes prepaid RTO rate of {int(prepaid_rto_rate * 100)}% with ₹{discount_amt} discount")

        elif action in ("HOLD_CANCEL", "HOLD", "CANCEL"):
            # If held or cancelled: saves RTO exposure, but if genuine, loses delivered gross margin
            avoided_rto_cost = round(rto_probability * rto_cost, 2)
            prob_genuine = max(0.0, 1.0 - rto_probability)
            opp_loss = round(prob_genuine * gross_contrib, 2)
            net_expected_benefit = round(avoided_rto_cost - opp_loss, 2)
            assumptions.append(f"Includes opportunity cost of ₹{opp_loss} for potentially genuine delivery")

        return {
            "expected_rto_cost_without_intervention": expected_rto_cost_without,
            "expected_avoided_rto_cost": avoided_rto_cost,
            "expected_gross_contribution": gross_contrib,
            "discount_amount": applied_discount,
            "intervention_cost": intervention_cost,
            "net_expected_benefit": net_expected_benefit,
            "assumptions": assumptions,
        }

    @staticmethod
    def calculate_dashboard_metrics(
        decisions: list,
        orders: list,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Computes aggregate KPIs for Founder Dashboard.
        Separates observed outcomes from counterfactual model estimates.
        """
        cfg_fin = config.get("financials", {}) if config else {}
        fwd = cfg_fin.get("forward_shipping", settings.forward_shipping_cost)
        ret = cfg_fin.get("return_shipping", settings.return_shipping_cost)
        pkg = cfg_fin.get("packaging_handling", settings.packaging_cost)
        prod_cost = cfg_fin.get("product_cost", settings.product_cost)
        dmg_prob = cfg_fin.get("damage_probability", settings.damage_probability)
        gm = cfg_fin.get("gross_margin", settings.gross_margin)
        aov = cfg_fin.get("aov", settings.aov_reference)

        rto_cost = FinancialService.calculate_expected_rto_cost(
            forward_shipping=fwd,
            return_shipping=ret,
            packaging=pkg,
            product_cost=prod_cost,
            damage_probability=dmg_prob
        )
        gross_contrib = round(aov * gm, 2)

        total_cod = len(decisions)
        bucket_counts = {
            "SHIP_AS_IS": 0,
            "SHIP_AFTER_CONFIRMATION": 0,
            "NUDGE_TO_PREPAID": 0,
            "HOLD_CANCEL": 0,
        }

        total_avoided_rto_cost = 0.0
        total_genuine_loss = 0.0
        total_discount_cost = 0.0
        total_intervention_cost = 0.0

        for d in decisions:
            act = d.action
            if act in bucket_counts:
                bucket_counts[act] += 1

            fin = d.financial_estimate or {}
            total_avoided_rto_cost += fin.get("expected_avoided_rto_cost", 0.0)
            total_discount_cost += fin.get("discount_amount", 0.0) if d.operational_status == "PAYMENT_SUCCESSFUL" else 0.0
            
            if act == "HOLD_CANCEL" and d.operational_status == "CANCELLED":
                prob_rto = fin.get("rto_probability", 0.70)
                prob_genuine = max(0.0, 1.0 - prob_rto)
                total_genuine_loss += prob_genuine * gross_contrib

        total_avoided_rto_cost = round(total_avoided_rto_cost, 2)
        total_genuine_loss = round(total_genuine_loss, 2)
        total_discount_cost = round(total_discount_cost, 2)
        net_impact = round(total_avoided_rto_cost - total_genuine_loss - total_discount_cost - total_intervention_cost, 2)

        return {
            "total_cod_evaluated": total_cod,
            "ship_as_is": bucket_counts["SHIP_AS_IS"],
            "ship_as_is_share": round(bucket_counts["SHIP_AS_IS"] / total_cod, 4) if total_cod else 0.0,
            "ship_after_confirmation": bucket_counts["SHIP_AFTER_CONFIRMATION"],
            "confirmation_share": round(bucket_counts["SHIP_AFTER_CONFIRMATION"] / total_cod, 4) if total_cod else 0.0,
            "nudge_to_prepaid": bucket_counts["NUDGE_TO_PREPAID"],
            "prepaid_share": round(bucket_counts["NUDGE_TO_PREPAID"] / total_cod, 4) if total_cod else 0.0,
            "hold_cancel": bucket_counts["HOLD_CANCEL"],
            "hold_share": round(bucket_counts["HOLD_CANCEL"] / total_cod, 4) if total_cod else 0.0,
            "financial_impact": {
                "estimated_rto_savings": total_avoided_rto_cost,
                "estimated_genuine_cancellation_loss": total_genuine_loss,
                "redeemed_prepaid_discounts": total_discount_cost,
                "intervention_costs": total_intervention_cost,
                "net_estimated_financial_impact": net_impact,
                "reporting_note": "Counterfactual model estimate; not audited realised savings.",
            }
        }
