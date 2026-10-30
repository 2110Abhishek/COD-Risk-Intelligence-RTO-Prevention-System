# UI/UX Design Specification --- COD Risk Intelligence

**Version:** 1.0\
**Product:** COD Risk Intelligence & RTO Prevention Platform\
**Audience:** Founder, Operations Manager, Marketing Manager,
Administrator\
**Design direction:** Premium, restrained, data-dense SaaS operations
console

## 1. Design objectives

The interface must help a founder understand financial impact in under
one minute and help an operations user resolve an individual order in a
few clicks.

Primary goals:

1.  Make the four decision buckets immediately understandable.
2.  Separate actual financial results from estimates.
3.  Explain why an order was flagged without requiring ML knowledge.
4.  Make customer confirmation and prepaid workflows easy to inspect.
5.  Expose configuration safely to non-technical users.
6.  Keep high-risk decisions auditable and human-controlled.
7.  Work well on desktop and remain usable on tablet.

The design should feel like a polished fintech/operations product: clear
hierarchy, strong typography, subtle borders, restrained color,
consistent spacing, and minimal decoration.

## 2. Visual direction

### 2.1 Overall style

-   Dark-first interface with optional light theme only if time permits.
-   Deep charcoal/navy application background.
-   Slightly lighter sidebar and card surfaces.
-   High-contrast primary text.
-   Muted secondary text.
-   Thin borders and subtle shadows.
-   Rounded cards, but avoid excessive pill shapes.
-   Use accent color sparingly.
-   Avoid gradients as the primary way to communicate status.
-   Avoid decorative charts that do not answer a business question.

### 2.2 Suggested design tokens

``` css
:root {
  --color-bg: #0B1020;
  --color-surface: #121A2B;
  --color-surface-raised: #182338;
  --color-border: #26344A;
  --color-text: #F4F7FB;
  --color-muted: #98A6BA;
  --color-primary: #7C9CFF;
  --color-success: #34C78A;
  --color-warning: #F4B860;
  --color-danger: #F07878;
  --color-info: #62B6D9;

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  --shadow-card: 0 8px 24px rgba(0, 0, 0, 0.16);
}
```

These are implementation starting points. Maintain contrast and test the
final palette.

### 2.3 Typography

Use a clean sans-serif such as Inter or system UI.

Hierarchy: - Page title: 24--28px, semibold. - Section title: 16--18px,
semibold. - KPI value: 26--32px, semibold/tabular numerals. - Body:
14px. - Secondary metadata: 12--13px. - Table text: 13--14px.

Use tabular numerals for rupee values, percentages, and counts so values
align visually.

### 2.4 Status colors

Use color consistently but do not rely on color alone.

  Status                    Suggested color   Meaning
  ------------------------- ----------------- --------------------------
  Ship as-is / delivered    Green             Normal / positive
  Confirmation              Blue              Waiting for customer
  Prepaid nudge             Violet            Payment intervention
  Hold / manual review      Amber             Needs attention
  Cancelled / explicit NO   Red               Stopped
  Unknown / unavailable     Grey              Insufficient information

Always pair a colored status with text and, where useful, an icon.

## 3. Application shell

### 3.1 Desktop layout

-   Fixed left sidebar: approximately 240px.
-   Main content area fills remaining width.
-   Top header: 64--72px.
-   Content max width: approximately 1440px.
-   Page padding: 24--32px.
-   Use a 12-column grid where useful.

### 3.2 Sidebar navigation

Brand area: - Small product mark. - Product name: `COD Intelligence`. -
Environment label: `DEMO` during assignment.

Navigation: 1. Overview 2. Orders 3. Risk Analysis 4. WhatsApp Simulator
5. Analytics 6. Configuration 7. Decision Logs

Bottom area: - API/backend status. - Model status/version. -
User/profile placeholder for demo.

Active item should use a subtle surface highlight and left accent
marker. Do not use oversized icons.

### 3.3 Top header

Show: - Current page title or breadcrumb. - Date range selector where
relevant. - Last refreshed timestamp. - Model status indicator. -
Optional refresh action.

Do not show a green "Live" indicator unless the data is actually
updating live.

## 4. Page 1 --- Founder Overview Dashboard

### 4.1 Purpose

Answer these questions immediately:

-   How many COD orders were processed yesterday?
-   How many went into each decision bucket?
-   What is the estimated RTO cost avoided?
-   What is the estimated cost of genuine cancellations?
-   What is the net estimated financial impact?
-   Which queue needs attention today?

### 4.2 Layout

Header: - Title: `Overview` - Subtitle:
`COD risk and financial performance` - Date selector default:
Yesterday - Last updated time

First row: four decision bucket cards: - Ship as-is - Confirmation -
Prepaid nudge - Hold / cancel

Each card: - Count. - Share of evaluated COD orders. - Small comparison
with previous period only when valid data exists.

Second row: financial KPI cards: - Estimated RTO savings. - Estimated
genuine cancellation loss. - Discount cost. - Net estimated impact.

Each financial card must include: - `Estimated` or `Actual` label. -
Tooltip explaining formula. - Date range.

Third row: - Decision distribution chart. - Financial impact trend.

Fourth row: - Needs attention queue. - Recent decisions table.

### 4.3 Dashboard interaction

-   Clicking a decision card filters Orders page by that decision.
-   Clicking an attention item opens order detail.
-   Date selector updates all cards and charts.
-   Tooltips explain calculations and assumptions.
-   Empty data state must say no decisions were recorded for the
    selected period.

### 4.4 Financial presentation rules

Do not show a single net number without its components. Show a
breakdown:

`Avoided RTO cost` `− Genuine cancellation opportunity cost`
`− Redeemed discount cost` `− Intervention cost`
`= Net estimated impact`

Use green/red only for sign and meaning, not to imply certainty. Show a
note: "Counterfactual estimate; not audited realised savings."

## 5. Page 2 --- Orders

### 5.1 Purpose

Give operations a searchable queue of orders and their current
decision/workflow status.

### 5.2 Header and filters

-   Search order ID/customer.
-   Date range.
-   Decision bucket.
-   Risk band.
-   State.
-   Courier.
-   Acquisition source.
-   Workflow status.

### 5.3 Table columns

-   Order ID.
-   Customer.
-   Order value.
-   Payment method.
-   RTO risk.
-   Decision.
-   Workflow status.
-   Created/decision time.
-   Actions.

Use a compact table with sticky header if the list is long. Keep
pagination server-driven.

### 5.4 Row behavior

-   Clicking a row opens Order Detail.
-   Status badge includes text.
-   Risk probability is shown as a percentage and textual band.
-   Phone number must be masked.
-   No customer PII should be exposed in list views unnecessarily.

### 5.5 Empty/loading/error states

-   Loading: skeleton rows.
-   Empty: explain that no orders match the filters.
-   Error: show retry action and safe error text.
-   Never render fake placeholder orders as if they were real.

## 6. Page 3 --- Order Detail

### 6.1 Purpose

Explain the decision and give an authorized operations user the
information needed to resolve the order.

### 6.2 Layout

Top summary: - Order ID. - Customer display name. - Order value. -
Payment method. - Created time. - Current workflow status.

Left/main column: 1. Decision summary card. 2. RTO probability and risk
band. 3. Plain-English explanation. 4. Reason-code list. 5. Customer
history. 6. Address validation details. 7. Financial estimate and
assumptions. 8. Event timeline.

Right column: - Recommended next action. - Confirmation/prepaid
status. - Manual review controls.

### 6.3 Decision summary

Example:

`SHIP AFTER CONFIRMATION`

"Estimated RTO risk is moderate. The address is usable, but customer
intent should be confirmed before dispatch."

Show: - Model version. - Policy version. - Decision timestamp. - LLM
status (completed/unavailable/not required).

### 6.4 Manual override

Actions may include: - Approve shipment. - Keep on hold. - Cancel order.

Rules: - Require a reason for every override. - Confirm destructive
cancellation. - Only authorized role can cancel. - Show that override is
logged. - Never allow the UI to bypass backend transition validation.

## 7. Page 4 --- Risk Analysis

### 7.1 Purpose

Help users understand patterns and model quality without encouraging
overconfident conclusions from small samples.

### 7.2 Sections

-   Model evaluation summary.
-   Probability calibration.
-   Confusion matrix.
-   RTO distribution by score band.
-   First-time vs returning cohort.
-   Geography performance.
-   Courier performance.
-   Acquisition channel performance.

### 7.3 Chart requirements

Every chart must show: - Date range. - Sample count. - Metric
definition. - Tooltip values. - Empty/low-sample warning.

Avoid ranking tiny pincode groups as "worst areas." Use minimum sample
thresholds and confidence warnings.

## 8. Page 5 --- WhatsApp Simulator

### 8.1 Purpose

Demonstrate confirmation and prepaid workflows without a real WhatsApp
integration.

### 8.2 Layout

Three-column desktop composition:

Left: - Select an order. - Order details. - Current workflow state.

Center: - Chat-style message history. - Outgoing message bubbles aligned
right. - Incoming messages aligned left. - Timestamps and mock delivery
indicators.

Right: - Workflow controls. - Reply buttons: YES, NO, ambiguous. -
Free-text reply field. - Simulate 24-hour timeout. - Prepaid payment
controls: success/failure. - Current state and next expected transition.

### 8.3 Interaction rules

-   Simulator calls backend endpoints; it must not mutate state only in
    React.
-   YES confirms only when the order is awaiting confirmation.
-   NO stops shipment.
-   Ambiguous response sends clarification and does not release.
-   Timeout moves to hold/manual review.
-   Prepaid success marks mock payment successful.
-   Payment failure preserves the original order.

### 8.4 Visual treatment

The simulator should look familiar but must be labelled
`WhatsApp mock simulator`. Do not use WhatsApp branding in a way that
implies official integration.

## 9. Page 6 --- Analytics

Show: - Daily order volume. - Decision bucket trends. - COD RTO rate
over time. - Prepaid conversion. - Confirmation response. - Timeout
rate. - Financial impact trend. - Actual vs estimated comparison.

Filters: - Date range. - Source. - Courier. - Region. - Customer cohort.

All data must come from backend endpoints and carry the metric
definition.

## 10. Page 7 --- Configuration

### 10.1 Purpose

Allow a non-technical authorized user to change policy values without
code edits.

### 10.2 Sections

Risk policy: - Ship-as-is maximum. - Confirmation maximum. - Prepaid
maximum. - Hold minimum.

Customer protection: - Protect first-time customers. - Manual review
before cancellation. - Geography alone cannot cancel. - LLM alone cannot
cancel.

Financial assumptions: - Forward shipping. - Return shipping. -
Packaging/handling. - Product cost. - Damage probability. - AOV. - Gross
margin. - CAC reference.

Interventions: - Prepaid discount. - Offer expiry. - Confirmation
timeout. - Reminder count.

AI: - LLM enabled/disabled. - Provider/model. - Timeout.

### 10.3 Save behavior

-   Validate before saving.
-   Show old and new values.
-   Require confirmation for material changes.
-   Create configuration version.
-   Record actor and timestamp.
-   Show "applies to new decisions" note.
-   Do not rewrite old decision records.

Use percentage inputs with clear percent labels, not ambiguous decimals.

## 11. Page 8 --- Decision Logs

Table columns: - Timestamp. - Order ID. - Action. - Risk probability. -
Model version. - Policy version. - Reason codes. - Actor/system. -
Override indicator.

Detail view: - Input snapshot. - Feature snapshot. - Model output. - LLM
output status. - Configuration version. - Policy result. - Event
history.

Logs should be read-only for ordinary users.

## 12. Responsive behavior

### Desktop (≥1200px)

-   Full sidebar.
-   Multi-column KPI grid.
-   Tables and charts side-by-side.

### Tablet (768--1199px)

-   Collapsible sidebar.
-   Two-column KPI grid.
-   Charts stack when needed.
-   Tables allow horizontal scrolling.

### Mobile (\<768px)

-   Compact top navigation or drawer.
-   One-column KPI cards.
-   Charts stack vertically.
-   Tables convert to card rows or horizontal scroll.
-   Simulator becomes stacked: order summary, chat, controls.
-   Keep primary action visible without hiding important context.

The founder dashboard is desktop-first, but core order review and
simulator actions must remain usable on mobile.

## 13. Accessibility and usability

-   Maintain WCAG-aware text contrast.
-   All controls have visible labels.
-   Keyboard focus is visible.
-   Do not communicate status by color alone.
-   Buttons have clear action verbs.
-   Destructive actions require confirmation.
-   Tooltips are also accessible through keyboard/focus.
-   Charts have text summaries or accessible labels.
-   Use semantic headings and table headers.
-   Avoid tiny click targets.

## 14. Component inventory

Reusable components:

-   `AppShell`
-   `Sidebar`
-   `Topbar`
-   `PageHeader`
-   `DateRangePicker`
-   `KpiCard`
-   `FinancialMetricCard`
-   `DecisionBadge`
-   `RiskBadge`
-   `StatusBadge`
-   `DataTable`
-   `FilterBar`
-   `EmptyState`
-   `ErrorState`
-   `LoadingSkeleton`
-   `ChartCard`
-   `DecisionExplanation`
-   `ReasonCodeList`
-   `OrderTimeline`
-   `CustomerSummary`
-   `AddressAssessmentCard`
-   `ChatMessage`
-   `SimulatorControls`
-   `ConfigurationField`
-   `ConfirmationDialog`

## 15. Frontend states

Every data-driven page must define:

-   Initial loading.
-   Refetching.
-   Success with data.
-   Success with empty data.
-   API error.
-   Invalid filter.
-   Permission denied (when auth is implemented).
-   Stale data indicator where relevant.

Do not replace failed API data with plausible-looking fake values.

## 16. Design acceptance criteria

-   Founder can identify all four decision counts immediately.
-   Financial impact displays components and estimation caveat.
-   Orders can be filtered and opened.
-   Every decision has understandable reasons.
-   Order detail shows model and policy versions.
-   Simulator demonstrates YES, NO, ambiguous, timeout, payment success,
    and payment failure.
-   Configuration can be changed and validated without code changes.
-   Manual cancellation requires authorization and a reason.
-   Logs show decision and override history.
-   UI works at desktop, tablet, and mobile widths.
-   Loading, empty, and error states exist.
-   Color is never the only status indicator.
