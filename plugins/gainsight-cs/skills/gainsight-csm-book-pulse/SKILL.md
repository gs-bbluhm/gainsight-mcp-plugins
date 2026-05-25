---
name: gainsight-csm-book-pulse
description: Focus a CSM on the accounts in their book that need attention THIS week. Pulls full book by the org's team-member field, layers insight flags, ranks by an engagement-staleness-aware composite priority.
user_type: ic
---

# CSM Book Pulse

## Discovery

**Auto-trigger phrases:**
- "focus my book"
- "what should I focus on this week"
- "book pulse for [CSM]"
- "where does [CSM] need to spend time"
- "show me [CSM]'s priorities"

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas (15-cap, OR not supported, determinism)
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Risk, Expansion, Summary)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)
- `../gainsight-cs-mcp-expert/references/write-path-patterns.md` — canonical CTA + Task + Timeline + SP recipes (for Step 6 close-out writes)
- `../gainsight-cs-mcp-expert/references/anti-patterns.md` — gotchas, custom field requirements, HTML formatting

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

The CSM's "where do I spend time this week" answer. Pulls their entire book of business from Staircase + Gainsight, layers stakeholder-insight flags as badges, and ranks by a composite that weights engagement staleness alongside health, ARR, and renewal proximity.

---

## Team-member field discovery (CRITICAL)

Staircase has a standard `Owner` field that's consistent across orgs. Most orgs also have custom team-member fields (e.g., `CSM`, `Account Manager`, `Renewal Owner`, or an org-bespoke variant) — these must be discovered via the Gainsight `get_object_metadata("company")` call. The `gainsight-mcp-setup` skill walks the user through this discovery once and caches the field name in the user profile.

In any query in this skill that filters by a CSM, substitute `<team-member-field>` with the field discovered during setup. Do not hardcode "CS CSM" or any other org-specific name.

---

## The prioritization thesis

> "An account at equal risk/health level — but one engaged this week and another not in 3 weeks — the 3-weeks one needs attention more. Tier and revenue inform priority too."

This skill encodes that rule. The composite score elevates accounts that are **quietly stale** in addition to the obvious risk + expansion + renewal signals.

---

## Step 0: Resolve the CSM

User can specify by:
- **The org's `<team-member-field>`** (preferred — the CSM-assignment field discovered during setup): "<CSM Name>"
- **`Owner` field** (Staircase standard, often sales/account ownership)
- **Self** ("my book") — resolve current user

For self-resolution, use the Gainsight `resolve_user` tool with the user's name.

---

## Step 1: Pull the CSM's full book + flags in a SINGLE unified query

Staircase MCP returns priority fields AND flag booleans for a CSM's book in one query. This is the production pattern — collapse a prior 6-query approach (1 book + 5 portfolio flags + client-side intersect) into a single fan-out query.

**Why "my accounts" framing was wrong:** Ask Staircase doesn't auto-scope queries to the user's book. "Which of my accounts are flagged X" returns ALL accounts the asking user can see (portfolio-wide for admins), and those portfolio lists TRUNCATE without explicit pagination — leading to under-counted flag intersections. The CSM-scoped fan-out query is the correct architecture.

**Query pattern (unified):**

```
staircase_query("List the accounts where the <team-member-field> is <CSM Name>.
   For each account, include the ARR, renewal date, health score,
   last engagement date, last reach-out date, sentiment score,
   engagement score, risk level, expansion readiness level, AND
   indicate whether the account is currently flagged with any of these
   insights: Account Dark, No QBR, No Reach Out, Single Threaded with
   Stakeholder, Account Personnel Changes.")
```

For Owner-field queries:
```
staircase_query("List the accounts owned by <Name> as the account owner.
   For each, include the same priority fields AND insight flags as above.")
```

**Returns:** a single structured table with both priority fields AND boolean flag columns.

### Why this matters

- **More accurate** — flag intersections are evaluated server-side per account, not derived from truncated portfolio lists
- **More efficient** — 1 MCP call instead of 6 (saves time + tokens)
- **More usable** — single structured table per CSM is easier to score and present

### Deprecated pattern (DO NOT USE)

A prior 6-query approach (book + 5 portfolio insight queries + client-side intersect) is deprecated. Portfolio "Which of my accounts are flagged X?" queries return PORTFOLIO-WIDE lists subject to truncation, and "my" does NOT auto-scope to the asking user's book.

---

## Step 2 (DEPRECATED — folded into Step 1)

Step 2 used to layer portfolio insight queries with client-side intersection. **This is no longer needed** — the unified Step 1 query returns flags directly.

Use portfolio insight queries ONLY when:
- You need narrative/evidence for a specific flag (e.g., "tell me what's driving No QBR across the portfolio")
- You need cross-CSM trend analysis (e.g., "what's the org-wide Personnel Changes rate?")

For per-book operational use, always use the unified Step 1 query.

---

## Step 3: 6-Tier composite priority scoring (client-side)

See `staircase-mcp-expert`'s Part 5 methodology for the canonical reference.

```
TIER_1 — Renewal urgency (×0.20)
  renewal_proximity:
    <30d=1.0, <60d=0.75, <90d=0.5, <180d=0.25, else 0
  + risk_level / 5

TIER_2 — Engagement health (×0.18) — the "3 weeks vs 1 week" rule
  days_since_last_engagement / 30 (cap 1.0)
  + days_since_last_touch_DM / 21 (cap 1.0 — DM touch more critical)
  + (100 - engagement_score) / 100

TIER_3 — Commercial value (×0.15)
  log10(ARR) / 7 (caps near $10M)
  + tier_weight (Enterprise=1.0 / Mid=0.6 / SMB=0.3)

TIER_4 — Health + sentiment (×0.15)
  (100 - health_score) / 100
  + (100 - sentiment_score) / 100

TIER_5 — Expansion + open items (×0.12)
  expansion_readiness_level / 5  (UPSIDE leverage)
  + (100 - open_items_score) / 100

TIER_6 — Recent acute events (×0.10) — boosts only
  + 0.15 if Churn Risk event in last 30 days
  + 0.10 if Extremely Negative Message in last 30 days
  + 0.10 if Account Personnel Changes in last 30 days (champion attrition)
  + 0.05 if No QBR / Account Dark / Single Threaded flag active

TIER_7 — Support intensity (×0.10)
  submitted_tickets_30d (normalized)
  + ticket_comments_volume (back-and-forth indicator)

composite_priority = sum of tier × weight, capped at 1.0

SAVE-INTO-EXPANSION BONUS: +0.10 if Risk Level ≥ 3 AND Expansion Readiness ≥ 3
  (QUALIFIED via Risk × Expansion Merge — see Step 4 — bonus may downgrade
   to +0.03 if merge classifies as "Skeptical Read")

RISK-WEIGHTED READINESS SKEPTICISM:
  TIER_5 readiness signal is discounted when Risk is high:
    if risk_level >= 4: skepticism_factor = 0.5  (heavy skepticism)
    elif risk_level == 3: skepticism_factor = 0.75 (moderate skepticism)
    else: skepticism_factor = 1.0
    effective_readiness = (readiness_level / 5) * skepticism_factor
  Rationale: Risk and Expansion analyses are run by INDEPENDENT analyst
  agents that do not reference each other. High-risk accounts often have
  Expansion signals that aren't credible without merge verification.
```

The TIER_2 engagement-health weight encodes the rule: an account 3-weeks-stale outranks one at equal health that was engaged this week. The TIER_6 acute-event boosts surface champion-attrition + churn-risk-event signals that the static-score tiers miss. The save-into-expansion bonus surfaces the highest-leverage CSM moves — BUT the bonus is now qualified by the Step 4 merge classification.

---

## Step 4: Per-account drill-down (top 3-5) — Risk × Expansion Merge for save-into-expansion candidates

For the top N accounts (default 5):

### 4A. Standard drill-down (non-save-into-expansion accounts)

```
staircase_account_lookup(name=<account>) → account_id
staircase_analyze_account(account_id, query="
   Summarize <Account>'s last 90 days including risks, sentiment,
   and renewal readiness. What single action would most move the needle
   THIS week? Include named stakeholder to engage and the recommended
   approach.")
```

### 4B. MANDATORY for save-into-expansion candidates (Risk ≥3 AND Readiness ≥3)

The Risk Analysis and Expansion Analysis are run by **independent analyst agents** that DO NOT reference each other. Acting on either alone produces a distorted picture. The skill MUST run both AND a merge reasoning step:

**Step 4B.1 — Independent Risk Analysis (with evidence date range)**
```
staircase_analyze_account(account_id, query="
   Provide the full Risk Analysis for <Account>. Include: (1) key risk
   reasons and severity, (2) products at risk, (3) named at-risk
   stakeholders with roles (champion / decision-maker / detractor),
   (4) recommended playbook per risk reason, (5) key evidence. ALSO
   INCLUDE THE DATE RANGE OF THE EVIDENCE CITED — both the earliest
   and most-recent evidence dates. Focus ONLY on risk.")
```

**Step 4B.2 — Independent Expansion Analysis (with evidence date range)**
```
staircase_analyze_account(account_id, query="
   Provide the full Expansion Analysis for <Account>. Include: (1)
   account-level expansion summary, (2) per-opportunity drill-down
   (products, drivers, readiness, blockers), (3) expansion-engaged
   stakeholders with engagement quality, (4) recommended approach per
   opportunity. ALSO INCLUDE THE DATE RANGE OF THE EVIDENCE CITED —
   both the earliest and most-recent evidence dates. Focus ONLY on
   expansion.")
```

**Why request evidence date ranges:** Staircase MCP does NOT expose explicit analysis generation timestamps. The most-recent-evidence date is the best proxy for analysis recency. When Risk and Expansion analyses disagree about the SAME stakeholder, the analysis anchored on more recent evidence wins.

**Step 4B.3 — Merge reasoning (Claude-side) — RECENCY-WEIGHTED**

Output:

0. **RECENCY COMPARISON** — compute `days_since_risk_evidence` and `days_since_expansion_evidence` from the date ranges returned in 4B.1 and 4B.2. The more-recent-anchored analysis reflects current state more accurately. If the gap is >14 days, flag the older analysis as potentially stale.
1. **Stakeholder reconciliation** — where Risk and Expansion describe the same person differently, the more-recent-anchored view usually wins. Document the recency justification.
2. **Expansion credibility per opportunity** — UNDERMINED / CONTINGENT / INDEPENDENT relative to the risk profile. Flag opportunities the customer has explicitly dismissed even if Expansion Analyst rated them positively. Stale expansion signals (>30d) deserve extra skepticism.
3. **Subtype classification:**
   - **Expansion-as-Save** — expansion close IS the save play (full +0.10 bonus retained)
   - **Save-then-Expand** — save first; expansion contingent on stabilization (full +0.10 bonus retained)
   - **Skeptical Read** — expansion thread partially/fully fantasy (bonus DOWNGRADED to +0.03)
4. **Action sequence** — 3-5 step time-ordered plan reflecting BOTH analyses, weighted by recency, with named stakeholders per step.
5. **Confidence note** — flag any conclusions where the analyses disagreed and the recency-weighting was decisive.

Parallel batches of 5 (each batch = 2 analyze_account calls per account).

---

## Step 5: Produce the pulse

### Output structure

```markdown
# CSM Book Pulse — <CSM name> · Week of <date>

## At a glance
- <count> accounts in book · $<total ARR> total
- <count> with renewal in next 90 days
- <count> health below 40
- <count> with engagement stale 14+ days
- <count> with insight flags (No QBR / Dark / Personnel Changes)

---

## Where to spend time this week (ranked)

| # | Account | Priority | Last engaged | Health | ARR | Renewal | Flags | Why |
|---|---------|----------|--------------|--------|-----|---------|-------|-----|
| 1 | <account> | 0.92 | 2d ago | 10 | $149K | 80d | No QBR | Renewal+health critical, QBR overdue |
| 2 | <account> | 0.88 | 6d ago | 0 | $105K | 250d | Dark | Health 0 + Account Dark |
| 3 | <account> | 0.83 | 1d ago | 10 | $141K | 224d | — | Health 10 — needs save plan |
| ... | | | | | | | | |

---

## Top 3-5 plays (per-account drill-down)

### 1. <Account> — Priority <score>

**The play (this week):** <one-sentence action from analyze_account>
**Engage:** <named stakeholder>
**Approach:** <recommended approach>
**Evidence:** <ID list>

### 2. <Account> ...

### 3. <Account> ...

---

## Watch list (next priority tier)
Brief list of accounts ranked 6-15 with one-line context each.

---

## Hidden in your book
Accounts the CSM might not be tracking actively but where insight flags or staleness suggest action:
- Account Dark accounts in book
- Accounts with personnel changes (champion loss alerts)
- Accounts not engaged in 21+ days regardless of health
```

### Format adaptation

- **Cowork:** lead with the ranked card; insight flags as colored badges; expandable per-account drill-downs.
- **Code:** full markdown to stdout.

---

## Step 6: Optional close-out actions (approval-gated)

- Bump CTAs created in Gainsight for the top 3 plays
- Save the pulse to a notes destination for next week's comparison (week-over-week trend)
- Trigger `gainsight-stakeholder-connect` to draft outreach emails for accounts with No Reach Out / Personnel Changes flags
- Trigger `gainsight-no-qbr-ebr-scheduler` for No QBR accounts

---

## Edge cases

| Situation | What to do |
|---|---|
| CSM name doesn't resolve | Try alternate spellings; fall back to user-provided account list |
| Book has 50+ accounts | Show top 15 ranked, summary stats for the rest |
| Multiple CSMs with same first name | Disambiguate via Gainsight `resolve_user` |
| Account flagged in multiple insight lists | Stack flag badges (don't deduplicate the priority bump) |
| Engagement timestamp older than 90 days (out of Staircase window) | Cap staleness at 1.0, note "engagement >90d ago — needs verification" |
| No engagement data for an account | Mark "no engagement data" — usually indicates Account Dark already flagged |

---

## Why this matters

The CSM question that never had a clean answer: "where do I spend my time this week?" The plugin pulls the full book with health, renewal, ARR, and engagement timestamps in one query, layers insight flags, applies the engagement-staleness rule (a 3-weeks-stale account scores higher than a fresh one at equal health), and surfaces the top accounts with a named stakeholder to engage. The CSM closes the prompt with a plan, not a research project.

---

## Sources

- `staircase-analyst-data-models.md` — per-account drill-down queries
- `gainsight-mappings.md` — Gainsight + Staircase field names

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md` — the plugin-wide canonical reference. Core rules:

1. **User approval gate.** Present a short plan (goal + key strategic choices + specific external commitments being drafted). Get explicit user approval before any write.
2. **Commitment discipline.** Default to PROPOSAL language. Every Email-type Task includes a "Verify Before Sending" checklist flagging external promises the CSM must validate.
3. **HTML formatting** in rich-text fields. Use `<p>`, `<ul>`, `<ol>`, `<strong>`, `<br>`. Plain-text newlines render as a wall.
4. **Teammate-facing, customer-focused content.** Never expose internal classification labels (Save-then-Expand, Skeptical Read, Engaged Frustration, Recency tiebreaker, Composite classifications). Synthesize the differences and present the unified customer state.
5. **Evidence as readable references.** `Email (Person, date): paraphrased content` / `Meeting (date): paraphrased content`. No `comm_#####` IDs in customer-facing surfaces.
6. **Reuse-vs-create discipline.** `fetch_cta_list` and `fetch_success_plan_list` BEFORE writing. UPDATE existing where applicable.
7. **Cleanup discipline.** Surface stagnant artifacts (past due, no activity) before creating new. Don't compound clutter.
8. **Org-specific discovery.** Discover each org's actual CTA Types / Reasons / SP Types / required Timeline custom fields / Tier-or-Segment field via `prepare_*` calls and `get_picklist_values`. Don't hardcode picklist values.

### Skill-specific emphasis

Step 6 close-out actions: optionally create CTAs from top-N ranked accounts (only with explicit user approval). The "save-into-expansion" bonus is an INTERNAL composite signal that guides WHAT to write — translate the strategic insight (risk + expansion both elevated → multi-thread save play) into stakeholder-state language for customer-facing fields. Never use the bonus label or composite classification names in CTA Comments, Task names, or Timeline content.

---

## Learnings

See `.learnings.md`.
