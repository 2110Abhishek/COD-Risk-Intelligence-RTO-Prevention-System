# COD Risk Intelligence & RTO Prevention System

**Autonomous Pre-Dispatch Risk Engine & Workflow Automation Platform**  
*Tailored for Direct-to-Consumer (D2C) Haircare Brands (Bliss Bloomly)*  
*Assignment: Associate Software Engineer – Take-Home Project*  
*Date: October 30, 2026 | Version: 1.0.0*

---

## 1. Executive Summary

In the Indian Direct-to-Consumer (D2C) ecosystem, Cash on Delivery (COD) accounts for over **55% of total orders**, but suffers from an acute **28% Return to Origin (RTO) rate**. Every RTO order incurs unrecoverable deadweight losses from forward shipping, return reverse logistics, custom packaging, handling, and damaged inventory.

Traditional approaches make one of two costly mistakes:
1. **Blind Shipment:** Shipping every COD order indiscriminately, burning ₹169.40 per failed delivery.
2. **Aggressive Auto-Cancellation:** Ruthlessly cancelling risky-looking orders, inadvertently rejecting genuine first-time buyers and destroying customer acquisition spend (CAC > ₹300).

The **COD Risk Intelligence & RTO Prevention System** is an end-to-end, full-stack decision and workflow automation platform. It calculates point-in-time RTO probability before dispatch and applies a progressive, 4-action intervention policy that optimizes **net business profit** rather than raw prediction accuracy.

---

## 2. Core Unit Economics & Financial Formulas

All financial calculations in the system are deterministic and governed by the business parameters defined in the specification:

| Parameter | Unit Cost | Source / Justification |
|---|---|---|
| **Forward Shipping** | ₹65.00 | 3PL standard surface forward shipping fee |
| **Return Shipping** | ₹65.00 | Reverse courier handling fee back to origin |
| **Packaging & Handling** | ₹25.00 | Tamper-proof mailer, box, bubble wrap, labor |
| **Average Product Cost** | ₹180.00 | Cost of Goods Sold (COGS) baseline |
| **Transit Damage Rate** | 8.0% | Historical inventory write-off on returned goods |
| **Delivered Gross Margin** | 62.0% | Contribution margin before CAC |
| **Average Order Value (AOV)** | ₹649.00 | Reference order value |
| **Customer Acquisition Cost (CAC)**| ₹300.00+ | Meta / Google Ads blended acquisition spend |

### Verified Cost Formulas

1. **Expected Damage Cost per RTO:**
   $$\text{Damage Cost} = ₹180.00 \times 8\% = ₹14.40$$

2. **Direct Expected RTO Loss per Delivery Failure:**
   $$\text{Direct RTO Cost} = ₹65 + ₹65 + ₹25 + ₹14.40 = \mathbf{₹169.40}$$

3. **Gross Contribution of Delivered Order:**
   $$\text{Gross Contribution} = ₹649.00 \times 62\% = \mathbf{₹402.38}$$

4. **Prepaid Conversion Incentive Economics:**
   - COD Baseline RTO Rate: 28%
   - Prepaid Baseline RTO Rate: 4%
   - Gross Avoided RTO Expectation per Conversion: $(28\% - 4\%) \times ₹169.40 = ₹40.66$
   - Instant Prepaid Discount Offered: ₹15.00
   - **Net Positive Contribution per Nudge Conversion:** $₹40.66 - ₹15.00 = \mathbf{+₹25.66}$

---

## 3. Four-Action Decision Matrix

Rather than treating RTO prevention as a binary ship/cancel gate, the system executes a calibrated 4-action progressive intervention pipeline:

```
                      [ Incoming COD Order ]
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
        [ ML Model Probability ]    [ Address & Name Guardrails ]
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                   [ Deterministic Policy Engine ]
                                │
        ┌────────────────┬──────┴──────────┬─────────────────┐
        ▼                ▼                 ▼                 ▼
   [ 0 - 20% ]      [ 20 - 40% ]      [ 40 - 65% ]       [ > 65% or Blocker ]
   SHIP_AS_IS    CONFIRMATION_REQ    NUDGE_TO_PREPAID      HOLD_FOR_REVIEW
        │                │                 │                 │
  Auto-approve    WhatsApp "YES/NO"    ₹15 Discount     Operations Queue
    Dispatch       Wait 24h Window      Payment Link    Manual Override Only
```

### Policy Actions & Thresholds

| Action | Risk Band | Default Threshold | Automated Trigger & Workflow Behavior |
|---|---|---|---|
| **`SHIP_AS_IS`** | Low Risk | $P(\text{RTO}) < 0.20$ | Auto-approves order for dispatch. No friction or customer interaction required. |
| **`SHIP_AFTER_CONFIRMATION`** | Moderate Risk | $0.20 \le P < 0.40$ | Holds dispatch; triggers automated WhatsApp confirmation message. Releases to dispatch only upon explicit customer confirmation (`YES`). |
| **`NUDGE_TO_PREPAID`** | Elevated Risk | $0.40 \le P < 0.65$ | Holds COD dispatch; sends interactive WhatsApp payment link offering instant ₹15 discount. Converts order to Prepaid on success. |
| **`HOLD_CANCEL`** | High Risk / Blocker | $P \ge 0.65$ or Invalid Data | Placed into Operations Review Queue. **Cannot be automatically cancelled.** Requires operations manager audit with documented reason. |

---

## 4. Key Architectural Safeguards

1. **First-Time Buyer Protection (Zero-Cancellation Rule):**
   First-time customers (`prior_orders == 0`) with usable addresses are **never automatically cancelled**. Even if geographic RTO risk is elevated, they are routed to WhatsApp confirmation (`SHIP_AFTER_CONFIRMATION`) to preserve top-of-funnel customer trust.
2. **Geographic & Courier Isolation:**
   No order is ever cancelled solely because of a high-risk pincode, tier-3 state, or specific courier allocation.
3. **Bounded LLM Guardrails:**
   LLMs are strictly restricted to unstructured Hinglish address and name validation. The LLM is **never** permitted to calculate financial numbers, assign risk scores, or trigger order cancellation. In the event of an LLM API outage, the system seamlessly uses deterministic heuristic fallbacks without downtime.
4. **Counterfactual Financial Transparency:**
   The Founder Dashboard clearly distinguishes between:
   - **Realised Savings:** Actual orders converted or stopped.
   - **Counterfactual Avoided RTOs:** Model-estimated savings against the no-intervention baseline.
   - **Genuine Opportunity Cost:** Foregone gross margin if a genuine order is mistakenly cancelled.

---

## 5. Technology Stack

- **Backend:**
  - **Runtime & Framework:** Python 3.11+, FastAPI (REST API with OpenAPI specification)
  - **Validation & Serialization:** Pydantic v2
  - **Database & ORM:** SQLite (development/local demonstration) with SQLAlchemy 2.0 ORM
  - **Machine Learning:** Scikit-learn (Calibrated Logistic Regression & HistGradientBoosting comparison)
  - **Data Processing:** Pandas, NumPy
  - **Testing:** Pytest (17 unit and integration tests passing)
- **Frontend:**
  - **Framework:** React 19 + TypeScript + Vite
  - **UI Aesthetic:** Bespoke Operations Console Dark Mode (`#0B1020`, `#111827`, `#10B981`, `#F59E0B`, `#EF4444`)
  - **Visualizations:** Recharts (Responsive bar charts, delivery rate breakdowns)
  - **Icons:** Lucide React
  - **Routing:** React Router DOM v7

---

## 6. Directory Structure

```
cod-risk-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # REST route handlers (health, orders, decisions, whatsapp, etc.)
│   │   ├── cli/                 # CLI entrypoints (init_db, import_orders, backtest)
│   │   ├── core/                # Settings and database session configuration
│   │   ├── llm/                 # Bounded LLM provider adapters and deterministic fallbacks
│   │   ├── ml/                  # Leakage-safe feature extraction, training, and inference
│   │   ├── models/              # SQLAlchemy database entity models
│   │   ├── schemas/             # Pydantic request and response schemas
│   │   ├── services/            # Business logic (Policy, Financials, Workflow state machine)
│   │   └── utils/               # Normalization, Indian mobile validator, landmark extractor
│   ├── tests/                   # Pytest test suite (17 comprehensive tests)
│   ├── pytest.ini               # Test configuration
│   └── requirements.txt         # Pinned Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI (Sidebar, TopBar, Badges)
│   │   ├── pages/               # Application views (Overview, Orders, Simulator, Risk, Analytics, Config, Logs)
│   │   ├── services/            # Typed API client wrapper
│   │   ├── types/               # TypeScript domain models and interfaces
│   │   ├── App.tsx              # Main application router
│   │   └── index.css            # Custom CSS design system
│   ├── package.json             # Frontend package manifest
│   └── vite.config.ts           # Vite bundler configuration
│
├── config/
│   └── decision_rules.json      # Dynamic business rules, thresholds, and financial constants
│
├── data/
│   └── orders_sample.csv        # Historical dataset (2,018 rows, deduplicated to 1,988 unique orders)
│
├── models/
│   └── rto_model_pipeline.joblib# Serialized, calibrated ML model artifact
│
├── docs/
│   ├── architecture.md          # Complete system architecture specification
│   ├── design.md                # UI/UX design tokens and component specs
│   ├── rules.md                 # Deterministic business rules and financial constants
│   ├── tasks.md                 # Sprint development breakdown and progress
│   ├── memory.md                # System context, trade-offs, and state
│   ├── business_memo.md         # Founder briefing memo on financial impact
│   ├── decision_log.md          # Architectural decisions and trade-offs
│   ├── ai_usage_log.md          # LLM prompt validation and safeguards log
│   ├── model_evaluation_report.md# ML performance report (ROC-AUC, PR-AUC, Confusion Matrix)
│   └── backtest_report.md       # Chronological holdout backtest results
│
├── README.md                    # Root project documentation (this file)
└── .gitignore                   # Version control ignore rules
```

---

## 7. Quick Start & Setup Guide (Windows / PowerShell)

The entire application runs locally on clean machines with no paid API keys or cloud services required.

### Prerequisites
- **Python:** Version 3.11+
- **Node.js:** Version 18+ and `npm`

---

### Step 1: Backend Setup & ML Pipeline Execution

Open a PowerShell terminal in the repository root:

```powershell
# Navigate to backend directory
cd "backend"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Train the ML model and generate evaluation report
python -m app.ml.train

# Initialize the SQLite database and seed configuration
python -m app.cli.init_db

# Ingest and evaluate historical sample orders (2,000 orders)
python -m app.cli.import_orders --file ..\data\orders_sample.csv

# Run the September 2026 chronological holdout backtest
python -m app.cli.backtest

# Run backend unit and integration test suite
pytest -v
```

### Step 2: Start Backend Server

```powershell
# From the backend directory with virtual environment active:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API and interactive Swagger documentation will be live at `http://127.0.0.1:8000/docs`.*

---

### Step 3: Frontend Setup & Launch

Open a second PowerShell terminal in the repository root:

```powershell
# Navigate to frontend directory
cd "frontend"

# Install frontend dependencies
npm install

# Verify TypeScript compilation and build production bundle
npm run build

# Start Vite development server
npm run dev
```
*Frontend application will be live at `http://localhost:5173`.*

---

## 8. Verification & Test Results

### 1. Pytest Test Suite (17 Tests Passing)
- `tests/test_financials.py`: Validates exact damage cost (₹14.40), direct RTO cost (₹169.40), gross margin (₹402.38), and prepaid incentive calculation.
- `tests/test_policy.py`: Confirms deterministic assignment into all 4 buckets and validates that first-time buyers are never cancelled.
- `tests/test_workflow.py`: Validates server-side state machine and rejects illegal transitions (e.g., `DISPATCHED` -> `HOLD`).
- `tests/test_api.py`: Tests end-to-end evaluation, WhatsApp YES/NO/ambiguous reply flows, and mock payment completion.

### 2. Machine Learning Model Performance (September 2026 Holdout)
- **Model:** Calibrated Logistic Regression with One-Hot & StandardScaler preprocessor
- **ROC-AUC:** **0.7393**
- **PR-AUC:** **0.5168** (vs. 0.259 baseline prevalence)
- **Recall:** **77.65%** (successfully detects >77% of all true RTO orders)
- **Brier Calibration Score:** **0.2026**

### 3. Historical Backtesting Results (Base Case Scenario)
- **Dataset:** September 2026 COD Holdout (328 orders, 85 baseline RTOs = 25.9%)
- **Baseline Direct Loss:** ₹14,399.00
- **Avoided RTO Deliveries:** **37.8 orders**
- **Avoided Direct RTO Cost:** **₹6,406.83**
- **Estimated Genuine Cancellation Opportunity Loss:** **₹140.83**
- **Redeemed Discounts Paid:** **₹198.00**
- **Net Estimated Positive Business Impact:** **+₹6,068.00**
- **Post-Intervention COD RTO Rate:** **14.4%** (relative reduction of **44.4%**)

---

## 9. Comprehensive Documentation Index

All detailed specifications, reports, and memos are maintained in `docs/`:

1. [Founder Business Memo (`docs/business_memo.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/business_memo.md) — Executive briefing for brand founders detailing financial returns, marketing tradeoffs, and progressive rollout phases.
2. [Historical Backtest Report (`docs/backtest_report.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/backtest_report.md) — Complete September 2026 holdout evaluation with Conservative, Base, and Optimistic sensitivity scenarios.
3. [Model Evaluation Report (`docs/model_evaluation_report.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/model_evaluation_report.md) — Comprehensive ML benchmark comparing Logistic Regression vs. Gradient Boosting, ROC/PR curves, and confusion matrix.
4. [Architectural Decision Log (`docs/decision_log.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/decision_log.md) — Technical tradeoffs, state machine design, leakage prevention methodology, and fallback architectures.
5. [AI & LLM Usage Log (`docs/ai_usage_log.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/ai_usage_log.md) — Audit of LLM boundary enforcement, prompts, output schemas, and deterministic fallbacks.
6. [System Architecture Document (`docs/architecture.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/architecture.md) — Component architecture, sequence diagrams, and schema contracts.
7. [Design System & UI Tokens (`docs/design.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/design.md) — Color palette, typography, layout guidelines, and component hierarchy.
8. [Deterministic Business Rules (`docs/rules.md`)](file:///d:/COD%20Risk%20Intelligence%20&%20RTO%20Prevention%20System/docs/rules.md) — Complete rule specification, reason codes, and unit economic constants.

---

## 10. PRD Definition of Done Verification

| PRD Requirement | Status | Verification Reference |
|---|---|---|
| Application runs locally with documented commands | **PASSED** | Runs via documented PowerShell commands with clean venv |
| Supplied dataset loaded, cleaned, and deduplicated | **PASSED** | 2,018 rows imported; 30 duplicates removed; 1,988 unique orders |
| ML model produces validated RTO probability | **PASSED** | Model calibrated; ROC-AUC 0.7393, PR-AUC 0.5168 |
| All 4 decision actions functional | **PASSED** | `SHIP_AS_IS`, `SHIP_AFTER_CONFIRMATION`, `NUDGE_TO_PREPAID`, `HOLD_CANCEL` |
| Business thresholds editable without code changes | **PASSED** | Editable via UI console & `/api/v1/config` (saved in JSON & DB) |
| LLM validates names and Hinglish addresses | **PASSED** | Bounded provider adapter with Pydantic output validation |
| LLM outage does not break engine | **PASSED** | Automatic deterministic fallback to regex/keyword rules |
| Every decision contains plain-English explanation | **PASSED** | 100% decision explanation coverage stored in audit trail |
| Interactive WhatsApp Simulator functional | **PASSED** | Simulator UI supports YES, NO, ambiguous replies, and 24h timeouts |
| Prepaid discount & payment simulation functional | **PASSED** | Mock Razorpay/UPI flow with instant order state conversion |
| Founder Dashboard displays KPIs & financial impact | **PASSED** | Daily KPIs, avoided RTOs, genuine loss estimates, net financial impact |
| Full test coverage | **PASSED** | 17/17 automated tests passing |
| Founder memo and audit documentation complete | **PASSED** | All 8 required markdown documents created in `docs/` |

---
*Built with precision for the Associate Software Engineer Take-Home Assignment.*
