import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.entities import Order

client = TestClient(app)


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_create_and_evaluate_order():
    order_data = {
        "order_id": "TEST-API-101",
        "customer_name": "Divya Sharma",
        "phone": "9876543210",
        "address": "Flat 402, Sunrise Apartments, Station Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560001",
        "order_value": 749.0,
        "items": "Hair Oil 100ml",
        "num_items": 1,
        "customer_prior_orders": 2,
        "customer_prior_rto": 0,
        "utm_source": "google_ads",
        "courier": "Delhivery",
        "payment_method": "COD"
    }

    # Evaluate order
    res = client.post("/api/v1/decisions/evaluate", json=order_data)
    assert res.status_code == 200
    data = res.json()
    assert data["order_id"] == "TEST-API-101"
    assert data["action"] in ["SHIP_AS_IS", "SHIP_AFTER_CONFIRMATION", "NUDGE_TO_PREPAID", "HOLD_CANCEL"]
    assert "rto_probability" in data
    assert "explanation" in data
    assert len(data["reason_codes"]) > 0


def test_whatsapp_reply_flow():
    # Setup order awaiting confirmation
    order_data = {
        "order_id": "TEST-WA-202",
        "customer_name": "Kavita Rao",
        "phone": "9876543210",
        "address": "Near Hanuman Mandir, Main Road",
        "city": "Nagpur",
        "state": "Maharashtra",
        "pincode": "440001",
        "order_value": 649.0,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    client.post("/api/v1/decisions/evaluate", json=order_data)

    # 1. Ambiguous reply does not release shipment
    ambig_res = client.post("/api/v1/whatsapp/reply", json={
        "order_id": "TEST-WA-202",
        "reply_text": "I am not sure, call me tomorrow"
    })
    assert ambig_res.status_code == 200
    assert ambig_res.json()["classification"] == "AMBIGUOUS"

    # 2. Explicit YES confirms and releases to SHIP_APPROVED
    yes_res = client.post("/api/v1/whatsapp/reply", json={
        "order_id": "TEST-WA-202",
        "reply_text": "YES please dispatch"
    })
    assert yes_res.status_code == 200
    assert yes_res.json()["classification"] == "YES"
    assert yes_res.json()["workflow_status"] == "SHIP_APPROVED"


def test_mock_prepaid_payment_flow():
    order_data = {
        "order_id": "TEST-PAY-303",
        "customer_name": "Rahul Verma",
        "phone": "9876543210",
        "address": "Plot 55, Tilak Marg",
        "city": "Indore",
        "state": "Madhya Pradesh",
        "pincode": "452001",
        "order_value": 898.0,
        "customer_prior_orders": 1,
        "customer_prior_rto": 0,
        "payment_method": "COD"
    }
    client.post("/api/v1/decisions/evaluate", json=order_data)

    # Simulate payment success
    pay_res = client.post("/api/v1/payments/mock-success", json={"order_id": "TEST-PAY-303"})
    assert pay_res.status_code == 200
    data = pay_res.json()
    assert data["status"] == "SUCCESSFUL"
    assert data["payment_method"] == "PREPAID"
    assert data["workflow_status"] == "SHIP_APPROVED"
