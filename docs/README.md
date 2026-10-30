# COD Risk Intelligence & RTO Prevention

An AI-assisted COD order risk assessment and RTO prevention platform for
a D2C haircare business. The application evaluates COD orders before
dispatch and recommends one of four actions: ship as-is, confirm on
WhatsApp, nudge to prepaid, or hold for review.

> **Project status:** Product and implementation specification. This
> repository becomes runnable once the application source code,
> dependencies, and model artifacts are implemented. The documentation
> does not claim that a working application or trained model already
> exists.

## 1. Business problem

The assignment describes a D2C business processing approximately 3,000
orders per month, with 55% COD orders and a 28% COD RTO rate. The
supplied operating assumptions include ₹65 forward shipping, ₹65 return
shipping, ₹25 packaging/handling, ₹180 average product cost, and 8%
damage among returned products.

Expected damage cost per RTO:

`₹180 × 8% = ₹14.40`

Expected direct RTO cost:

`₹65 + ₹65 + ₹25 + ₹14.40 = ₹169.40`

At 1,650 COD orders and a 28% RTO rate, the baseline estimate is 462 COD
RTOs and ₹78,262.80 in expected direct RTO cost per month. This is a
business-assumption estimate, not a measured result from the sample CSV.

## 2. Product capabilities

-   Historical CSV profiling, cleaning, and leakage-safe feature
    preparation.
-   ML model that estimates RTO probability.
-   Deterministic decision policy with four assignment-level actions.
-   LLM-assisted interpretation of ambiguous names and Hinglish
    addresses.
-   Configurable risk thresholds and financial assumptions.
-   Mock WhatsApp confirmation flow with YES, NO, ambiguous reply, and
    timeout handling.
-   Mock prepaid discount and payment flow.
-   Founder dashboard for decision buckets and estimated financial
    impact.
-   Decision history, workflow events, audit trail, and historical
    backtesting.

## 3. Technology stack

  Layer         Technology
  ------------- ----------------------------------
  Frontend      React, Vite, TypeScript
  Styling       CSS Modules / plain CSS
  Charts        Recharts
  Backend       Python, FastAPI, Uvicorn
  Validation    Pydantic
  Data          Pandas, NumPy
  ML            Scikit-learn
  Persistence   SQLAlchemy, SQLite
  LLM           Optional provider adapter
  Testing       Pytest and frontend test tooling

No real WhatsApp account or payment gateway is required for the
assignment demo. The LLM integration must be optional; the app must run
without API credentials.

## 4. Repository layout

``` text
cod-risk-intelligence/
├── frontend/
├── backend/
├── data/
│   └── orders_sample.csv
├── models/
├── config/
│   └── decision_rules.json
├── docs/
│   ├── architecture.md
│   ├── tasks.md
│   ├── rules.md
│   ├── design.md
│   ├── memory.md
│   ├── business_memo.md
│   ├── decision_log.md
│   └── ai_usage_log.md
├── README.md
└── .gitignore
```

The three core technical documents (`architecture.md`, `tasks.md`, and
`rules.md`) define the implementation contract. `design.md` defines the
UI/UX system. `memory.md` is a compact context file for AI-assisted
development.

## 5. Prerequisites

Install:

-   Python 3.11 or later (use a version supported by the pinned backend
    dependencies).
-   Node.js 20 or later.
-   npm.
-   Git.

Verify:

``` powershell
python --version
node --version
npm --version
git --version
```

## 6. Local setup --- Windows PowerShell

The following commands describe the intended setup after the source
files and dependency manifests have been added.

### 6.1 Backend

``` powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Initialize the database and import data using the commands documented by
the implemented backend. Example intended commands:

``` powershell
python -m app.cli.init_db
python -m app.cli.import_orders --file ..\data\orders_sample.csv
python -m app.ml.train
```

Start the API:

``` powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation:

-   Swagger UI: `http://127.0.0.1:8000/docs`
-   Health: `http://127.0.0.1:8000/api/v1/health`

### 6.2 Frontend

Open a second PowerShell terminal:

``` powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the local Vite URL printed in the terminal, normally
`http://localhost:5173`.

### 6.3 Environment variables

Backend `.env.example` should include only placeholders:

``` dotenv
APP_ENV=development
DATABASE_URL=sqlite:///./cod_risk.db
CORS_ORIGINS=http://localhost:5173
TIMEZONE=Asia/Kolkata
LLM_ENABLED=false
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=8
```

Frontend `.env.example`:

``` dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Never commit real credentials. The demo must remain usable with
`LLM_ENABLED=false`.

## 7. Data and model workflow

1.  Place the supplied CSV at `data/orders_sample.csv`.
2.  Run the data profiling and cleaning pipeline.
3.  Review duplicate handling and unresolved statuses.
4.  Create chronological train/validation/holdout splits.
5.  Build customer and geographic features using point-in-time history
    only.
6.  Train a baseline model.
7.  Compare candidate models and probability calibration.
8.  Save model version and evaluation report.
9.  Evaluate the decision policy on an untouched chronological holdout.

Do not use `final_status` as a predictor. Do not use future customer
history or post-order delivery data. Do not tune policy thresholds on
the final holdout.

## 8. Decision actions

  -----------------------------------------------------------------------
  Action                              Intended behavior
  ----------------------------------- -----------------------------------
  `SHIP_AS_IS`                        Approve normal shipment

  `SHIP_AFTER_CONFIRMATION`           Hold dispatch until customer
                                      confirms

  `NUDGE_TO_PREPAID`                  Offer configured discount and mock
                                      payment

  `HOLD_CANCEL`                       Hold for manual review;
                                      cancellation is a separate
                                      controlled state
  -----------------------------------------------------------------------

The default thresholds in `config/decision_rules.json` are starting
assumptions only. They must be validated against out-of-time data and
expected financial impact.

## 9. Financial assumptions

-   Expected direct RTO cost: ₹169.40.
-   Delivered gross contribution estimate: ₹649 × 62% = ₹402.38.
-   Initial prepaid discount experiment: ₹15.

The ₹15 offer is a test hypothesis, not a proven optimal discount. A
simple comparison of COD and prepaid RTO rates is observational and does
not establish the causal effect of converting a COD customer to prepaid.

Dashboard numbers must distinguish actuals, estimates, and assumptions.
Do not claim that a flagged order equals an avoided RTO.

## 10. Testing

Backend:

``` powershell
cd backend
pytest -q
```

Frontend:

``` powershell
cd frontend
npm test
```

Use the actual scripts declared in `package.json` and test
configuration. Critical tests include:

-   Target mapping and data leakage prevention.
-   Point-in-time customer history.
-   Financial formulas.
-   Risk threshold boundaries.
-   First-time customer protection.
-   LLM unavailable/malformed response fallback.
-   YES / NO / ambiguous replies.
-   24-hour timeout.
-   Payment success/failure/idempotency.
-   Invalid workflow transitions.
-   Dashboard actual-vs-estimated metric definitions.

## 11. Demo walkthrough

1.  Open the founder dashboard and select yesterday.
2.  Review four decision buckets and financial estimates.
3.  Open an order and inspect probability, reason codes, and
    model/policy versions.
4.  Evaluate a demo low-risk COD order and show `SHIP_AS_IS`.
5.  Evaluate a moderate-risk order and simulate YES.
6.  Simulate NO and confirm dispatch is stopped.
7.  Simulate no reply and trigger the 24-hour hold.
8.  Run an elevated-risk order through prepaid offer and mock payment
    success/failure.
9.  Change a risk threshold in Configuration and evaluate a new order.
10. Open decision logs and explain how every action is auditable.

## 12. Submission documentation

Maintain these files as implementation progresses:

-   `docs/architecture.md`: components, APIs, database, and data flows.
-   `docs/tasks.md`: implementation backlog and acceptance criteria.
-   `docs/rules.md`: deterministic policy and financial formulas.
-   `docs/design.md`: visual system, page layouts, and interaction
    behavior.
-   `docs/memory.md`: durable project context for AI-assisted work.
-   `docs/business_memo.md`: founder-facing findings and backtest.
-   `docs/decision_log.md`: important choices and alternatives.
-   `docs/ai_usage_log.md`: tools used, verification, and corrected weak
    outputs.

Do not invent model performance, intervention response rates, customer
behavior, or financial savings. Clearly label assumptions and
limitations.

## 13. Current limitations

-   The architecture and documentation define the intended product;
    source-code implementation is tracked separately in `tasks.md`.
-   WhatsApp and payment are mock workflows until real provider
    integrations are deliberately implemented.
-   LLM functionality is optional and must degrade gracefully.
-   Historical data cannot reveal how customers would have responded to
    a hypothetical intervention.
-   Small sample sizes limit reliable pincode-level and subgroup
    conclusions.
-   Automatic cancellation is disabled by default in the MVP; high-risk
    orders go to hold/manual review.

## 14. License and data handling

Add an appropriate repository license before public release. Do not
publish customer personal data. Before making the repository public,
verify whether the supplied CSV contains personal information and
replace it with a synthetic or properly anonymized sample if required.
