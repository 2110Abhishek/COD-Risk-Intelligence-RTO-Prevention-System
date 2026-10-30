from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, index=True, nullable=False)
    order_datetime = Column(DateTime, default=datetime.utcnow, index=True)
    customer_name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(128), index=True)
    state = Column(String(128), index=True)
    pincode = Column(String(16), index=True)
    order_value = Column(Float, nullable=False)
    items = Column(Text, nullable=True)
    num_items = Column(Integer, default=1)
    customer_prior_orders = Column(Integer, default=0)
    customer_prior_rto = Column(Integer, default=0)
    utm_source = Column(String(128), index=True)
    courier = Column(String(128), index=True)
    payment_method = Column(String(32), default="COD", index=True)
    final_status = Column(String(32), nullable=True, index=True)  # DELIVERED, RTO, IN_TRANSIT, or NULL
    workflow_status = Column(String(64), default="RECEIVED", index=True)  # State machine status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("RiskPrediction", back_populates="order", cascade="all, delete-orphan")
    decisions = relationship("OrderDecision", back_populates="order", cascade="all, delete-orphan")
    interactions = relationship("CustomerInteraction", back_populates="order", cascade="all, delete-orphan")
    payment_attempts = relationship("PaymentAttempt", back_populates="order", cascade="all, delete-orphan")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), index=True, nullable=False)
    rto_probability = Column(Float, nullable=False)
    risk_band = Column(String(32), nullable=False, index=True)  # LOW, MODERATE, ELEVATED, HIGH
    model_version = Column(String(64), nullable=False)
    feature_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    order = relationship("Order", back_populates="predictions")


class OrderDecision(Base):
    __tablename__ = "order_decisions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), index=True, nullable=False)
    action = Column(String(64), nullable=False, index=True)  # SHIP_AS_IS, SHIP_AFTER_CONFIRMATION, NUDGE_TO_PREPAID, HOLD_CANCEL
    operational_status = Column(String(64), default="RECEIVED")  # SHIP_APPROVED, AWAITING_CONFIRMATION, PREPAID_OFFERED, HOLD, CANCELLED
    reason_codes = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)
    financial_estimate = Column(JSON, nullable=True)
    rule_version = Column(String(32), default="1.0")
    is_override = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    order = relationship("Order", back_populates="decisions")


class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), index=True, nullable=False)
    channel = Column(String(32), default="WHATSAPP")
    direction = Column(String(16), nullable=False)  # OUTBOUND, INBOUND
    template_key = Column(String(64), nullable=True)
    message = Column(Text, nullable=False)
    response_type = Column(String(32), nullable=True)  # YES, NO, AMBIGUOUS, TIMEOUT, PAYMENT_SUCCESS, PAYMENT_FAILURE
    delivery_status = Column(String(32), default="DELIVERED")  # SENT, DELIVERED, READ, FAILED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    order = relationship("Order", back_populates="interactions")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), index=True, nullable=False)
    original_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    payable_amount = Column(Float, nullable=False)
    payment_status = Column(String(32), default="PENDING", index=True)  # PENDING, SUCCESSFUL, FAILED, EXPIRED
    transaction_reference = Column(String(128), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    order = relationship("Order", back_populates="payment_attempts")


class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), ForeignKey("orders.order_id"), index=True, nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    previous_status = Column(String(64), nullable=True)
    new_status = Column(String(64), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    order = relationship("Order", back_populates="events")


class SystemConfiguration(Base):
    __tablename__ = "system_configuration"

    id = Column(Integer, primary_key=True, index=True)
    configuration_key = Column(String(64), unique=True, index=True, nullable=False)
    configuration_value = Column(JSON, nullable=False)
    version = Column(String(32), default="1.0")
    updated_by = Column(String(64), default="SYSTEM")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(64), default="SYSTEM", index=True)
    action = Column(String(64), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
