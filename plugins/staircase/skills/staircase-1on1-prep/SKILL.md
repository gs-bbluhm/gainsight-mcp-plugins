---
name: staircase-1on1-prep
description: "Builds a manager's 1:1 prep for one teammate: their book (health/risk/renewal), personal effort against the overwhelmed test, expansion pipeline, and talking points, from live Staircase MCP data. The artifact a manager brings into the room. Triggers on \"1:1 prep for <name>\", \"prep me for my 1:1 with <name>\", \"how is <name> doing\", \"<name>'s book\", \"coach <name>\"."
user_type: exec
allowed-tools: Bash, Write, mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase 1:1 Prep (manager / one teammate)

A manager walks into a 1:1 wanting one thing: "here's this person's book, here's how they're actually doing, here's what to raise." This skill answers that for exactly one teammate, curated for the *manager's* perspective (is this person overwhelmed, does their book need help, what do I bring up), not the IC's own working view. It reuses `../staircase-book-triage/`'s validated 7-motion account table (by reference, scoped to one person's book) rather than re-deriving it, and adds the personal-effort/overwhelmed layer that skill doesn't carry.

**This is the single-teammate lens, from a manager's chair.** For the whole team at once use `../staircase-team-manager/`; for that person's *own* working view of their book (the IC's Monday cockpit) use `../staircase-book-triage/` with scope set to them; for one account's full deep read use `../staircase-account-deep-dive/` or `../staircase-risk-check/`; to zoom out to portfolio risk use `../staircase-risk-radar/`.

## Foundation references (read BEFORE composing any query)
- `../staircase-mcp-expert/SKILL.md` step 0: the resolved book-owner field; do not assume `Owner`.
- `../staircase-mcp-expert/references/report-recipes.md`: `book.context`, `team.rollup`, and `lifecycle.evidence`; `advanced-report-patterns.md` for the argument system and lifecycle events (§1, §3).
- `../staircase-book-triage/SKILL.md`: the 7-motion lens table (churn / unspoken-renewal-risk / silent-risk / blindsided / fragile-save / cadence-break / expansion-in-motion) and the deterministic churn-lifecycle-event detection. This skill applies the SAME table, scoped to one person's book, not a rewrite of it.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.

## Scope (decide first)
1. **Use the resolved book-owner field.** Read `scope.book_owner_field` from `~/.staircase-mcp/user-profile.md`; if absent, run the foundation's first-call contract (`scope.membership`).
2. **Resolve the person.** If arriving via `staircase-team-manager`'s `sendPrompt` hand-off, the team baseline (`overwhelmed_threshold_hrs`, this person's percentile) is already in the prompt text; use it directly, don't re-pull the whole team. If invoked standalone, resolve the name with a direct `run_report` lookup on `user.full_name Equal "<name>"` (`generate_report` is a fallback).

## The pulls (scoped to one person, not the whole team)
```
Personal effort, entity: user, filter: user.full_name Equal "<name>"
  columns: same stat set as staircase-team-manager's R1 (effort, email/event/ticket
  stats with dateRange+filter.customer). One row.

Book, entity: customer,
  filter: status Active AND customer.<book_owner_field>.full_name Equal "<name>"
  columns: same set as staircase-team-manager's R2 (tier, revenue, risk, health,
  renewal_date, last_engagement, last_reach_out, email.customer_last_sent ("Last
  email from them"), event.last_event ("Last meeting"), stakeholders_count,
  multi_threaded, team/owner effort hours, time_range_revenue, ticket.{submitted_count,
  comments_count}, expansion readiness/momentum)

Expansion, entity: expansion_opportunity,
  filter: customer.<book_owner_field>.full_name Equal "<name>"
  columns: same set as staircase-team-manager's R3
```
If you already have a `staircase-team-manager` run's saved CSVs, just re-run `${CLAUDE_PLUGIN_ROOT}/_shared/scripts/team_engine.py` with `--person "<name>"` against them instead of re-pulling: the `person_view` block extracts this person's slice from the already-computed roster result. Otherwise pull fresh with the person-scoped filters above, save each CSV, and run the engine on just this one row/book.

## What to build the artifact from
1. **The overwhelmed test, shown transparently**, with both conditions and real numbers rather than a hidden verdict: *"Effort 42h (team p90=38h → HIGH LOAD) AND response 31h (>24h → DEGRADED) → OVERWHELMED."* If it doesn't clear both, say so plainly (busy is not the same as overwhelmed).
2. **The bandwidth read, separately** (renamed from "coverage-gap": that name read as "their accounts are poorly covered"; the actual test is about the *person's* workload, not account coverage). Is this person's book exposed (at-risk + neglected-high-value + stale ≥1) while their *personal* effort sits low among book-carriers? This is a different finding from overwhelmed and can coexist with "not overwhelmed": a healthy-looking workload with an exposed, under-touched book is itself the coaching moment. If they carry zero accounts under the book-owner field for this cohort, say that plainly rather than implying a capacity judgment either way.
3. **The book, via `staircase-book-triage`'s 7 motions**, scoped to this person: churn (lifecycle-event detected, confirmed vs. signal), unspoken renewal risk, silent risk, blindsided, fragile (single-threaded) saves, cadence breaks, expansion-in-motion. Same deterministic churn detection (EXISTS `lifecycle_event.type = "churn"` + `churn.synopsis` for confirmed-vs-signal). Do not re-derive from summary text. For the fragile/single-threaded motion, show `Stakeholders count` alongside `Last reach-out` / `Last email from them` / `Last meeting`: an account can carry several named stakeholders and still be genuinely single-threaded if only one replies; the extra columns make that legible instead of looking contradictory.
4. **Expansion pipeline:** count, category/momentum mix, multi-opportunity accounts. Never a dollar total (`opportunity_value` is prose).
5. **Talking points:** 3-5 read-only bullets a manager brings into the room: open with a real win if one exists, surface the at-risk account before they do, ask about capacity if the bandwidth read fired, name the renewal(s) in the next 90 days by name. Text only, never a button: this is a human conversation, not a write action.

## Output: the 1:1 brief
```
# 1:1 Prep: <name> · <date>

**Book:** <n> accounts · <$> · **At-risk:** <n> (<$>) · **Renewing ≤90d:** <n>

## Read
<the one interpreted paragraph: book size/exposure, the overwhelmed verdict with
its numbers, the bandwidth verdict if it fired, framed as what this means for
the conversation, not a report generator filling slots.>

## Talking points
1-5 read-only bullets, ordered: win first, then the thing they need to hear,
then the ask.

## By motion (scoped to this person's book)
### Renewals with a clock / Silent slides / Blindsided / Fragile / Gone quiet / Expansion heating
<same tables as staircase-book-triage, one section per motion that fired>

## Expansion pipeline
<count, category/momentum mix, multi-opportunity accounts>

---
## Sources
- Staircase `staircase_run_report` (person-scoped effort + book + expansion)
- Bundled `team_engine.py --person` (the crunching)
- `staircase_analyze_account` (only on the accounts drilled)
```
**Format adaptation:** Cowork leads with the Read + talking points card, then by-motion tables. Code prints markdown + optional `1on1-prep-<name>-<date>.md`, and a manager may want this one open *during* the actual 1:1; see the standalone widget below. No CRM/Gainsight writes.

## Interactive brief (the flagship output inside Claude)
Two artifacts, per `../staircase-app-design/`:
- `experiences/1on1-prep.widget.html`, chat-embedded (`show_widget`) and `sendPrompt`-enabled: the overwhelmed/bandwidth callout up top, by-motion tables below with inline accordion (click an account → expand in place, first-paragraph summary, never a top panel), a live-deep-dive button per account routing to `../staircase-account-deep-dive/` or `../staircase-risk-check/`, and a "zoom out to the team" button routing back to `../staircase-team-manager/`.
- `experiences/1on1-prep.html`: a full standalone document, no `sendPrompt`, offline-shippable, because unlike the roster view, a manager plausibly wants this one open on a second screen *during* the actual 1:1.

Design rules from `../staircase-app-design/`: dark-mode-safe CSS vars, weights 400/500, sentence case, Tabler outline icons, no `position:fixed`, render all rows.

## Edge cases
| Situation | What to do |
|-----------|------------|
| Person has no book under the confirmed field | Say so; they may only be staffed on a different role field (per-product CSM roles, a TAM, or another specialist role); check those too before concluding "no book" |
| Arriving without a `staircase-team-manager` baseline | Computing the overwhelmed threshold from this person's own history is not possible solo: either pull the team quickly for the p90 baseline, or present personal stats without the percentile framing and say why |
| Book is quiet (no motion fires) | Good news: say so, lead the talking points with the expansion-heating plays if any, otherwise with a genuine "nothing needs raising" |
| Same account fires multiple motions | Dedupe to the dominant reason, per `staircase-book-triage`'s rule |

## Reliability guardrails (on top of the foundation's rules in anti-patterns.md)
- **Never default to `Owner`** as this person's book field. Use the resolved field (anti-patterns.md R7b).
- **Filter a Reference role field through its `.full_name` leaf** (`customer.<book_owner_field>.full_name Equal "<name>"`), never the bare Reference field compared to a name.
- **Talking points are read-only text, never buttons.** This skill never writes to Gainsight/Staircase and never sends anything on the manager's behalf.
- **Portability:** the book-owner field is a runtime parameter; no `_c` id hardcoded.
