---
name: staircase-risk-radar
description: "Builds the CS-leader portfolio risk view. Report-first: where revenue is at risk across the book, WHY (the deterministic driving factors), how urgent (risk against renewal timing), and the recommended play, segmented by tier/team and weighted by revenue. Returns the risk-to-revenue heatmap, the top at-risk accounts with reason and action, the blindsided watchlist (risk the health score has not caught), the systemic driver theme, and the coverage check. Triggers on \"portfolio risk\", \"where are we at risk\", \"risk radar\", \"book of business risk\", \"what's at risk this quarter\", \"revenue at risk\", \"risk by segment\", \"risk by team\"."
user_type: exec
allowed-tools: mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Risk Radar (leader / portfolio)

A CS leader does not need a red list of hundreds of accounts. They need four answers: **how much revenue is at risk, why, which of it has a clock on it, and what to do**, segmented so they can point a team at it. This skill answers those from structured reports (deterministic ranking, counts, revenue rollups), then grounds the "why" in the Risk analyst's stored driving factors and the cohort's own communication themes.

**This is the portfolio lens.** For a single account's full risk read + save sequence use `../staircase-risk-check/`; for one CSM's weekly action list across every motion use the Book Triage skill. This skill deliberately stops at the leader's decisions: where to invest, which program to stand up, which deals to personally step into.

## Foundation references (read BEFORE composing any query)
- `../staircase-mcp-expert/` and `../staircase-mcp-expert/references/advanced-report-patterns.md`: the report engine, the EXISTS/child-aggregation forms, the argument system, field ids, and the reliability rules in `../staircase-mcp-expert/references/anti-patterns.md`. This skill assumes them.
- `../staircase-app-design/`: the app chrome + the interactive-experiences standard the radar follows. Read before rendering the visual.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.

## Scope (decide first)
- **Whole org** (default for a leader): status = Active, no owner filter.
- **A segment:** add `customer.tier` In [...] (tier names via the `tier` entity; they vary per org, so discover them rather than assuming).
- **A team, by book owner:** `customer.owner` is not always the CSM; on some orgs it holds a structurally different role, and attributing risk "by owner" then routes the finding to the wrong people. Use the resolved book-owner field (`scope.book_owner_field` in the profile, or the foundation's first-call contract), then filter `customer.<book_owner_field> In [<user_ids>]` (ids from `current_user_id` or a `user` roster report) or `customer.<book_owner_field>.full_name In ["<names>"]`.
- **Portable fields only.** Never hardcode a specific `_c` field id (e.g. a custom ARR field). Use `customer.revenue_converted` for revenue, `tier.name` for segment, and the confirmed book-owner field (a runtime parameter) for team rollups. Discover what exists per org via `report_metadata`.

## Two states of risk (the factoring: read both)
`customer.risk.risk_level` (1-5) fires ONLY when the Risk analyst detected a churn risk in communications in ~the last 3 months. It is confirmed but **lagging**, and it misses accounts **silently sliding** before any analyst fires. A complete portfolio read is the union of:
- **Flagged:** `risk.risk_level` populated (>= 4 acute, 3 watch). Carries the `risk.analysis` narrative.
- **Silent / emerging:** `risk.risk_level` empty AND **corroborated** deterioration: low `buckets.health` AND (low `buckets.engagement.score` OR stale `last_engagement` OR negative `buckets.sentiment.score`). Corroboration is required: a lone `health = Low`/`0` is usually missing data, not decline.

Optional sharper cohort where enabled: `insight EXISTS ChurnRisk` (∨ `NegativeSentimentTrend`, `CustomerDark`, `Farewell`) via the child-EXISTS filter form. Probe availability first, since not every insight fires per org; degrade to the `risk_level` + silent-net definition above when absent.

---

## The leader flow (seven report-first reads)

### 1. Define the risk cohort
`customer` report, status Active, `risk.risk_level >= 3` (validated internally: this returns the flagged cohort). Lean columns: `customer.id, customer.tier, customer.revenue_converted, customer.risk.risk_level, customer.buckets.health, customer.renewal_date`. Also run the **silent net** (risk empty + corroborated decline) and union client-side, tagging each row **flagged** vs **silent**. Validate the row count narrowed vs an unfiltered baseline (a mis-keyed filter silently returns the whole table).

### 2. Risk-to-revenue heatmap (the headline): child-aggregation group-by
Make the segment the **root entity** and roll the at-risk cohort up under it. Root `tier`, columns `tier.name` + a COUNT child-agg + a SUM(`customer.revenue_converted`) child-agg, each with the risk-cohort `condition`. (Same pattern with root `user` gives risk-to-revenue by owner/team.) This is the single most important leader output: it converts hundreds of flat rows into "**$X at risk, concentrated in segment Y**". Validated internally: the segment with the fewest at-risk logos can carry the most at-risk revenue. The dollars concentrate where the logo count does not.

### 3. Urgency = risk x renewal timing (the clock)
The risk cohort AND `renewal_date` InRange the next quarter (`"[YYYY-MM-DD,YYYY-MM-DD]"`, Date field takes a scalar range). This is the at-risk revenue with a forcing function: the slice a leader personally works. Sort by `revenue_converted` desc. Validated internally. (Renewal dates here are approximate; CRM is authoritative for the true date.)

### 4. Reasons -> actions (deterministic) for the top-N by revenue-at-risk
Pull `customer.risk.analysis` (a stored narrative of the current driving factors) for the top ~10 of the urgent slice; add a `revenue_converted > <floor>` filter to keep the payload lean (this string is large). Read each into a one-line **driver** and a **recommended action**. This is deterministic and evidence-derived: do NOT default to `analyze_account` for the list; reserve that for a single account's deep read. Map each driver to a lens (below) so the leader sees the pattern, not ten anecdotes.

### 5. Blindsided watchlist (risk the score has not caught)
Within the risk cohort, the accounts where **health still reads High/Average** but risk fired: the ones a health-score dashboard would show green. These are the leadership surprises. (Add the silent-net rows near a renewal, the high-value catches a risk-level-only view misses.) Keep it a short, named watchlist.

### 6. Systemic driver (the "solve once" theme): cohort-scoped topics
`parent_topic` report, each metric scoped to the risk cohort via the `filter.customer` argument (with `dateRange` e.g. `Past3Months` and `commType`). Rank the **canonical parents only** (Support & issues, Commercial & contracts, Feature requests, Implementation & projects, Risk & dissatisfaction, Customer success & relations, Security & compliance, Organizational changes, Competitors, Expansion opportunities, Advocacy & value realization, Product knowledge) by negative volume AND by negative **rate** (neg / total). A theme with a high rate on real volume is the systemic driver to get ahead of. Validated internally: in one at-risk cohort, Support & issues dominated negative volume while Risk & dissatisfaction carried the highest negative rate. Ignore org-internal/instance topics (they appear when the org is itself a Staircase instance).

### 7. Coverage check (are we even engaging the risk?)
On the at-risk cohort, read BOTH `customer.email.owner_sent_count` (the standard `Owner` relationship specifically; this field is wired to `Owner`, not to the confirmed CSM/book-owner field, so read it as "the named account owner's engagement," which may or may not be the same person as the CSM per R7b) AND `customer.email.organization_sent_count` (the whole org). `organization_sent_count` needs `filter.user: {"operator":"And","conditions":[]}`. Near-zero on both = **silent risk at scale** (we are not working accounts that are sliding). Org-heavy / owner-light = support is carrying a CSM-absent account. This is the manager's accountability cut; pair with `stakeholders_count` + `multi_threaded` (column-only, filter client-side) for the coverage-depth read.

---

## The five lenses (the shared "why", with the leader's systemic play)
Risk is not one thing. Every driving factor from Step 4 maps to one of five lenses; the renewal is the clock, the lens is the fix. For a leader, each lens has a **program**, not a per-account save (that lives in `risk-check` / Book Triage):

| Lens | Why it churns / shrinks | Portfolio signal | Systemic play (solve once) |
|---|---|---|---|
| **Value** | "We can't justify the spend / don't see it" | high revenue + low health + value/commercial neg themes | a reusable ROI + leadership-dashboard program tied to the customer's own metric |
| **Competitive** | displacement by a competitor or an internal/LLM build | competitor themes (`parent_topic` volume) + alternative/build language in `risk.analysis` | a battlecard + a "vs build-it-yourself / data-moat" narrative for the recurring competitor |
| **Stakeholder-change** | champion loss, missing economic buyer, single-threading, OUR-side CSM churn | low `stakeholders_count`, `multi_threaded=false`, org-change themes | a multi-threading push + a CSM-transition playbook (measure: how many at-risk accounts did WE just reassign) |
| **Product** | adoption / fit / integration / output-trust gaps | low `engagement` + Support/Feature-request themes | a product-fix backlog **with ARR-at-risk attached**: one fix de-risks many accounts (the CS-to-roadmap bridge) |
| **Renewal** (axis) | latent dissatisfaction becomes a dated decision | `renewal_date` window + risk fired | sequence the saves by the window; stand up the program the underlying lens calls for |

Count which lens dominates the at-risk cohort. That tells the leader where to invest ONCE instead of improvising N times.

## Prioritization (which accounts a leader personally steps into)
Rank by **revenue-at-risk x urgency x winnability**, surface the top few:
- **Revenue-at-risk** = `revenue_converted` (CRM authoritative when a decision hinges on the figure).
- **Urgency** = renewal proximity (Step 3; < 30 days dominates, past-due is a fire).
- **Winnability** = a live thread + an addressable blocker in `risk.analysis`. An explicit non-renewal / confirmed migration is likely lost: brief it, protect any retained piece, but do not spend the save energy there.

Severity-sort alone is a trap: it floats already-lost and not-yet-urgent accounts to the top.

## Output: the leader readout
```
# Risk Radar: <scope> · <date>

**At risk:** <n> accounts · **Revenue at risk:** $<sum> (confirm ARR in CRM)
**Most concentrated:** <segment> ($<x>, <n> accts) · **Most urgent:** <account> (<$>, renews <date>)
**Top systemic driver:** <theme> (<neg rate>) · **Dominant lens:** <lens> (<n> of cohort)

## Headline
<3-4 sentences: total revenue at risk, where it concentrates, the one systemic driver worth
solving once, and the 2-3 deals leadership should step into this quarter.>

## Revenue at risk by segment
| Segment | At-risk accts | Revenue at risk | Note |
|---------|---------------|-----------------|------|

## Team load (who carries the at-risk revenue, by confirmed CSM/book-owner field, R7b)
| CSM | At-risk accts | Revenue at risk | Most urgent |
|-----|---------------|-----------------|-------------|
<!-- root=user child-agg, or client-side rollup of the cohort, grouped by the confirmed book-owner field (NOT the standard `Owner` field unless the org confirmed that's the same role). This is the routing cut: a leader assigns action by CSM. -->

## Renewing this quarter · act now (the FULL cohort, owner-attributed)
List EVERY at-risk account renewing this quarter (do not truncate to a top-N; a leader triages the whole set, then a Monday drill picks the few). Sort by revenue, keep it scannable; the driver/action can compress to a phrase per row.
| Account | Owner | Segment | Revenue | Renews (days) | Risk | Health | Coverage | Driver / next move |
|---------|-------|---------|---------|---------------|------|--------|----------|--------------------|

## Blindsided watchlist (health still green, risk fired)
<short named list: account, revenue, why the score misses it.>

## Systemic driver
<the theme, its negative rate + volume, the accounts it spans, and the one program that gets ahead of it.>

## Coverage check
<the risk accounts we are NOT engaging (owner+org comms ~0), and the owner-light/org-heavy ones support is carrying.>

## Recommended plays (by lens, ranked by revenue protected)
<one program per dominant lens, each tied to the revenue it defends.>

---
## Sources
- Staircase `staircase_run_report` (risk cohort; risk-to-revenue child-aggregation; urgency; risk.analysis reasons; cohort-scoped parent_topic driver; owner+org coverage)
- Staircase `staircase_analyze_account` / `staircase_semantic_search` (only where a single account or theme needed the deep read)
```

**Format adaptation:** Cowork leads with the headline card + the revenue-at-risk-by-segment table + the urgent table, blindsided/systemic/coverage as cards. Code prints markdown + optional `risk-radar-<date>.md`. No CRM writes.

## Interactive dashboard (the flagship output inside Claude)
When rendering inside Claude (the `visualize` / `show_widget` surface), the best deliverable is not a static table. It is a **clickable Monday-morning dashboard** the leader drives. Build it with `show_widget` (call `read_me` first). Shape:
- **KPI row:** revenue at risk this quarter, account count, count renewing within 14 days, the most-loaded owner.
- **Two clickable rollup strips:** revenue-at-risk by **segment** and by **owner**; each chip filters the table (the routing cut).
- **The full cohort table:** every at-risk account renewing this quarter, owner-attributed, sortable by any column (revenue / days-to-renewal / risk / health), filterable (search, segment, owner, "renews < 30d", "single-threaded"). Never truncate: the leader wants the whole set with the controls to slice it.
- **Saveable vs confirmed-lost split:** separate the at-risk revenue into **saveable** and **confirmed lost** using the deterministic churn signal (below). The KPIs and a filter chip should let a leader see "$X still saveable / $Y already lost". Don't spend save energy on the lost; route them to the churn retrospective. Confirmed-lost rows carry a `lost` tag.
- **Click a row -> expand inline, then live deep-dive:** clicking a row expands its detail **in place** (accordion; click again to collapse). Never use a top-anchored panel, which loses the leader's place, and `position:fixed` is banned. The detail shows the embedded first-paragraph `customer.summary` (instant context: it routinely reveals a confirmed non-renewal the risk columns read only as "at risk") and a **live deep-dive** button that `sendPrompt(...)`s Claude for the fresh evidence-grounded read (drivers, coverage/economic buyer, last-90-days, whether it's confirmed-lost or saveable, the play before renewal). Snapshot + summary embedded, live detail on click: the dynamic-MCP bridge.

**Churn split: deterministic detection.** A `churn` **lifecycle event** fires on still-Active accounts before churn; it is the reliable "already leaving" signal (validated internally: the event caught materially more of the at-risk-renewing cohort than parsing summary text did, so the event is more complete). Detect via EXISTS: `{"field":{"rootEntityPath":"customer","childEntity":"lifecycle_event","referenceField":"lifecycle_event.customer","aggregation":"EXISTS","condition":{"operator":"And","conditions":[{"field":{"id":"lifecycle_event.type"},"operator":"Equal","value":"churn"}]}},"operator":"Equal","value":true}`. (`lifecycle_event` is also a root report entity, so you can list the event rows directly when you need them.) Then read `customer.churn.synopsis` (populated on Active accounts, and it states the outcome) to mark **confirmed lost** vs an unresolved **churn signal**. Do NOT use a summary-text heuristic: the event + synopsis are deterministic.

Design rules (from `../staircase-app-design/` + the `visualize` design system): dark-mode-safe CSS variables only, weights 400/500, sentence case, Tabler outline icons, no `position: fixed`, render all rows (no nested scroll). Embed the cohort as a compact `DATA` array (scannable fields + one-line signal + first-paragraph summary; the full narrative comes from the live click). Cost note: the summary is ~360 tokens full, so embed only the **first paragraph** (~330 chars, split on the blank line); it carries the decisive headline at ~1/5 the cost. Reference template: `experiences/monday-risk-radar.widget.html`.

**Alternate visual:** `experiences/risk-radar.html` is a standalone polar radar (composite severity x renewal urgency, node size = revenue, angle = lens, silent-risk in a dashed "Emerging" sector). Use it when a spatial "where is the danger" read beats the table. Set its `FISCAL_YEAR_START_MONTH` constant to the org's fiscal calendar so the renewal bands line up with the leader's quarters. Outside Claude (Cowork / Code-with-browser) fall back to the ranked markdown table.

## Edge cases
| Situation | What to do |
|-----------|------------|
| Risk cohort is huge (hundreds) | Expected at book scale. Lead with the revenue-weighted segment rollup + the urgent slice, never the flat list. |
| `revenue_converted` is 0 / unpopulated on some accounts | Report count + reasons; note revenue-at-risk needs the CRM figure for those. Don't drop them from the count. |
| An insight (e.g. ChurnRisk EXISTS) returns nothing | That insight may be disabled in this org. Fall back to `risk_level >= 3` + the silent net. Say which definition you used. |
| Trend fields (`absolute_growth_percentage`) absent | They are flag-gated per org. Degrade to current-period negative volume + rate; note trends unavailable. |
| Systemic driver is an org-internal topic (vendor instance) | Ignore instance/product-feedback topics; rank only the canonical customer-facing parents. |
| Leader asks for a single account's full risk read | Hand to `../staircase-risk-check/`; this skill is the portfolio lens. |

## Reliability guardrails (on top of the foundation's rules in anti-patterns.md)
- **Validate narrowing:** always confirm the risk report narrowed vs baseline. A false-full (whole table returned silently) is the most dangerous failure here.
- **Two nets:** `risk_level` alone is lagging. Always union the silent net, and corroborate silent decline (health + engagement/recency/sentiment), never a lone health=0.
- **`multi_threaded` is column-only, not filterable:** pull it as a column and filter client-side.
- **Date vs DateTime:** `renewal_date` (Date) takes a scalar/`InRange` scalar; `last_engagement`/`last_reach_out` (DateTime) need `InRange "[start,end]"`.
- **`organization_sent_count` needs `filter.user: {And, conditions:[]}`** or it returns owner-only.
- **`risk.analysis` re-derivations are approximate:** ground any shared verbatim claim in a fetched evidence id; the field is the driver summary, not a quote.
- **Portability:** discover fields via `report_metadata`; use standard `customer.*` / `tier.*` only; never hardcode a `_c` field.
