# Staircase MCP — Advanced Patterns

Deeper-probe findings that supersede or extend the basic query patterns. Includes the validated long-list-then-prioritize workflow, the structured-summary type catalog, and the operating envelope for cross-account queries.

---

## 1. The "15 cap" is parallel-account analysis, NOT list length

Single-dimension list queries can return open-ended result counts (200+ rows when criteria are broad). The 15-account cap applies when the MCP performs `analyze_account`-equivalent parallel enrichment per item, not when returning a simple list.

### The validated workflow: long-list → prioritize → deep-dive 15

```
Step 1: Single-dim portfolio list query (200+ rows possible)
  staircase_ask("Which of my accounts have <single criterion>?")

Step 2: Enrich with prioritization signals (parallel)
  - Pull ARR, RenewalDate, Tier, CSM Owner from Gainsight Company object
  - Use Staircase Health/Sentiment from the original list response or supplemental query

Step 3: Client-side priority scoring
  Composite priority = w1*renewal_proximity + w2*ARR_log + w3*readiness/health + w4*tier_weight
  Default weights for renewal-prep flows: w1=0.4, w2=0.3, w3=0.2, w4=0.1

Step 4: Deep-dive top 15 in parallel
  staircase_analyze_account(account_id, query=<summary-type-specific>)
  Run as 3 parallel batches of 5 each to respect 60 req/min rate limit

Step 5: Synthesize report
```

### When to use

- Cross-portfolio renewal report at quarter-end
- Expansion targeting (top expansion plays prioritized from a long list of readiness-ranked accounts)
- Churn-risk save sprint planning across a book of business
- VoC pattern hunter at scale (run pattern-hunter twice: once on the prioritized 15, once on the long tail)

---

## 2. Per-account structured summary types — all 6 work

Each query template below returns 5 evidence IDs plus named stakeholders and categorical structure.

### Account Summary
```
query="Generate the Account Summary for <Account>: company overview, current state, top 3 themes from the last 60 days, key relationships and engagement quality, commercial position, and most important context."
```
Returns: comprehensive 6-section briefing. Best for executive-friendly account overviews.

### Risk Analysis
```
query="Pull the full Risk Analysis for <Account>. Include: top risks by category (commercial / product / adoption / stakeholder), severity, named stakeholders driving the risk, mitigation suggestions, and supporting evidence IDs."
```
Returns: categorical risks (Product / Adoption / Stakeholder / Commercial) with severity rating per category, named stakeholder per risk, mitigation paragraph per risk.

### Expansion Analysis
```
query="Pull the full Expansion Analysis for <Account>. Include: expansion opportunities (named), expansion readiness rating, key buying signals, named champions and decision makers, recent buying-intent evidence with IDs."
```
Returns: opportunities list, readiness (note: scale here is 0-10, distinct from the portfolio query's 1-5 scale), buying signals, decision-makers by opportunity.

### Handoff Analysis
```
query="Build a Handoff Analysis for <Account>: account summary, why they bought, current goals, stakeholders (champions / decision makers / detractors), recommended onboarding actions, onboarding readiness assessment, top risks, top expansion opportunities, key context for a new CSM."
```
Returns: 9-section structured output ready for a new-CSM brief. (`gainsight-account-handoff-onboarding` uses this.)

### Churn Summary
```
query="Generate the Churn Summary for <Account>: current churn risk level (low / medium / high / critical), specific churn signals detected, timing if known, named stakeholders involved, and recommended save actions."
```
Returns: 5-section churn assessment with timing of risk signals (e.g., "strongest signals appeared in the last 2-3 weeks").

### Renewal Summary
```
query="Generate the Renewal Summary for <Account>: renewal date, contract terms, renewal trajectory (low / medium / high risk), top risks to the renewal, expansion opportunities at renewal, key stakeholders for the renewal conversation, recommended action plan for the 90 days leading to renewal."
```
Returns: structured renewal brief including the **90-day action plan** — directly actionable.

### Best practice
Use these as drop-in query templates rather than ad-hoc phrasing. Each returns rich content because the query phrasing maps to Staircase's internal report types. There is a defined catalog of supported analysis types behind the scenes.

---

## 3. OR logic — NOT supported

The reporting system only supports AND logic between filter conditions.

When the user asks for OR composition (e.g., "accounts that had a churn risk in 30 days OR have readiness 3+ OR have an expansion summary defined"), use the decompose-and-union pattern:

1. Run query A: "accounts with churn risk in last 30 days" → list_a
2. Run query B: "accounts with expansion readiness 3+" → list_b
3. Run query C: "accounts with AI expansion opportunity summary" → list_c
4. Client-side union (case-insensitive name match)
5. Annotate each result with which criterion (A / B / C) it satisfies

This is symmetric with the decompose-and-intersect pattern already documented for AND composition.

---

## 4. Other capabilities to know about

### Text search hybrid mode
`search_documents` runs text search alongside semantic search when `text_keywords` are provided. Semantic always runs; text keywords enrich threads with body snippets. When looking for specific quotes or phrases, append `text_keywords` to drive precision.

### Stakeholder sort
Stakeholder lists arrive pre-ranked: economic buyer and executive sponsor bubble to the top; unknown roles fall last. Don't re-sort client-side.

### Cross-account guardrails
The MCP will decline (return empty) rather than guess for unsupported patterns like ranking or sorting. This keeps hallucination risk low but means you must design queries to fit the supported envelope (see "What still doesn't work" in `staircase-query-patterns.md`).

---

## 5. Scale-of-readiness clarification (important nuance)

**Portfolio expansion query** returns Readiness on a **1-5 scale** (categorical pipeline-stage).

**Per-account `analyze_account` Expansion Analysis** returns Readiness on a **0-10 scale** (e.g. "5/10 (moderate, heating)") — a continuous-ish maturity assessment.

These are two different metrics, not the same metric on different scales. Do not assume portfolio Readiness 5 maps to per-account Readiness 5/10.

---

## 6. Long-list-then-prioritize workflow for renewal prep

For high-stakes / executive renewal-prep work, the long-list-then-prioritize pattern is preferred over a single cross-account query:

```
1. staircase_ask("Which of my accounts have a renewal date in next <N> days?")
   → 200+ rows: name + renewal date

2. staircase_ask("Which of my accounts have at-risk sentiment or
   declining health?")
   → 50+ rows: name + health + sentiment

3. Client-side join → at-risk renewal set (e.g., 30 accounts)

4. Parallel Gainsight enrichment per account: ARR, Tier, CSM

5. Composite priority score → pick top 15

6. Parallel analyze_account on top 15:
   query="Generate the Renewal Summary for <Account>: renewal date,
   contract terms, renewal trajectory, top risks, expansion opportunities
   at renewal, key stakeholders, recommended 90-day action plan."

7. Synthesize report
```

For demo contexts, the fast-path is more impressive; for **production use cases**, the long-list-then-prioritize pattern is more defensible.
