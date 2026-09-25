---
name: staircase-renewal-watchlist
description: "Renewal Command: a renewal priority planner for CSMs and a risk-weighted renewal forecast for CS leaders. Pulls every upcoming renewal in one report; for a CSM, ranks them by where effort moves the outcome most (proximity x value x risk x salvageability) with a save-or-grow-at-renewal play each; for a leader, rolls the window up by segment into likely-renew / at-risk / churn-flagged revenue. Churn-aware (a confirmed non-renewal is a forecast loss, not a save target). Triggers on \"renewal planner\", \"plan my renewals\", \"which renewals need attention\", \"renewal priorities\", \"renewal watchlist\", \"renewal forecast\", \"renewals by segment\", \"renewal exposure this quarter\", \"where can I move the needle on renewals\", \"what's renewing this quarter\"."
user_type: exec
allowed-tools: mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Renewal Command

Two jobs over one renewal window. For a **CSM**, it flight-plans the book: every renewal with the signals that decide it (risk, health, sentiment, expansion readiness, engagement, threading), ranked by where effort changes the outcome, each with a concrete play: defend, grow, or both. For a **CS leader**, it forecasts the window: renewals rolled up by segment into likely-renew / at-risk / churn-flagged revenue, so leadership sees the quarter's exposure and where to put the team. Both are **report-first** (renewal date, revenue, and analyst reads are structured fields) and **churn-aware** (a renewal already carrying a churn event is a forecast loss to manage, not a save to chase).

## Which mode
- **CSM planner** (default when scoped to one owner): Steps 0-4 below, the ranked priority plan with per-account plays.
- **Leader forecast** (whole book / a tier / a team): the "Leader mode" section, the risk-weighted, churn-aware segment rollup. Run it first for the exec picture, then drop into the planner for any segment that needs account detail.

## Foundation & portability (read first)
This is a **workflow skill built on top of `staircase-mcp-expert`**. That foundation owns the query mechanics (the EXISTS forms for insights/lifecycle events, child-aggregation group-by, the argument system, `../staircase-mcp-expert/references/query-patterns.md` + `../staircase-mcp-expert/references/advanced-report-patterns.md`, and the Priority-Weighting composite). This skill composes those primitives into the renewal workflow; it does not re-teach them. Always read the foundation before composing queries this session.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **User profile:** `~/.staircase-mcp/user-profile.md` holds the user's resolved scope. No scope → ask.

**Portability law (this skill ships to any Staircase customer).** Use ONLY standard Staircase primitives (the fields, insights, and lifecycle events every org has), never instance-specific `_c` custom fields and never a hardcoded account, owner, tier, or product name in logic. Segment names come from the org's own `tier` entity; owner ids from `report_metadata`. **Discover before relying:** call `report_metadata` and probe each insight/lifecycle-event type per org, since not all are enabled everywhere. If a signal is absent, degrade gracefully and say so; never fail because one insight or trend field is missing. Revenue: `customer.revenue` (contract) or `customer.revenue_converted` (corporate currency); both standard.

## Where Staircase renewal data stands (read once)
`customer.renewal_date` and `customer.revenue` are **structured, queryable, sortable fields**. In many orgs they are populated (verified live: a full renewal window came back with dates and revenue). Use them to build and rank the plan. The CRM remains authoritative for the contracted dollar and date, so any account where the decision hinges on the exact figure gets a "confirm in CRM" note, not a blocker. This corrects the old premise that Staircase holds no renewal dates.

## Step 0: Scope + window
- **Scope:** my accounts = `customer.<book_owner_field> In [<user_id>]` (the book field the foundation resolved; never assume `customer.owner`); a named CSM = `customer.<book_owner_field>.full_name In ["<name>"]`; a leader forecast = no owner scope.
- **Window:** default the next 120 days (a quarter-plus of runway). Ask if the user wants a specific quarter. Filter `renewal_date InRange [today, today+120d]`.

## Step 1: The renewal report (one call)
```
entity: customer
columns: customer.id, customer.name, customer.<book_owner_field>.full_name, customer.renewal_date, customer.revenue,
  customer.risk.risk_level, customer.buckets.health, customer.buckets.sentiment.score,
  customer.expansion.readiness_level, customer.expansion.momentum_indicator,
  customer.last_engagement, customer.relationship_score.multi_threaded, customer.next_qbr_date
filter: renewal_date in [today .. today+120d]  AND  <owner scope>
sort: renewal_date ascending
```
Keep the verbose analyst strings (`risk.analysis`, `expansion.summary`) OUT of this listing; pull them per-account for the shortlist. Confirm the count is a plausible book slice, not the whole org.

## Step 1.5: Renewal-engagement signals (is anyone actually working it?)
The report fields tell you the account's *state*; these standard lifecycle-event / insight primitives (via the EXISTS form from the foundation) tell you the *engagement*: the difference between a renewal being handled and one drifting. Add them as supplementary EXISTS passes over the Step-1 cohort (each is optional per org: probe availability, degrade if absent). `lifecycle_event` is also a root report entity, so it can be reported on directly. **Discover the event labels, don't assume them:** the `lifecycle_event.type` enum is partly org-specific and relabeled for display (for example, `renewal_discussion` displays as "Commercial discussion"), so read the available types and their labels from `report_metadata` before filtering on them.
- **Active renewal conversation:** a `renewal_discussion` lifecycle event (or the org's equivalent type) **dated recently** (e.g. `lifecycle_event.date` in the last ~45-60 days, nested in the EXISTS condition). Verified: the event fires historically for almost the whole at-risk cohort, so **date-bound it** or it doesn't discriminate; recent = a live commercial conversation.
- **No active conversation (the gap):** the `NoRenewalDiscussion` insight (EXISTS), or simply the absence of a recent `renewal_discussion` event. This is the sharp one: an at-risk or churn-flagged renewal with **nobody talking to them** is the highest-priority "act now" account (verified live: a large share of at-risk renewals had no recent conversation, and only part of that set carried the explicit `NoRenewalDiscussion` insight). A saveable renewal + no conversation = get someone on it today.
- **Churn-risk signal:** the `churn_risk` lifecycle event or `ChurnRisk` insight. Note this is BROAD on an already-at-risk cohort (fires for most), so it is more useful as a **portable way to define the at-risk cohort itself** (`insight EXISTS ChurnRisk` instead of `risk.risk_level >= 4`, for orgs where the level isn't scored) than as a per-account discriminator here. (Distinct from the `churn` event, which is the confirmed-leaving signal; see churn-aware ranking.)
- **Engaged stakeholders:** `customer.relationship_score.stakeholders_count` (the count of tracked relationships) with `multi_threaded`. Thin coverage (1-2, or `multi_threaded=false`) on a near renewal is a structural risk regardless of the other signals.

## Step 2: Rank by where effort moves the outcome
Apply the foundation composite, whose TIER_1 is renewal urgency. The renewal lens sharpens three inputs:
- **Proximity** (renewal_date): <30d = act now, <60d = plan now, <90-120d = get ahead.
- **Salvageability / needle-movement**: an at-risk account (risk >= 3, low health, declining sentiment, single-threaded) is where CSM effort *changes* the result. A healthy, quiet renewal needs a light touch. Rank the movable-and-valuable accounts up; don't bury a large risk-4 renewal under a small risk-5 one.
- **Engagement gap (a top multiplier)**: a saveable renewal with **no active conversation** (Step 1.5) is the most actionable account on the board: winnable AND nobody's on it. Push these to the top of the Defend list; the move is "get someone in the room this week." Conversely, a manage-closure account with no conversation is just a clean exit.
- **Value**: `revenue` (confirm in CRM). A big risk-4 renewal outranks a small risk-5 one on leverage.

Then classify each priority account's **play** (this is the planner's output, not a raw score):
- **Manage closure (churn-flagged):** a `churn` lifecycle event has fired (see Leader mode for the EXISTS form). Read `customer.churn.synopsis`: if it confirms a non-renewal/termination, this is a **forecast loss**. Don't spend save hours; manage the closure cleanly, capture the reason, feed the churn retrospective. If the synopsis is unresolved/pending, treat it as an acute Defend and verify fast. Pull these OUT of the "saveable" leverage ranking so they don't crowd it.
- **Defend:** risk present, expansion low/none. Save motion: resolve the friction, re-thread, prove value before the date.
- **Grow at renewal:** healthy + expansion readiness >= 3 (esp. Heating). Bundle the expansion into the renewal conversation.
- **Defend then grow (save-into-expansion):** risk >= 3 AND expansion readiness >= 3. Highest leverage. Sequence: stabilize, then expand. (Foundation's Risk x Expansion merge; keep the scoring internal, surface the sequenced recommendation in plain language.)
- **Steady:** healthy, no expansion signal, well ahead of date. Light-touch confirm; keep it off the priority list.

## Step 3: Detail the shortlist (driving factors → recommended action)
For the top N (default 8-10), pull the narrative for those ids in a second report (add `customer.risk.analysis`, `customer.expansion.summary`, `customer.renewal.synopsis`). **`customer.risk.analysis` is the deterministic "why at risk"**: a current, dated narrative of the driving factors (verified: it names things like "commercial pressure on renewal terms + a connector breakage after a recent release" or "an unresolved strategic-fit objection to Product A"). Turn each risk reason into a **specific recommended action** in the plan (the connector fix + commercial re-frame; the roadmap conversation with the exec). Only drill with `analyze_account` when you need evidence/quotes or the named stakeholder the deterministic field doesn't give:
```
analyze_account(id, "For the upcoming renewal at <Account>: the single biggest threat to renewal
and the named stakeholder behind it, any expansion the renewal could carry, the most recent
relevant evidence, and the most concrete play a CSM should run before the renewal date. Cite
evidence IDs; separate evidenced from inferred.")
```
Stay within the parallel per-account analysis cap (10 today); batches of ~5.

## Step 4: Produce the plan
```
# Renewal Plan: <Owner> · next <N> days (<date>)

**Renewals in window:** <count> · **At risk (risk >=3 or Low health):** <count> · **Grow-at-renewal candidates:** <count> · **Revenue in window:** <sum, confirm in CRM>
> Renewal dates and revenue shown from Staircase; confirm the contracted figure/date in the CRM before acting.

## Headline
<2-3 sentences: the shape of the quarter's renewals, where the real risk-to-revenue concentrates,
and the single highest-leverage move this week.>

## Priority plan (ranked by leverage)
| # | Account | Renews | Revenue | Risk | Health | Expansion | Play | Next action (owner, by when) |
|---|---------|--------|---------|------|--------|-----------|------|------------------------------|
| 1 | Acme Corp | 2026-09-26 | $X | 4 | High | none | Defend | Re-confirm value w/ sponsor before 09-12 (CSM) |
| 2 | Globex | 2026-11-13 | $Y | 4 | High | 4 Heating | Defend then grow | Resolve friction, then attach expansion (CSM) |

## Priority deep dives (top N)
### <Account> · renews <date> · <Play>
- **Biggest threat to renewal:** <what + named stakeholder> (evidence: <ID>)
- **Grow potential (if any):** <named expansion opportunity>
- **Engagement state:** <last touch, threading; flag single-threaded / no next QBR>
- **Play & next action:** <concrete move, owner, by when>

## Steady renewals (light touch)
<Brief list of healthy, ahead-of-date renewals that need only a confirm.>

## Cross-book plays
<Patterns: e.g. a cohort of single-threaded renewals needing re-threading; a value-story push to the risk-4 cohort.>

---
## Sources
- Staircase renewal window via `staircase_run_report`, with `staircase_generate_report` as the fallback (renewal_date, revenue, risk, health, sentiment, expansion, engagement, threading)
- Staircase `staircase_analyze_account` (per-account renewal threat + play, where run)
```

**Format adaptation:** Cowork leads with the headline card and the ranked plan table (sortable), deep dives + next-actions as cards. Code prints markdown + optional `renewal-plan-<owner>-<date>.md`. No CRM writes.

## Leader mode: the risk-weighted renewal forecast
A CS leader does not want hundreds of renewals listed; they want the quarter's **exposure**: how much is renewing, how much is at risk, how much is already leaving, by segment. One child-aggregation report gives it. Make the segment the root entity and roll the renewal window up with three revenue measures (total, at-risk, churn-flagged), using a **nested EXISTS inside the child-aggregation condition** for the churn cut (verified live):
```
entity: tier   columns:
  tier.name
  COUNT(customer) WHERE status=Active AND renewal_date InRange[window]            -> renewing accts
  SUM(customer.revenue_converted) same condition                                   -> renewing $
  SUM(customer.revenue_converted) + AND risk.risk_level >= 4                        -> at-risk $
  SUM(customer.revenue_converted) + AND EXISTS(lifecycle_event.type = "churn")      -> churn-flagged $
```
(Each SUM is a child-aggregation column: `{field:{rootEntityPath:"tier",childEntity:"customer",referenceField:"customer.tier",aggregation:"SUM",aggregatedField:"customer.revenue_converted",condition:{…}}}`. The churn column's condition nests the lifecycle-event EXISTS leaf. Root `user` instead of `tier` gives the forecast by team/owner.) Verified live on a whole-org, next-120-day window: one call returns renewing, at-risk, and churn-flagged revenue for every segment the org defines.

Read it as a forecast: **likely-renew** ≈ renewing − at-risk; **at-risk** = risk≥4 but no churn event (the save target, where the team goes); **churn-flagged** = a churn event fired (subtract from the forecast; split confirmed-lost vs pending via `churn.synopsis`). Output: the segment table, the three-bucket forecast totals, the tiers where at-risk revenue concentrates, and the recommended coverage (which segment/team gets the renewal push). Then hand each hot segment to the CSM planner for account detail.

**Add the engagement cut (the coverage gap).** A fifth conditional SUM (renewals in window with **no recent `renewal_discussion` event**, or the `NoRenewalDiscussion` insight) gives the leader the "**$X renewing with no active conversation**" number per segment. That's the exposure nobody is working: the most alarming line on a forecast, and the clearest coverage ask. Pair it with at-risk: at-risk **and** no conversation is where the quarter is quietly lost.

## Interactive cockpit (inside Claude)
Render the renewal window as a cockpit via `show_widget` (call `read_me` first; same pattern as `../staircase-risk-radar/` and the Book Triage cockpit, see `../staircase-risk-radar/experiences/monday-risk-radar.widget.html`). Leader mode leads with the segment-forecast bars (likely / at-risk / churn-flagged, and the no-conversation line); CSM mode leads with the ranked plan. Details:
- **KPIs:** renewing $ · at-risk $ · churn-flagged $ · **no-active-conversation $** (the coverage gap).
- **Filter chips:** by play (defend / manage-closure / verify / grow) and by segment.
- **Table column order:** `Play · Account · Seg · Revenue · Renews · Risk · Health · Conversation · Owner`. The account-data block (seg/revenue/renews/risk/health/conversation) sits in the middle, **owner on the far right**. The Conversation column shows active (recent `renewal_discussion`) vs a red "no convo" gap.
- **Inline accordion** (click a row → expand in place, toggle to collapse; never a top panel): the first-paragraph `customer.summary`, the engaged-stakeholder count + threading, the churn-risk/conversation flags, the play, and a live deep-dive button (`sendPrompt`).

## Edge cases
| Situation | What to do |
|-----------|------------|
| `renewal_date` unpopulated for many accounts | Note the gap; rank the dated ones, and pull dates for the undated from the CRM. Don't silently drop them. |
| The window is empty | No renewals in range. Widen the window or report the quiet quarter honestly. |
| Big risk-5 but tiny revenue vs big risk-4 high revenue | Leverage ranking handles this: value x salvageability. Surface both; don't let a small acute case crowd out a large movable one. |
| Account healthy but renewal imminent | Steady list, light touch. Don't manufacture risk. |
| User wants only at-risk renewals | Filter risk_level >= 3 (or Defined) in Step 1; skip the grow/steady classes. |
| Expansion-heavy, low-risk book | Lead with grow-at-renewal plays; the plan tilts offensive. |
