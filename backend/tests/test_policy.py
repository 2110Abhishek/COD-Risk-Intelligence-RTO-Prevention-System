import pytest
from app.services.policy_service import PolicyService


@pytest.fixture
def default_config():
    return {
        "policy_version": "1.0",
        "risk_thresholds": {
            "ship_as_is_max": 0.20,
            "confirmation_max": 0.40,
            "prepaid_max": 0.65,
            "hold_min": 0.65
        },
        "customer_protection": {
            "protect_first_time_customers": True,
            "manual_review_before_cancellation": True,
            "geography_alone_can_cancel": False,
            "llm_alone_can_cancel": False
        },
        "prepaid_offer": {
            "enabled": True,
            "discount_amount": 15.0
        }
    }


def test_ship_as_is_for_low_risk(default_config):
    order = {
        "order_id": "TEST-100",
        "customer_name": "Aarav Sharma",
        "phone": "9876543210",
        "address": "Flat 302, Green Valley Apartments, MG Road",
        "order_value": 649.0,
        "customer_prior_orders": 2,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.12, config=default_config)
    assert res["action"] == "SHIP_AS_IS"
    assert res["risk_band"] == "LOW"
    assert res["operational_status"] == "SHIP_APPROVED"


def test_confirmation_for_moderate_risk(default_config):
    order = {
        "order_id": "TEST-101",
        "customer_name": "Priya Patel",
        "phone": "9876543210",
        "address": "House 45, Sector 12, near Water Tank",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.28, config=default_config)
    assert res["action"] == "SHIP_AFTER_CONFIRMATION"
    assert res["risk_band"] == "MODERATE"
    assert res["operational_status"] == "AWAITING_CONFIRMATION"
    assert "FIRST_TIME_CUSTOMER" in res["reason_codes"]


def test_nudge_to_prepaid_for_elevated_risk(default_config):
    order = {
        "order_id": "TEST-102",
        "customer_name": "Rohan Gupta",
        "phone": "9876543210",
        "address": "Plot 12, Gandhi Nagar, Opp. Railway Station",
        "order_value": 898.0,
        "customer_prior_orders": 1,
        "customer_prior_rto": 1,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.52, config=default_config)
    assert res["action"] == "NUDGE_TO_PREPAID"
    assert res["risk_band"] == "ELEVATED"
    assert res["operational_status"] == "PREPAID_OFFERED"


def test_hold_for_high_risk(default_config):
    order = {
        "order_id": "TEST-103",
        "customer_name": "Vikram Singh",
        "phone": "9876543210",
        "address": "Near Hanuman Mandir",
        "order_value": 1499.0,
        "customer_prior_orders": 3,
        "customer_prior_rto": 2,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.78, config=default_config)
    assert res["action"] == "HOLD_CANCEL"
    assert res["risk_band"] == "HIGH"
    assert res["operational_status"] == "HOLD"


def test_hard_blocker_invalid_phone(default_config):
    order = {
        "order_id": "TEST-104",
        "customer_name": "Suresh Rao",
        "phone": "12345",  # Invalid
        "address": "Valid address on MG Road",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.10, config=default_config)
    assert res["action"] == "HOLD_CANCEL"
    assert res["operational_status"] == "HOLD"
    assert "INVALID_PHONE_FORMAT" in res["reason_codes"]


def test_first_time_customer_never_auto_cancelled(default_config):
    order = {
        "order_id": "TEST-105",
        "customer_name": "New Customer",
        "phone": "9876543210",
        "address": "Valid address, near Metro Station",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    res = PolicyService.evaluate_policy(order, rto_probability=0.72, config=default_config)
    # Even at high risk, first time customer goes to HOLD / manual review, never CANCELLED
    assert res["operational_status"] == "HOLD"
    assert res["action"] == "HOLD_CANCEL"
