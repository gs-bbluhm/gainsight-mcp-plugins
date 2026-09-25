# staircase

A Claude plugin that turns the **Staircase AI MCP** into reliable, repeatable account and portfolio workflows. Built for CSMs, account managers, sales, and CS leaders who want Staircase's communication intelligence at their fingertips inside Claude Code and Claude Cowork.

This is the **solo Staircase plugin**: Staircase only, no Gainsight dependency. It reads, synthesizes, and produces artifacts (reports, briefs, draft emails). It does not write to a CRM.

## Prerequisite: connect the Staircase MCP

Every skill in this plugin calls the Staircase AI MCP, so connect it before anything else. Either:

- **Claude (web, desktop, Cowork):** add Staircase AI as a connector in your claude.ai connector settings and authorize it, or
- **Claude Code:** run `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`, then authenticate when prompted.

Running `staircase-setup` confirms the connection, so if anything is off you find out there.

## How to start

1. **Optionally run `staircase-setup` first.** It is a short welcome: it confirms the Staircase MCP connection, resolves which accounts are yours automatically, runs a short practice query, and caches a profile so every other skill can scope to "my accounts". About two minutes. Skipping it is fine; the foundation resolves your scope on the first call either way.
2. **Then use the skills below** by describing what you want ("catch me up on Acme", "show me my portfolio risk", "prep me for my meeting with Acme").

## Skills

Organized by `user_type`.

### Foundation (read by other skills; not usually called directly)

- **`staircase-mcp-expert`**: the canonical reference for the Staircase MCP: a first-call contract that resolves your scope and your org's custom setup, context-complete report recipes for core questions, the lifecycle-event evidence chain, and the analysis methodology.
- **`staircase-setup`**: optional onboarding: confirms the connection, resolves your scope automatically, runs a practice round, writes `~/.staircase-mcp/user-profile.md`.
- **`staircase-app-design`**: the read-only app-rendering foundation. Chrome, components, and content rules for in-chat experiences; read by any skill before rendering user-facing output.

### CSM (`user_type: ic`)

- **`staircase-book-triage`**: the CSM's Monday cockpit. One owner-scoped report becomes one ranked "what needs me this week" list across every motion (silent risk, blindsided, unspoken renewal risk, fragile single-threaded saves, cadence breaks, in-motion expansion), each row an account plus the one next move. Renders as an interactive, motion-filterable cockpit with click-through to a live per-account deep-dive.
- **`staircase-account-deep-dive`**: the richest single-account synthesis. "Catch me up" / general account context: status, dated developments, open threads, sentiment trend, next action.
- **`staircase-meeting-prep`**: pre-meeting brief: where you left off, both-sides commitments, risks, wins, who's who, talking points.
- **`staircase-risk-check`**: health and risk read with exact language and sources, trajectory, top actions.
- **`staircase-follow-up-draft`**: a ready-to-send follow-up email grounded in real interactions, with the sources to verify.
- **`staircase-account-handoff`**: onboarding brief for a CSM inheriting an account: stakeholders, goals, open commitments, red flags, first-30-days plan.

### Cross-account / portfolio (`user_type: exec`)

- **`staircase-risk-radar`**: the CS-leader portfolio risk view. Report-first: revenue at risk by segment/team (heatmap), urgency = risk x renewal timing, the driving factors -> recommended action, the blindsided watchlist, the systemic driver theme, and the coverage check.
- **`staircase-team-manager`**: the CS leader's across-team roster, live from the MCP (no CSV export). Rolls up every teammate who holds a book (workload, book risk exposure, bandwidth to help, renewals, expansion pipeline) using a bundled engine script (`_shared/scripts/team_engine.py`) that ports a validated team-effort methodology (the overwhelmed test, the anti-libel bandwidth read). Uses the book-owner field resolved per org; never assumes `Owner`.
- **`staircase-1on1-prep`**: a manager's 1:1 prep for one teammate: their book by risk motion (reusing `staircase-book-triage`'s 7-motion table), personal effort against the overwhelmed test, expansion pipeline, and read-only talking points. The sibling of `staircase-team-manager` for the single-teammate, manager's-chair view.
- **`staircase-renewal-watchlist`**: Renewal Command. A CSM priority planner (every renewal ranked by leverage, each with a defend / grow / both / manage-closure play) and a CS-leader risk-weighted forecast (the window rolled up by segment into likely-renew / at-risk / churn-flagged revenue). Churn-aware.
- **`staircase-churn-review`**: quarterly churn retrospective. What churned and why (synopses, reason clustering, lost revenue by tier) plus the rising negative themes that predict the next churns.
- **`staircase-voice-of-customer`**: cohort intelligence: what customers are saying, quantified. Report-first: a cohort-scoped topic profile (volume, negative rate, rising trend), drilled to the child-topic reasons (count>1), grounded in verbatim quotes with evidence. Works for any cohort (book / tier / team / at-risk / renewal window), the topic engine no CRM has.
- **`staircase-expansion-scout`**: expansion-analyst workbench. The whole book's expansion readiness (level, momentum, named opportunities, whitespace, ARR potential, timing) ranked into tracked next actions.

## Canonical references (read first)

- **`_shared/staircase-output-best-practices.md`**: the house style, query discipline, and output/export discipline every skill follows.
- **`skills/staircase-mcp-expert/`**: the MCP foundation (SKILL.md + `references/{report-recipes, field-catalog, advanced-report-patterns, query-patterns, anti-patterns, analyst-data-models, analysis-methodology}.md`).

## Prerequisites

- **Staircase AI MCP** connected and authenticated (see "Prerequisite: connect the Staircase MCP" above).
- Optional: a meeting-notes source (Notion, Zoom, Granola, Fireflies, Gong) for richer meeting prep; Gmail for drafting follow-ups.

## Naming and frontmatter

- All skills are prefixed `staircase-`.
- Every SKILL.md uses standard Claude Code frontmatter (`name`, `description`, optional `allowed-tools` and `disable-model-invocation`) plus a plugin-internal `user_type` (`foundation` | `ic` | `exec` | `experimental`). Claude Code ignores unknown keys, so `user_type` is safe.

## Known behavior (Staircase MCP): report-first

- **Lists/rankings/filters go through structured reports** (`run_report` by default, `generate_report` as a fallback), where **combined AND/OR criteria work**. The old "combined criteria / OR return empty" limit was the prose `query`/`ask` path only; don't decompose a filterable list into single-dimension prose queries.
- **Analyst outputs are structured columns**, not prose to scrape: expansion (readiness, momentum, opportunities, drivers, whitespace, ARR potential, timing, exec engagement), churn (date, issues, synopsis), handoff (strategic summary, objectives), risk (level, analysis). Read them directly; use `analyze_account` for evidence/quotes.
- **`revenue` and `renewal_date` are queryable and often populated.** Use them (CRM authoritative for the contracted figure/date). Seat counts, product-usage, and industry/segment filters still live in the CRM.
- **The `stakeholder` entity filters by account** for the roster (names/titles/roles); per-person *stance* still needs `analyze_account` (report tone defaults Neutral).
- **`staircase_list_communications`** resolves lifecycle events to their underlying emails and calls, with meeting issues and action items; pass a row's evidence id to `staircase_fetch_evidence` for verbatim text.
- **Topic reports currently return topic ids without names.** Don't present a bare id as a theme name.
- `staircase_analyze_account` uses `query`, not `question`.
- ~90 to 120 day communication window for narrative depth (not extendable); older history from the CRM.
- Cross-account capacity: the parallel per-account analysis cap (10 today) applies to `analyze_account` fan-out; reports return far more.
- Non-determinism: `analyze_account`/`query` can return empty then rich; retry, then re-phrase. Reports are deterministic.

## Relationship to the joint plugin

A separate `gainsight-cs` plugin pairs Staircase with the Gainsight CS MCP (CRM state + write paths). This solo plugin is for customers who use Staircase without Gainsight. The Staircase query mechanics are shared; the joint plugin adds Gainsight reads, write-backs, and approval gates that this plugin intentionally omits.
