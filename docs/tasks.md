# Development Tasks --- COD Risk Intelligence & RTO Prevention

**Version:** 1.0\
**Planning basis:** One developer, assignment-scale MVP\
**Priority:** P0 = required for submission, P1 = important, P2 = stretch

## 1. Delivery strategy

Build a working vertical slice early, then improve model quality and
reporting. Do not spend the whole assignment on model experimentation
before there is an end-to-end application.

Recommended order:

1.  Repository and environment.
2.  Data audit and leakage-safe dataset pipeline.
3.  Baseline ML and evaluation.
4.  Deterministic policy and financial engine.
5.  APIs and persistence.
6.  Frontend dashboard and order review.
7.  WhatsApp and payment simulator.
8.  Backtest, tests, and documentation.

## 2. Epic overview

  Epic                          Outcome                                Priority
  ----------------------------- -------------------------------------- ----------
  E1 Project foundation         Reproducible local setup               P0
  E2 Dataset pipeline           Clean, documented training data        P0
  E3 ML model                   Validated RTO probability              P0
  E4 Decision policy            Four explainable actions               P0
  E5 Financial engine           Consistent unit economics              P0
  E6 API and persistence        Working backend contracts              P0
  E7 WhatsApp simulator         Confirmation and prepaid flows         P0
  E8 Founder dashboard          Daily operational and financial view   P0
  E9 Configuration and audit    Editable policy and traceability       P0
  E10 Backtesting               Historical policy evaluation           P0
  E11 Quality and submission    Tests, README, memo, logs              P0
  E12 Production integrations   Shopify/real WhatsApp/payment          P2

## 3. E1 --- Project foundation

### TASK-001: Create repository structure

**Priority:** P0\
**Dependencies:** None

Create: - `frontend/` - `backend/` - `data/` - `models/` - `config/` -
`docs/` - root `README.md` - root `.gitignore`

Acceptance criteria: - Structure matches the architecture document. -
Frontend and backend can be installed independently. - CSV is stored in
the documented location. - `.env`, virtual environments, database files,
and generated secrets are ignored by Git.

### TASK-002: Initialize FastAPI backend

**Priority:** P0\
**Dependencies:** TASK-001

Implement: - FastAPI app entry point. - Settings management. - CORS for
local frontend. - Structured error response. - `GET /api/v1/health`.

Acceptance criteria: - Backend starts using documented command. - Health
endpoint returns a successful status. - Missing optional LLM credentials
do not prevent startup.

### TASK-003: Initialize React frontend

**Priority:** P0\
**Dependencies:** TASK-001

Implement: - Vite + React + TypeScript. - Router. - Global layout. -
Navigation shell. - API client with base URL from environment. -
Loading, error, and empty-state components.

Acceptance criteria: - Frontend starts using documented command. -
Navigation routes render. - API base URL is configurable. - No secret
key is included in frontend build.

### TASK-004: Add environment configuration

**Priority:** P0\
**Dependencies:** TASK-002, TASK-003

Create `.env.example` for backend and frontend environment variables.

Acceptance criteria: - No real API key is committed. - App works with
LLM disabled. - README explains configuration.

## 4. E2 --- Dataset pipeline

### TASK-005: Inspect and profile CSV

**Priority:** P0\
**Dependencies:** TASK-001

Measure: - Row and column counts. - Column types. - Missing values. -
Duplicate order IDs. - Status distribution. - Payment-method
distribution. - Date range. - Numeric ranges. - Category cardinality.

Acceptance criteria: - Produce `docs/data_profile.md`. - Record exact
counts from the supplied CSV. - Distinguish raw rows from deduplicated
rows. - Do not hardcode exploratory findings into the application.

### TASK-006: Implement data normalization

**Priority:** P0\
**Dependencies:** TASK-005

Implement: - Status normalization. - Payment-method normalization. -
Datetime parsing. - Pincode normalization to string. - Phone
normalization/validation. - Numeric validation. - Missing-value
handling. - Duplicate handling with documented rule.

Acceptance criteria: - Pipeline is repeatable. - Original raw file
remains unchanged. - Every dropped or excluded row has a documented
reason. - Unresolved statuses are not assigned a binary target.

### TASK-007: Create target and leakage checks

**Priority:** P0\
**Dependencies:** TASK-006

Target: - Delivered = 0. - RTO = 1. - Unresolved/unknown = excluded from
supervised labels.

Acceptance criteria: - Target mapping is unit-tested. - `final_status`
is excluded from predictors. - Future delivery fields are excluded. -
Duplicate IDs cannot cross train/test splits.

### TASK-008: Build point-in-time customer features

**Priority:** P0\
**Dependencies:** TASK-006

Calculate for each order using only earlier records: - Prior orders. -
Prior RTOs. - Prior RTO rate. - Prior delivery success rate. -
First-time indicator.

Acceptance criteria: - Current order is excluded from its own history. -
Later orders never affect earlier feature values. - Tests cover a
customer with multiple chronological orders.

### TASK-009: Build geographic features

**Priority:** P1\
**Dependencies:** TASK-006

Calculate historical pincode/city/state rates with sample counts and
smoothing.

Acceptance criteria: - Small groups are marked low-confidence or shrunk
toward a global prior. - Missing pincode does not imply high risk. - No
future outcomes enter historical aggregates. - Geography alone cannot
trigger automatic cancellation.

## 5. E3 --- Machine learning

### TASK-010: Create chronological data split

**Priority:** P0\
**Dependencies:** TASK-007, TASK-008

Define: - Training period. - Validation period. - September 2026
holdout, if data volume permits.

Acceptance criteria: - Split boundaries are documented. - Holdout labels
are not used for model or threshold tuning. - All preprocessing is
fitted on training data only.

### TASK-011: Train baseline model

**Priority:** P0\
**Dependencies:** TASK-010

Train a Logistic Regression pipeline with: - Numeric imputation/scaling
where needed. - Categorical imputation/encoding. - Class weighting only
if justified by training distribution.

Acceptance criteria: - Reproducible training script. - Saved model
pipeline. - Model version metadata. - No target leakage.

### TASK-012: Train and compare candidate model

**Priority:** P1\
**Dependencies:** TASK-011

Compare a tree-based candidate, e.g. Random Forest or
HistGradientBoosting.

Acceptance criteria: - Same chronological evaluation split. - Compare
PR-AUC, ROC-AUC, recall, precision, F1, and calibration. - Record
selected model and reason. - Do not select a model based only on
training score.

### TASK-013: Calibrate probabilities

**Priority:** P0\
**Dependencies:** TASK-011

Evaluate calibration and apply calibration only if validation data
supports it.

Acceptance criteria: - Brier score or calibration report included. -
Predicted probabilities are bounded from 0 to 1. - Calibration is fitted
without holdout leakage. - If calibration is unreliable due to sample
size, disclose limitation.

### TASK-014: Build scoring service

**Priority:** P0\
**Dependencies:** TASK-011

Input: validated feature dictionary.\
Output: probability, model version, timestamp.

Acceptance criteria: - Handles unknown categories. - Returns clear error
if model artifact missing. - Does not select an action. - Includes unit
tests.

### TASK-015: Produce model evaluation report

**Priority:** P0\
**Dependencies:** TASK-012, TASK-013

Report: - Eligible row count. - Class balance. - Split periods. -
Confusion matrix. - Precision, recall, F1. - ROC-AUC, PR-AUC. -
Calibration. - Segment results with sample counts.

Acceptance criteria: - Metrics are calculated on out-of-time data. -
Small subgroup samples are explicitly flagged. - No unsupported accuracy
claims.

## 6. E4 --- LLM validation

### TASK-016: Implement deterministic validators first

**Priority:** P0\
**Dependencies:** TASK-006

Implement: - Phone format validation. - Pincode format validation. -
Required-field checks. - Empty/placeholder string dictionary checks. -
Address length and obvious missing-field checks.

Acceptance criteria: - These checks do not require an LLM. - Results
have stable reason codes. - Missing information is not automatically
labelled fraud.

### TASK-017: Define LLM provider interface

**Priority:** P0\
**Dependencies:** TASK-002

Create provider abstraction and configuration for supported provider(s).

Acceptance criteria: - Provider can be disabled. - Timeout is
configurable. - API key remains server-side. - Provider errors are
normalized.

### TASK-018: Implement structured name/address assessment

**Priority:** P0\
**Dependencies:** TASK-017

LLM tasks: - Identify likely placeholder/test names. - Interpret
Hinglish address descriptions. - Assess address usability and missing
details. - Return structured JSON.

Acceptance criteria: - Output validated with Pydantic. - Prompt says not
to infer identity or legitimacy from demographic attributes. - LLM
output cannot independently cancel an order. - Store only necessary
output and minimal input.

### TASK-019: Implement LLM fallback behavior

**Priority:** P0\
**Dependencies:** TASK-018

Acceptance criteria: - Timeout/malformed output/provider outage returns
`UNAVAILABLE` or `UNCERTAIN`. - Decision engine still works. -
Unavailable LLM is not treated as a risk signal. - Tests simulate
provider failure.

## 7. E5 --- Decision and financial engine

### TASK-020: Implement configuration schema

**Priority:** P0\
**Dependencies:** TASK-002

Create validated configuration for: - Risk thresholds. - Customer
protection. - Confirmation timeout. - Discount amount. - RTO cost
assumptions. - LLM settings.

Acceptance criteria: - Invalid threshold ordering is rejected. -
Configuration is versioned. - Defaults are documented. - Existing
decisions retain their original policy version.

### TASK-021: Implement financial functions

**Priority:** P0\
**Dependencies:** TASK-020

Functions: - Expected RTO cost. - Expected RTO exposure. - Delivered
contribution estimate. - Discount cost. - Confirmation cost, if
applicable. - Estimated cancellation opportunity cost. - Net impact.

Acceptance criteria: - Unit tests validate all formulas. - RTO cost
default is ₹169.40 under supplied assumptions. - Discount cost is
calculated only for eligible successful discounted orders, with offer
exposure separately tracked. - Estimated and actual values are
distinct. - No double counting.

### TASK-022: Implement deterministic policy engine

**Priority:** P0\
**Dependencies:** TASK-014, TASK-016, TASK-019, TASK-020, TASK-021

Implement four assignment buckets: - `SHIP_AS_IS` -
`SHIP_AFTER_CONFIRMATION` - `NUDGE_TO_PREPAID` - `HOLD_CANCEL`

Acceptance criteria: - Same input + same configuration gives same
action. - Every action has reason codes and readable explanation. -
First-time status alone never causes cancellation. - Sparse geography
alone never causes cancellation. - LLM text cannot directly select
action. - Cancellation requires configured strong evidence and manual
review during MVP.

### TASK-023: Add decision explanation builder

**Priority:** P0\
**Dependencies:** TASK-022

Acceptance criteria: - Explanation uses factual reason codes. - No
unsupported claims such as "fraudulent customer". - Explanation is short
and understandable to operations. - Each reason is traceable to an input
or calculation.

### TASK-024: Persist predictions and decisions

**Priority:** P0\
**Dependencies:** TASK-022

Acceptance criteria: - Store feature snapshot, probability, action,
reasons, policy version, and model version. - Decision is
reproducible. - Failed persistence does not report success.

## 8. E6 --- API and persistence

### TASK-025: Implement SQLAlchemy models and migrations/init

**Priority:** P0\
**Dependencies:** TASK-002

Tables: - orders - risk_predictions - order_decisions -
customer_interactions - payment_attempts - order_events -
system_configuration - audit_logs

Acceptance criteria: - Foreign keys and uniqueness constraints work. -
Database initializes from documented command. - Indexes exist for common
lookup fields.

### TASK-026: Implement order endpoints

**Priority:** P0\
**Dependencies:** TASK-025

Endpoints: - Create order. - List/filter/paginate orders. - Get order
details.

Acceptance criteria: - Duplicate order IDs handled safely. - Input
validation errors are readable. - Pagination and filters work.

### TASK-027: Implement decision endpoints

**Priority:** P0\
**Dependencies:** TASK-024, TASK-026

Endpoints: - Evaluate order. - Get decision by order. - List decisions.

Acceptance criteria: - Only COD orders enter COD policy evaluation. -
Prepaid orders are handled through a separate/appropriate path. -
Prediction and decision are persisted. - API response matches documented
schema.

### TASK-028: Implement configuration endpoints

**Priority:** P0\
**Dependencies:** TASK-020, TASK-025

Acceptance criteria: - Get active config. - Update config with
validation. - Store version history. - Write audit event. - Future
decisions use new version; old decisions remain unchanged.

### TASK-029: Implement dashboard and analytics endpoints

**Priority:** P0\
**Dependencies:** TASK-021, TASK-024, TASK-025

Acceptance criteria: - Date range and timezone are explicit. - Bucket
counts are based on decision date. - Financial metrics use central
functions. - Actual, estimated, and assumed figures are separated.

## 9. E7 --- WhatsApp and payment simulation

### TASK-030: Implement workflow state machine

**Priority:** P0\
**Dependencies:** TASK-025

Acceptance criteria: - Valid transitions are enforced server-side. -
Invalid transitions return conflict errors. - Every transition appends
an event. - Duplicate event requests are idempotent.

### TASK-031: Build confirmation message templates

**Priority:** P0\
**Dependencies:** TASK-030

Support English and configurable Hindi/Hinglish templates.

Acceptance criteria: - Message includes order ID and amount. - Message
clearly asks for YES/NO. - No real WhatsApp API is called. - Template
selection is recorded.

### TASK-032: Implement reply parsing

**Priority:** P0\
**Dependencies:** TASK-031

Support: - YES variants. - NO variants. - Ambiguous responses. - One
clarification attempt.

Acceptance criteria: - Case and whitespace normalized. - Explicit NO
never releases shipment. - Ambiguous reply does not release shipment. -
State transitions are tested.

### TASK-033: Implement 24-hour timeout simulation

**Priority:** P0\
**Dependencies:** TASK-030, TASK-031

Acceptance criteria: - Manual "simulate timeout" control works. -
Expired confirmation remains on hold. - Operations review event is
recorded. - No automatic fraud label is applied.

### TASK-034: Implement prepaid offer calculation

**Priority:** P0\
**Dependencies:** TASK-021, TASK-030

Acceptance criteria: - Discount is configurable. - Amount cannot become
negative. - Payable amount is calculated server-side. - Discount and
offer expiry are recorded.

### TASK-035: Implement mock payment outcomes

**Priority:** P0\
**Dependencies:** TASK-034

Support success and failure.

Acceptance criteria: - Successful payment changes payment method/status
to prepaid and approves shipment. - Failed payment does not mark order
prepaid. - Duplicate success callbacks do not duplicate payment. - Mock
transaction references are clearly labelled as mock.

### TASK-036: Implement conversation history endpoint

**Priority:** P0\
**Dependencies:** TASK-031, TASK-032

Acceptance criteria: - Messages are ordered by timestamp. - Incoming and
outgoing messages are distinguishable. - Workflow state is visible.

## 10. E8 --- Frontend

### TASK-037: Build dashboard overview

**Priority:** P0\
**Dependencies:** TASK-029, TASK-003

Display: - Four decision bucket counts. - RTO savings estimate. -
Estimated genuine cancellation loss. - Discount cost. - Net impact. -
Date range and last updated time.

Acceptance criteria: - Values come from API. - Estimates are labelled. -
Empty states are meaningful. - No hardcoded production metrics.

### TASK-038: Build orders list and filters

**Priority:** P0\
**Dependencies:** TASK-026, TASK-003

Filters: - Date. - Decision. - Risk band. - State. - Courier. - Source.

Acceptance criteria: - Pagination works. - Search works. -
Loading/error/empty states work.

### TASK-039: Build order detail page

**Priority:** P0\
**Dependencies:** TASK-027

Display: - Customer/order summary. - Risk probability. - Decision and
reasons. - LLM status. - Workflow timeline. - Financial estimate. -
Manual review controls.

Acceptance criteria: - Sensitive phone number is masked. - Manual
override requires a reason. - UI does not permit invalid transitions.

### TASK-040: Build WhatsApp simulator UI

**Priority:** P0\
**Dependencies:** TASK-036

Acceptance criteria: - Shows conversation. - Supports YES/NO/random
reply. - Supports timeout simulation. - Shows state changes. - Shows
mock prepaid payment actions.

### TASK-041: Build configuration UI

**Priority:** P0\
**Dependencies:** TASK-028

Acceptance criteria: - Risk thresholds editable. - Financial assumptions
editable. - Discount editable. - Validation errors shown. - Save
operation creates a new config version.

### TASK-042: Build analytics and decision logs

**Priority:** P1\
**Dependencies:** TASK-029

Acceptance criteria: - Trend and segment data comes from API. - Sample
sizes are shown. - Small samples are flagged. - Decision history is
filterable.

## 11. E9 --- Backtesting and business reporting

### TASK-043: Implement historical replay

**Priority:** P0\
**Dependencies:** TASK-022, TASK-010

Replay eligible historical COD orders using only point-in-time features.

Acceptance criteria: - September holdout is not used for
training/tuning. - Every replayed order has one policy action. - Output
is reproducible for fixed model/configuration. - Historical observed
outcome is kept separate from simulated intervention outcome.

### TASK-044: Define intervention assumptions

**Priority:** P0\
**Dependencies:** TASK-043

Create explicit configurable assumptions for: - Confirmation response
rate. - Confirmation effectiveness among responders. - Prepaid offer
acceptance rate. - RTO rate after prepaid conversion. - Manual review
release/cancel rates.

Acceptance criteria: - Defaults are labelled assumptions, not dataset
findings. - Sensitivity analysis shows conservative/base/optimistic
scenarios. - Assumptions can be changed without code.

### TASK-045: Generate backtest report

**Priority:** P0\
**Dependencies:** TASK-043, TASK-044

Report: - Orders per bucket. - Actual RTO/delivery outcomes by bucket. -
Estimated avoided RTOs. - Estimated genuine cancellations. - Discount
expense. - Net estimated impact. - Baseline comparison. - Assumption
sensitivity.

Acceptance criteria: - No causal claims from observational data. - All
formulas and assumptions documented. - Results can be regenerated.

### TASK-046: Draft founder memo

**Priority:** P0\
**Dependencies:** TASK-005, TASK-015, TASK-045

Acceptance criteria: - At least three real data findings with counts and
denominators. - Rules and September backtest results. -
Operations/Marketing trade-off in rupees. - Risks and monitoring. -
Two-week roadmap. - No invented or unsupported numbers.

### TASK-047: Create decision log

**Priority:** P0\
**Dependencies:** Ongoing

For each major choice record: - Date. - Decision. - Alternatives
considered. - Reason. - Consequence/trade-off.

Acceptance criteria: - Includes model, policy, LLM, discount,
cancellation, and architecture decisions.

### TASK-048: Create AI usage log

**Priority:** P0\
**Dependencies:** Ongoing

Record: - AI tool. - Task. - Prompt/use. - Output used. - Verification
method. - At least 2--3 weak/incorrect AI outputs and how they were
caught and corrected.

Acceptance criteria: - Examples are genuine and reproducible from actual
work. - Do not fabricate AI mistakes.

## 12. E10 --- Quality and release

### TASK-049: Unit test critical functions

**Priority:** P0\
**Dependencies:** TASK-021, TASK-022, TASK-032, TASK-034

Test: - RTO cost. - Discount. - Threshold boundaries. - Missing
fields. - First-time customer protection. - LLM fallback. -
YES/NO/ambiguous responses. - Timeout. - Payment idempotency.

Acceptance criteria: - All critical paths have automated tests. -
Boundary conditions are covered.

### TASK-050: Integration test full workflows

**Priority:** P0\
**Dependencies:** TASK-027, TASK-030, TASK-035

Scenarios: - COD low risk to shipment approval. - COD moderate risk to
YES to shipment. - Confirmation NO to stop. - No response to hold. -
Prepaid success to shipment. - Payment failure to fallback. -
Configuration update to changed decision.

Acceptance criteria: - Tests use isolated test database. - No real
external message/payment is sent.

### TASK-051: Frontend smoke test

**Priority:** P0\
**Dependencies:** TASK-037 to TASK-041

Acceptance criteria: - Main pages load. - API errors are handled. -
Critical simulator controls work. - Dashboard renders with real API
data.

### TASK-052: README and clean-machine run

**Priority:** P0\
**Dependencies:** TASK-049, TASK-050, TASK-051

README must include: - Prerequisites. - Windows PowerShell setup. -
Backend commands. - Frontend commands. - Dataset location. - Model
training command. - LLM optional setup. - Demo workflow. -
Troubleshooting. - Known limitations.

Acceptance criteria: - A reviewer can run the app in under 10 minutes
with dependencies already available. - No private credentials required
for demo. - No hidden manual setup.

### TASK-053: Final release checklist

**Priority:** P0\
**Dependencies:** All P0 tasks

Acceptance criteria: - Four actions demonstrated. - All required
simulator responses demonstrated. - Dashboard formulas verified. -
Backtest reproducible. - Documentation included. - Git repository
contains no secrets. - Known limitations disclosed.

## 13. Dependency-critical path

``` text
Foundation
   |
Data profile -> Cleaning -> Point-in-time features -> Chronological split
   |                                           |
   |                                           v
   |                                      Train/evaluate
   |                                           |
   v                                           v
Database/API --------------------------> ML scoring
                                               |
LLM validators -------------------------------+
                                               |
Configuration + financial engine -------------+
                                               |
                                        Decision engine
                                               |
                              +----------------+----------------+
                              |                |                |
                         Workflow         Dashboard         Backtest
                              |                |                |
                         Simulator        Frontend          Memo
                              +----------------+----------------+
                                               |
                                         Tests + README
```

## 14. Suggested execution plan

### Day 1

-   TASK-001 to TASK-008.
-   Produce data profile and clean pipeline.

### Day 2

-   TASK-010 to TASK-015.
-   Train baseline, compare model, report limitations.

### Day 3

-   TASK-016 to TASK-024.
-   LLM adapter, rules, financial functions, decision engine.

### Day 4

-   TASK-025 to TASK-030.
-   Database, API, state machine.

### Day 5

-   TASK-031 to TASK-036.
-   Confirmation, prepaid, timeout, payment simulation.

### Day 6

-   TASK-037 to TASK-042.
-   Dashboard, orders, simulator, configuration.

### Day 7

-   TASK-043 to TASK-053.
-   Backtest, tests, memo, logs, README, final review.

This is an aggressive schedule. If time is limited, prioritize a correct
end-to-end workflow and honest backtest over decorative UI or additional
model complexity.

## 15. Definition of done

The assignment is submission-ready only when:

-   A new COD order can be evaluated end-to-end.
-   The system returns one of the four required buckets.
-   Every decision has reason codes and an explanation.
-   Business thresholds are editable.
-   LLM use is bounded and optional.
-   Confirmation and prepaid workflows are demonstrable.
-   Dashboard displays all required metrics.
-   Historical evaluation avoids leakage.
-   Financial assumptions and counterfactual limitations are explicit.
-   Tests cover the critical business paths.
-   README allows a reviewer to run the project.
-   Decision and AI usage logs reflect actual development.
