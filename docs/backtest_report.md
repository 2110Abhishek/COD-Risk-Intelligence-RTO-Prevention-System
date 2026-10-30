# Historical Policy Backtest Report (September 2026 Holdout)

**Evaluation Dataset:** September 2026 COD Holdout (Strict point-in-time, no leakage)  
**Total Evaluated COD Orders:** 328  
**Actual September Baseline RTOs:** 85 (25.9%)  
**Baseline Direct RTO Losses:** ₹14,399.00 (@ ₹169.40 per RTO)  
**Date of Run:** October 30, 2026

---

## 1. Decision Bucket Distribution & Historical Accuracy

| Decision Action | Orders Flagged | Share | Actual Delivered | Actual RTO | RTO Rate in Bucket |
|---|---|---|---|---|---|
| **`SHIP_AS_IS`** | 42 | 12.8% | 40 | 2 | 4.8% |
| **`SHIP_AFTER_CONFIRMATION`** | 105 | 32.0% | 88 | 17 | 16.2% |
| **`NUDGE_TO_PREPAID`** | 110 | 33.5% | 80 | 30 | 27.3% |
| **`HOLD_CANCEL`** | 71 | 21.6% | 35 | 36 | 50.7% |

---

## 2. Financial Sensitivity Analysis

Because customer behavior under new interventions is simulated counterfactually, we evaluate three rigorous scenarios:

| Scenario | Avoided RTOs | Avoided RTO Savings | Genuine Cancellation Loss | Redeemed Discounts | **Net Estimated Impact** | New RTO Rate |
|---|---|---|---|---|---|---|
| **Conservative** | 33.3 | ₹5,642.23 | ₹281.67 | ₹132.00 | **₹5,228.56** | 15.8% |
| **Base Case** | 37.8 | ₹6,406.83 | ₹140.83 | ₹198.00 | **₹6,068.00** | 14.4% |
| **Optimistic** | 42.5 | ₹7,200.95 | ₹70.42 | ₹297.00 | **₹6,833.54** | 13.0% |

---

## 3. Operations vs. Marketing Tradeoff Analysis
- **Operations:** RTO rate drops from 25.9% down to **14.4%**, preventing ~37.8 RTOs and saving ₹6,406.83 in direct shipping and packaging waste.
- **Marketing:** Customer acquisition is protected by strictly forbidding automatic cancellation for first-time buyers; genuine cancellation risk is kept below 1%, protecting long-term LTV and customer trust.
