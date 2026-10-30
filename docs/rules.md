# Business Rules & Financial Policy --- COD Risk Intelligence

**Version:** 1.0\
**Currency:** INR (₹)\
**Timezone:** Asia/Kolkata\
**Status:** Initial policy proposal; thresholds require chronological
validation

## 1. Purpose and policy hierarchy

This document defines the deterministic rules used to select one of four
assignment actions:

1.  `SHIP_AS_IS`
2.  `SHIP_AFTER_CONFIRMATION`
3.  `NUDGE_TO_PREPAID`
4.  `HOLD_CANCEL`

The system must separate:

-   **Prediction:** estimated probability that an order will RTO.
-   **Evidence:** customer history, data quality, and address
    validation.
-   **Policy:** deterministic action selection.
-   **Workflow:** what happens after the action.
-   **Financial evaluation:** estimated cost/benefit of each
    intervention.

A risk score is not proof of fraud. A first-time customer is not
inherently suspicious. A pincode with little data is unknown, not high
risk.

## 2. Source assumptions

Supplied business assumptions:

  Parameter                        Default
  ------------------------------ ---------
  Monthly orders                     3,000
  COD share                            55%
  COD RTO rate                         28%
  Prepaid RTO rate                      4%
  AOV                                 ₹649
  Delivered gross margin               62%
  CAC                                ₹300+
  Forward shipping                     ₹65
  Return shipping                      ₹65
  Packaging/handling                   ₹25
  Product cost                        ₹180
  Returned-product damage rate          8%

These are assignment-level baseline assumptions. Replace them with
measured values when reliable operational data becomes available.

## 3. Financial constants and formulas

### 3.1 Expected damage cost per RTO

`Expected damage cost = Product cost × Damage probability`

`= ₹180 × 0.08 = ₹14.40`

### 3.2 Expected direct cost per RTO

`Expected RTO cost = Forward shipping + Return shipping + Packaging/handling + Expected damage cost`

`= ₹65 + ₹65 + ₹25 + ₹14.40`

`= ₹169.40`

This is an expected average cost, not the cost of every individual RTO.
It assumes the supplied 8% damage rate applies to returned products.

### 3.3 Monthly baseline estimate

`Monthly COD orders = 3,000 × 55% = 1,650`

`Expected COD RTOs = 1,650 × 28% = 462`

`Expected monthly direct RTO cost = 462 × ₹169.40 = ₹78,262.80`

This is a baseline estimate. It does not establish how many RTOs the new
system can prevent.

### 3.4 Delivered gross contribution

`Gross contribution per delivered order = AOV × gross margin`

`= ₹649 × 62% = ₹402.38`

Use this as the estimated gross contribution before additional costs not
already included in the gross-margin definition. Do not call it net
profit.

### 3.5 Prepaid discount comparison

Observed baseline difference:

`COD RTO rate - prepaid RTO rate = 28% - 4% = 24 percentage points`

Simplified expected RTO-cost difference:

`24% × ₹169.40 = ₹40.656`, approximately ₹40.66.

At a ₹15 discount:

`₹40.66 - ₹15 = ₹25.66`

This is a simplified expected-cost comparison. It assumes a COD order
converted to prepaid behaves like the existing prepaid cohort. That
assumption may be wrong due to customer selection effects and must be
tested.

### 3.6 Prepaid offer economics with conversion

For each eligible order, define:

-   `p_accept`: probability customer accepts the offer.
-   `r_cod`: expected RTO probability if order remains COD.
-   `r_prepaid`: expected RTO probability if successfully converted to
    prepaid.
-   `d`: discount amount.
-   `c_msg`: message/communication cost, if known.

Expected RTO cost reduction for a successful conversion:

`(r_cod - r_prepaid) × RTO_COST`

Expected value per eligible offer, simplified:

`p_accept × ((r_cod - r_prepaid) × RTO_COST - d) - c_msg`

This excludes any difference in conversion/abandonment and payment
processing fees. Add those when reliable data exists.

Discount must be applied only once and only to an eligible order. Do not
apply it to an already-paid order or stack multiple offers.

### 3.7 Confirmation economics

Define:

-   `p_reply`: probability of a valid response.
-   `p_confirm`: probability a responding customer confirms.
-   `r_after_confirm`: RTO probability after confirmation.
-   `r_without`: baseline RTO probability.
-   `c_confirm`: communication/handling cost.

Simplified expected value:

`p_reply × p_confirm × ((r_without - r_after_confirm) × RTO_COST) - c_confirm`

A confirmation is not guaranteed to prevent RTO. A customer saying YES
confirms intent at that time; delivery can still fail.

### 3.8 Cancellation opportunity cost

For a cancelled order, estimate probability it would otherwise have been
delivered, `p_genuine`.

`Estimated lost gross contribution = p_genuine × AOV × gross margin`

At the supplied AOV and margin:

`₹649 × 62% = ₹402.38` per order if it would have been delivered.

For `n` cancelled orders:

`Estimated lost gross contribution = n × p_genuine × ₹402.38`

This is an opportunity-cost estimate, not cash already paid out. Do not
automatically add CAC again: acquisition spend is usually already
incurred. If management wants a separate CAC allocation view, show it
separately and label it clearly.

### 3.9 Net estimated impact

Use a consistent counterfactual baseline:

`Net estimated impact = Estimated avoided RTO cost - Estimated lost gross contribution - Discount cost - Intervention cost - Incremental operating cost`

Rules:

-   Count each order's avoided RTO benefit at most once.
-   Do not count both a full RTO cost and its component costs.
-   Do not count a discount for an offer that was not redeemed, unless
    the discount was actually issued.
-   Separate actual cost from expected cost.
-   Do not count a cancelled order as a prevented RTO unless its
    counterfactual RTO probability supports that estimate.
-   Report uncertainty and assumptions beside the total.

## 4. Risk probability bands

Initial configurable thresholds:

  Predicted RTO probability   Band       Default policy
  --------------------------- ---------- -------------------------
  0.00--\<0.20                LOW        Ship as-is
  0.20--\<0.40                MODERATE   Ship after confirmation
  0.40--\<0.65                ELEVATED   Prepaid nudge
  0.65--1.00                  HIGH       Hold / manual review

Boundary handling:

-   Exactly 0.20 enters MODERATE.
-   Exactly 0.40 enters ELEVATED.
-   Exactly 0.65 enters HIGH.
-   Probability must be finite and between 0 and 1.

These thresholds are initial product defaults, not evidence-based
optimal cutoffs. Calibrate them on validation data using expected
financial cost and customer-protection constraints. Do not tune them
against the September holdout.

## 5. Action selection rules

### 5.1 Precedence

Apply rules in this order:

1.  Validate order and payment type.
2.  Detect duplicate/invalid order record.
3.  Apply hard operational blockers.
4.  Calculate ML probability and deterministic evidence.
5.  Apply risk band.
6.  Apply customer-protection and evidence overrides.
7.  Calculate action economics where required.
8.  Persist action, reasons, policy version, and assumptions.

### 5.2 Rule A --- Ship as-is

Choose `SHIP_AS_IS` when:

-   Predicted risk is below the confirmation threshold.
-   No hard operational blocker exists.
-   Required shipping information is sufficiently usable.
-   No strong invalid-order evidence exists.

Reason examples:

-   `LOW_PREDICTED_RTO_RISK`
-   `ADDRESS_USABLE`
-   `NO_STRONG_NEGATIVE_HISTORY`

Do not require an LLM result to ship a low-risk order if deterministic
data is sufficient.

### 5.3 Rule B --- Ship after confirmation

Choose `SHIP_AFTER_CONFIRMATION` when:

-   Risk is in the moderate band; or
-   Risk is elevated but prepaid is unavailable/declined and policy
    permits confirmation; or
-   There is address ambiguity that the customer can reasonably clarify.

Workflow: - Send confirmation message. - Hold dispatch. - YES: mark
confirmed and release to shipment queue. - NO: stop dispatch and mark
customer-declined/cancelled according to policy. - Ambiguous reply: send
one clarification. - No valid response within 24 hours: hold and create
operations review.

A YES response does not change the model's original score. It changes
workflow status and provides a new piece of evidence.

### 5.4 Rule C --- Nudge to prepaid

Choose `NUDGE_TO_PREPAID` when:

-   Risk is elevated.
-   A prepaid offer is enabled.
-   Order is eligible for the discount.
-   The estimated benefit of a successful conversion is positive under
    configured assumptions.
-   No hard invalid-order blocker exists.

If offer economics are negative, use confirmation or manual review
instead.

Fallback: - Successful payment: mark prepaid and release. - Payment
failure: keep order and offer retry or confirmation. - Customer
declines: preserve COD and use confirmation/manual review policy. - No
response in 24 hours: expire offer; do not automatically cancel.

### 5.5 Rule D --- Hold / cancel

Assignment bucket: `HOLD_CANCEL`.

Use HOLD for: - High predicted risk. - Missing or invalid
delivery-critical details. - Uncertain LLM assessment. - Conflicting
signals requiring review. - Confirmation timeout. - Payment/workflow
inconsistency.

Use CANCEL only when: - Customer explicitly says NO; or -
Duplicate/invalid order is verified; or - Strong operational evidence
makes fulfilment impossible; or - An authorized human reviews the order
and approves cancellation.

For the MVP, high model probability alone must route to HOLD/manual
review, not automatic cancellation.

Do not cancel solely because: - Customer is first-time. - Pincode has
few observations. - Customer belongs to a particular state/city. -
Acquisition source is Meta. - LLM returns `UNCERTAIN`. - Phone format is
unusual but still reachable.

## 6. Customer history rules

### 6.1 First-time customers

Definition: no prior completed order history available before the
current order timestamp.

Policy: - Do not add an automatic cancellation penalty. - Use the model
probability and available data. - Prefer confirmation/prepaid
interventions over cancellation when risk is uncertain. - Track
first-time cohort performance separately.

### 6.2 Previous RTO history

Calculate:

`Prior RTO rate = Prior RTO count / Prior eligible orders`

Rules: - Use only historical orders before the current order. - Include
sample count with the rate. - Shrink small-sample estimates toward the
global prior or mark low confidence. - Do not use a raw one-order
history as conclusive evidence. - Multiple previous RTOs can contribute
to high-risk review but do not prove fraud.

### 6.3 Geographic history

-   Use pincode/state/city rates only with sample counts.
-   Use smoothing for small groups.
-   Mark low-volume geography as `INSUFFICIENT_HISTORY`.
-   Never use geography as the sole cancellation reason.
-   Monitor group-level false-positive rates and customer impact.

### 6.4 Acquisition source

-   Acquisition channel may be a model feature only if it is available
    at decision time and passes validation.
-   Do not hardcode Meta as risky or safe.
-   Report outcomes by channel with sample counts.
-   Evaluate customer acquisition cost and future value separately from
    order-level RTO cost.

## 7. Data-quality and LLM rules

### 7.1 Deterministic checks

Use code for: - Required field presence. - Phone format. - Six-digit
pincode format. - Numeric order value. - Duplicate order IDs. -
Empty/placeholder string exact matches. - Historical rate
calculations. - Financial arithmetic.

### 7.2 LLM checks

Use an LLM only for: - Ambiguous name patterns beyond simple placeholder
matching. - Natural-language address interpretation. - Hinglish address
parsing. - Address completeness and landmark extraction.

LLM result enums:

`name_quality`: `VALID`, `SUSPICIOUS`, `UNCERTAIN`

`address_quality`: `USABLE`, `NEEDS_CLARIFICATION`, `INSUFFICIENT`,
`UNCERTAIN`

### 7.3 LLM policy

-   `VALID` is not proof of a real person/address.
-   `SUSPICIOUS` is a review signal, not a cancellation command.
-   `UNCERTAIN` is neutral.
-   LLM unavailable is neutral.
-   LLM output must be schema-validated.
-   LLM cannot calculate risk probability or financial impact.
-   LLM cannot directly select or execute cancellation.

### 7.4 Hard blockers

A hard blocker is limited to a deterministic, operationally meaningful
issue, such as: - Duplicate order ID already processed. -
Invalid/non-positive order amount. - Explicit customer refusal. -
Delivery-critical address data absent and not recoverable. - Verified
invalid order.

A missing pincode alone is not necessarily a hard blocker if the address
can be manually resolved.

## 8. WhatsApp message rules

### 8.1 Confirmation message

Send immediately after `SHIP_AFTER_CONFIRMATION` is selected.

Must include: - Customer first name where available. - Brand name. -
Order ID. - Order amount. - Clear YES/NO instruction. - Support contact
or help instruction if configured.

Language: - English default. - Hindi/Hinglish option. - Do not infer
language from name, religion, state, or other sensitive attributes. Use
an explicit customer preference if available; otherwise use default or a
neutral language setting.

### 8.2 Reply parsing

Normalize whitespace and case.

Explicit YES examples: - YES - Y - HAAN - HAA - CONFIRM

Explicit NO examples: - NO - N - NAHI - CANCEL

Do not interpret ambiguous phrases such as "maybe", "later", or "okay"
as confirmation. Ask the customer to reply YES or NO.

### 8.3 Reminder and timeout

-   Send initial message immediately.
-   At most one reminder, if enabled, before the 24-hour deadline.
-   At 24 hours without valid response, set `CONFIRMATION_TIMEOUT` and
    `HOLD`.
-   Do not dispatch on timeout.
-   Do not auto-cancel solely due to silence.
-   Record all message timestamps and statuses.

### 8.4 Prepaid offer

Initial discount: ₹15.

-   Offer is optional.
-   Show original amount, discount, and payable amount.
-   Use server-calculated amount.
-   Set offer expiry to 24 hours by default.
-   Do not stack discounts.
-   If customer declines or offer expires, retain COD unless another
    independent policy reason requires review.

### 8.5 Mock payment

-   Payment success must be an explicit simulator action.
-   Payment failure must not change payment method to prepaid.
-   Store a mock transaction reference.
-   Never imply that a real payment occurred.

## 9. Configuration defaults

Example `config/decision_rules.json`:

``` json
{
  "policy_version": "1.0",
  "timezone": "Asia/Kolkata",
  "risk_thresholds": {
    "ship_as_is_max": 0.20,
    "confirmation_max": 0.40,
    "prepaid_max": 0.65,
    "hold_min": 0.65
  },
  "financials": {
    "forward_shipping": 65,
    "return_shipping": 65,
    "packaging_handling": 25,
    "product_cost": 180,
    "damage_probability": 0.08,
    "aov": 649,
    "gross_margin": 0.62,
    "cac_reference": 300
  },
  "prepaid_offer": {
    "enabled": true,
    "discount_amount": 15,
    "currency": "INR",
    "expiry_hours": 24
  },
  "confirmation": {
    "enabled": true,
    "timeout_hours": 24,
    "max_reminders": 1
  },
  "customer_protection": {
    "protect_first_time_customers": true,
    "manual_review_before_cancellation": true,
    "geography_alone_can_cancel": false,
    "llm_alone_can_cancel": false
  },
  "intervention_assumptions": {
    "confirmation_response_rate": null,
    "confirmation_effectiveness": null,
    "prepaid_acceptance_rate": null,
    "prepaid_rto_rate": 0.04
  }
}
```

`null` intervention assumptions mean they must be supplied for scenario
simulation or clearly reported as unavailable. Do not silently
substitute fabricated values.

Validation: - Probabilities must be between 0 and 1. - Thresholds must
be ordered and cover the full interval. - Costs and discounts must be
non-negative. - Gross margin must be between 0 and 1. - Timeout must be
positive. - Configuration changes create a new version and audit record.

## 10. Dashboard reporting definitions

### 10.1 Four bucket counts

Count unique orders by their latest decision for the selected decision
date:

-   Ship as-is.
-   Ship after confirmation.
-   Nudge to prepaid.
-   Hold/cancel.

Do not count message retries as new orders. Decide whether the dashboard
shows initial recommended bucket or current operational status; expose
both if useful.

### 10.2 Estimated avoided RTOs

A counterfactual estimate must be explicit. Example scenario method:

`Estimated avoided RTOs = eligible intervention orders × assumed intervention success rate × estimated RTO reduction`

Then:

`Estimated avoided RTO cost = Estimated avoided RTOs × ₹169.40`

Do not use "number of risky orders" as the number of avoided RTOs.

### 10.3 Estimated genuine cancellations

`Estimated genuine cancellations = cancelled orders × estimated probability of delivery without cancellation`

`Estimated lost gross contribution = estimated genuine cancellations × ₹402.38`

The probability must come from a documented estimate or validated model.
If unavailable, show "not yet estimable" rather than invent a figure.

### 10.4 Discount cost

Report separately: - Offers sent. - Offers accepted. - Discounts
redeemed. - Total discount value actually granted.

### 10.5 Net impact

`Net estimated impact = estimated avoided RTO cost - estimated lost gross contribution - redeemed discount cost - intervention cost`

Display actual and estimated components separately. Show the assumptions
used.

## 11. Backtest rules

-   Use chronological train/validation/test splits.
-   September 2026 can be holdout only if it is excluded from training
    and threshold selection.
-   Compute customer and geography history as of each order timestamp.
-   Deduplicate before splitting.
-   Exclude unresolved statuses from binary outcome evaluation.
-   Replay only eligible COD orders for COD policy evaluation.
-   Do not pretend historical data reveals how customers would have
    responded to messages.
-   Confirmation and prepaid conversion assumptions must be labelled
    scenario inputs until measured in a live test.
-   Report conservative, base, and optimistic scenarios.
-   Show sample size for every subgroup.

## 12. Policy boundary examples

  -----------------------------------------------------------------------
  Scenario                Expected action         Reason
  ----------------------- ----------------------- -----------------------
  Risk 8%, usable address Ship as-is              Low estimated risk

  Risk 28%, first-time    Confirmation            Protect customer while
  buyer                                           checking intent

  Risk 52%, prepaid offer Prepaid nudge           Intervention may reduce
  has positive expected                           expected loss
  value                                           

  Risk 78%, uncertain     Hold/manual review      High risk and
  address                                         unresolved information

  Customer replies NO     Stop/cancel             Explicit customer
                                                  refusal

  Customer does not reply Hold                    No confirmation
  for 24h                                         received

  LLM unavailable         Continue without LLM    Provider outage is not
                                                  customer risk

  Pincode has 2           Do not geographically   Insufficient evidence
  historical orders       cancel                  

  First-time customer     Use score +             Geography/newness alone
  from high-RTO state     intervention            cannot cancel

  Mock payment succeeds   Mark prepaid            Verified simulator
                                                  event

  Mock payment fails      Keep original order     No successful payment
  -----------------------------------------------------------------------

## 13. Monitoring and policy review

Review at least weekly during controlled rollout:

-   RTO rate by decision bucket.
-   RTO rate for first-time and returning customers.
-   Genuine cancellation rate from manual review.
-   Confirmation response and timeout rates.
-   Prepaid offer acceptance and payment completion.
-   Discount spend per incremental prepaid conversion.
-   Net financial impact.
-   False-positive rate by geography and acquisition source.
-   Model calibration and drift.
-   LLM failure and uncertain-result rates.

Pause or roll back an intervention if: - Genuine cancellation rate
exceeds the approved limit. - First-time customer conversion materially
deteriorates. - Net impact becomes negative for a sustained period. -
Model/data pipeline shows leakage or material corruption. - A
configuration change causes unexpected bucket spikes.

## 14. Non-negotiable safeguards

1.  No automatic cancellation based only on ML score in the MVP.
2.  No cancellation based only on LLM output.
3.  No cancellation based only on pincode/state.
4.  First-time customer status alone is not a negative signal.
5.  No shipment release on ambiguous confirmation.
6.  No shipment release on payment failure.
7.  No fabricated dashboard savings.
8.  No use of future data in historical prediction.
9.  Every decision stores policy/model version.
10. Every manual override requires a reason.
