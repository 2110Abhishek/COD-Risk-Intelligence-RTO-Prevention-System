# Executive Business Memo — COD Risk Intelligence & RTO Prevention

**To:** Founder & Executive Leadership  
**From:** Associate Software Engineer  
**Date:** October 30, 2026  
**Subject:** COD Risk Assessment Platform — Historical Audit, Unit Economics & Rollout Recommendation  

---

## 1. Executive Summary

At our current monthly scale of **3,000 orders**, Cash on Delivery (COD) represents **55% of total order volume** (1,650 orders/month). However, **28% of incoming COD orders result in Return to Origin (RTO)**, compared to just **4% for prepaid orders**.

Each RTO incurs direct operational losses across four distinct cost heads:
1. **Forward shipping:** ₹65.00
2. **Return shipping:** ₹65.00
3. **Packaging & handling:** ₹25.00
4. **Expected product damage (8% rate on ₹180 product cost):** ₹14.40
**Total direct cash loss per preventable RTO:** **₹169.40**

At 462 monthly COD RTOs, this drains **₹78,262.80 per month** in direct operational cash, completely excluding indirect overheads such as customer support, tied-up inventory, and wasted acquisition spend.

To eliminate this waste while protecting genuine customer acquisition, we have designed and built a **financially intelligent decision platform**. Rather than rejecting customers or relying on rigid black-box rules, the platform evaluates each COD order and applies one of four progressive business interventions:
1. **Ship As-Is:** Low risk, clean address, genuine intent (immediate dispatch).
2. **Ship After Confirmation:** Moderate risk or first-time buyer (WhatsApp 2-way verification).
3. **Nudge to Prepaid:** Elevated financial exposure (offer ₹15 discount to secure prepaid payment).
4. **Hold for Review:** High risk, missing address, or customer refusal (human operations review before any cancellation).

---

## 2. Key Findings from the Historical Dataset (`orders_sample.csv`)

A rigorous audit of the supplied 2,018 historical order records revealed several critical operational patterns:

### Finding 1: Duplicate Order IDs & Data Ingestion Hazards
- **Total raw rows:** 2,018
- **Unique orders:** 2,000
- **Duplicate records identified:** **18 duplicate orders** (0.9% of total volume).
- *Action taken:* The data pipeline strictly deduplicates incoming orders using an idempotent ingestion policy to prevent duplicate dispatches and double billing.

### Finding 2: Unresolved Orders & Target Integrity
- Exactly **1 record** had status `IN_TRANSIT` (September 2026).
- *Action taken:* To prevent data leakage and label corruption, unresolved orders are strictly excluded from supervised model training and binary performance metrics.

### Finding 3: The Power of Progressive Interventions (First-Time Buyers)
- Over **58% of our customer base are first-time buyers** with no prior completed orders (`customer_prior_orders == 0`).
- *Marketing vs. Operations Conflict:* Automatically cancelling risky first-time buyers destroys acquisition ROI (CAC ₹300+) and lifetime customer value.
- *Solution:* Our decision policy enforces a **strict customer protection safeguard**: first-time buyers with moderate risk are routed to **WhatsApp confirmation**, verifying intent without brand friction.

### Finding 4: Address Quality as a Predictive Signal
- Analysis revealed that orders with severe placeholder text (e.g. `xyz`, single characters, or missing street details) suffered a **100% RTO rate**.
- Conversely, addresses containing colloquial Hinglish landmarks (e.g. *"Station chowk se left, Hanuman Mandir ke saamne"*) achieved successful delivery in over **82% of cases**.
- *System Design:* Our hybrid validation engine treats colloquial landmarks as valuable locational assets while flagging genuine placeholders for operations review.

---

## 3. September 2026 Holdout Backtest Results

To evaluate true real-world efficacy, we conducted an out-of-time chronological backtest on the **September 2026 holdout dataset** (orders that the machine learning model had never seen during training).

### Decision Distribution on September COD Orders
- **Total September COD Orders Evaluated:** ~260 orders
- **Ship As-Is (Low Risk):** 46.2% of orders
- **Ship After Confirmation (Moderate Risk):** 28.5% of orders
- **Nudge to Prepaid (Elevated Risk):** 16.5% of orders
- **Hold for Review (High Risk / Blockers):** 8.8% of orders

### Financial Sensitivity Analysis (Three Scenarios)

Because live customer response rates cannot be retrospectively observed, we modeled three explicit scenarios:

| Metric | Conservative | Base Case | Optimistic |
|---|---|---|---|
| **WhatsApp Confirmation Response Rate** | 50% | **65%** | 80% |
| **Confirmation Effectiveness** | 50% | **70%** | 80% |
| **Prepaid Discount Conversion Rate** | 8% | **12%** | 18% |
| **Avoided Monthly RTOs** | ~18 orders | **~26 orders** | ~35 orders |
| **Avoided Direct RTO Losses** | ₹3,049.20 | **₹4,404.40** | ₹5,929.00 |
| **Less: Genuine Cancellation Opportunity Cost** | ₹482.86 | **₹241.43** | ₹120.71 |
| **Less: Redeemed Prepaid Discounts (@ ₹15)** | ₹51.60 | **₹77.40** | ₹116.10 |
| **Net Estimated Monthly Benefit (Holdout Sample)** | **+₹2,514.74** | **+₹4,085.57** | **+₹5,692.19** |

*Extrapolating Base Case to full brand monthly volume (1,650 COD orders):*  
- **Expected preventable RTOs:** **150–165 orders per month**
- **Net monthly financial savings:** **~₹22,000 – ₹27,500 per month**
- **Relative COD RTO rate reduction:** **from 28.0% down to ~18.5% – 20.0%**

---

## 4. Reconciling Stakeholder Conflicts

### For Head of Operations
- Immediate elimination of high-risk dispatches (unusable addresses, repeated historical refusals).
- Transparent queue of held orders with specific, plain-English reason codes.
- Real-time courier performance tracking to identify logistics failure points.

### For Head of Marketing
- **Zero automatic cancellations for new customers.** First-time buyers receive polite, brand-aligned WhatsApp confirmation prompts.
- Customers nudged to prepaid are offered an attractive ₹15 discount, driving higher prepaid adoption and building payment trust.
- Non-delivery risk is verified by customer action, not demographic profiling or geographic discrimination.

---

## 5. Five-Phase Implementation Roadmap

1. **Phase 1: Local Verification & Shadow Mode (Weeks 1–2)**
   - Ingest live Shopify webhook orders in shadow mode.
   - Record recommended decisions without modifying courier dispatch.
   - Validate calibration and false-positive rates against actual outcomes.

2. **Phase 2: Controlled WhatsApp Confirmation (Weeks 3–4)**
   - Introduce WhatsApp confirmation for moderate-risk orders.
   - Measure actual customer reply rates (target: >60%) and turnaround time.

3. **Phase 3: Prepaid Discount Pilot (Weeks 5–6)**
   - Pilot the ₹15 prepaid discount incentive on elevated-risk orders.
   - Measure incremental conversion and payment completion via payment gateway webhook.

4. **Phase 4: Limited Automation (Weeks 7–8)**
   - Automate immediate dispatch for `SHIP_AS_IS` low-risk orders.
   - Keep high-risk orders under operations manager manual review.

5. **Phase 5: Continuous Optimization & Policy Governance (Ongoing)**
   - Operations teams adjust risk thresholds and discount amounts via the Configuration Console without developer intervention.

---

## 6. Conclusion

This platform balances financial prudence with customer growth. By combining scikit-learn probability estimation, deterministic business rules, and transparent unit economics, the brand can prevent over **₹25,000/month in avoidable shipping waste** while preserving customer trust and checkout conversion.
