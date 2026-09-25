# Staircase per-skill chrome mappings

The deterministic chrome each Staircase skill renders. Components reference `component-library.md`; interactive experiences reference `interactive-experiences.md`. Content inside is adaptive; the chrome below is fixed. Every skill here is read-only synthesis: no writes, no approval gates, evidence IDs on every claim, yellow = neutral.

---

## staircase-risk-radar (the flagship)

**Header:** app header, title `Risk Radar`, scope (Owner or "Portfolio"), as-of date.

**Tabs (fixed order, with counts):**

| # | Tab | Components | Content |
|---|---|---|---|
| 1 | **Overview** | metric-card grid (3x2) + section callout | Accounts scanned · revenue at risk · acute-band count · renewals < 90d · silent-risk count · stabilizing. Callout for the systemic pattern (for example, "most near-term at-risk renewals have no working session booked"). |
| 2 | **Radar** | **interactive experience** (`../../staircase-risk-radar/experiences/risk-radar.html`) | The polar radar: accounts by severity + urgency (radius), revenue (size), dominant lens (angle), health (color). Hover tooltip, click detail panel, health/lens color toggle. This is the exemplar of when to render interactive over a table. |
| 3 | **Priorities** | ranked table + drill-down cards | Top accounts ranked by winnable x high-stakes x urgent. Columns: account · revenue · renewal (days) · severity · health · why-here pill. Row click opens the read-only drill-down (state, stakeholders, recommended next moves as text, evidence IDs). |
| 4 | **Silent risk** | ranked table | Accounts sliding on health/sentiment/engagement with no fired risk flag. The "not yet flagged" set. |
| 5 | **Trend** | section callouts + metric deltas | Lens-firing counts across the cohort (which lens dominates), and the systemic solve. |

## staircase-renewal-watchlist

**Header:** app header, title, scope, as-of date.
**Tabs:** (1) **Overview** metric grid + callout. (2) **Priorities** ranked table + read-only drill-downs. (3) **Trend** lens-firing counts / theme landscape. It leads its table with renewal-days ascending. Consider the radar experience when the cohort is multi-dimensional enough to earn it.

## staircase-risk-check (single account)

**Header:** `<Account> · Risk check`, ARR, renewal, health band.
**Tabs:** (1) **Snapshot** metric cards (severity, health, sentiment, engagement, coverage, renewal). (2) **Lenses** which of the five are firing, each with its signal. (3) **Evidence** the source communications behind the read.

## staircase-account-deep-dive / staircase-meeting-prep / staircase-account-handoff (single account)

**Header:** `<Account>` + tier + ARR + as-of.
**Tabs:** (1) **Snapshot** metric cards. (2) **Signals** health/sentiment/engagement detail. (3) **Stakeholders** the map (chips) with roles and stance. (4) **Evidence / History** timeline of source communications. Handoff adds a **90-day plan** section rendered as read-only ordered steps.

## staircase-expansion-scout (cross-account)

**Header:** `Expansion Scout`, scope, as-of.
**Tabs:** (1) **Overview** metric grid (expansion-ready count, ARR in play). (2) **Ready** ranked table (signal pill = the expansion signal), read-only drill-downs. (3) **Evidence**. Signal-blue for opportunity; yellow stays neutral.

## staircase-voice-of-customer (cross-account themes)

**Header:** `Voice of Customer`, scope, as-of.
**Tabs:** (1) **Themes** ranked table of themes (accounts touched, sentiment mix, growth). (2) **Evidence** the quotes/communications per theme. (3) **Accounts** which accounts drive each theme. A theme-by-account heatmap is a candidate interactive experience when the matrix is dense.

## staircase-follow-up-draft

**Header:** short title, account or scope.
Mostly a single artifact (a draft) plus an evidence list. Render as one card with the draft, then a callout with the evidence IDs. Draft, do not send: the user reviews and sends from their own tools.

## staircase-setup

Linear onboarding flow, not a dashboard. Skip the tabbed chrome; render the setup as a short sequential flow.

---

## Universal rules
- **Read-only.** No writes, no approval gates. Recommended next moves render as read-only, copy-ready text.
- **Yellow = neutral / average**, never "concern".
- **Evidence on every claim.** Carry evidence IDs; ground shared claims in fetched evidence.
- **Lead with the answer.** Headline and metric grid first, then the prioritized detail, then sources.
- **Static by default; interactive when the data has structure a table hides** (see `interactive-experiences.md`).
- **Code/CLI surface** degrades to the same section structure as markdown headers plus tables; interactive experiences fall back to their ranked table.
