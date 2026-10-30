# Technical Architecture --- COD Risk Intelligence & RTO Prevention

**Version:** 1.0\
**Date:** October 30, 2026\
**Status:** Implementation specification

## 1. Architecture objectives

Build a locally runnable, auditable application that evaluates COD
orders before dispatch, recommends one of four business actions,
simulates customer interventions, and reports operational and financial
outcomes.

Architecture priorities:

1.  Separate prediction from policy: the ML model estimates RTO
    probability; a deterministic policy engine chooses the action.
2.  Keep financial calculations deterministic and centrally implemented.
3.  Keep LLM use narrow, optional, structured, and non-authoritative.
4.  Persist decisions and events so the same decision can be
    reconstructed later.
5.  Make configuration changes possible without code changes.
6.  Distinguish observed outcomes from estimated counterfactual
    outcomes.
7.  Make the initial system simple enough to run locally in under 10
    minutes.

## 2. System context

### 2.1 Logical context

``` text
Shopify / CSV / Demo Order Input
             |
             v
      FastAPI Application
             |
    +--------+---------+
    |                  |
    v                  v
Data Validation    Customer History
    |                  |
    +--------+---------+
             |
             v
       Feature Builder
             |
       +-----+------+
       |            |
       v            v
   ML Scorer    LLM Validator
       |            |
       +------+-----+
              |
              v
       Decision Policy Engine
              |
      +-------+--------+---------+
      |       |        |         |
      v       v        v         v
   Ship    Confirm   Prepaid    Hold
              |        |
              v        v
       WhatsApp Mock  Payment Mock
              |
              v
       Order Event / Audit Store
              |
              v
       Dashboard & Analytics
```

### 2.2 Deployment topology

For the assignment, use a single local application deployment:

-   Frontend: Vite development server.
-   Backend: FastAPI with Uvicorn.
-   Database: SQLite.
-   Model: serialized scikit-learn pipeline.
-   LLM: optional provider adapter configured through environment
    variables.
-   Dataset: local CSV under `data/`; never commit real secrets or
    unnecessary personal data.

Do not introduce microservices, Redis, Kubernetes, or a message broker
for this small take-home implementation. Keep service boundaries as
Python modules so they can be extracted later if volume requires it.

## 3. Technology choices

  -----------------------------------------------------------------------
  Layer                   Choice                  Responsibility
  ----------------------- ----------------------- -----------------------
  UI                      React + Vite +          Dashboard, order
                          TypeScript              review, simulator,
                                                  configuration

  Styling                 CSS Modules / plain CSS Responsive visual
                                                  system without Tailwind
                                                  dependency

  Charts                  Recharts                KPI trends and
                                                  distributions

  API                     FastAPI                 Validation, business
                                                  APIs, orchestration

  Schemas                 Pydantic                Request/response
                                                  validation

  Data                    Pandas / NumPy          CSV ingestion and
                                                  feature preparation

  ML                      Scikit-learn            Baseline and candidate
                                                  risk models

  Persistence             SQLAlchemy + SQLite     Orders, decisions,
                                                  events, configuration

  LLM                     Provider adapter        Name/address
                                                  interpretation only

  Tests                   Pytest + frontend test  Unit and integration
                          runner                  coverage
  -----------------------------------------------------------------------

## 4. Backend component architecture

Recommended backend package:

``` text
backend/app/
  main.py
  api/
    routes/
      health.py
      orders.py
      decisions.py
      whatsapp.py
      payments.py
      dashboard.py
      configuration.py
      analytics.py
  core/
    settings.py
    database.py
    logging.py
    errors.py
  models/
    order.py
    prediction.py
    decision.py
    interaction.py
    payment.py
    event.py
    configuration.py
    audit.py
  schemas/
    order.py
    decision.py
    whatsapp.py
    payment.py
    dashboard.py
    configuration.py
  services/
    ingestion_service.py
    order_service.py
    decision_service.py
    policy_service.py
    financial_service.py
    workflow_service.py
    dashboard_service.py
    audit_service.py
  ml/
    train.py
    predict.py
    features.py
    evaluation.py
    artifacts/
  llm/
    base.py
    provider.py
    prompts.py
    validator.py
  utils/
    normalization.py
    phone.py
    address.py
  tests/
```

### 4.1 API layer

Responsibilities:

-   Parse HTTP requests.
-   Validate payloads with Pydantic.
-   Authenticate/authorize in production.
-   Invoke service functions.
-   Return stable response schemas.
-   Translate known exceptions into safe HTTP errors.

API routes must not contain model training, financial formulas, or
decision policy logic.

### 4.2 Ingestion and normalization service

Responsibilities:

-   Accept an order from a demo form, CSV import, or future Shopify
    webhook.
-   Normalize payment method, status, phone, pincode, dates, and text.
-   Validate required fields.
-   Detect duplicate order IDs.
-   Store the normalized order.
-   Make ingestion idempotent.

Duplicate behavior: an existing `order_id` must not silently create a
second order. Return the existing record or a conflict response,
depending on endpoint semantics.

### 4.3 Customer history service

Responsibilities:

-   Retrieve only history available before the current order timestamp.
-   Calculate prior orders, prior RTOs, delivery success ratio, and
    history sample size.
-   Exclude the current order from historical aggregates.
-   Avoid future leakage when replaying historical data.

For historical backtests, history features must be computed using a
point-in-time snapshot, not the final customer totals in the complete
CSV.

### 4.4 Feature engineering service

Feature groups:

-   Customer: prior order count, prior RTO count, prior RTO rate,
    first-time indicator.
-   Order: order value, item count, average item value, weekday, hour.
-   Geography: state, city, pincode historical RTO rate and sample
    count.
-   Operations: courier, acquisition source.
-   Data quality: phone validity, pincode validity, missing address,
    name/address flags.

Use a fitted preprocessing pipeline. Categorical encoders and imputers
must be fitted on training data only. Unknown categories must be handled
without crashing.

Do not use `final_status`, delivery timestamps, eventual RTO outcomes,
or any information created after the decision timestamp as predictors.

### 4.5 ML scoring service

Responsibilities:

-   Load a versioned model artifact.
-   Validate required feature inputs.
-   Return calibrated RTO probability from 0 to 1.
-   Return model version and scoring timestamp.
-   Fail safely if the artifact is unavailable.

Model workflow:

1.  Establish a simple baseline, such as Logistic Regression.
2.  Compare a tree-based candidate, such as Random Forest or
    HistGradientBoosting.
3.  Use chronological train/validation/holdout splits.
4.  Evaluate PR-AUC, ROC-AUC, precision, recall, F1, confusion matrix,
    and calibration.
5.  Select a model based on out-of-time performance and business cost,
    not accuracy alone.
6.  Persist the entire preprocessing + model pipeline.
7.  Record model version and training window.

If sample size is too small for stable geographic features, shrink those
rates toward the global average or mark them unavailable. Do not treat a
small sample rate as reliable evidence.

### 4.6 LLM validation service

LLM use is restricted to unstructured interpretation:

-   Assess whether a name resembles placeholder/test text.
-   Interpret address completeness and ambiguity.
-   Parse Hinglish or colloquial landmark directions into structured
    fields.
-   Produce a short explanation of address quality.

Do not use the LLM for:

-   Probability calculations.
-   Pincode history aggregation.
-   Phone format checks.
-   Duplicate detection.
-   Financial calculations.
-   Threshold comparisons.
-   Final cancellation authority.

Suggested output schema:

``` json
{
  "name_quality": "VALID | SUSPICIOUS | UNCERTAIN",
  "address_quality": "USABLE | NEEDS_CLARIFICATION | INSUFFICIENT | UNCERTAIN",
  "has_landmark": true,
  "issues": [],
  "reason": "Short factual explanation"
}
```

Do not rely on a model-generated confidence score as a calibrated
probability. Validate the response against an enum/schema. On timeout,
malformed JSON, provider error, or low-confidence ambiguity, mark the
LLM result `UNAVAILABLE` or `UNCERTAIN` and continue with deterministic
checks.

Send only the minimum text needed. Do not send customer phone numbers or
unrelated order details to the LLM. Keep provider keys on the backend.

### 4.7 Policy / decision service

Inputs:

-   Calibrated RTO probability.
-   Customer history.
-   Deterministic validation results.
-   LLM quality flags.
-   Order economics.
-   Active policy configuration.

Outputs:

-   Assignment bucket: `SHIP_AS_IS`, `SHIP_AFTER_CONFIRMATION`,
    `NUDGE_TO_PREPAID`, or `HOLD_CANCEL`.
-   Operational substatus, e.g. `HOLD` or `CANCELLED`.
-   Reason codes.
-   Human-readable explanation.
-   Financial estimate and assumptions.
-   Model and policy versions.

The policy service must be deterministic for identical inputs and
configuration. It must never let free-form LLM text directly select an
action.

### 4.8 Financial service

One central module owns all financial formulas. The dashboard, backtest,
and decision detail must call the same functions.

Track three categories separately:

1.  Observed: actual RTO, actual delivered orders, actual discount
    issued.
2.  Estimated: predicted avoided RTOs, estimated genuine cancellations,
    expected costs.
3.  Assumed: intervention response/conversion rates and counterfactual
    outcomes.

Never label an estimate as realised savings.

### 4.9 Workflow service

Owns valid order-state transitions and interaction workflows. A workflow
transition must:

-   Validate current state.
-   Validate requested event.
-   Update the order status.
-   Append an immutable event record.
-   Append an audit record for manual overrides.
-   Avoid duplicate event processing.

### 4.10 Dashboard service

Aggregates order decisions and events by the selected local reporting
date. Use a configured business timezone (`Asia/Kolkata` by default for
this assignment). Define whether "yesterday" refers to order-created
date or decision-created date; the dashboard should default to decision
date for bucket counts and disclose that definition.

## 5. Frontend architecture

Recommended structure:

``` text
frontend/src/
  app/
    App.tsx
    router.tsx
  components/
    layout/
    cards/
    charts/
    tables/
    badges/
    forms/
    simulator/
  pages/
    OverviewPage.tsx
    OrdersPage.tsx
    OrderDetailPage.tsx
    RiskAnalysisPage.tsx
    WhatsAppSimulatorPage.tsx
    AnalyticsPage.tsx
    ConfigurationPage.tsx
    DecisionLogsPage.tsx
  services/
    apiClient.ts
    orders.ts
    decisions.ts
    dashboard.ts
    whatsapp.ts
    configuration.ts
  hooks/
  types/
  styles/
```

### 5.1 Main screens

-   Overview: previous-day decision buckets and financial impact.
-   Orders: searchable, filterable order list.
-   Order detail: score, reasons, validation, events, financial
    estimate.
-   Risk analysis: model performance and risk segments.
-   WhatsApp simulator: conversation and workflow controls.
-   Analytics: historical trends and backtest comparison.
-   Configuration: editable thresholds and financial assumptions.
-   Decision logs: model/policy versions, events, and overrides.

### 5.2 Frontend behavior

-   Show loading, empty, and error states.
-   Do not fabricate chart values when an endpoint returns no data.
-   Display estimates with an "Estimated" label.
-   Show the timestamp and date range for every dashboard view.
-   Confirm before destructive manual actions.
-   Disable invalid workflow actions.
-   Never store LLM or payment secrets in browser code.

## 6. Data model

Minimum tables:

### `orders`

`id`, `order_id` (unique), customer fields, address fields, order value,
items, customer history snapshot, source, courier, payment method,
source status, created timestamp, updated timestamp.

### `risk_predictions`

`id`, `order_id`, probability, risk band, model version, feature
snapshot JSON, created timestamp.

### `order_decisions`

`id`, `order_id`, bucket, operational status, reason codes JSON,
explanation, policy version, financial estimate JSON, created timestamp.

### `customer_interactions`

`id`, `order_id`, channel, direction, message template, message body,
response classification, provider/mock status, timestamp.

### `payment_attempts`

`id`, `order_id`, original amount, discount, payable amount, status,
mock transaction reference, timestamps.

### `order_events`

`id`, `order_id`, event type, previous state, new state, metadata JSON,
idempotency key, timestamp.

### `system_configuration`

`id`, key, value JSON, version, updated by, updated timestamp.

### `audit_logs`

`id`, actor, action, entity type/id, previous value, new value, reason,
timestamp.

Use foreign keys and indexes for `order_id`, timestamps, status, and
frequently filtered dimensions. Store configuration versions so a past
decision can be reproduced.

## 7. API contracts and interactions

Prefix all routes with `/api/v1`.

  Method   Endpoint                               Purpose
  -------- -------------------------------------- -----------------------------------
  GET      `/health`                              Health status
  POST     `/orders`                              Create/import an order
  GET      `/orders`                              Paginated and filtered orders
  GET      `/orders/{order_id}`                   Order detail
  POST     `/decisions/evaluate`                  Score and decide an order
  GET      `/decisions`                           Decision history
  GET      `/decisions/{order_id}`                Latest decision
  POST     `/whatsapp/send`                       Create mock outbound message
  POST     `/whatsapp/reply`                      Simulate customer response
  POST     `/whatsapp/timeout`                    Trigger timeout behavior
  GET      `/whatsapp/conversations/{order_id}`   Conversation history
  POST     `/payments/create-mock`                Create mock payment request
  POST     `/payments/mock-success`               Simulate payment success
  POST     `/payments/mock-failure`               Simulate payment failure
  GET      `/dashboard/summary`                   Bucket counts and KPIs
  GET      `/dashboard/financial-impact`          Financial metrics
  GET      `/dashboard/trends`                    Time series
  GET      `/config`                              Active configuration
  PUT      `/config`                              Validate and update configuration
  GET      `/config/history`                      Configuration versions
  GET      `/analytics/model-performance`         Model metrics
  GET      `/analytics/rto-by-region`             Region performance
  GET      `/analytics/courier-performance`       Courier performance

### 7.1 Evaluate request

``` json
{
  "order_id": "DEMO-1001",
  "customer_name": "Asha Patil",
  "phone": "9999999999",
  "address": "Near Hanuman Mandir, Main Road",
  "city": "Nagpur",
  "state": "Maharashtra",
  "pincode": "440001",
  "order_value": 649,
  "items": ["Hair Oil"],
  "num_items": 1,
  "customer_prior_orders": 0,
  "customer_prior_rto": 0,
  "utm_source": "Meta",
  "courier": "Courier A",
  "payment_method": "COD"
}
```

### 7.2 Evaluate response

``` json
{
  "order_id": "DEMO-1001",
  "rto_probability": 0.27,
  "risk_band": "MODERATE",
  "action": "SHIP_AFTER_CONFIRMATION",
  "reason_codes": ["MODERATE_RTO_RISK", "FIRST_TIME_CUSTOMER"],
  "explanation": "The estimated risk is moderate. Ask the customer to confirm before dispatch.",
  "llm_status": "COMPLETED",
  "model_version": "baseline-1",
  "policy_version": "1",
  "financial_estimate": {
    "expected_rto_cost_without_intervention": 45.74,
    "assumptions": ["RTO probability multiplied by expected RTO cost"]
  }
}
```

Values are illustrative. The API must return actual model outputs.

### 7.3 API conventions

-   Use ISO 8601 timestamps with timezone.
-   Use INR numeric values in rupees, not formatted strings, in API
    responses.
-   Use pagination (`page`, `page_size`) and stable sorting.
-   Return structured errors with `code`, `message`, and optional
    `details`.
-   Validate enum values and numeric ranges.
-   Use idempotency keys for webhook-like events and payment callbacks.
-   In production, protect endpoints with authentication and role-based
    authorization.

## 8. Workflow and state transitions

The assignment's four decision buckets are reporting categories.
Internal operational states must be more granular.

Confirmation flow:

`EVALUATED -> AWAITING_CONFIRMATION -> CONFIRMED -> SHIP_APPROVED -> DISPATCHED`

Alternative transitions:

-   `AWAITING_CONFIRMATION -> CUSTOMER_DECLINED`
-   `AWAITING_CONFIRMATION -> CONFIRMATION_TIMEOUT -> HOLD`
-   `HOLD -> MANUAL_REVIEW -> SHIP_APPROVED or CANCELLED`

Prepaid flow:

`EVALUATED -> PREPAID_OFFERED -> PAYMENT_PENDING -> PAYMENT_SUCCESSFUL -> SHIP_APPROVED`

If no payment or offer expires:

`PREPAID_OFFERED -> OFFER_EXPIRED -> COD_CONFIRMATION or MANUAL_REVIEW`

All transitions must be validated server-side. A frontend button must
not directly mutate order state.

## 9. End-to-end data flows

### 9.1 New COD order

1.  Receive order.
2.  Validate schema and deduplicate.
3.  Persist order.
4.  Retrieve point-in-time customer history.
5.  Build features.
6.  Score with model.
7.  Run deterministic data-quality checks.
8.  Call LLM only if relevant unstructured fields need interpretation.
9.  Apply policy configuration.
10. Persist prediction, decision, reasons, and versions.
11. Start selected workflow.
12. Refresh dashboard aggregates.

### 9.2 Confirmation response

1.  Receive simulated reply.
2.  Normalize reply text.
3.  Classify explicit YES / NO / ambiguous response using deterministic
    matching.
4.  If ambiguous, send one clarification prompt.
5.  If YES, validate state and approve shipment.
6.  If NO, stop dispatch and record customer decline.
7.  If timeout, hold for review.
8.  Persist interaction and event.

Do not use an LLM for simple YES/NO classification unless the response
is genuinely ambiguous and a safe fallback exists.

### 9.3 Prepaid flow

1.  Create offer from configured discount.
2.  Calculate payable amount server-side.
3.  Generate mock payment link/reference.
4.  Simulate success or failure.
5.  Verify order state and amount.
6.  On success, mark prepaid and approve shipment.
7.  On failure/expiry, preserve original order and apply configured
    fallback.
8.  Persist payment attempt and event.

### 9.4 Dashboard flow

1.  Frontend requests summary for a date range.
2.  Backend queries decisions and events.
3.  Backend computes counts and financial estimates using central
    financial functions.
4.  Backend returns values, methodology, assumptions, and timestamp.
5.  Frontend renders cards/charts and clearly labels estimates.

## 10. ML evaluation and deployment architecture

Use chronological evaluation rather than random split. For a September
holdout, train only on data available before September and compute
customer/geographic aggregates as they would have existed at each
historical order timestamp.

Required model report:

-   Number of eligible labeled rows.
-   Class balance.
-   Split date ranges.
-   Precision, recall, F1.
-   ROC-AUC and PR-AUC.
-   Confusion matrix.
-   Calibration plot or Brier score.
-   Performance by first-time/returning customers.
-   Performance by region only where sample sizes are adequate.

Do not train on duplicate rows or unresolved statuses. If September is
the holdout, do not tune thresholds using September labels. Record
limitations caused by the small dataset.

## 11. Security, privacy, and reliability

-   Store secrets in `.env`; commit only `.env.example`.
-   Never send phone numbers to the LLM.
-   Minimize address data sent to external AI providers.
-   Mask phone numbers in the UI.
-   Validate all input on the backend.
-   Use SQLAlchemy parameterized operations.
-   Add role-based access before production.
-   Add audit records for configuration changes and manual overrides.
-   Apply request timeouts and safe fallbacks for LLM calls.
-   Keep mock payments clearly labelled as simulations.
-   Never represent mock WhatsApp delivery as a real message.
-   Do not automatically cancel based solely on LLM output or sparse
    pincode history.

## 12. Observability

Log structured events for:

-   Order received.
-   Prediction completed.
-   Decision generated.
-   LLM success/failure/timeout.
-   Message sent/failed.
-   Customer response.
-   Payment simulation.
-   State transition.
-   Manual override.
-   Configuration change.

Monitor:

-   API errors and latency.
-   Model scoring failures.
-   LLM failure rate.
-   Number and share of each decision bucket.
-   Confirmation response and timeout rates.
-   Prepaid conversion.
-   Actual RTO rate after rollout.
-   False-positive review outcomes.
-   Financial estimates versus realised outcomes.

## 13. Local run and configuration

Expected developer setup:

1.  Create Python virtual environment.
2.  Install backend requirements.
3.  Copy `.env.example` to `.env`.
4.  Run data import and model training commands.
5.  Start FastAPI.
6.  Install frontend dependencies.
7.  Start Vite.

The README must provide exact Windows PowerShell commands and a no-LLM
fallback path. The application must run without external API
credentials.

## 14. Architecture acceptance criteria

-   Frontend never calculates authoritative financial results.
-   API layer contains no business policy logic.
-   Model produces a probability, not an action.
-   Policy service chooses the action deterministically.
-   LLM cannot directly cancel or approve an order.
-   Every decision stores model and policy versions.
-   All workflow transitions are validated and audited.
-   Dashboard differentiates actual and estimated financial values.
-   Historical features are point-in-time and leakage-safe.
-   LLM outage does not stop order evaluation.
