# Staircase MCP — Anti-patterns + Gotchas

Read this when something fails OR before unfamiliar operations.

Organized: **The 15-cap clarification (CRITICAL)** → **Query composition anti-patterns** → **Determinism + reliability** → **Recently shipped capabilities** → **Scale-of-readiness nuance**.

---

## ⚠️ CRITICAL: The "15-account cap" is for PARALLEL PER-ACCOUNT ANALYSIS, not list length

This is the single most-misunderstood gotcha in the Staircase MCP.

### What the 15 cap actually is

**Direct PR evidence:** `staircase-ai/staircase-ml#2169` (merged 2026-05-18) — *"Raises `_MAX_PARALLEL_ACCOUNTS` from 5 to 15, updates the tool docstring, fixes the single-account result description (array not object), and bumps the Filter-Resolved routing threshold from 5 to 15 to match."*

The 15 cap applies when the MCP performs **`analyze_account`-equivalent parallel enrichment per item** — i.e., when you ask Staircase to do per-account drill-down across many accounts simultaneously.

### What the 15 cap is NOT

- ❌ NOT a cap on cross-account list query result size. Single-dimension list queries return **25-100+ accounts** routinely.
- ❌ NOT a cap on how many accounts you can include in a structured cross-account query for context.
- ❌ NOT a cap on the long-list-then-prioritize-15 workflow's list step — only on the deep-dive step.

### How to use the 15 cap intentionally (as a feature, not just a limit)

You can prompt Staircase to fan out per-account analysis on a list of up to 15 accounts. This is a workflow accelerator, not just a limit:

```
"Run a per-account analysis on each of these 15 accounts in parallel:
<list of 15 names or account IDs>. For each, return: <structured query>."
```

Use for post-prioritization deep-dive, workshop demos, or time-bounded portfolio reviews.

---

## Query composition anti-patterns

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| **Combined-criteria query** ("A AND B AND C in one ask") | Returns empty consistently | Decompose into single-criterion queries, intersect client-side |
| **OR composition** ("A OR B OR C") | MCP only supports AND. Direct quote: *"the reporting system only supports AND logic between filter conditions"* | Run each criterion separately, union client-side. Annotate which result satisfied which criterion. |
| **Open-ended ranking** ("rank by urgency") | MCP doesn't compute abstract scores | Pull the list, compute scores client-side |
| **Open-ended profile match** ("find accounts like `<account>`") | "Context only includes one account snapshot" | Pull a long list + per-account enrichment + score client-side |
| **Time-window deltas at portfolio scope** ("what changed in 24h") | Returns empty — MCP reasons about persistent signals not deltas | Use Gainsight for time deltas (`CreatedDate >= today-1d` filters) |
| **Industry / segment filter** | "Filtering by industry not supported in customer metadata" | Use Gainsight `industry__gc` for industry segmentation |
| **Asking the MCP to compute composite scores** ("show me composite priority across my book") | Returns empty | Pull raw fields, compute scores client-side |
| **Cross-account portfolio similarity** ("which other customers look like X") | MCP only knows one account per `analyze_account` call | Pull candidate list separately, score each |
| **"My accounts" without explicit field filter** | Doesn't auto-scope — returns all-accounts-user-can-see + truncates | Use unified fan-out query with explicit team-member field (`CSM is <Name>`, etc.) |
| **Assuming tier/segment field name** | Field names vary per org (`Tier`, `Segment`, `touch_model__gc`, etc.) | Discover via Gainsight `get_object_metadata("company")` before filtering |

---

## Determinism + reliability

**MCP non-determinism is real.** The same query phrasing can return empty or rich on different attempts.

### Mitigations
- If first attempt returns empty for a query you have reason to believe should work, **retry up to 2 times** with the same phrasing
- If retries still fail, try alternate phrasing (variants in `references/query-patterns.md`)
- Trust negative results from `staircase_analyze_account` — when it says "no usable evidence in 90-day context," it's not fabricating
- Cap deep-dive enrichment at 15 parallel accounts (see above)

### What "trust negative results" looks like
- ✅ "No usable evidence in 90-day window" → believe it, move on
- ✅ "Stakeholder list returned empty" → believe it, surface in artifact
- ❌ Re-running same query 5 times hoping for different content → wastes budget, results don't get better

---

## Recently shipped capabilities

These affect plugin behavior. Document so we don't reinvent.

### Text search hybrid mode
*"Extends `search_documents` to run text search alongside semantic search when `text_keywords` are provided"* — semantic always runs; text keywords enrich threads with body snippets. Replaces the old dual-mode toggle.

**Plugin implication:** when looking for specific quotes / phrases, append `text_keywords` to drive precision.

### Stakeholder decision-maker sort
*"Economic buyer and executive sponsor bubble to the top of the stakeholders list; unknown roles fall last."*

**Plugin implication:** stakeholder maps now arrive pre-ranked by decision-maker role. Don't re-sort client-side.

### Single lifecycle event fetch by ID
`GET /api/lifecycle-events/{id}` — backend API for fetching a single lifecycle event. Not yet exposed via MCP but the underlying data + filtering is now query-by-id ready.

**Plugin implication:** request MCP exposure as a follow-up.

### Filter-Resolved threshold raised to 15
The routing threshold for "filter-resolved account queries" bumped from 5 to 15.

**Plugin implication:** queries phrased as "filter accounts by X" route to the broader cross-account scope automatically.

### Cross-account prompt overhaul
Added: "sales handoff" as routable AI insight field, multi-account scope rule fixes, fallback no longer permits hallucinating from general knowledge.

**Plugin implication:** hallucination risk is lower, but the MCP will more aggressively decline rather than guess — which is why "ranking" and "sorting" queries return empty rather than estimate.

### Lifecycle events V2 fully shipped
V2 of the lifecycle event pipeline is fully live.

**Plugin implication:** structured lifecycle events should become a primary data source for cross-account intelligence. Worth a follow-up probe on whether `staircase_query` (vs `ask`) now supports structured lifecycle event filtering.

---

## Scale-of-readiness nuance (important)

**Portfolio expansion query** returns Readiness on a **1-5 scale**.

**Per-account `analyze_account` Expansion Analysis** returns Readiness on a **0-10 scale** ("5/10 (moderate, heating)").

These appear to be **two different metrics, not the same metric on different scales.** The portfolio score is a categorical pipeline-stage; the per-account score is a continuous-ish maturity assessment.

**Plugin implication:** do NOT assume portfolio Readiness 5 maps to per-account Readiness 5/10. They're not the same number.

Documentation gap filed for DS.

---

## Key teaching points

1. **Owner is standard; CSM/AM/etc are custom.** Discover your org's custom team-member field names — they vary per org.
2. **The 15 cap is parallel per-account analysis, not list length.** Long-list-then-prioritize-15 is the production workflow.
3. **OR not supported; abstract ranking not supported.** Use single-criterion queries + client-side composition.
4. **Action-oriented phrasing wins.** "Summarize / Draft / Identify" beats "What is / Tell me about."
5. **Trust negative results.** When Staircase says "no usable evidence," it's not hiding — it's being honest.
6. **Single Threaded with Stakeholder is often a portfolio-wide risk.** Many orgs surface hundreds of accounts with this flag — most CSMs don't have that visibility today.
7. **Risk × Expansion analyses are independent.** Merge is Claude-side, not MCP-side.
