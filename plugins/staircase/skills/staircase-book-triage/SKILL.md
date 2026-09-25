---
name: staircase-book-triage
description: "Builds the CSM's Monday-morning cockpit. One owner-scoped report becomes one ranked \"what needs me this week\" action list across every motion (silent risk, blindsided risk, unspoken renewal risk, fragile single-threaded saves, cadence breaks, and in-motion expansion plays), each row an account plus the one next move. Report-first and deterministic: a single base pull, every lens a client-side filter over it. Triggers on \"what needs me this week\", \"my book\", \"where should I focus\", \"triage my accounts\", \"my cockpit\", \"what should I work on\", \"Monday\", \"my at-risk accounts\", \"my expansion plays\"."
user_type: ic
allowed-tools: mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Book Triage (CSM cockpit)

A CSM opens Monday with a full book and three hours. This skill turns the whole book into one ranked "do this first" list: not a health dashboard, an action queue. It reads every motion at once (risk that's loud, risk that's silent, renewals with a clock, coverage that's one-deep, accounts gone quiet, expansion that's heating) and hands back the few accounts that actually need the CSM this week, each with the one next move.

**The architecture (why it's cheap):** ONE owner-scoped report pulls the ~14 signal columns for the whole book; every lens below is a **client-side filter over that single pull**. No per-account calls to build the list; those are reserved for the drill on the few accounts the CSM picks.

**This is the single-book lens.** For the portfolio/leader view use `../staircase-risk-radar/`; for one account's deep read use `../staircase-account-deep-dive/` or `../staircase-risk-check/`; to plan renewals specifically use `../staircase-renewal-watchlist/`. **A manager prepping for a 1:1 with a teammate** (personal effort/overwhelmed test + this same book, from the manager's chair) should use `../staircase-1on1-prep/` instead. It reuses this skill's 7-motion table by reference rather than duplicating it.

## Foundation references (read BEFORE composing any query)
- `../staircase-mcp-expert/` + `../staircase-mcp-expert/references/advanced-report-patterns.md`: the report engine, the argument system, owner scoping, field ids, and the reliability rules in `../staircase-mcp-expert/references/anti-patterns.md`.
- `../staircase-app-design/`: the interactive-cockpit standard (see the visual section).
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **User profile (if present):** `~/.staircase-mcp/user-profile.md`, the CSM's identity / owner scope.

## Scope (decide first)
- **Use the resolved book-owner field.** `customer.owner` is not always the CSM; on some orgs it holds a different role and the real book lives on another field. Read `scope.book_owner_field` from `~/.staircase-mcp/user-profile.md`; if absent, run the foundation's first-call contract (`../staircase-mcp-expert/SKILL.md` step 0, recipe `scope.membership`), which computes it and asks only when ambiguous. Use that field for all scoping below.
- **Self (the default):** `customer.<book_owner_field> In [current_user_id]` (or `Equal <id>` for a custom Reference field). `current_user_id` comes from `report_metadata` and is exact. This is how the CSM running the skill scopes to their own book.
- **A named CSM** (a manager looking at one rep, or when the profile names someone): `customer.<book_owner_field>.full_name In ["<name>"]` in `run_report`. A bare name on the Reference field itself errors; go through the `.full_name` leaf, or use the person's `user.id`.
- **Portable fields only.** Never hardcode a specific `_c` field id. The confirmed book-owner field is a runtime parameter, discovered per org, not baked into this skill.

## The base pull (one report, all lenses)
```
entity: customer   filter: status = Active AND <book_owner_field> In [current_user_id]
columns: customer.id, customer.revenue_converted, customer.risk.risk_level,
  customer.buckets.health, customer.buckets.engagement.score, customer.buckets.sentiment.score,
  customer.renewal_date, customer.last_engagement, customer.next_qbr_date,
  customer.relationship_score.stakeholders_count, customer.relationship_score.multi_threaded,
  customer.expansion.readiness_level, customer.expansion.momentum_indicator
sort: customer.revenue_converted desc
```
A typical CSM book (under ~100 accounts) returns in one lean call. Everything below is computed from these columns, with no extra queries to build the list. (Validated internally on a real CSM book: a sizable share had a fired risk, and every lens populated.)

## The lenses (each a filter over the base pull)
Compute all, then dedupe into one ranked list (an account can fire several lenses; carry its dominant reason). `today` = run date.

| Lens | Filter (client-side over the base pull) | The one next move |
|---|---|---|
| **Churn** (already leaving) | a `churn` **lifecycle event** has fired (see churn detection below) | Two tiers: **confirmed** (churn analysis states a non-renewal/termination outcome) → manage the closure, capture the reason, feed the churn retrospective; **signal** (event fired, outcome unconfirmed/pending) → verify before investing, it may still be saveable. Churn outranks every other motion. |
| **Unspoken renewal risk** (the clock) | `renewal_date` within ~90d AND (risk fired ∨ silent-decline ∨ health Low) | Get ahead of the renewal: name the blocker, book the working session, don't let it ride on email. |
| **Silent risk** (the quiet slide) | risk **empty** AND health Low AND engagement Low (corroborated; a lone health=Low is often missing data) | Proactive save before it flags: re-engage, diagnose, land one quick win. |
| **Blindsided** (score hasn't caught it) | risk fired AND health High/Average | Believe the risk over the score; open the account and find what the health metric is missing. |
| **Fragile save** (coverage-critical) | risk fired AND `multi_threaded = false` (single-threaded) | Multi-thread now. One contact carrying a churn risk is one departure from lost. |
| **Cadence break** (gone quiet) | `last_engagement` older than ~60d (no recent touch) | Re-open the relationship with a value reason, not a check-in. |
| **Expansion in-motion** (advance the play) | `expansion.readiness_level >= 4` AND `momentum_indicator = Heating` AND not silent-risk | Advance the known opportunity: the next concrete step toward the upsell (this is a tracked deal, not a discovery). |

Notes: `multi_threaded` is column-only (filter it client-side). `next_qbr_date` is unpopulated in many orgs (validated internally: nearly empty on a real book), so prefer `last_engagement` staleness for cadence, and treat a null QBR as a soft signal only. Expansion trend/readiness fields degrade gracefully where an org hasn't enabled them.

### Churn detection (deterministic: do NOT parse text for this)
The **`churn` lifecycle event** is the reliable churn signal, and it fires on still-**Active** accounts (before status flips to Churned). Detect it with a supplementary EXISTS query over the base cohort (`lifecycle_event` is also a root report entity if you need the event rows themselves):
```
{"field":{"rootEntityPath":"customer","childEntity":"lifecycle_event","referenceField":"lifecycle_event.customer",
  "aggregation":"EXISTS","condition":{"operator":"And","conditions":[
  {"field":{"id":"lifecycle_event.type"},"operator":"Equal","value":"churn"}]}},"operator":"Equal","value":true}
```
Then read `customer.churn.synopsis` (populated on Active accounts too) to split the two tiers. The synopsis **states the outcome**: "churned / non-renewal / lost $X" (confirmed), "outcome is pending" (signal), or even "ultimately renewed / retained" (a resolved event, NOT churn; leave it in its normal motion). Validated internally on a real book: the synopsis split the fired events into confirmed losses, unresolved signals, and a few that had actually renewed. **This replaces any summary-text heuristic.** The event + synopsis are deterministic and the synopsis carries the resolution the risk columns cannot.

## Prioritize into the "this week" list
Rank the deduped set by **urgency x stakes x winnability**, lead with the top 3-5:
- **Urgency** = renewal proximity + how loud the signal is (past-due renewal or a risk-5 with a near date dominates; a silent-risk with a far renewal is important but not this-week-urgent unless it's a whale).
- **Stakes** = `revenue_converted` (a silent-risk on the book's biggest account outranks a loud risk on a small one).
- **Winnability** = is there a live thread + an addressable blocker? Single-threaded + dark + far renewal = lower yield than an engaged account with a nameable fix.

Then the **drill** (only for the few the CSM picks): `analyze_account` / `account_info` for the driver, stakeholders, and the save/grow play; `fetch_evidence` for verbatims. Never per-account-drill the whole book to build the list.

## Output: the ranked week
```
# Book triage: <CSM> · week of <date>

**Book:** <n> accounts · **Need me this week:** <n> · **Renewing <=90d:** <n> · **Silent slides:** <n> · **Expansion heating:** <n>

## Do first (top 3-5)
1. <Account> · <$rev> · <the trigger in one line> -> **<the one next move>**

## By motion
### Renewals with a clock (<n>)
| Account | $ | Renews (days) | Risk | Health | Next move |

### Silent slides · no flag yet (<n>)
| Account | $ | Health/Eng | Last touch | Next move |
<lead with the biggest: a quietly-sliding whale is the highest-leverage catch a risk-list misses.>

### Blindsided · risk fired, score still green (<n>)
| Account | $ | Risk | Renews | Next move |

### Fragile · single-threaded + risk (<n>)
| Account | $ | Stakeholders | Next move (multi-thread) |

### Gone quiet · cadence break (<n>)
| Account | $ | Days since touch | Next move |

### Expansion heating · advance the play (<n>)
| Account | $ | Readiness / momentum | Next move |

---
## Sources
- Staircase `staircase_run_report` (one owner-scoped base pull; all lenses derived client-side)
- Staircase `staircase_analyze_account` (only on the accounts drilled)
```

**Format adaptation:** inside Claude, render the interactive cockpit (below). In Cowork, lead with the "Do first" card + the by-motion tables. In Code, print markdown + optional `book-triage-<date>.md`. No CRM writes.

## Interactive cockpit (the flagship output inside Claude)
When rendering inside Claude (`show_widget`; call `read_me` first), build the CSM cockpit, the personal sibling of the leader Risk Radar, with **three levels of progressive disclosure**:
1. **Row (free):** each account tagged with its dominant motion (churn chip first, in red; churn rows carry a `lost`/`signal` tier tag); sortable (revenue / days-to-renewal / risk / last-touch), searchable, motion-filter chips (one per motion incl. **Churn**). KPI row on top (need-me count, churn confirmed/signal, renewing <=90d, expansion heating).
2. **Inline expandable summary (click a row):** the row expands **in place** (accordion; click again to collapse), showing the stored `customer.summary` for instant context, with no round-trip and no jump to the top (review, act, move to the next). This is the layer that catches what the signals alone miss: the summary/synopsis routinely reveals a *confirmed non-renewal* that the risk/renewal columns read only as "at risk", flipping the next move from "save" to "manage closure". Never a top-anchored panel (`position:fixed` is banned and it loses the user's place); insert the detail row after the clicked row.
3. **Live deep-dive (button -> `sendPrompt`):** the full fresh MCP read (drivers + evidence, coverage/economic buyer, last 90 days, the save/grow play; for churn rows the prompt asks whether it's confirmed-lost or still saveable). The dynamic-MCP bridge: fetched on demand, always current.

**Cost discipline for the summary layer (measured):** `customer.summary` is a real multi-paragraph brief (~360 tokens each), so embedding ALL of them for a 90-account book is ~34K tokens, too heavy. Embed the **first paragraph only** (split on the blank line, ~330 chars); it carries the decisive headline in practice, at ~1/5 the cost (~6K tokens for the need-me set). Pull it in a *second* report scoped to the cockpit accounts (`customer.id In [...]`) so the lean base pull stays fast, then trim client-side before embedding. The full summary and everything beyond it come from the live deep-dive.

Design rules (from `../staircase-app-design/` + the `visualize` system): dark-mode-safe CSS variables, weights 400/500, sentence case, Tabler outline icons, no `position: fixed`, render all rows. Reference template: `../staircase-risk-radar/experiences/monday-risk-radar.widget.html` (same scaffold; swap the segment/owner rollups for motion chips, add the summary block to the detail panel).

## Edge cases
| Situation | What to do |
|-----------|------------|
| Book is quiet (few fire any lens) | Good news. Say so, and surface the expansion-heating plays as the week's offense. |
| `current_user_id` owns no accounts | The caller isn't a CSM with a book (admin/exec). Ask whose book, then use `generate_report` with the name. |
| Same account fires 3+ lenses | Dedupe to one row with the dominant reason; note the others in its drill, don't list it six times. |
| `next_qbr_date` empty across the book | Org may not populate it. Rely on `last_engagement` staleness for cadence; don't over-report "no QBR". |
| Expansion fields empty | Org hasn't enabled the expansion analyst. Drop that lens, say so, keep the risk/renewal/coverage motions. |
| A silent-risk account has health=Low but High engagement + recent touch | Not a real slide (a scoring gap). Require corroboration (Low health AND Low engagement), don't inflate the silent set. |

## Reliability guardrails (on top of the foundation's rules in anti-patterns.md)
- **One base pull, client-side lenses:** don't fan out per-account to build the list; that's slow and rate-limited. Drill only the few the CSM picks.
- **Validate the base pull narrowed** to the owner (owner scoping silently returning the whole org is the dangerous failure).
- **Silent risk needs corroboration** (Low health AND Low engagement / stale / negative), never a lone health signal.
- **`multi_threaded` is column-only:** filter client-side.
- **Date vs DateTime:** `renewal_date` (Date) scalar/`InRange`; `last_engagement` (DateTime) needs `InRange "[start,end]"` if you filter it (or pull it and compute staleness client-side).
- **Portability:** standard `customer.*` only, discovered via `report_metadata`; no `_c` fields.
