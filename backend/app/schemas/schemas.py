from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# Order Schemas
class OrderBase(BaseModel):
    order_id: str
    customer_name: str
    phone: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    order_value: float = Field(gt=0, description="Order value must be positive")
    items: Optional[str] = None
    num_items: int = 1
    customer_prior_orders: int = 0
    customer_prior_rto: int = 0
    utm_source: Optional[str] = None
    courier: Optional[str] = None
    payment_method: str = "COD"


class OrderCreate(OrderBase):
    order_datetime: Optional[datetime] = None


class OrderRead(OrderBase):
    id: int
    order_datetime: datetime
    final_status: Optional[str] = None
    workflow_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Decision Schemas
class FinancialEstimate(BaseModel):
    expected_rto_cost_without_intervention: float
    expected_avoided_rto_cost: float
    expected_gross_contribution: float
    discount_amount: float
    intervention_cost: float
    net_expected_benefit: float
    assumptions: list[str] = []


class EvaluateOrderRequest(OrderBase):
    pass


class EvaluateOrderResponse(BaseModel):
    order_id: str
    rto_probability: float
    risk_band: str  # LOW, MODERATE, ELEVATED, HIGH
    action: str  # SHIP_AS_IS, SHIP_AFTER_CONFIRMATION, NUDGE_TO_PREPAID, HOLD_CANCEL
    operational_status: str
    reason_codes: list[str]
    explanation: str
    financial_estimate: FinancialEstimate
    model_version: str
    rule_version: str
    llm_status: str  # COMPLETED, UNAVAILABLE, SKIPPED
    decision_timestamp: datetime


class DecisionRead(BaseModel):
    id: int
    order_id: str
    action: str
    operational_status: str
    reason_codes: list[str]
    explanation: str
    financial_estimate: Optional[dict] = None
    rule_version: str
    is_override: bool
    override_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# WhatsApp & Customer Interaction Schemas
class WhatsAppSendRequest(BaseModel):
    order_id: str
    template_type: str = "CONFIRMATION"  # CONFIRMATION, PREPAID_NUDGE
    language: str = "en"  # en, hi


class WhatsAppReplyRequest(BaseModel):
    order_id: str
    reply_text: str


class WhatsAppTimeoutRequest(BaseModel):
    order_id: str


class CustomerInteractionRead(BaseModel):
    id: int
    order_id: str
    channel: str
    direction: str
    template_key: Optional[str] = None
    message: str
    response_type: Optional[str] = None
    delivery_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Schemas
class CreateMockPaymentRequest(BaseModel):
    order_id: str


class MockPaymentActionRequest(BaseModel):
    order_id: str


class PaymentAttemptRead(BaseModel):
    id: int
    order_id: str
    original_amount: float
    discount_amount: float
    payable_amount: float
    payment_status: str
    transaction_reference: str
    created_at: datetime

    class Config:
        from_attributes = True


# Override Schema
class ManualOverrideRequest(BaseModel):
    action: str  # SHIP_APPROVED, HOLD, CANCELLED
    reason: str = Field(min_length=3, description="A valid operational reason is required for manual override")


# Configuration Schemas
class RiskThresholdsConfig(BaseModel):
    ship_as_is_max: float = Field(ge=0.0, le=1.0)
    confirmation_max: float = Field(ge=0.0, le=1.0)
    prepaid_max: float = Field(ge=0.0, le=1.0)
    hold_min: float = Field(ge=0.0, le=1.0)


class FinancialsConfig(BaseModel):
    forward_shipping: float = Field(ge=0.0)
    return_shipping: float = Field(ge=0.0)
    packaging_handling: float = Field(ge=0.0)
    product_cost: float = Field(ge=0.0)
    damage_probability: float = Field(ge=0.0, le=1.0)
    aov: float = Field(ge=0.0)
    gross_margin: float = Field(ge=0.0, le=1.0)
    cac_reference: float = Field(ge=0.0)


class PrepaidOfferConfig(BaseModel):
    enabled: bool = True
    discount_amount: float = Field(ge=0.0)
    currency: str = "INR"
    expiry_hours: int = Field(gt=0)


class ConfirmationConfig(BaseModel):
    enabled: bool = True
    timeout_hours: int = Field(gt=0)
    max_reminders: int = Field(ge=0)


class CustomerProtectionConfig(BaseModel):
    protect_first_time_customers: bool = True
    manual_review_before_cancellation: bool = True
    geography_alone_can_cancel: bool = False
    llm_alone_can_cancel: bool = False


class InterventionAssumptionsConfig(BaseModel):
    confirmation_response_rate: float = Field(ge=0.0, le=1.0, default=0.65)
    confirmation_effectiveness: float = Field(ge=0.0, le=1.0, default=0.70)
    prepaid_acceptance_rate: float = Field(ge=0.0, le=1.0, default=0.12)
    prepaid_rto_rate: float = Field(ge=0.0, le=1.0, default=0.04)


class AIConfig(BaseModel):
    enabled: bool = False
    provider: str = "gemini"
    model_name: str = "gemini-1.5-flash"
    timeout_seconds: int = 8
    validate_names: bool = True
    validate_addresses: bool = True


class FullConfiguration(BaseModel):
    policy_version: str = "1.0"
    timezone: str = "Asia/Kolkata"
    risk_thresholds: RiskThresholdsConfig
    financials: FinancialsConfig
    prepaid_offer: PrepaidOfferConfig
    confirmation: ConfirmationConfig
    customer_protection: CustomerProtectionConfig
    intervention_assumptions: InterventionAssumptionsConfig
    ai_config: Optional[AIConfig] = None


# Dashboard Schemas
class DecisionBucketCounts(BaseModel):
    total_cod_evaluated: int
    ship_as_is: int
    ship_as_is_share: float
    ship_after_confirmation: int
    confirmation_share: float
    nudge_to_prepaid: int
    prepaid_share: float
    hold_cancel: int
    hold_share: float


class FinancialImpactSummary(BaseModel):
    estimated_rto_savings: float
    estimated_genuine_cancellation_loss: float
    redeemed_prepaid_discounts: float
    intervention_costs: float
    net_estimated_financial_impact: float
    reporting_note: str = "Counterfactual estimate based on configured decision thresholds and assumptions."


class DashboardSummaryResponse(BaseModel):
    reporting_date: str
    last_updated: datetime
    bucket_counts: DecisionBucketCounts
    financial_impact: FinancialImpactSummary
    needs_attention_count: int
