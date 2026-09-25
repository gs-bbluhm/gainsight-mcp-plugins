---
name: staircase-risk-radar
description: "Builds the portfolio risk view for the accounts a leader is responsible for. Report-first: how much revenue is at risk, which of it renews soon, whether each account can still be saved, what is driving the risk (and whether it concerns this product or another), and the one systemic cause worth fixing once. Returns the headline, a segment rollup, the renewal-clock slice, the blindsided and silent-risk watchlists, the systemic driver, and decision-maker coverage, as an interactive dashboard inside Claude. Triggers on \"portfolio risk\", \"where are we at risk\", \"risk radar\", \"book of business risk\", \"what's at risk this quarter\", \"revenue at risk\", \"risk by segment\", \"risk by team\"."
user_type: exec
allowed-tools: mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Risk Radar (leader / portfolio)

A leader doesn't need a red list of hundreds of accounts. They need four answers for the accounts they're responsible for: **how much revenue is at risk, which of it has a clock on it, what's driving it, and what to do**. This skill answers them from structured reports (deterministic counts, rollups, and rankings), then grounds the "why" in the Risk analyst's stored narratives and the accounts' lifecycle events.

**This is the portfolio lens.** For one account's full risk read and save plan use `../staircase-risk-check/`; for one CSM's weekly action list use `../staircase-book-triage/`.

## Read first
- `../staircase-mcp-expert/` (the first-call contract resolves scope), `../staircase-mcp-expert/references/report-recipes.md` (`risk.cohort`, `renewal.window`, `lifecycle.evidence`, `team.rollup`, `voc.pain_profile`), and `../staircase-mcp-expert/references/anti-patterns.md`.
- `../staircase-app-design/` before rendering.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.

## Scope: the user's responsibility, never the whole org by default
Use the scope from the profile (`../staircase-mcp-expert/` step 0):
- **Book or team:** `customer.<book_owner_field> In [<user_id>]`, or the team through `customer.<book_owner_field>.manager In [<manager_user_id>]`.
- **A portfolio slice** (`scope.filter`): the part of the portfolio this person owns, such as a product line (a product revenue field of 1 or more), a segment, or a region. Apply it to every report. When the slice has its own revenue field (`scope.revenue_field`), use it as the revenue column and in every total, and show total account revenue only as context.
- **Whole org:** only when the user has no slice and says so, or asks for it explicitly.
- Segment filters use the name leaf: `customer.tier.name In [...]`. Tier names vary per org; drop tiers with zero accounts from any rollup.
- Portable fields only: discover fields from metadata; never ship an org's custom field id.

## Risk states
- **Acute:** `risk.risk_level` 4-5. **Watch:** level 3. Report them separately; acute leads.
- **Silent:** no risk level, but low health corroborated by low engagement or sentiment. A lone low health is usually missing data. The silent net catches accounts no dashboard flags.
- **Fresh vs chronic:** "Last churn-risk fired" (child MAX of `churn_risk` event dates). Fired in the last 30 days is fresh; an old fire behind a high level is chronic. Risk levels persist between fires, so the level alone can't tell them apart.

## The flow (report-first)
1. **Cohort.** The `risk.cohort` recipe (level 4+ or a `ChurnRisk` insight) plus level 3 as watch, within scope, with the slice's revenue field, "Last churn-risk fired", `last_dm_touch`, `event.next_event`, and the book owner. Run the silent net as a second call and tag its rows.
2. **Rollup.** Root `tier` with child COUNT and SUM columns for acute, watch, and acute renewing in 90 days (same pattern with root `user` for a team). One call turns hundreds of rows into "where the money concentrates".
3. **The clock (the headline).** Acute and watch accounts renewing in the next 90 days, split fresh vs chronic. This is the slice a leader personally works. A renewal date in the past on an Active account is a stale date to fix in the CRM, not an emergency.
4. **State.** For each account, decide one of five states:

   | State | Rule |
   |---|---|
   | **Saveable** | No churn event this cycle, or a conditional one ("won't renew unless...") |
   | **Notice given** | A `churn` event (or termination signals) in the past six months, outcome not yet confirmed |
   | **Partial** | The notice or downsell covers another product or part of the scope; the rest continues |
   | **Lost** | `churn.synopsis` or the risk narrative states a non-renewal decision |
   | **Verify** | The only churn event is older than the current renewal cycle; confirm before counting it |

   Never count a partial as a full loss, and never treat a signal as intent on its own (an auto-renewal opt-out is often a procurement ask).
5. **Driver and where the risk sits.** Pull `customer.risk.analysis` for the cohort (for a large cohort, the top by revenue and renewal first) and read each into a one-line driver and one of the five lenses below. On multi-product accounts, the account-level risk can be about a different product than the user's slice: read `lifecycle_event.products` on the recent `churn_risk` and `churn` events plus the narrative, and tag each account **this product**, **mixed**, or **another product**. Report the revenue where this product is part of the risk separately.
6. **Systemic driver.** Count the driver themes across the narratives and attach revenue to each. The theme that spans the most revenue is the "solve once" finding; name the accounts it covers. When it points at the product itself (data mapping, sync, capture, reliability), it's a roadmap input with revenue attached. Topic metrics (`voc.pain_profile`) are a secondary read; say that topic names are unavailable while that gap lasts.
7. **Blindsided and silent.** Health still High with risk fired: the surprises a health dashboard shows green. Plus the silent net near a renewal.
8. **Coverage.** Lead with decision-maker access: `last_dm_touch` older than six months, or none, on an at-risk renewal. Check the base rate before using `multi_threaded` (anti-patterns.md R17): when nearly every account is multi-threaded, it carries no signal. Use owner vs org email counts from `risk.cohort` to spot accounts nobody is working.

## The five lenses
| Lens | Why it churns or shrinks | Systemic play (solve once) |
|---|---|---|
| **Value** | "We can't justify the spend" | A reusable ROI and leadership-dashboard program tied to the customer's own metric |
| **Competitive** | Displacement by a competitor or an in-house build | A battlecard and a "vs build it yourself" narrative for the recurring competitor |
| **Stakeholder** | Champion loss, missing economic buyer, our own CSM changes | A multi-threading push and a CSM-transition playbook |
| **Product** | Adoption, fit, integration, data quality, reliability | A fix backlog with revenue at risk attached: one fix de-risks many accounts |
| **Renewal** | Terms, pricing, procurement, auto-renew clauses | Sequence the saves by renewal date; standard answers for recurring procurement asks |

## Prioritization
Rank by **revenue at risk x urgency x winnability**. Winnability comes from the state: saveable and partial get the save energy; notice-given accounts get a direct executive conversation if the notice is recent; lost accounts go to `../staircase-churn-review/`. Severity-sort alone floats already-lost and not-yet-urgent accounts to the top.

## Team load (only when the leader routes by person)
When several role fields carry books (for example one CSM field per product), ask once which role to route by and cache it. Show pooled or shared users (placeholder users carrying hundreds of accounts, no title, no mailbox) as their own row. Present load and exposure so the leader knows where to help; never rank people by risk (`../staircase-mcp-expert/references/analysis-methodology.md`).

## Output: the leader readout
```
# Risk Radar: <scope> · <date>

**At risk:** <n> accounts · <revenue> (acute <n> · watch <n>)
**Renews in 90 days:** <n> · <revenue> (fresh <n> · chronic <n>)
**Gave notice or lost:** <n> · <revenue> · **Partial:** <n>
**Systemic driver:** <theme> · <n> accounts · <revenue>
**Where the risk sits:** this product <revenue> · another product <revenue>

## Headline
<3-4 sentences: the revenue on the clock, how much is still saveable, the one systemic cause worth fixing once, and the 2-3 accounts leadership should step into.>

## Renewing in 90 days (every account, not a top-N)
| Account | Revenue | Renews (days) | Risk | State | Driver | Last fired | DM touch |

## Systemic driver
<theme, the accounts it spans, the revenue attached, and the one fix or program that gets ahead of it>

## Blindsided and silent
<health still High with risk fired; unscored accounts with corroborated decline>

## Coverage
<at-risk renewals with no decision-maker touch in six months; accounts nobody is working>

## Revenue at risk by segment
| Segment | Acute | Watch | Renewing 90d |

---
Sources: staircase_run_report (cohort, rollup, events, narratives); staircase_list_communications and staircase_fetch_evidence only for a single account's deep read.
```
Outside Claude, print the markdown (and optionally `risk-radar-<date>.md`). No CRM writes.

## Interactive dashboard (the flagship output inside Claude)
Build with `show_widget` (call `read_me` first). Reference template: `experiences/monday-risk-radar.widget.html`.
- **KPI row:** revenue at risk (accounts), revenue where this product is part of the risk (when a slice is set), renewing in 90 days, gave notice or lost, and the systemic driver's revenue and account count.
- **Clickable strips:** state, driver lens, where the risk sits, segment. Each chip filters the table and shows revenue and count.
- **Filters:** renews in 90 days, fired in the last 30 days, health still high (blindsided), no decision-maker touch in six months, the systemic theme, search.
- **The full table:** every account in scope, sortable. Columns: account (tier and health beneath), revenue, renews (days), risk, state, driver (with where it sits), last fired, DM touch.
- **Click a row, expand in place:** the one-line driver, total account revenue, book owner (or "shared pool"), next meeting, churn event date, an "Open in Staircase" link (`customer.url`), and a live deep-dive button that `sendPrompt`s a risk check on that account. Never a top panel, never `position: fixed`.
- **Color:** red for risk 4-5, lost, and notice given; green for saveable; yellow only for Average health (yellow means average, never concern).
- Embed the rows as a compact `DATA` array (short driver lines, not full narratives). Render every row; no nested scroll.

**Alternate visual:** `experiences/risk-radar.html`, a polar radar (severity x renewal urgency, node size = revenue, angle = lens, silent risk in a dashed sector). Set its `FISCAL_YEAR_START_MONTH` to the org's fiscal calendar.

## Edge cases
| Situation | What to do |
|---|---|
| A quarter or more of accounts are acute | The at-risk total isn't a decision number. Lead with the 90-day slice and the saveable share |
| The slice's revenue field is empty on some accounts | Count them, show total account revenue as context, and say revenue at risk is understated |
| A churn event is years old | State **Verify**; don't count it as notice |
| An insight (ChurnRisk EXISTS) returns nothing | The insight may be off in this org; use level 4+ and say which definition you used |
| Nearly every account is multi-threaded, or none has a QBR | Base rate is near 100% or 0%; report it once, don't flag rows |
| Asked for one account's full read | Hand to `../staircase-risk-check/` |

## Guardrails
- Two nets, always: risk level alone lags; union the silent net and corroborate it.
- `multi_threaded` is column-only: never put it in a filter or a child-aggregation condition.
- `organization_sent_count` needs `filter.user: {"operator":"And","conditions":[]}` or it returns owner-only.
- `risk.analysis` is a driver summary, not a quote: fetch evidence before quoting anyone.
