---
name: staircase-at-risk-renewals
description: Cross-portfolio at-risk renewal report combining renewal-date proximity with Staircase health, sentiment, and risk evidence. Produces ranked accounts with top risks, named stakeholders, and recommended actions.
user_type: experimental
disable-model-invocation: true
---

# Staircase At-Risk Renewals

## Discovery

**Auto-trigger phrases:**
- "at-risk renewals"
- "which accounts are at risk"
- "Q2 renewal risk"
- "renewals in the next 90 days that need attention"
- "build the at-risk renewal report"

**Validation history:** 15-account fast-query path validated against real portfolio data (returns ranked table + evidence IDs in one call). Decompose-and-intersect fallback validated for combined-criteria queries that return empty.

**Currently flagged experimental** — may consolidate with `gainsight-exec-renewal-radar` later (significant scope overlap).

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — validated phrasings + decompose-and-intersect
- `../staircase-mcp-expert/references/anti-patterns.md` — 15-cap clarification, OR not supported, determinism mitigations
- `../staircase-mcp-expert/references/field-catalog.md` — what's queryable

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)

---

Cross-account intelligence skill. Surfaces the accounts most at risk of churning in the upcoming renewal window, combining Gainsight commercial data (renewal date, ARR) with Staircase communication signal (health score, sentiment, risk evidence).

## Why this skill exists

Single-account queries to Staircase work great. Combined cross-account queries (renewal AND at-risk AND named stakeholders AND evidence IDs) **return empty**. The skill works around this with a **decompose-and-intersect pattern** that gets the right answer reliably.

## Step 1: Define the window

Default: next 90 days. Adjust on user request ("Q2", "next 60 days", "by end of fiscal year").

Translate to: `today + N days`.

## Step 2A: PRIMARY PATH — 15-account fast query

Recent Staircase MCP improvements unlocked single-query at-risk-renewal reports with evidence IDs. **This is now the default.**

```
staircase_ask("Examine 15 of my customers with renewals in the next <N>
   days that are showing at-risk signals. For each, summarize: account
   name, renewal date, health score, top risk, and one named stakeholder
   driving the risk.")
```

Returns: 15-row table with account, renewal date, health score, top risk narrative, AND 15 evidence IDs anchoring each account's risk claim. Verified against real-org Gainsight + Staircase data.

If this returns the full ranked list cleanly, **skip Step 2B** — go straight to Step 4.

**When it might still return empty** — abstract criteria ("rank by severity", combined with industry filter). If the response is empty or thin (< 5 rows), drop to the decompose path below.

## Step 2B: FALLBACK — Decompose into single-dimension queries

```
A. staircase_ask("Which of my accounts have a renewal date in the next <N> days?")
   → returns table of name + renewal date (200+ rows possible)

B. staircase_ask("Which of my accounts currently have at-risk sentiment
   (sentiment < 40) or declining health (health < 40)? Include health and
   sentiment scores.")
   → returns table of name + health + sentiment

C. (Optional, if time permits)
   staircase_ask("Which of my accounts have explicit churn-risk signals,
   unresolved escalations, or competitor evaluations in the last 60 days?")
   → returns table of name + signal type
```

**Critical:** Do not combine A+B+C into one query. Verified that combined queries return empty or "I couldn't retrieve the requested account list."

### Optional fast path — when intersection size <= 15

If a quick pulse (not the full report) is acceptable, use the **15-account list+summarize pattern** instead of the decompose-and-intersect flow:

```
staircase_ask("Examine 15 of my customers with renewals coming up that
   show at-risk signals. For each, summarize: account, renewal date,
   health score, top risk, named stakeholder driving the risk, and
   most recent risk activity.")
```

Verified to work at the 15-account scale. Faster (one query vs. decompose-and-intersect), but the structured output is more fragile — if it returns empty, fall back to the decompose path.

## Step 3: Intersect client-side

In-memory join the result sets by account name. Match fuzzy (case-insensitive, ignoring legal suffixes like "Inc." / "Ltd." / "GmbH"). Produce the intersection set.

## Step 4: Enrich top N (default 10)

For each account in the intersection (cap at 10 to control runtime):

```
staircase_account_lookup → account_id
staircase_analyze_account(account_id, query="
   Top 2 churn risks at <Account>, named stakeholders driving the risk,
   the single most recent risk-related evidence, and the most concrete
   recommended next action. Cite evidence IDs.")
```

Run in batches of 3 in parallel to keep latency manageable.

## Step 5: Optional Gainsight enrichment

If time permits and the user wants depth:

For each enriched account:
```
gainsight resolve_customer(account_name) → company GSID
gainsight fetch_cta_list(CompanyId, IsClosed=false, DueDate>=today-90d)
```

Pull: open Risk CTAs, current CSM owner, ARR, Tier.

Skip if the user wants a fast turn (<30s).

## Step 6: Produce the report

### Output structure

```
# At-Risk Renewal Report — Next <N> Days

**Generated:** <date> · **Window:** <today> to <today + N>
**Accounts in window:** <count_renewing>
**Accounts with at-risk signal:** <count_risky>
**Intersection (the at-risk-renewal set):** <count> accounts

---

## Headline

<2-3 sentences. Total ARR at risk, common themes across the top 5, the single highest-leverage move>

## Top <N> Accounts at Risk

| Rank | Account | Renewal | ARR | Health | Sentiment | Top Risk | Recommended Action |
|------|---------|---------|-----|--------|-----------|----------|---------------------|

(For each top account, a deeper drill-down block follows)

## Account Deep Dives

### <Account Name> — <renewal date>
- **Health / Sentiment:** <h> / <s>
- **CSM Owner (Gainsight):** <name>
- **Top risk:** <risk> (evidence: <ID>)
- **Named stakeholders:** <list>
- **Recommended next action:** <action with owner>

(repeat per top account)

## Common Themes

Pattern analysis across the at-risk set:
- <Theme 1, with count of accounts exhibiting it>
- <Theme 2>
- ...

## Recommended Plays

Higher-level plays the CSM org should run across the at-risk cohort, ranked by leverage.

---

## Sources

- Staircase MCP `ask` (3 portfolio queries)
- Staircase MCP `analyze_account` (per-account enrichment for top N)
- Gainsight MCP `resolve_customer` + `fetch_cta_list` (if Gainsight enrichment enabled)
```

### Format adaptation

- **Cowork:** lead with a card showing the headline + ranked table; deep dives as expandable cards
- **Code:** full markdown to stdout + optional file artifact (filename like `at-risk-renewal-report-<date>.md`)

## Edge cases

| Situation | What to do |
|-----------|------------|
| Intersection set is empty | Likely the portfolio is healthy. Report that honestly. |
| Account in renewal window but not found via `account_lookup` | Skip enrichment for that account, note in report |
| `analyze_account` returns thin data for an account | Note "low confidence — Staircase has limited communication data" |
| User wants a different criterion (e.g., "show me churn risk regardless of renewal date") | Drop dimension A from the join |

## Limitations to document (for the Staircase product team)

- Cross-dimension queries don't compose today. The skill works around this with client-side intersection.
- `ask` doesn't return evidence IDs at portfolio scope. Evidence retrieval requires per-account follow-up.
- The "renewal date" returned in `ask` is derived from communications + Gainsight sync; spot-check accuracy on a sample of accounts before treating it as authoritative.

## Output Best Practices (when chaining into Gainsight writes)

This skill primarily READS from Staircase. If you chain into Gainsight writes (Risk CTAs on top at-risk accounts, Timeline activities for context delivery to the team), follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Key rules: user approval gate before customer-facing writes, commitment discipline (proposal language), HTML formatting in rich-text, teammate-facing language (no synthesis labels), reuse-vs-create discipline (`fetch_cta_list` first), org-specific discovery (no hardcoded CTA Types or picklist values).

---

## Learnings

See `.learnings.md`.
