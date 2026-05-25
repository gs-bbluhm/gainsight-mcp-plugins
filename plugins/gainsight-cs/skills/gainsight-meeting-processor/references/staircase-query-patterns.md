# Staircase Query Patterns

Verified working patterns for `staircase_analyze_account`, `staircase_ask`, `staircase_query`, and `staircase_account_lookup` in the meeting-processor context.

## Parameter quirks

- `staircase_analyze_account` uses parameter `query`, **not** `question`. Passing `question=` returns a validation error.
- `staircase_account_lookup` returns matches with `confidence: "high" | "low"`. Common name variants (e.g. an account informally referenced vs. its legal entity name with suffix) typically resolve high-confidence on first call. Retry logic with suffix variants ("Inc", "LLC", "Corp", "Software") is a safety net for the long tail.
- When `account_lookup` returns multiple high-confidence matches (parent + subsidiary, or two related entities), ask the user before proceeding to `analyze_account`.

## Account-scoped queries — the default playbook

### The validated query templates

For single-account context, **action-oriented phrasing outperforms information-retrieval phrasing.** "Draft renewal talking points" outperforms "What are the current risks..." by a wide margin across thousands of tested queries.

| Use case | Template | Notes |
|---|---|---|
| **90-day health/risk/renewal summary** | `"Summarize <Account>'s last 90 days including risks, sentiment, and renewal readiness"` | High success rate; default for fan-out |
| **Stakeholder map** | `"Who are the key stakeholders at <Account> and their engagement patterns?"` | Reliable across most accounts |
| **Risk surfacing** | `"What are the top concerns or risks for <Account>?"` | Reliable; pairs well with the summary query |
| **Renewal prep** | `"Draft renewal talking points for <Account> based on recent communications"` | Most resilient query across accounts including problematic ones |
| **Value/ROI** | `"What specific outcomes or results has <Account> achieved?"` | Weakest; fails when no ROI conversations exist in comms |
| **Handoff brief** | `"Build a handoff brief for a new CSM taking over <Account>: account summary, why they bought, current goals, stakeholders, recommended actions, onboarding readiness, top risks, expansion opportunities, key context."` | Verified working |

**Default for meeting processor's account fan-out** (use these verbatim):

```
A. staircase_analyze_account(account_id, query="
   Summarize <Account>'s last 90 days including risks, sentiment, and
   renewal readiness. Include named stakeholders, evidence IDs, and any
   explicit churn or expansion signals.")

B. staircase_analyze_account(account_id, query="
   Who are the key stakeholders at <Account> and their engagement patterns?
   Identify champions, decision-makers, detractors, and recent stakeholder
   shifts with evidence IDs.")
```

Top-quality runs typically return 5 evidence IDs, a structured trajectory narrative, and named stakeholders across multiple sections.

### What you GET

- **Health Score** (0-100, numeric)
- **Sentiment Score** (0-100, numeric)
- **Health/Sentiment divergence** is more actionable than either score alone (e.g. Health 70 + Sentiment 45 = operational issues without overall relationship damage)
- **Trajectory narrative** alongside numeric ("turbulent but constructive", "improving but fragile")
- **ARR** when present in contract snapshots in communications
- **Renewal date** when surfaced in recent comms
- **Internal account team** (CSM, AM, SA, PM names + roles)
- **Stakeholder shifts** (new contacts, departures, role transitions, ownership changes)
- **Risk signals** (categorized: operational / adoption / strategic / commercial)
- **Expansion signals** (named products, readiness 1-5 scale via the right phrasing)
- **Evidence IDs** (linkable via `staircase_fetch_evidence`)

### What you DON'T get

- Structured lifecycle events with timestamps (signals only, inferred from comms)
- Account tier classification (lives in CRM, not surfaced)
- Product usage metrics
- Full org charts (thread participants only, not the whole organization)
- Real-time alerts

## Cross-account queries — the 15-account tier

Cross-account capacity in Staircase MCP supports up to 15 accounts with multi-field detail per query.

### ✅ Works at 15-account scale

**Pattern 1 — List + multi-field summarize**
```
staircase_ask("Examine 15 of my customers with <criterion> and summarize:
   account name, <field 2>, <field 3>, <field 4>, most recent activity.")
```
Returns a clean table, up to 15 rows.

**Pattern 2 — Pattern detection + theme grouping + evidence IDs**
```
staircase_ask("Across 15 of my customers, identify common patterns or
   themes in <signal type> from the last <N> days. Group by theme and
   list the accounts under each.")
```
Returns grouped themes + accounts + 3-5 evidence IDs. Unlocks portfolio-wide thematic intelligence.

**Pattern 3 — Single-dimension list (unbounded)**
```
staircase_ask("Which of my accounts have <single criterion>?")
```
Returns 200+ rows when the criterion is broad (e.g. "renewals in next 90 days"). Use as the first step of decompose-and-intersect when you need more than 15.

**Pattern 4 — Reference pool**
```
staircase_ask("Which of my customers have publicly spoken about <product>
   or appeared as customer references in the last year?")
```
Returns 20-40 accounts annotated with activity_type (e.g. event video, testimonial, advocacy).

### ❌ Still doesn't work

| Anti-pattern | Symptom |
|---|---|
| Combined-criteria filters ("A AND B AND C") | Returns empty or apology |
| Abstract ranking ("rank by severity / urgency") | Returns empty |
| Industry / segment filtering ("financial services accounts") | "Filtering by industry not supported in metadata" |
| Open-ended profile matching ("find customers like <account>") | "Context only includes one account snapshot" |
| Asking for evidence IDs in a structured-output query | Fragile. Sometimes works, sometimes returns empty |

### Workaround for unsupported patterns

**Decompose-and-intersect:**
1. Run query A (single dimension, e.g. "renewals in next 90 days")
2. Run query B in parallel (single dimension, e.g. "at-risk sentiment or declining health")
3. Client-side fuzzy join on account name (case-insensitive, ignoring legal suffixes)
4. Enrich top N (default 5-10) via per-account `analyze_account` in batches of 3 parallel

This pattern underpins at-risk-renewal, expansion-targeting, and reference-finder workflows.

## Evidence handling

- Evidence IDs (`comm_Email_...`, `comm_Calendar_...`, `comm_Ticket_...`) are stable identifiers. Use verbatim.
- 5 evidence items per query is the maximum observed.
- Use `staircase_fetch_evidence(id)` to retrieve full text for direct quotation.
- Don't fabricate IDs; if claiming Staircase signal without one, flag as "from synthesis".

## Confidence indicators

- **5 evidence items, multi-channel** (meetings + emails + tickets + chat) → high confidence
- **1 evidence item, single source** → low confidence, flag in output
- **0 evidence items** → name-matching may have failed silently, retry with variants
- **Health 0 specifically** → real signal but warrants verification (could indicate either churn OR sync-failure)

## Score interpretation guide

| Health | Sentiment | Pattern |
|---|---|---|
| 0 | N/R | Confirmed churn / critical |
| < 40 | < 40 | At risk — both below midpoint |
| 60-70 | 60+ | Moderate-to-healthy |
| 70+ | < 50 | Mixed — operational issues, relationship intact |

Divergence (Health vs. Sentiment gap > 20) is more actionable than either score alone. It points to a specific risk type rather than a generic "at risk" label.

## Data window

- **~90-120 days** of communication history (not strict 90).
- Natural language time references ("last 6 months") filter *within* the window, don't extend it.
- Oldest data observed in testing: ~116 days back.

## Rate limiting

- ~60 req/min observed.
- Batch per-account enrichment in groups of 3 parallel for reliable throughput.
- Never fire unbounded portfolio scans without a filter.
