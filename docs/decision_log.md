# Technical & Product Decision Log — COD Risk Intelligence

**Project:** COD Risk Intelligence & RTO Prevention System  
**Date:** October 30, 2026  
**Status:** Active  

This document logs key architectural, mathematical, and product decisions made during system design and implementation.

---

## Decision 1: Separation of Prediction (ML) from Business Action (Policy)

- **Date:** October 30, 2026
- **Context:** Deciding how the system should determine whether to ship, confirm, nudge, or hold an order.
- **Alternatives Considered:**
  1. Multi-class classification model predicting the four actions directly (`0 = SHIP_AS_IS`, `1 = CONFIRM`, `2 = PREPAID`, `3 = HOLD`).
  2. Binary classification model predicting calibrated RTO probability `P(RTO)`, coupled with an external, deterministic policy rules engine.
- **Decision:** Selected Alternative 2.
- **Rationale:** Business thresholds and discount amounts change frequently based on courier contracts and marketing campaigns. Hardcoding actions into an ML model requires retraining every time a threshold is tweaked. Separating prediction from policy allows business users to modify thresholds dynamically without retraining models.
- **Trade-off:** Requires a two-stage evaluation pipeline (ML scoring followed by policy execution).

---

## Decision 2: Strictly Bounded LLM Responsibilities & Graceful Degradation

- **Date:** October 30, 2026
- **Context:** Determining what role Large Language Models (LLMs) should play in order evaluation.
- **Alternatives Considered:**
  1. Sending entire order JSON to an LLM to decide whether to cancel or ship.
  2. Restricting the LLM exclusively to interpreting unstructured text (Hinglish addresses, placeholder names) and using code for arithmetic, thresholds, and state transitions.
- **Decision:** Selected Alternative 2.
- **Rationale:** LLMs are non-deterministic, can hallucinate financial calculations, and introduce non-deterministic latency. Using an LLM as a final cancellation authority violates basic operational safety. Furthermore, if an external LLM API fails or times out, the system must seamlessly fall back to deterministic regex rules without interrupting order fulfillment.
- **Trade-off:** Unstructured address interpretation requires structured schema parsing and fallback logic.

---

## Decision 3: Progressive Customer Interventions vs. Binary Ship/Cancel

- **Date:** October 30, 2026
- **Context:** Reconciling the conflict between Operations (RTO reduction) and Marketing (customer acquisition).
- **Alternatives Considered:**
  1. Binary decision: Automatically cancel high-probability RTO orders and ship the rest.
  2. Progressive 4-bucket strategy: Ship as-is, Confirm on WhatsApp, Nudge to Prepaid with ₹15 discount, and Hold for manual review.
- **Decision:** Selected Alternative 2.
- **Rationale:** In D2C eCommerce, over 55% of customers prefer COD, and 58% are first-time buyers. Automatically cancelling orders destroys customer acquisition cost (CAC ₹300+) and permanently alienates customers. Progressive interventions allow genuine customers to verify their intent via WhatsApp or pay online with an incentive.
- **Trade-off:** Requires managing state machines for asynchronous customer responses (YES, NO, timeouts, mock payments).

---

## Decision 4: Distinguishing Observed Financials from Counterfactual Estimates

- **Date:** October 30, 2026
- **Context:** Reporting financial impact on the Founder Dashboard.
- **Alternatives Considered:**
  1. Reporting all flagged orders as "Realised Financial Savings".
  2. Strictly categorizing financials into: (a) Realised Cash (redeemed discounts), (b) Counterfactual Estimates (avoided RTO costs based on simulated response rates), and (c) Opportunity Costs (lost contribution from cancelled genuine orders).
- **Decision:** Selected Alternative 2.
- **Rationale:** Presenting counterfactual estimates as realised savings is fraudulent reporting. An operations tool must disclose exact formula assumptions and sensitivity ranges to maintain founder trust.
- **Trade-off:** Dashboard UI requires clear labeling and tooltip explanations.

---

## Decision 5: Chronological Out-of-Time Data Splitting (No Future Leakage)

- **Date:** October 30, 2026
- **Context:** Designing the validation and test strategy for historical data.
- **Alternatives Considered:**
  1. Random train_test_split (80/20) with cross-validation.
  2. Chronological point-in-time splitting: April–July for training, August for validation, and September 2026 as an untouched holdout set.
- **Decision:** Selected Alternative 2.
- **Rationale:** Random splitting causes severe data leakage: customer prior order counts and geographic delivery rates from future months contaminate earlier training samples. In production, models only ever predict forward in time.
- **Trade-off:** Chronological splits can reflect seasonal shifts and sample size constraints on recent months.

---

## Decision 6: Localized Single-Process Architecture for Assignment MVP

- **Date:** October 30, 2026
- **Context:** Selecting backend infrastructure and persistence layer.
- **Alternatives Considered:**
  1. Distributed microservices with Redis queues, Celery, and PostgreSQL.
  2. Modular monolithic FastAPI backend with SQLite persistence and React Vite frontend.
- **Decision:** Selected Alternative 2.
- **Rationale:** The take-home assignment must be easily clonable and runnable locally by a reviewer in under 10 minutes without requiring Docker, external databases, or message brokers. Clear modular package boundaries ensure the code can be extracted into microservices later if volume demands it.
- **Trade-off:** SQLite does not support high-concurrency multi-instance writes, but is ideal for single-server local evaluation.
