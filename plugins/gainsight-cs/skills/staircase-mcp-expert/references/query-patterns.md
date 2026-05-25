# Staircase MCP — Query Patterns

How to translate business-language asks into Staircase queries that actually return rich data. Use this as a recipe book before composing queries.

Organized: **Business-language translation** → **Validated phrasings** → **Priority weighting methodology** → **Risk × Expansion merge methodology** → **Intentional fan-out trigger**.

---

## Step 1 — Identify the SCOPE

| User says... | Scope is... |
|---|---|
| "my accounts" / "my book" | Specific user's book — filter by their team-member field (org-bespoke; see `field-catalog.md` + `gainsight-mcp-setup` user profile) |
| "high-touch accounts" / "enterprise" | Tier filter (org-bespoke segmentation — `Tier`, `Segment`, `touch_model__gc`, etc.) |
| "this quarter" / "next 90 days" | Date window (renewal or event) |
| "across our customers" | Portfolio-wide |
| Specific account name | Single account via `staircase_analyze_account` |

## Step 2 — Identify the DIMENSION

| Business term → | Staircase field |
|---|---|
| "at risk" | Risk level, Churn Risk event, Negative sentiment, low Health score |
| "expanding" | Expansion readiness level, Expansion opportunities, Highly positive |
| "stale" / "quiet" | Last engagement, Account Dark, No Reach Out |
| "ready for QBR" | No QBR insight |
| "lost their champion" | Account Personnel Changes |
| "alone with one contact" | Single Threaded with Stakeholder |
| "renewing soon" | Renewal Date in window |
| "executive engaged" | Exec to Exec Connect event |
| "ROI conversation" | AI Expansion Analysis + commercial discussion event |

## Step 3 — Compose the query plan

**Rule of thumb:** one dimension per `ask` query. Combine client-side.

| Question shape | Query plan |
|---|---|
| "List X with property Y" | Single `ask` query for Y, intersect with X scope client-side |
| "Top N by score" | Pull list, sort client-side, optionally `analyze_account` top N in parallel |
| "Compare A and B accounts" | `analyze_account` per account in parallel, synthesize client-side |
| "Patterns across portfolio" | `staircase_ask("Across 15 of my customers, identify themes...")` — pattern-detection query |
| "Full structured analysis of one account" | `staircase_analyze_account` with the rich analyst-data-model query |

---

## Validated phrasing patterns

### Single-criterion list (highest reliability)

```
"Which of my accounts have <single criterion>?"
"List my accounts that <single attribute>."
"Which of my accounts are flagged as <insight>?"
```

### Unified scoped fan-out (CSM book or scoped reads — collapses 6 queries into 1)

Important: "my accounts" doesn't auto-scope in the MCP. Always use an explicit field filter.

```
"List accounts where <team-member-field> is <CSM Name>. For each account, include:
name, ARR, renewal date, health score, last engagement date, last reach-out date,
sentiment score, engagement score, risk level, expansion readiness, and boolean
flags for Account Dark, No QBR, No Reach Out, Account Personnel Changes,
Single Threaded with Stakeholder."
```

`<team-member-field>` is org-bespoke and must be discovered per org. The standard Staircase `Owner` field is universal; everything else (`CSM`, `Account Manager`, `Renewal Owner`, `TAM`, or any org-specific variant) varies. The `gainsight-mcp-setup` skill walks the user through discovery once and caches the field name in the user profile so sibling skills auto-apply the filter. To discover ad-hoc, call `get_object_metadata("company")` against Gainsight.

### 15-account list + summarize

```
"Examine 15 of my customers with <criterion>. For each, summarize:
<field 1>, <field 2>, <field 3>, <field 4>."
```

### Pattern detection + theme grouping (cross-account)

```
"Across 15 of my customers, identify common themes in <signal> from the
last <N> days. Group by theme and list accounts with supporting evidence IDs."
```

This is the workshop-grade pattern-hunter query.

### Per-account drill-down

Use the structured queries in `references/analyst-data-models.md` (Handoff, Expansion, Risk, Churn, Renewal, Summary). Each maps to Staircase's internal report types and returns 5 evidence IDs + named stakeholders + categorical structure.

### Long-list-then-prioritize-15 (the production cross-account workflow)

```
Step 1: Single-dim portfolio list query (200+ rows possible)
  staircase_ask("Which of my accounts have <single criterion>?")

Step 2: Enrich with prioritization signals
  - Pull ARR, RenewalDate, Tier, and the org's team-member field from Gainsight Company object
  - Use Staircase Health/Sentiment from list response or supplemental query

Step 3: Client-side priority scoring (composite — see methodology below)

Step 4: Deep-dive top 15 in parallel
  staircase_analyze_account(account_id, query=<summary-type-specific>)
  Run as 3 parallel batches of 5 each to respect 60 req/min rate limit

Step 5: Synthesize report
```

Production-defensible for renewal prep, expansion targeting, churn-risk save sprints, VoC pattern-hunting at scale.

---

## Priority Weighting Methodology — The 6-Tier Composite

The canonical "where should I focus" composite score. Used by `gainsight-csm-book-pulse`, `gainsight-renewal-priority-planner`, `gainsight-exec-renewal-radar`, `_experimental/staircase-at-risk-renewals`, and `_experimental/staircase-expansion-scout`.

```
priority_score =
  TIER_1 (renewal urgency)       × 0.20
+ TIER_2 (engagement health)     × 0.18
+ TIER_3 (commercial value)      × 0.15
+ TIER_4 (health + sentiment)    × 0.15
+ TIER_5 (expansion + open items) × 0.12
+ TIER_6 (recent acute events)   × 0.10
+ TIER_7 (support intensity)     × 0.10
```

### TIER_1 — Renewal urgency (0.20)
- `Renewal Date proximity`: <30d=1.0, <60d=0.75, <90d=0.5, <180d=0.25, else 0
- `Risk level / 5` (or /10 for account-scoped)

### TIER_2 — Engagement health (0.18) — the "3 weeks vs 1 week" rule
- `days_since_last_engagement / 30` (capped at 1.0)
- `days_since_last_touch_DM / 21` (capped at 1.0 — DM touch is more critical)
- `Engagement score` inverted

### TIER_3 — Commercial value (0.15)
- `log10(Revenue) / 7` (caps near $10M)
- Tier weight: Enterprise=1.0, Mid=0.6, SMB=0.3

### TIER_4 — Health + Sentiment (0.15)
- `(100 - Health score) / 100`
- `(100 - Sentiment score) / 100`

### TIER_5 — Expansion + open items (0.12)
- `Expansion readiness level / 5` (UPSIDE — separate from risk)
- `(100 - Open items score) / 100` (lower score = more unresolved = higher priority)

### TIER_6 — Recent acute events (0.10) — boosts, not standalone
- +0.15 if Churn Risk event in last 30 days
- +0.10 if Extremely Negative Message in last 30 days
- +0.10 if Account Personnel Changes in last 30 days (champion attrition)
- +0.05 if No QBR / No Reach Out / Account Dark / Single Threaded flag active

### TIER_7 — Support intensity (0.10)
- Submitted tickets in last 30 days (normalized)
- Ticket comments volume (back-and-forth indicator)

### Cap the priority_score at 1.0.

### Save-into-expansion bonus

Accounts with BOTH Risk Level ≥ 3 AND Expansion Readiness ≥ 3 are highest-leverage attention. Add **+0.10 bonus** — these are the "save into expansion" plays.

### Risk-weighted readiness skepticism

When Risk ≥ 3, the Expansion Readiness score should be treated skeptically (Expansion Analyst may not be aware of the active risk):
- R ≥ 4 → multiply Expansion readiness contribution by 0.5
- R = 3 → multiply by 0.75
- R ≤ 2 → no skepticism applied

This corrects for the independence between Risk and Expansion analyses (see merge methodology below).

---

## Risk × Expansion Merge Methodology

**Core principle:** the Risk Analyst and Expansion Analyst run INDEPENDENTLY. Neither sees the other's output. For save-into-expansion candidates, Claude must MERGE them. This is internal reasoning — never expose the synthesis labels in customer-facing artifacts.

### When to trigger the merge

Account meets: Risk Level ≥ 3 AND Expansion Readiness ≥ 3.

### The 7-step merge procedure

**Step 0 — Recency Comparison**
Pull dates of evidence in BOTH analyses (most-recent evidence date is the proxy for analysis recency, since explicit timestamps aren't exposed). Note which is more recent.

**Step 1 — Pull both analyses**
- Risk Analysis: top risks by category, severity, named stakeholders, mitigation suggestions
- Expansion Analysis: opportunities, readiness, buying signals, named decision-makers per opportunity

**Step 2 — Stakeholder reconciliation**
Compare named stakeholders. Same person may appear with different framings:
- Risk Analyst: "detractor today" (recent friction)
- Expansion Analyst: "executive sponsor with high but cautious engagement" (broader read)
Pick the framing that's most-recent-evidence-supported. Note the conflict for internal reasoning.

**Step 3 — Expansion credibility per opportunity**
For each expansion opportunity, ask: does the Risk Analysis credibly threaten this specific opportunity? If yes, this is "save before expand." If no, this is "expansion despite risk."

**Step 4 — Per-thread classification (when account has multiple expansion threads)**
Classify each thread separately. Aggregate to account-level posture only after per-thread analysis. Threads can land differently.

**Step 5 — Account subtype classification**
- **Expansion-as-Save** — Risk is real but expansion engagement IS the path forward. Sponsor wants more, hesitation is about scope/timing not retention.
- **Save-then-Expand** — Risk must be resolved before expansion can land. Sequential motion. Multi-threading required.
- **Skeptical Read** — Expansion Analyst's optimism contradicts Risk Analyst's recent evidence. Treat expansion signals with low weight; focus on save.

**Step 6 — Action sequence**
3-5 step action plan grounded in the classification. Save-first if Save-then-Expand or Skeptical Read; parallel-track if Expansion-as-Save.

**Step 7 — Output**
For internal reasoning: full merge with classification label.
For customer-facing artifacts: customer state, stakeholder map, action plan only. NEVER expose the classification labels ("Save-then-Expand," "Skeptical Read") in Gainsight CTAs / Timeline / SP fields. The output discipline doc (`_shared/gainsight-output-best-practices.md`) enforces this.

---

## Intentional fan-out trigger (the 15-cap as a feature)

The 15-account cap on parallel per-account analysis is a workflow feature when used intentionally:

```
"Run a per-account analysis on each of these 15 accounts in parallel:
<list of 15 names or account IDs>. For each, return: <structured query>."
```

This triggers Staircase's fan-out machinery deliberately. Useful for:
- Post-prioritization deep-dive (the long-list-then-prioritize-15 capstone step)
- Live demo: show 15 simultaneous account reports landing in seconds
- Time-bounded portfolio review (a CSM's top 15 accounts before a leadership 1:1)

See `references/anti-patterns.md` for the cap-vs-list distinction (the 15 is for PARALLEL ANALYSIS, not list length).
