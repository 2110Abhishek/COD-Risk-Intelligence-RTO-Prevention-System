export type RiskBand = 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH' | 'UNKNOWN';

export type DecisionAction =
  | 'SHIP_AS_IS'
  | 'SHIP_AFTER_CONFIRMATION'
  | 'NUDGE_TO_PREPAID'
  | 'HOLD_CANCEL'
  | 'PENDING';

export type WorkflowStatus =
  | 'RECEIVED'
  | 'VALIDATING'
  | 'EVALUATED'
  | 'SHIP_APPROVED'
  | 'AWAITING_CONFIRMATION'
  | 'CONFIRMED'
  | 'PREPAID_OFFERED'
  | 'PAYMENT_PENDING'
  | 'PAYMENT_SUCCESSFUL'
  | 'CUSTOMER_DECLINED'
  | 'CONFIRMATION_TIMEOUT'
  | 'HOLD'
  | 'MANUAL_REVIEW'
  | 'CANCELLED'
  | 'DISPATCHED'
  | 'DELIVERED'
  | 'RTO';

export interface OrderListItem {
  id: number;
  order_id: string;
  customer_name: string;
  phone_masked: string;
  address: string;
  city?: string;
  state?: string;
  pincode?: string;
  order_value: number;
  payment_method: string;
  workflow_status: WorkflowStatus;
  final_status?: string;
  order_datetime: string;
  decision: DecisionAction;
  risk_band: RiskBand;
  rto_probability?: number;
  explanation?: string;
}

export interface FinancialEstimate {
  expected_rto_cost_without_intervention: number;
  expected_avoided_rto_cost: number;
  expected_gross_contribution: number;
  discount_amount: number;
  intervention_cost: number;
  net_expected_benefit: number;
  assumptions: string[];
}

export interface DecisionDetail {
  action: DecisionAction;
  operational_status: WorkflowStatus;
  reason_codes: string[];
  explanation: string;
  financial_estimate: FinancialEstimate;
  rule_version: string;
  is_override: boolean;
  override_reason?: string;
  created_at: string;
}

export interface PredictionDetail {
  rto_probability: number;
  risk_band: RiskBand;
  model_version: string;
  feature_snapshot: Record<string, any>;
  created_at: string;
}

export interface CustomerInteraction {
  id: number;
  channel: string;
  direction: 'INBOUND' | 'OUTBOUND';
  template_key?: string;
  message: string;
  response_type?: string;
  delivery_status: string;
  created_at: string;
}

export interface PaymentAttempt {
  id: number;
  original_amount: number;
  discount_amount: number;
  payable_amount: number;
  payment_status: string;
  transaction_reference: string;
  created_at: string;
}

export interface OrderEvent {
  id: number;
  event_type: string;
  previous_status?: string;
  new_status: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface OrderDetailResponse {
  order: {
    id: number;
    order_id: string;
    customer_name: string;
    phone: string;
    address: string;
    city?: string;
    state?: string;
    pincode?: string;
    order_value: number;
    items?: string;
    num_items: number;
    customer_prior_orders: number;
    customer_prior_rto: number;
    utm_source?: string;
    courier?: string;
    payment_method: string;
    workflow_status: WorkflowStatus;
    final_status?: string;
    order_datetime: string;
  };
  latest_decision?: DecisionDetail;
  latest_prediction?: PredictionDetail;
  interactions: CustomerInteraction[];
  payments: PaymentAttempt[];
  timeline: OrderEvent[];
}

export interface DecisionBucketCounts {
  total_cod_evaluated: number;
  ship_as_is: number;
  ship_as_is_share: number;
  ship_after_confirmation: number;
  confirmation_share: number;
  nudge_to_prepaid: number;
  prepaid_share: number;
  hold_cancel: number;
  hold_share: number;
}

export interface FinancialImpactSummary {
  estimated_rto_savings: number;
  estimated_genuine_cancellation_loss: number;
  redeemed_prepaid_discounts: number;
  intervention_costs: number;
  net_estimated_financial_impact: number;
  reporting_note: string;
}

export interface DashboardSummary {
  reporting_date: string;
  last_updated: string;
  bucket_counts: DecisionBucketCounts;
  financial_impact: FinancialImpactSummary;
  needs_attention_count: number;
}

export interface FullConfiguration {
  policy_version: string;
  timezone: string;
  risk_thresholds: {
    ship_as_is_max: number;
    confirmation_max: number;
    prepaid_max: number;
    hold_min: number;
  };
  financials: {
    forward_shipping: number;
    return_shipping: number;
    packaging_handling: number;
    product_cost: number;
    damage_probability: number;
    aov: number;
    gross_margin: number;
    cac_reference: number;
  };
  prepaid_offer: {
    enabled: boolean;
    discount_amount: number;
    currency: string;
    expiry_hours: number;
  };
  confirmation: {
    enabled: boolean;
    timeout_hours: number;
    max_reminders: number;
  };
  customer_protection: {
    protect_first_time_customers: boolean;
    manual_review_before_cancellation: boolean;
    geography_alone_can_cancel: boolean;
    llm_alone_can_cancel: boolean;
  };
  intervention_assumptions: {
    confirmation_response_rate: number;
    confirmation_effectiveness: number;
    prepaid_acceptance_rate: number;
    prepaid_rto_rate: number;
  };
  ai_config?: {
    enabled: boolean;
    provider: string;
    model_name: string;
    timeout_seconds: number;
    validate_names: boolean;
    validate_addresses: boolean;
  };
}
