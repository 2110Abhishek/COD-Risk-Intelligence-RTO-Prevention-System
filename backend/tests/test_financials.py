import pytest
from app.services.financial_service import FinancialService


def test_expected_damage_cost():
    # 180 * 0.08 = 14.40
    damage = FinancialService.calculate_expected_damage_cost(180.0, 0.08)
    assert damage == 14.40


def test_expected_rto_cost():
    # 65 + 65 + 25 + 14.40 = 169.40
    rto_cost = FinancialService.calculate_expected_rto_cost(
        forward_shipping=65.0,
        return_shipping=65.0,
        packaging=25.0,
        expected_damage=14.40
    )
    assert rto_cost == 169.40


def test_delivered_gross_contribution():
    # 649 * 0.62 = 402.38
    contrib = FinancialService.calculate_delivered_gross_contribution(649.0, 0.62)
    assert contrib == 402.38


def test_evaluate_order_intervention_ship_as_is():
    res = FinancialService.evaluate_order_intervention(
        order_value=649.0,
        rto_probability=0.15,
        action="SHIP_AS_IS"
    )
    assert res["expected_rto_cost_without_intervention"] == round(0.15 * 169.40, 2)
    assert res["expected_avoided_rto_cost"] == 0.0
    assert res["discount_amount"] == 0.0


def test_evaluate_order_intervention_prepaid_discount():
    res = FinancialService.evaluate_order_intervention(
        order_value=649.0,
        rto_probability=0.50,
        action="NUDGE_TO_PREPAID",
        config={"prepaid_offer": {"discount_amount": 15.0}, "intervention_assumptions": {"prepaid_rto_rate": 0.04}}
    )
    # Expected avoided = (0.50 - 0.04) * 169.40 = 77.92
    assert res["expected_avoided_rto_cost"] == 77.92
    assert res["discount_amount"] == 15.0
    assert res["net_expected_benefit"] == round(77.92 - 15.0, 2)
