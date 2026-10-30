# AI Assistance & Verification Log

**Project:** COD Risk Intelligence & RTO Prevention System  
**Date:** October 30, 2026  

This log documents how AI assistance was utilized throughout development, the prompt strategies employed, the manual verification steps applied, and specific instances of weak or incorrect AI outputs that were caught and corrected.

---

## 1. Summary of AI Tools Utilized

- **Tool:** Google Antigravity AI Coding Assistant (Gemini 3.8 Flash).
- **Core Tasks:**
  - Scaffolding FastAPI routes, Pydantic schemas, and SQLAlchemy database models.
  - Designing scikit-learn feature engineering pipelines and model comparison scripts.
  - Generating TypeScript contracts and React dashboard layout components.
  - Drafting backtest simulation algorithms and business documentation.

---

## 2. Verification Protocol

Every AI-generated code artifact was subjected to the following mandatory checks before acceptance:
1. **Financial Formula Verification:** Cross-referenced all arithmetic against the base problem statement:
   - Expected damage: `₹180 × 8% = ₹14.40`
   - Expected RTO cost: `₹65 + ₹65 + ₹25 + ₹14.40 = ₹169.40`
   - Delivered gross contribution: `₹649 × 62% = ₹402.38`
2. **Leakage & Target Verification:** Verified that `final_status` is never used as an input feature and that customer history is computed strictly point-in-time.
3. **State Machine Integrity:** Enforced server-side state transitions so that UI clicks cannot illegitimately approve or cancel orders.
4. **Offline Resilience:** Tested that the platform starts and functions 100% deterministically when LLM credentials are absent.

---

## 3. Caught and Corrected AI Mistakes (Real Instances)

### Weak Output 1: Attempted Automatic Cancellation of First-Time Customers
- **AI Suggestion:** In an early draft of the policy rules, the AI proposed:
  ```python
  if rto_probability > 0.65:
      action = "CANCEL"
  ```
- **Why It Was Weak/Flawed:** This logic would automatically cancel orders from first-time customers with elevated risk scores (e.g. from low-data regions or missing pincode characters). In D2C ecommerce, first-time customers represent 58% of new orders and cost ₹300+ in acquisition spend. Automatically cancelling them destroys acquisition ROI.
- **Correction Applied:** Replaced automatic cancellation with **customer protection safeguards**:
  ```python
  if rto_probability > 0.65:
      action = "HOLD_CANCEL"
      operational_status = "HOLD" # Requires manual review, never auto-cancelled
  ```

### Weak Output 2: Double-Counting Customer Acquisition Cost (CAC) as a Cancellation Loss
- **AI Suggestion:** During the financial impact calculation, the AI generated:
  ```python
  cancellation_loss = genuine_orders * (gross_margin_loss + cac_reference)
  ```
- **Why It Was Weak/Flawed:** Customer Acquisition Cost (CAC) is a sunk cost already incurred when the customer placed the order through advertising (Meta/Google). Adding CAC again to the lost gross contribution double-counts the marketing loss.
- **Correction Applied:** Fixed the formula to measure only lost gross contribution:
  ```python
  cancellation_loss = genuine_orders * (order_value * gross_margin)
  # CAC is tracked as a separate reporting reference, not double-counted as cash loss
  ```

### Weak Output 3: Claiming Causal Intervention Lift from Observational Historical Data
- **AI Suggestion:** In an early backtest draft, the AI stated: *"Our backtest proves that sending WhatsApp messages reduces COD RTO by exactly 24%."*
- **Why It Was Weak/Flawed:** Historical order data only records what happened under standard dispatch without interventions. It cannot causally prove how customers would have responded to a hypothetical WhatsApp message or prepaid discount.
- **Correction Applied:** Clarified that intervention performance is an **assumed counterfactual scenario** subject to sensitivity analysis (Conservative, Base, Optimistic), and must be validated through controlled live experimentation.
