---
name: staircase-expansion-scout
description: "Builds an expansion-analyst workbench over a book of business, split into three motions: advance the deals already in motion (readiness 4-5, usually already known / in Salesforce), develop the emerging ones (readiness 3), and discover uncovered whitespace (healthy accounts with no expansion signal). Steers the user to the right job per tier instead of re-surfacing known opps. Reads the Staircase expansion analyst fields directly (readiness 1-5, momentum, named opportunities, readiness drivers, product whitespace, ARR-potential estimate, critical timing, executive engagement). Triggers on \"expansion scan\", \"expansion opportunities\", \"which accounts are ready to expand\", \"upsell pipeline\", \"where's my whitespace\", \"expansion book review\", \"what expansion should I develop\", \"who should I pitch expansion to\"."
user_type: exec
---

# Staircase Expansion Scout

The expansion analyst's workbench for a whole book. Staircase runs an Expansion analyst on every account and writes its output to **structured, queryable fields**, and it is best at *tracking open opportunities*, so a high readiness score usually means a deal already in motion (and usually already known to the owner / in Salesforce). The value of this skill is not re-listing those; it is **steering the user across three motions**: advance the in-motion deals (4-5), develop the emerging ones (3), and discover uncovered whitespace (healthy accounts the analyst scored no opportunity on). The report already carries the analysis (named opportunities, drivers, whitespace, exec engagement); per-account drill-down is enrichment for the top few, not the main path.

## Foundation references
Read before composing queries if you have not this session:
- `../staircase-mcp-expert/`: report-first mechanics, field ids, reliability rules. **This skill is report-first**: the expansion fields are structured columns, not prose to scrape.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **User profile:** `~/.staircase-mcp/user-profile.md` carries the resolved scope; if it's absent, the foundation's first-call contract (`../staircase-mcp-expert/SKILL.md` step 0) resolves it. Never run the whole org unscoped for a personal ask (the readiness>=3 population can run to hundreds of accounts).

## The expansion analyst fields (the whole point)
All live on the `customer` entity, all columnable. Confirm exact ids once via `report_metadata` (they are standard, present in every org).

| Field id | What it tells you | How to use it |
|---|---|---|
| `customer.expansion.readiness_level` | 1-5, populated only when the analyst fired | The primary filter (>=3) and primary rank key. Its *presence* is the signal. |
| `customer.expansion.momentum_indicator` | Heating / Steady / Cooling | The **tempo** signal. Heating = pursue now; Cooling = readiness is going stale, de-prioritize even at a high level. |
| `customer.expansion.customer_opportunities` | Named opportunities (Collection/list) | The concrete plays to pitch. This is your pipeline line-items. |
| `customer.expansion.readiness_drivers` | First-order / second-order reasons | The *why now* and your pitch angle. |
| `customer.expansion.product_spread` | Products they already have | Whitespace = products they DON'T have. |
| `customer.expansion.total_arr_potential` | Qualitative estimate: significant / moderate / small | Value tier. **It is a word, not a number; do not sort numerically.** CRM is authoritative for the real dollar. |
| `customer.expansion.critical_timing` | Timing narrative, often renewal-linked | When to strike. A renewal window is the sharpest trigger. |
| `customer.expansion.executive_engagement` | Named execs + engagement strength | Whether you have the air cover to expand. |
| `customer.expansion.summary` | The analyst's prose summary | The narrative for the top picks. Verbose. |
| `customer.expansion.recent_changes` | What moved recently | Freshness / what to reference in outreach. |

> **Verbosity warning (validated internally):** the narrative fields (`summary`, `readiness_drivers`, `customer_opportunities`, `executive_engagement`, `critical_timing`) are long, ~135KB for 10 rows with all of them selected. **Two-tier column strategy below.**

> **Opportunity-level detail:** the `customer.expansion.*` fields above are one row per account. When you need one row per individual opportunity, the `expansion_opportunity` report entity carries them (including `confidence_level` High/Medium/Low and `momentum_state`). An account can have several rows there, so don't assume one row per account when joining back to `customer`.

## Step 0: Scope
- **My accounts:** `customer.<book_owner_field> In [<user_id>]`, using the book field the foundation resolved. Never assume `customer.owner`.
- **A named teammate's book:** `customer.<book_owner_field>.full_name In ["<name>"]` (a bare name on the Reference field itself errors).
- **A leader view:** no owner scope; say so, and rank the whole portfolio.

## Step 1: The three expansion motions (the most important thing to internalize)
The analyst scores readiness 1-5, but the distribution is skewed and **that skew is the routing signal** (validated internally: the large majority of scored accounts sit at readiness 4-5, a much smaller band at 3, very few at 1-2, and a large share of the book has no readiness score at all). The analyst is best at *tracking open opportunities*, so a high score usually means a deal that's already in motion, not a discovery. Three motions, three different jobs:

| Motion | Population | What it means | The job (the value you add) |
|---|---|---|---|
| **In motion** | readiness **4-5** | A live opportunity. **The account owner almost always already knows this, and it usually already has a Salesforce opportunity.** | **Track the next action**, not "here's an opportunity." Advance the known deal: the move + the timing. |
| **Emerging** | readiness **3** | Real signal, not yet a deal. Momentum decides. | **Develop it.** Foster a Heating 3 toward a live opp; nudge or drop a Cooling 3. |
| **Uncovered / whitespace** | **no readiness** (or 1-2) | The analyst detected no opportunity, but a product gap + a healthy, happy account may hide one. | **Discover.** Propose a play from whitespace the owner may not have considered. |

> Do NOT just rank the book readiness-high-first and present the 4-5s as finds; you'd be handing the owner opportunities they already have open in Salesforce. Lead with the *next action* on those, and spend the discovery energy on the emerging and uncovered tiers. Treat 4-5 as "already known."

## Step 2: Pull the book (two passes)
**Owner scope** per Step 0 on both. Validate the count narrowed vs the unscoped baseline (R1).
1. **Scored pass** (in-motion + emerging): `run_report` `readiness_level >= 3` AND owner, **lean columns**: `readiness_level, momentum_indicator, product_spread, total_arr_potential, renewal_date, risk_level, buckets.health`. (Named owner → `generate_report` "expansion-ready accounts (readiness 3+) owned by <Name>, columns …".)
2. **Whitespace pass** (uncovered): a separate `run_report`: `buckets.health Equal "High" AND expansion.readiness_level NotDefined` AND owner, columns `product_spread, revenue, tier.name, renewal_date, buckets.sentiment.score`. `product_spread` shows what they DO have → the gap is what they lack. (Optionally add a positive-sentiment or `PositiveSentimentTrend` insight condition to focus on the happiest.)

## Step 3: Route each account to its motion, then rank WITHIN it
Sort every account into its motion (Step 1) and give it the right job. Don't rank across motions, rank inside each:
- **In-motion (4-5):** the named opportunity + `critical_timing` (flag a renewal window) + the single next action to advance it. Momentum Heating = push now; **Cooling = the open deal is stalling, re-engage.** Rank by momentum then timing.
- **Emerging (3):** the opportunity + the `readiness_drivers` to reinforce (what moves it 3 → live) + momentum direction (building vs fading).
- **Uncovered:** name the product gap from `product_spread`, pair with health/sentiment, and propose a concrete discovery play.

Then the **risk cross-check** (internal): readiness + `risk_level >= 3` = **save-then-expand**. Sequence the friction fix first, then the opportunity. Keep the scoring internal; surface only the sequenced recommendation.

## Step 4: Pull the detail for the shortlist
For the top N per motion, run a **second report** on just those account ids adding the narrative columns (`customer_opportunities`, `readiness_drivers`, `executive_engagement`, `critical_timing`, `recent_changes`, `summary`). This keeps the verbose fields off the full-book pull. Filter `customer.id In [<shortlist ids>]`.

The narrative columns usually answer everything ("what's the play, who's the exec, why now"). Only when you need **evidence/quotes** for a high-stakes pitch, drill that account with `analyze_account` (after `account_lookup`), and `fetch_evidence` for the source. Stay within the parallel per-account analysis cap (10 today); you rarely need more than 3-5 here.

## Step 5: Produce the report, split by motion
The whole point is to steer, so the report is organized by motion, not one flat readiness ranking. Each section has a different job.

```
# Expansion Book: <Owner> · <date>

**In motion (4-5):** <n>  ·  **Emerging (3):** <n>  ·  **Whitespace candidates:** <n>
> ARR-potential is Staircase's estimate; the 4-5s are likely already open Salesforce opps. Confirm figures/dates in the CRM.

## Headline
<2-3 sentences: how many deals are already in motion (and the top next action), where the real
NEW upside is (emerging + whitespace), and the single highest-leverage move this week.>

## In motion · advance the open deals (you likely already know these)
| Account | Readiness | Momentum | Open opportunity | Timing | Next action to advance | Status |
|---------|-----------|----------|------------------|--------|------------------------|--------|
| Acme Corp | 5 | Heating | Full-user true-up | overage now | Send true-up quote (the AM) | Not started |
| <Cooling 4-5> | 4 | Cooling | ... | ... | **Re-engage: the deal is stalling** | ... |

## Emerging · develop toward a live opportunity
| Account | Momentum | Signal / opportunity | What moves it to a deal | Next step |
|---------|----------|----------------------|-------------------------|-----------|
| Globex | Heating | Support-survey automation | Reinforce the driver; scope it | Discovery call |

## Whitespace · uncovered candidates to prospect
| Account | Health | Has | Gap (propose) | Why now |
|---------|--------|-----|---------------|---------|
| <acct> | High | Product A, Product B | an add-on module | Happy + no add-on yet |

## Save-then-expand (risk present)
<Accounts readiness+risk >=3: sequence the friction fix, then the opportunity. One line each.>

## Recommended plays
<Org-level moves. Separate "advance in-motion" from "develop emerging" from "prospect whitespace"; they are different motions with different owners and cadence.>

---
## Sources
- Staircase expansion analyst fields via `staircase_run_report` (readiness, momentum, opportunities, drivers, whitespace, ARR potential, timing) + a whitespace pass (healthy, no readiness signal)
- Staircase `staircase_analyze_account` (evidence enrichment for top picks, where run)
```

**Format adaptation:** Cowork leads with the headline card and the tracked plays table (sortable), deep dives as expandable cards, each next-action as an action card. Code prints markdown + optional `expansion-book-<owner>-<date>.md`. No CRM writes; actions are drafts the user owns.

## Edge cases
| Situation | What to do |
|-----------|------------|
| Report returns the full unscoped row count | The Owner filter didn't apply (R1). Re-check the owner id / re-scope; don't present an unscoped book. |
| Readiness column mostly 3-4, few 5s | Normal. Rank by momentum + timing to find the *now* plays inside the 4s. |
| Account is Heating readiness-5 but also risk >= 3 | Save-then-expand. Sequence the friction fix first; note it plainly. |
| User asks to sort by ARR dollars | `total_arr_potential` is a qualitative word. Rank by it as a tier; get the dollar from the CRM. |
| User wants expansion within an industry/segment | Staircase doesn't filter industry reliably. Produce the list; segment from the CRM. |
| User wants to track over time | This is a point-in-time read. Save the dated file; re-run to compare `recent_changes` and momentum shifts. |
