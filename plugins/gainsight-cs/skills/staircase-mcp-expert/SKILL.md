---
name: staircase-mcp-expert
description: Foundation skill for the Staircase AI MCP. Catalogs queryable fields (standard + CRM-synced custom + events + insights + AI analyses), translates business-language asks into multi-step query plans, encodes the priority-weighting methodology, and warns about anti-patterns (OR not supported, combined filters fail, non-determinism, the 15-account parallel-analysis cap). Sibling skills read this before composing any non-trivial Staircase query.
user_type: foundation
allowed-tools: mcp__staircase-ai__ask, mcp__staircase-ai__fetch, mcp__staircase-ai__staircase_account_lookup, mcp__staircase-ai__staircase_analyze_account, mcp__staircase-ai__staircase_query, mcp__staircase-ai__staircase_fetch_evidence, mcp__staircase-ai__staircase_generate_report
---

# Staircase MCP Expert

## What this skill is for

The Staircase AI MCP is how every account-intelligence skill in this plugin reads customer signals — engagement, sentiment, risk, expansion, communications, named stakeholders, AI analyses. The tools work well, but the query surface is uneven: OR composition isn't supported, combined-criteria queries return empty, the MCP doesn't compute abstract scores, and there's a 15-account cap on parallel per-account analysis that's commonly misunderstood.

This skill is the canonical reference for sibling skills. Read it (or its references) before composing Staircase queries you haven't run recently in this session.

## When to invoke

**Direct invocation triggers:**
- "How do I query Staircase for X?"
- "What fields can I filter on?"
- "Which insights are queryable?"
- "Translate this business question into a Staircase query plan."
- "Rank my accounts by [criterion]."

**Sibling-skill reference triggers** (these skills MUST read this before querying):
- `gainsight-csm-book-pulse` — uses the priority weighting verbatim
- `gainsight-meeting-processor` — uses the analyst data models for context fan-out
- `gainsight-exec-renewal-radar` — uses tier-stratified scoring
- `gainsight-renewal-priority-planner` — uses composite + save-into-expansion bonus
- `gainsight-account-workspace` / `gainsight-account-handoff-onboarding` — uses per-account analyses
- Any `staircase-*` cross-account skill (pattern-hunter, at-risk-renewals, expansion-scout) — uses field catalog + anti-patterns

## Top patterns (the 5 things you'll do 80% of the time)

### 1. Single-criterion list query (consistently works)
Decompose any complex question into single-criterion `ask` queries. AND/OR composition fails — decompose first, intersect client-side.

```
"List my accounts where [single criterion]."
"Which of my accounts are flagged as [insight]?"
```

Full phrasing patterns + validated success rates in `references/query-patterns.md`.

### 2. Unified scoped fan-out query (book + flags in one call)
For CSM book-of-business work, pull the scoped list + insight booleans in one structured query — collapses 6 sequential queries into 1.

```
"List accounts where [team-member field] is [name]. For each account, include:
name, ARR, renewal date, health score, last engagement date, sentiment score,
risk level, expansion readiness, and boolean flags for Account Dark, No QBR,
No Reach Out, Account Personnel Changes, Single Threaded with Stakeholder."
```

The team-member field name is org-bespoke (`CSM`, `Owner`, `Account Manager`, etc.) — discover via `gainsight-cs-mcp-expert/references/org-discovery.md`. Never assume.

### 3. Long-list-then-prioritize-15 (the production cross-account workflow)
Cross-account list queries (book, tier × renewal-window, competitor scan) routinely return 25-100+ accounts. The 15 cap is for the parallel per-account-analysis trigger — NOT for list size. Use list → rank client-side → drill-down on top 15 via parallel `analyze_account` calls.

The 15-cap distinction matters and is widely misunderstood. See `references/anti-patterns.md` for the full explanation.

### 4. Risk × Expansion merge (Claude-side synthesis, not MCP-side)
Risk and Expansion analyses run independently — neither analyst sees the other's output. For "save-into-expansion" candidates (Risk ≥ 3 AND Expansion Readiness ≥ 3), Claude must MERGE the two analyses with recency weighting + stakeholder reconciliation + classification into one of 3 subtypes (Expansion-as-Save / Save-then-Expand / Skeptical Read).

This is internal reasoning. Customer-facing artifacts NEVER expose the classification labels. Full procedure in `references/query-patterns.md` + `_shared/gainsight-output-best-practices.md`.

### 5. Per-account drill-down with structured analyst queries
For deep account intelligence, use `staircase_analyze_account` with the structured queries that match the AI analysis type (Handoff, Expansion, Risk, Churn, Renewal, Summary). Each analysis type has a specific data model.

Full validated query templates per analyst type in `references/analyst-data-models.md`.

## Anti-patterns (top 5; full list in references/anti-patterns.md)

| Avoid | Why |
|---|---|
| Combined-criteria queries ("A AND B AND C in one ask") | Returns empty consistently. Decompose into single-criterion queries, intersect client-side. |
| OR composition | MCP only supports AND between filter conditions. Run criteria separately, union client-side. |
| Asking the MCP to compute abstract scores ("rank by urgency", "composite priority") | Returns empty. Pull raw fields, compute scores client-side. |
| Assuming the 15-account cap limits cross-account LIST queries | The 15 cap is on parallel per-account-analysis fan-out. List queries return 25-100+. Long-list-then-prioritize-15 is the production pattern. |
| Industry / segment filter directly | "Filtering by industry not supported in customer metadata." Use Gainsight `industry__gc` for industry segmentation. |

## Reference library

| File | When to read |
|---|---|
| `references/field-catalog.md` | Before composing any query — what's actually queryable (standard fields, events, insights, AI analyses) |
| `references/query-patterns.md` | Before composing queries — business-language → query translation, validated phrasings, the 6-tier priority methodology, Risk × Expansion merge |
| `references/anti-patterns.md` | Before unfamiliar operations OR when something fails — including the critical 15-cap clarification |
| `references/analyst-data-models.md` | Before per-account `analyze_account` calls — structured queries per analysis type (Handoff, Expansion, Risk, Churn, Renewal, Summary) |

## Determinism note

MCP non-determinism is real. The same query can return empty or rich on different attempts.

- If first attempt returns empty for a query that should work, retry up to 2 times with the same phrasing
- If retries still fail, try alternate phrasing (variants in `references/query-patterns.md`)
- Trust negative results from `staircase_analyze_account` — "no usable evidence in 90-day context" means it's not hiding, it's being honest
- Cap deep-dive enrichment at 15 parallel accounts (the `_MAX_PARALLEL_ACCOUNTS` cap from `staircase-ai/staircase-ml#2169`)

## When to use Staircase vs Gainsight vs both

| User question | Primary MCP | Secondary |
|---|---|---|
| ARR / renewal date / owner | Gainsight (authoritative) | Staircase ARR sometimes surfaces |
| Customer said recently / sentiment | Staircase | — |
| Open CTAs / Cockpit / Success Plans | Gainsight | — |
| What changed in the last 24 hours | Gainsight (time-bounded CTA/Timeline filter) | — |
| Strategic state / persistent signals | Staircase | — |
| Play for this account | Staircase `analyze_account` | Gainsight context |
| Patterns across portfolio | Staircase pattern-detection | — |
| Daily / weekly cockpit | Both combined | — |

## Cross-references

- **Cross-walk doc:** `../../_shared/mcp-cross-walk.md` — field-level Staircase ↔ Gainsight mapping, 5-Phase chain walked end-to-end, org-bespoke discovery split.
- **Paired foundation:** `../gainsight-cs-mcp-expert/` — Gainsight CS MCP foundation. Staircase reads → Claude synthesizes → Gainsight writes is the canonical chain.
- **Output discipline:** `../../_shared/gainsight-output-best-practices.md` (v1.1) — for any analysis that feeds Gainsight writes. Synthesis labels stay internal; customer-facing fields are teammate-facing AND customer-focused.
- **User profile:** `~/.gainsight-mcp/user-profile.md` (created by `gainsight-mcp-setup`) — applies the user's filter to "my accounts" / "my book" queries automatically. Sibling IC-tier skills read this.

## Learnings

See `.learnings.md` for accumulated validation, surprises, and refinements per session.
