---
name: staircase-team-manager
description: "The CS leader's across-team roster. Rolls up every teammate who holds a book (workload, book risk exposure, bandwidth to help, renewals, expansion pipeline) from live Staircase MCP data, with no CSV export. Answers \"is my team covering the book, and who needs me?\" Report-first and deterministic: one roster pull, one book pull, one expansion pull, with every lens computed by a bundled engine script rather than eyeballed. Triggers on \"my team\", \"team roster\", \"team coverage\", \"team workload\", \"is my team covering the book\", \"who's overwhelmed on my team\", \"team effort\"."
user_type: exec
allowed-tools: Bash, Write, mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Team Manager (leader / across-team)

A manager does not need ten dashboards. They need one roster: who holds a book, how big it is, how exposed it is, who's stretched, and what's coming up, so they know who needs them this week. This skill builds that roster live from the Staircase MCP (`user`, `customer`, `expansion_opportunity`), ports a workload/coverage methodology validated internally (the overwhelmed test, the anti-libel under-utilization read, book rollup), and hands the crunching to a bundled script so the model spends its intelligence on interpretation, not re-deriving percentiles every run.

**This is the across-team lens.** To prep for a 1:1 with one teammate, use `../staircase-1on1-prep/`. For portfolio risk independent of who's carrying it, use `../staircase-risk-radar/`.

## Foundation references (read BEFORE composing any query)
- `../staircase-mcp-expert/SKILL.md` step 0 (the first-call contract): resolves the book-owner field per org. **`customer.owner` is not always the CSM**; use the resolved field for everything below.
- `../staircase-mcp-expert/references/report-recipes.md`: `team.rollup` and `scope.membership`.
- `../staircase-mcp-expert/references/advanced-report-patterns.md`: the argument system (§1), rollups with a discovered role field as the `referenceField` (§7), and teams via `user.manager` (§9). Prefer `In` for multi-value filters (anti-patterns.md R6).
- `../staircase-app-design/`: the interactive-cockpit standard (see the visual section below).
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **User profile (if present):** `~/.staircase-mcp/user-profile.md` carries the resolved book-owner field (`scope.book_owner_field`).

## Scope (decide first)
1. **Use the resolved book-owner field.** Read `scope.book_owner_field` from the profile; if absent, run the foundation's first-call contract (`scope.membership`), which computes it and asks only when a person sits in two role fields. Never assume `Owner`.
2. **Resolve the team.** Try `user.manager.full_name Equal "<manager's name>"` first (a single `Equal`: clean, confirmed working, no fan-out). If the org's `Manager` field is sparse/unpopulated, fall back to an explicit roster the manager names, scoped with `user.full_name In [...]` (also confirmed working in one call).
3. **Portable fields only.** The confirmed book-owner field is a runtime parameter (from step 1); never hardcode a specific `_c` id.

## The three base pulls
```
R1 (roster + personal effort), entity: user
  filter: user.manager.full_name Equal "<manager>"  (or user.full_name In [<roster full names>])
  columns: First name, Last name, Title, Manager,
    effort.effort_hours, email_stats.{sent_count,received_count,response_time_hours,
    positive_received_count,negative_received_count,neutral_received_count},
    event_stats.{attended_count,total_hours}, ticket_stats.assigned_count
    (each stat column takes dateRange + filter.customer; default [Past3Months],
    state the window once. Occasionally times out on ~8 stacked columns for a
    roster; retry once, unchanged config, before concluding it's broken.)

R2 (book + account signals), entity: customer
  filter: status Equal Active AND customer.<book_owner_field>.full_name In [<roster full names>]
  columns: id, <book_owner_field>, owner, tier.name, revenue, risk.risk_level,
    buckets.health_score, renewal_date, last_engagement, last_reach_out,
    email.customer_last_sent (label "Last email from them"), event.last_event
    (label "Last meeting"), relationship_score.{stakeholders_count, multi_threaded},
    effort.{team_effort_hours, team_effort_cost, team_effort_time_range_revenue,
    owner_effort_hours}, event.count, ticket.{submitted_count, comments_count},
    expansion.{readiness_level, momentum_indicator}
  (last_reach_out / event.last_event / email.customer_last_sent / ticket.*
  all require a `productId` argument; pass `[]` for "all products", same
  convention as `commType: []`. See field-catalog.md §6: ticket count/comments
  ARE available here, contrary to the older "use the CRM" note, which was
  about ticket status-of-record only.)

R3 (expansion pipeline, optional), entity: expansion_opportunity
  filter: customer.<book_owner_field>.full_name In [<roster full names>]
  columns: customer, customer.<book_owner_field>, offering, category, momentum_state
  (opportunity_value is a STRING, so never sum it; count + momentum/category mix only)
```
All three are `run_report` labels chosen to match `../../_shared/scripts/team_engine.py`'s expected column contract exactly (see its docstring). Save each result's CSV, then run:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/_shared/scripts/team_engine.py" \
  --roster r1.csv --book r2.csv --expansion r3.csv \
  --role-col "<book-owner field label>" --out /tmp/team_manager.json
```
Read the JSON. It is the single source of truth for everything below; do not re-derive percentiles, the overwhelmed test, or book rollups by eyeballing rows.

## What the engine computes (read `../staircase-mcp-expert/references/analysis-methodology.md`'s pitfalls before interpreting)
| Block | Answers |
|---|---|
| `team_pulse` | Effort percentiles, the **overwhelmed** flag (effort ≥ p90 **AND** response>24h **OR** negative-sentiment-ratio>15%, never raw hours alone), per-manager rollup |
| `book.rollup` | Per-person book: accounts, ARR, team hours, at-risk/stale/neglected-high-value counts, **renewals in the next 90 days (a real per-person count; never hardcode 0)**, avg health, AM (`Owner`) engagement share (a *different* role than the CSM here; read it as cross-functional engagement, not coverage) |
| `account_flags` | Overspend (cost as % of **`Time frame revenue`**, not annual revenue), underspend-high-value, **at-risk-low-effort (uncapped: show the full list, not a top-N sample)**, stale-high-value, **renewals_90d (uncapped, sorted by soonest)**, single-threaded-at-risk. Every row carries `CSM` (the confirmed book-owner name) and `Tier`; never show an account row without who owns it. |
| `capacity_signals` (renamed from "under_utilization"/"coverage gap": the old name read as "these accounts are poorly covered"; the actual test is about the *person's* bandwidth, not account coverage) | `bandwidth_candidates`: bottom-40th-percentile personal effort **among book-carriers only** (never the whole roster) **AND** book exposure ≥1, each with a plain-language `reason` string carrying the real numbers. `not_a_book_carrier`: roster members who match zero accounts under the book-owner field in this pull. Informational: answers "why isn't `<name>` flagged either way" (they may simply not carry a book in this cohort's pull) without asserting a capacity judgment about them |
| `org_summary.by_tier` | Accounts, revenue, at-risk count, avg health broken out by Tier: the manager-level "by tier" cut across every account lens |
| `expansion` | Opportunity count, multi-opportunity-account count, category/momentum mix per person, never a dollar total |

Three interpretation rules (ported verbatim from the validated methodology): normalize before ranking (segment by book size: a pooled 30-account book and a focused 3-account book aren't comparable per-hour); owner/AM hours ≠ CSM coverage (judge coverage from the book rollup); low effort is only bad when the book is exposed.

**`Multi threaded` vs `Stakeholders count`:** these answer different questions and can legitimately disagree. An account can carry several named stakeholders and still be flagged single-threaded if only one of them actually replies (validated internally: an account with several stakeholders showed `Multi threaded=false`, with the last email FROM the customer over a month stale while `Last reach-out` from us was recent). Read `single_threaded_at_risk` rows alongside `Last reach-out` / `Last email from them` / `Last meeting` / `Ticket count` / `Ticket comments`, not `Stakeholders count` alone. The engine includes all of these so the disagreement is self-explanatory, not a bug to chase.

## Output: the roster readout
```
# Team Manager: <manager> · <date>

**Team:** <n> · **Book $:** <sum> · **At-risk $:** <sum> (<n> accts) ·
**Overwhelmed:** <n> · **Has bandwidth:** <n> · **Renewing ≤90d:** <n> · **Expansion heating:** <n>

## Headline
<3-4 sentences: who needs support, who's exposed but not personally overloaded
(the bandwidth distinction: book at risk while effort has room), where the
book-owner field's role diverges from the standard Owner (if the manager
hasn't seen that yet), the one thing to do first.>

## Team roster (sorted by book revenue-at-risk desc, tier shown per row)
| Team member | Status | Effort | Meetings / emails | Tier(s) | Accounts | Book $ | At-risk ($/n) | Renewals ≤90d |

## By tier
| Tier | Accounts | Revenue | At-risk | Avg health |

## At-risk + low effort (full list: every account clearing risk≥4, revenue>100K, hours<5)
| Account | CSM | Tier | Revenue | Risk | Health | Renewal date | Team hours |

## Renewing in the next 90 days (full list, sorted soonest-first)
| Account | CSM | Tier | Revenue | Renewal date | Days out | Risk | Health |

## Single-threaded + at-risk (with the detail that explains the flag)
| Account | CSM | Stakeholders | Last reach-out | Last email from them | Last meeting | Tickets (count/comments) |

## Bandwidth candidates (book at risk, personal effort has room; each row's reason spelled out)
## Overwhelmed (high load + a degradation signal)
## Expansion pipeline by person (count, momentum mix, no dollar total)
---
## Sources
- Staircase `staircase_run_report` (roster + book + expansion, three pulls)
- Bundled `team_engine.py` (the crunching)
```
**Format adaptation:** Cowork leads with the headline card + roster table. Code prints markdown + optional `team-manager-<date>.md`. No CRM/Gainsight writes.

## Interactive cockpit (the flagship output inside Claude)
`show_widget` (call `read_me` first), rows = people, same scaffold as `../staircase-risk-radar/experiences/monday-risk-radar.widget.html`. The SKILL does the join described in the widget's header comment: `team_pulse.all_members` + `book.rollup` + `capacity_signals` + `expansion`, PLUS `person_accounts()` per person for real account-level detail; never leave a person's `top` array empty when `book.rollup` shows `at_risk>0` or `renewals_90d>0` for them.
- **KPI row:** book $, at-risk $ + count, overwhelmed count, bandwidth-candidate count, renewals ≤90d, expansion-heating count.
- **View toggle:** Table (default) or **Workload & risk map**: an SVG quadrant scatter (x = effort percentile, y = share of book at-risk, bubble size = book ARR) that answers "who needs me" visually, without reading every row. This is the non-tabular view for a manager scanning a whole team at a glance.
- **Table column order** (from UX review): Team member, Status, Effort, Meetings / emails (attended meetings and sent emails from `team_pulse`, one combined column), Accounts, Book $, At-risk $, Renews ≤90d. Health is dropped from the table (it's still shown per-account in the accordion) because it wasn't pulling its weight as a roster-level column.
- **Chips:** per-status (Overwhelmed/Has bandwidth/Healthy), "renews <30d".
- **Table, sorted by book revenue-at-risk desc by default** (not alphabetical).
- **Level 2 (click a row or bubble → inline accordion):** `person_accounts()`'s `needs_attention` field: the FULL, UNCAPPED union of this person's at-risk accounts and accounts renewing within 90 days, each tagged with why it's included (`at_risk`, `renews_90d`, or both). Never cap this to a top-N sample (UX review found that capping it at 2-3 hid real at-risk accounts). A strict at-risk-AND-renews-soon intersection is too narrow to default to: the two conditions rarely overlap in practice, so a person can have a dozen at-risk accounts and an empty intersection; the union is what a 1:1/roster drill-down should show. Plus the `reason` string when they're a bandwidth candidate.
- **Level 3 (`sendPrompt`):** *"Full 1:1 prep on `<name>`"* → routes to `staircase-1on1-prep`, **carrying this run's `overwhelmed_threshold_hrs` and this person's percentile in the prompt text** so the 1:1 skill doesn't re-pull the whole team just for a baseline.
- **Footnote:** `capacity_signals.not_a_book_carrier` as a short informational line under the table (not a status, not a warning), so "why doesn't `<name>` show up flagged either way" always has a visible answer.

Design rules from `../staircase-app-design/`: dark-mode-safe CSS vars, weights 400/500, sentence case, Tabler outline icons, no `position:fixed`, render all rows.

## Edge cases
| Situation | What to do |
|-----------|------------|
| `Manager` field sparse/unpopulated | Ask the manager to name their team explicitly; scope with `user.full_name In [...]` instead |
| Book-owner field surfaces multiple valid candidates (e.g. Owner AND a custom `<book_owner_field>` both score well) | Present both, ask which is the CSM/book-owner dimension for THIS ask; never auto-pick the higher-scoring one |
| A role value is a pooled team label (e.g. a scaled-team queue name), not a person | Exclude from personal-effort/overwhelmed analysis (no matching `user` row); report as its own aggregate coverage bucket |
| Roster-wide stat pull times out | Retry once, unchanged config (non-determinism, not a hard column-count ceiling) |
| `expansion_opportunity` sparse or absent | Drop that section, say so; the roster/effort/risk lenses stand alone |
| A roster member has real personal effort but 0 accounts under the book-owner field in this pull | Surface via `not_a_book_carrier`, not silence; do not guess at a capacity verdict for them |
| `renewal_date` missing on some rows | Exclude those rows from `renewals_90d` (they're not "not renewing," just unparseable); don't report a suspiciously-low renewal count without checking for this first |

## Reliability guardrails (on top of the foundation's rules in anti-patterns.md)
- **Never default to `Owner` as the book dimension.** Use the resolved field (anti-patterns.md R7b).
- **Prefer `In`** for any "these N named people/values" filter: one condition, confirmed clean on plain and nested fields (`Or` also works in report filters).
- **Filter a Reference role field through its `.full_name` leaf** (`customer.<book_owner_field>.full_name In [<names>]`), never the bare Reference field compared to a name.
- **`effort.*` fields are column-only, not filterable.** Every effort-based flag is computed in the engine, never as a report filter.
- **Portability:** the book-owner field is always a runtime `--role-col` parameter; no `_c` id in this skill's own text or queries.
