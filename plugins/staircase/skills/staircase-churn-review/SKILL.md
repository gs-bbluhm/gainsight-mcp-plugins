---
name: staircase-churn-review
description: "Runs a quarterly churn retrospective across a book of business. Two halves in one report-first workflow: what churned and why (churned-account synopses, reason clustering, lost revenue by tier) plus the leading indicators (rising negative themes across the still-active book that predict the next churns). Produces a churn review a CS leader can present. Triggers on \"churn review\", \"quarterly churn\", \"what did we lose and why\", \"churn retrospective\", \"churn drivers\", \"why are customers churning\", \"churn patterns this quarter\"."
user_type: exec
---

# Staircase Quarterly Churn Review

A churn retrospective with a forward edge. Half of it is the post-mortem: who churned this quarter, the lost revenue, and the reasons, straight from the Churn analyst's stored synopses and issue lists. The other half is the leading indicator: which negative themes are *rising* across the accounts you still have, so the review ends in prevention, not just accounting. Both halves are structured reports; the churn analyst has already done the reading.

## Foundation references
Read before composing queries if you have not this session:
- `../staircase-mcp-expert/`: report mechanics, the `parent_topic` theme-ranking primitive, field ids.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **User profile** (`~/.staircase-mcp/user-profile.md`): the `Owner` scope for a per-CSM review; a leader may want the whole book (name the scope explicitly).

## The two data sources (both verified live)
| Half | Tool + fields |
|---|---|
| **Retrospective (what/why)** | `customer` report filtered `status = Churned` + `churn.churn_date` in the quarter. Columns: `customer.churn.churn_date`, `customer.revenue`, `customer.tier`, `customer.churn.issues` (Collection of reason phrases), `customer.churn.synopsis` (AI Churn Analysis narrative). |
| **Leading indicators (what's rising)** | `parent_topic` report with the trend fields: `accounts_count`, `negative_sentiment`, `current_period_volume`, `previous_period_volume`, `absolute_growth_percentage`. Rank by growth% x negative volume to find themes heating up across the active book. |

## Step 0: Scope + quarter
- **Scope:** leader review = whole book (say so); CSM review = their book through the resolved book-owner field (`customer.<book_owner_field> In [<user_id>]`, or `customer.<book_owner_field>.full_name In ["<name>"]` for a named CSM). Never assume `customer.owner`.
- **Quarter:** default the trailing 90 days; ask if they mean a named fiscal quarter, and set the `churn_date` window accordingly.

## Step 1: The churned-account report (retrospective)
```
entity: customer
filter: status = Churned  AND  churn.churn_date in [quarter start .. quarter end]  [AND owner scope]
columns: customer.id, customer.churn.churn_date, customer.revenue, customer.tier,
  customer.churn.issues, customer.churn.synopsis
sort: churn.churn_date descending
```
`issues` and `synopsis` are verbose but you want them here: this is the small churned set, not the whole book, so the payload stays manageable. If it doesn't, pull `issues` for all and `synopsis` only for the largest losses.

## Step 2: Cluster the reasons (client-side)
The `issues` Collection gives per-account reason phrases; the `synopsis` gives the narrative. Cluster the reasons into a handful of churn themes (e.g. product-reliability, missing-capability, value-not-realized, commercial/price, competitive-loss, champion-loss, non-decision/exit-intent). Count accounts and sum lost revenue per theme. Note the **decisive** reason vs contributing friction. The synopses distinguish these ("the decisive factor was explicit exit intent rather than a recoverable product problem"); carry that distinction, since it changes what's preventable.

## Step 2.5: Unforced errors + feature blockers (the two highest-value cuts)
Leaders act on what was *preventable*. Two specific passes make this concrete (both verified against real churn):

**A. Unforced errors: did WE cause or miss it?** Separate market losses (competitive, M&A, budget cut; not preventable) from execution failures we own. Two evidence sources:
- **The `issues`/`synopsis` text** already names them: "renewal outreach came too late", "no proactive rescue before churn notice", "transactional auto-renew emails to new POCs, no value recap", "no EBR / tailored success narrative", "forced package migration without a sandbox", "support was reactive during a sensitive renewal period." Tag each churned account preventable / partly / not.
- **The engagement runway (quantitative).** For the churned cohort, pull our outreach in the two quarters before churn with windowed metrics, and reference BOTH `customer.email.owner_sent_count` (the CSM) and `customer.email.organization_sent_count` (the whole org) at `[prior-quarter range]` and `[final-quarter range]` (fixed `["YYYY-MM-DD","YYYY-MM-DD"]` windows; `organization_sent_count` needs `filter.user` = `{"operator":"And","conditions":[]}`). **We went dark = ~0 across both windows** on most churned accounts (verified); a long, unworked disengagement runway is the clearest preventable signal. The owner-vs-org gap matters too: org-heavy/owner-light means support was carrying a CSM-absent account into churn. (Keep to 2-3 windowed columns: the churned cohort × many windowed columns can time out.)

**B. Feature-request blockers: what missing capability blocked renewal.** Mine `issues`/`synopsis` for capability gaps (e.g. "granular progress tracking", "report attachments", "translation/localization missing", "compliance reporting API/data gaps"), and optionally a `semantic_search` `Feature requests` topic pass scoped to the churned account_ids. These carry lost-logo evidence; route them to product as churn-attributed gaps.

**C. Destination: where did they go?** For each churned account, capture the *destination*: a competitor, an in-house build, a consolidation onto another platform, or simply sunset. The `issues`/`synopsis` often name it ("Competitive replacement by <competitor>", "leadership-approved migration to <competitor>", "consolidation onto <platform>"). For confirmation + the switch reasoning, `staircase_analyze_account(id, "This account churned. What is their destination: a competitor, in-house, or consolidation? Which one, what will they use instead, and why? Cite evidence.")` (verified: returns the destination, e.g. "moved to <competitor>", with reasons + evidence ids). Destination is core churn context: it drives competitive intel, win-back framing, and product positioning. Tally destinations across the cohort (which competitors are taking our logos).

## Step 3: The rising-themes report (leading indicators)
```
entity: parent_topic
columns: parent_topic.id, parent_topic.accounts_count, parent_topic.negative_sentiment,
  parent_topic.current_period_volume, parent_topic.previous_period_volume,
  parent_topic.absolute_growth_percentage
filter: negative_sentiment > 0
sort: absolute_growth_percentage descending
```
Rank themes by growth% AND negative volume (a theme that doubled off a tiny base matters less than one up 30% on a large base). These are the churn drivers forming *now* in the accounts you still have. Cross-reference the top rising themes against this quarter's churn reasons; where they overlap, that's the systemic driver to get ahead of.

> Org note: `parent_topic` includes org-specific topics alongside the standard parents (Support & issues, Risk & dissatisfaction, Commercial & contracts, Competition, Feature requests, etc.). Focus on the churn-relevant parents; note that internal/product topics may appear if the org is itself a vendor instance.

## Step 4 (optional): Evidence + a live at-risk cross-check
- For a decisive churn theme, `semantic_search` (topics+semantic, the matching `parent_topic`) to pull representative evidence quotes for the readout.
- To connect retrospective to action, run one `customer` report for still-active accounts carrying the same signal (e.g. `risk.risk_level >= 4` AND low health): "here are the accounts showing the pattern that just cost us X."

## Step 5: Produce the review
```
# Churn Review: <scope> · <quarter> (<date>)

**Accounts churned:** <count> · **Revenue lost:** <sum, confirm in CRM> · **By tier:** <n per tier>
**Top decisive reason:** <theme> (<n> accounts, <$>) · **Fastest-rising risk theme:** <theme> (+<growth>%)

## Headline
<3-4 sentences: how much churned, the dominant decisive reason, the one rising theme most worth
preventing, and the single systemic change that would protect the most revenue.>

## What we lost
| Account | Churned | Revenue | Tier | Decisive reason | Destination | Preventable? |
|---------|---------|---------|------|-----------------|-------------|--------------|
| Acme Corp | YYYY-MM-DD | $X | <tier> | Product reliability + missing localization | A competitor | Partly |

## Where they went (destination tally)
<Competitors / in-house / consolidation taking our logos, counted. e.g. Competitor A xN, Competitor B xN, platform consolidation xN, in-house xN, sunset xN. Competitive intel + win-back targets.>

## Why: churn themes
### <Theme>: <n> accounts · <$ lost>
<2-3 sentences from the synopses. Decisive vs contributing. Representative account(s).>

## Unforced errors (preventable)
<The churn we could have stopped. Group by failure mode with counts: went dark (0 outreach on the runway),
late/transactional renewal motion, no EBR/save plan, self-inflicted change risk, slow support. Name accounts.
This is the section that changes behavior.>

## Feature-request blockers
| Missing capability | Accounts it cost | Route to |
|--------------------|------------------|----------|
| Granular progress tracking | Globex, … | Product |

## What's rising (leading indicators)
| Theme | Accounts | Neg items | Volume Δ | Growth % | Overlaps churn? |
|-------|----------|-----------|----------|----------|-----------------|
| Escalation | N | N | a → b | +X% | yes |

## Get ahead of it
<Systemic plays ranked by revenue protected. Tie each to a rising theme + the churn it mirrors.
Where useful, name the still-active accounts showing the pattern.>

---
## Sources
- Staircase churn analyst via `staircase_run_report` (churned accounts: date, revenue, tier, issues, synopsis)
- Staircase `parent_topic` trend report (rising negative themes)
- Staircase `staircase_semantic_search` (theme evidence, where run)
```

**Format adaptation:** Cowork leads with the headline card + the lost-revenue and rising-themes tables, churn themes as cards. Code prints markdown + optional `churn-review-<quarter>.md`. No CRM writes.

## Edge cases
| Situation | What to do |
|-----------|------------|
| No churned accounts in the window | Good news: report it, and still run the rising-themes half as pure prevention. |
| `revenue` unpopulated on churned accounts | Report the count and reasons; note revenue-lost needs the CRM figure. |
| A churn synopsis blames a non-recoverable exit (M&A, budget cut) | Mark it not-preventable; don't inflate the preventable-churn number. Leaders act on preventable. |
| `parent_topic` growth spikes off a tiny base | De-emphasize; a large jump on a meaningful base (dozens of items) matters, a +200% on 1→3 does not. Weight by absolute negative volume. |
| User wants only the retrospective (no prevention half) | Run Steps 1-2 only; note the leading-indicator half is available. |
| Rising theme is an internal/product topic (vendor instance) | Note it; focus the review on customer-facing churn themes. |
