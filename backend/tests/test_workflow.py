import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.entities import Order, OrderEvent
from app.services.workflow_service import WorkflowService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_valid_state_transitions(test_db):
    order = Order(
        order_id="TEST-WF-1",
        customer_name="Test Customer",
        phone="9876543210",
        address="Test Address",
        order_value=649.0,
        workflow_status="RECEIVED"
    )
    test_db.add(order)
    test_db.commit()

    # RECEIVED -> AWAITING_CONFIRMATION
    WorkflowService.transition_state(test_db, order, "AWAITING_CONFIRMATION", "TRIGGER_CONFIRMATION")
    assert order.workflow_status == "AWAITING_CONFIRMATION"

    # AWAITING_CONFIRMATION -> CONFIRMED
    WorkflowService.transition_state(test_db, order, "CONFIRMED", "CUSTOMER_YES")
    assert order.workflow_status == "CONFIRMED"

    # CONFIRMED -> SHIP_APPROVED
    WorkflowService.transition_state(test_db, order, "SHIP_APPROVED", "RELEASE_SHIPMENT")
    assert order.workflow_status == "SHIP_APPROVED"

    # Verify event trail
    events = test_db.query(OrderEvent).filter(OrderEvent.order_id == "TEST-WF-1").all()
    assert len(events) == 3


def test_invalid_state_transition_rejected(test_db):
    order = Order(
        order_id="TEST-WF-2",
        customer_name="Test Customer 2",
        phone="9876543210",
        address="Test Address 2",
        order_value=649.0,
        workflow_status="CANCELLED"
    )
    test_db.add(order)
    test_db.commit()

    # CANCELLED cannot transition to SHIP_APPROVED under SYSTEM actor
    with pytest.raises(ValueError):
        WorkflowService.transition_state(test_db, order, "SHIP_APPROVED", "TRY_SHIP")
