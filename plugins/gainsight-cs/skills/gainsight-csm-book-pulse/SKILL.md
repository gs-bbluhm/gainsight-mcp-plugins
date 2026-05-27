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

**Rendering discipline (for Cowork app-feel):**
- `../mcp-app-design/references/patterns.md` — patterns + when-to-use
- `../mcp-app-design/references/component-library.md` — concrete HTML markup for each visual component
- `../mcp-app-design/references/per-skill-mappings.md` — per-skill chrome (tabs, components, mode picker). Look up your skill's row FIRST when rendering output.

## ⚡ Pre-query quality gate (mandatory before any non-trivial Staircase query plan)

Canonical reference: `plugins/gainsight-cs/skills/staircase-mcp-expert/references/query-patterns.md` — top-of-doc Execution Checklist. 30-second scan before composing.

**Composition rules — run mentally per query:**

- [ ] **One dimension per `ask` query.** AND/OR composition fails. Decompose first, intersect client-side.
- [ ] **Scope explicitly.** "My accounts" doesn't auto-scope. Filter by the org's team-member field (`Csm` / `Owner` / org-bespoke — read from user profile or discover via `gainsight-cs-mcp-expert/references/org-discovery.md`).
- [ ] **No abstract score requests** to the MCP. Pull raw fields; compute "urgency" / "composite priority" / "save-into-expansion score" client-side.
- [ ] **15-cap discipline.** The 15 is for PARALLEL per-account analysis fan-out. Cross-account LIST queries return 25-100+ accounts routinely. Use long-list-then-prioritize-15 for portfolio-wide work.
- [ ] **Action-verb phrasing** for `analyze_account`. "Summarize / Identify / Draft / List" outperforms "What are the current X."
- [ ] **Risk × Expansion are INDEPENDENT.** Pull both. Merge client-side with recency weighting + stakeholder reconciliation + classification. NEVER expose Save-then-Expand / Skeptical Read / Expansion-as-Save labels in customer-facing fields.

**Pre-query validation summary — surface to user for complex plans (>2 calls or compound logic):**

```
Pre-query validation — <user ask>

Scope: <e.g., Hannah Lee's 31 accounts via Csm filter>
Dimensions: <one per call — e.g., (1) Risk Level + (2) Expansion Readiness + (3) Renewal <120d>
Plan: <N single-dim ask calls + client-side intersect + top-N analyze_account>
Drill-down depth: <0 / per-account analyses on top N>

Estimated MCP load: <N queries / parallel limit>
```

Skip for single-criterion lookups. Use for compound logic, fan-out, expensive deep-dives.

**Failure modes from prior sessions to avoid:**
- Compound queries returning empty (decompose first)
- "My accounts" without explicit scope filter (use the team-member field)
- Asking the MCP to compute abstract scores (pull raw, compute client-side)
- Conflating list size with the 15-cap (long-list-then-prioritize-15)
- Exposing internal classification labels in customer-facing artifacts (merge labels stay internal)

Full anti-pattern catalog: `staircase-mcp-expert/references/anti-patterns.md`.

---

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

**Canonical rendering reference:** `mcp-app-design` — top-of-doc Rendering Checklist. Read before producing output.

Detect the surface FIRST. If Cowork → app-feel (tabs + cards + buttons). If Code → scannable markdown. Mode heuristics in the canonical doc.

### Cowork rendering (primary optimization target)

**Layout: colored app header + tab nav with counts + per-tab content. NEVER lead with prose.**

#### Colored app header (always-on, top of viewport)

Render the colored app header component (`cowork-component-library.md` §1) with:
- **Icon:** 📊
- **Title:** "Book Pulse"
- **Persona:** the CSM's name
- **Date:** "Week of <date>"
- **Brand:** `gainsight` (Gainsight orange `#FF7A00`)

#### Tab navigation with counts

Render the tab nav component (`cowork-component-library.md` §4):

```
At a glance · Priorities (N) · Active work (N) · Watch / briefing (N)
```

- "At a glance" gets no count (it's the overview tab).
- Tab counts reflect populated items per tab.

#### Tab 1 · At a Glance

**Render in this order:**

1. **Metric card grid (3+3, signal-color-striped)** — component library §2:

   | Position | Card | Stripe |
   |---|---|---|
   | 1 | Book size · N accts · `<tier mix>` | neutral |
   | 2 | Total ARR · `$<X>K` · avg `$<Y>K` | neutral |
   | 3 | High-risk signals · N · Risk 4-5 in Staircase | `--risk` |
   | 4 | Overdue CTAs · N · `<tasks>` | `--risk` if >0, else neutral |
   | 5 | EBRs in window · N · renewal 60-120d | `--watch` |
   | 6 | Expansion-ready · N · ER 3+ in Staircase | `--expansion` |

2. **Section callout** (component library §3) for any urgent observation. Example: amber `--warning` callout for "5 accounts past renewal — needs reconciliation today" with action button "Draft deal desk ask."

3. **Primary CTA button** at the bottom: "Take me to top priorities →" (jumps to Tab 2).

**Do NOT include guidance prose** ("Tap Navy Bayview Supply in Priorities to start...") on this tab. If guidance is needed, put it behind a `?` help icon on the primary CTA. Cowork's job is to surface the data; the user discovers the flow by clicking.

#### Tab 2 · Priorities (the working surface)

**Render in this order:**

1. **Working mode picker** (component library §7) — full state on first visit, collapses to single line after selection.

2. **Ranked table** (component library §5) — top 8-10 rows, sortable with chevrons, signal-pill color tied to row signal-dot.
   - Default sort: priority/composite score descending.
   - Signal column required — every row needs a signal label (`Active exit` / `EBR window` / `CTA false-pos` / `Past renewal` / `Expansion play` / `Risk + low ER` / `Health floor` etc.).
   - Watch list 11-25 collapsed behind `[Show watch list (9-15)]` button.

3. **Drill-down card** (component library §6) — opens on row click. Shows State (3 concrete bullets) + Stakeholders (chips, 2-4) + Next Moves (2-4 buttons, first is `--primary`).
   - Drill-down placement: inline below the clicked row if Cowork supports it; otherwise pinned-right or sticky-bottom.
   - ALWAYS show Next Moves buttons — never empty.

#### Tab 3 · Active Work

**Render in this order:**

1. **Top-of-tab counts strip:** `Open CTAs · N` `Active SPs · N` `Closed SPs (recent) · N` `Cleanup actions · N`

2. **Section: Open CTAs** — list with per-row context callout (`--warning` if false-positive flagged, `--info` if status update needed). Each row has an action button: `[ Review ]` or specific action like `[ Close as false-positive ]`.

3. **Section: Success Plans** — list with progress + status. **Use done-state badge** (component library §11) for 100%-complete plans (NOT an action button — implies action when none needed). For active SPs, primary action button.

4. **Section: Cleanup recommendations** — bulleted list, BUT each bullet has an inline action button matching the recommended action: `[ Close as false-positive ]` / `[ Open new CTA ]` / `[ Open Success Plan ]`. Don't render cleanup bullets without buttons.

#### Tab 4 · Watch / Briefing

**Rename from "Watch / briefing" to just "Briefing" or "Worth flagging"** if it fits the tab nav width.

**Render in this order:**

1. **Section: Past-renewal accounts** — list grouped by timing.
   - Headline: "N past renewal + M borderline (timing pattern: ER ≥ 3)"
   - Each row has inline `[ Check status ]` button.
   - Use sub-grouping if count mismatch would otherwise occur ("5 past renewal · 2 borderline cases").

2. **Section: Briefing notes (severity-iconed)** — bullets with severity icons matching content:
   - ⚠ for concerning observations ("Zero Staircase insight flags fired — could mean stale flags")
   - ℹ for neutral structural notes ("All accounts SMB tier — no Enterprise stratification")
   - Each note worth investigating gets a `[ Investigate ]` button inline.

3. **Final section: What's NOT here** — only if relevant (no feature requests, no flagged insights, etc.). Each item gets a contextual action (`[ Widen lookback to 180d ]` etc.).

#### Sticky pending-action footer (when actions accumulate)

Render the pending-action footer component (`cowork-component-library.md` §10) once the user has approved their first move. Updates live as actions queue up. "Review all" button opens the consolidated pre-write validation card before any Gainsight write fires.

#### Tab 2 · Priorities (the working surface)

**Top of tab — working mode picker (inline choice card):**

```
How do you want to work through these?
  ⚪ Walk me through one at a time  (default, conversational)
  ⚪ Show me all proposed actions   (batch mode)
  ⚪ Just must-do this week         (focused, skip watch list)
```

**Ranked sortable table (top 8-10 rows):**

| # | Account | ARR | Renewal | Risk | Health | Flags | Why here |
|---|---|---|---|---|---|---|---|

- Sortable by any column header
- Badge decoration in Flags column (🔴 🟡 🟢 🔵 per `cowork-output-patterns.md` §8)
- Row click expands to drill-down card
- "Why here" column is mandatory — short specific phrase per row

**Per-row drill-down card (opens on row tap):**

```
┌─ <Account> · ARR $<X>K · Renewal <Nd> · Risk <N> · Health <N>
│
│   <2-3 sentence customer state>
│
│   Recommended next moves:
│     ┌──────────────────────────────────────────┐
│     │ ▶ Draft outreach to <stakeholder>         │
│     │ ▶ Update <CTA name> → <new status/scope>  │
│     │ ▶ Schedule EBR / Reframe EBR / etc.       │
│     └──────────────────────────────────────────┘
│
│   When user picks a move → produces THAT card next (see Action tee-up below)
│
└─ [ Skip this account ] [ More context ]
```

#### Tab 3 · Active Work (existing CTAs + SPs)

Two collapsible sub-sections:

- **Open CTAs in your name** — table with status, due date, age, cleanup recommendation per row (close as false positive, advance, escalate)
- **Active Success Plans** — table with progress %, due date, action needed per plan

Per-row buttons: `[ Update ] [ Close ] [ Add Task ]` → opens approval card.

#### Tab 4 · Watch / Briefing

- **Past-renewal accounts** — needs status reconciliation. Per-row `[ Check status ]` button → triggers ad-hoc query.
- **Briefing notes** — observations Claude wants to surface (no flagged insights → ops check, no feature requests → widen lookback, etc.). Plain prose; short.

### Action tee-up sequence (the key behavioral pattern)

**Do NOT dump 6 proposed actions in a markdown table. Do NOT close the response with "Reply with A,C to draft."**

When user picks an action from a drill-down card:

1. Produce ONLY that ONE deliverable as a new card.
2. Card shows preview (email body, CTA fields, EBR outline, etc.) + approve/edit/skip buttons.
3. On approve → write executes → confirmation card → return to Tab 2 with the next priority surfaced or the same account if more moves remain.
4. If user picked "batch mode" in the working-mode picker, fall back to the markdown action queue with checkboxes.

Full spec: `mcp-app-design/references/patterns.md` (action tee-up).

### Preference question pattern

When the per-account approach has a meaningful branch (e.g., save-with-incentive vs offboarding-first for a detractor situation), surface an inline choice card. Spec: `mcp-app-design/references/patterns.md` (preference question card).

Examples for this skill:
- "How should we approach <Account>?" — Save-with-incentive / Offboarding-first / Multi-thread first
- "What lens for <Account>?" — Renewal-execution / Expansion-prep / Risk-recovery

### Code rendering (CLI fallback)

The legacy markdown structure still works for Code users. Keep it scannable:

```markdown
# CSM Book Pulse — <CSM Name> · Week of <date>

## At a Glance
- <N> accounts · $<X>K total ARR
- <N> renewals in 60d · <N> past-renewal · <N> EBRs due
- <N> open CTAs · <N> active SPs · <N> expansion-ready

## Priorities (ranked top 10)
| # | Account | ARR | Renewal | Risk | Health | 🚩 | Why here |
|---|---|---|---|---|---|---|---|
| 1 | ... | $45K | 46d | 5 | 34 | 🔴 | ... |

## Active Work
- Open CTAs in your name: <list with status + age>
- Active Success Plans: <list with progress>

## Watch List
- Past-renewal: <accounts needing reconciliation>
- Briefing notes: <observations>

## Proposed Actions (batch mode)
| # | Action | Account | Type | Notes |
| A | Draft outreach to <stakeholder> | <Account> | Gmail draft | <one-line context> |
| B | Update CTA <name> → <status> | <Account> | UPDATE | <one-line context> |
| C | Reframe EBR as exit management | <Account> | Notes doc | <one-line context> |

Reply `approve A,C` (selective) or `approve all`, or `walk me through these` for sequential mode.
```

Also write the full packet to `inbox/workshop/csm-book-pulse-<csm>-<date>.md` so the user can grab it from disk.

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

## ⚡ Pre-write quality gate (mandatory before any Gainsight write)

Canonical reference: `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md` — top-of-doc Execution Checklist. 30-second scan before composing any write.

**Composition rules — run mentally per artifact:**

- [ ] **CTA description = TLDR ONLY.** 1-3 sentences: what + why + pointer to Tasks. NOT the action playbook.
- [ ] **Each CTA has ≥2 Tasks.** Each Task = one discrete action.
- [ ] **Task descriptions carry the accelerator** — pre-drafted email body, agenda, discovery script, escalation template. Not "draft an email."
- [ ] **Timeline activity for strategic motions** with TLDR / Findings / Stakeholders / Action sequence / Evidence. Attach via `success_plan_id` or `cta_id` so it lives where the work lives.
- [ ] **HTML, not Markdown** in rich-text fields (`<p>`, `<ul>`, `<strong>`, `<br>`).
- [ ] **No em dashes. No AI-isms. No internal classification labels** (Save-then-Expand, Skeptical Read, Engaged Frustration, Recency tiebreaker) in customer-facing fields.

**Discipline rules — run mentally before the approval gate:**

- [ ] **Fetch existing CTAs + SPs first** (`fetch_cta_list` + `fetch_success_plan_list` on the company). Surface stagnant artifacts to the user.
- [ ] **Reuse-vs-create check.** If an open CTA covers the same signal → update, don't duplicate.
- [ ] **SP threshold.** Don't create a Success Plan unless ≥3 strategic CTAs + clear outcome goal + measurable success criteria. Otherwise use standalone CTA(s).
- [ ] **Commitment discipline.** Default to PROPOSAL language ("I'd like to propose…", "Can we align on…"). Email Tasks include a **Verify Before Sending** checklist for every external commitment.
- [ ] **Org-specific discovery.** Discover CTA Types / Reasons / SP Types / required Timeline custom fields via `prepare_*` calls. Never hardcode picklist labels.

**Pre-write validation summary — paste-ready, surface BEFORE any write tool call:**

```
Pre-write validation — <Account>

Artifacts about to land:
- [N] Success Plan(s) with Plan Info enriched
- [N] CTA(s) · all descriptions TLDR · [N] attached to SP
- [N] Tasks total · each Task description carries accelerator content
- [N] Timeline activity attached to [SP / CTA / company]

Discipline checks:
- Existing artifacts reviewed: [N] stagnant CTAs, [N] active SPs
- Reuse-vs-create: [decisions per existing artifact]
- SP threshold: [N CTAs ≥3 ✓ / else using standalone CTAs]
- Formatting ✓ HTML · ✓ No em dashes · ✓ No internal labels in customer-facing fields

Ready to write?  [Approve all / Adjust / Hold]
```

**If any rule fails, regenerate before writing. Never silently violate.**

### Skill-specific emphasis

Step 6 close-out actions. Get user consent before any write. Convert top-N priority accounts into CTAs only when user explicitly says "create CTAs for these." The "save-into-expansion" bonus is an INTERNAL composite signal that guides WHAT to write — translate the strategic insight (risk + expansion both elevated → multi-thread save play) into stakeholder-state language for customer-facing fields. Never use the bonus label or composite classification names in CTA Comments, Task names, or Timeline content.

### Failure modes from prior sessions to avoid

- **Action content in CTA description instead of Tasks** → CTA description stays TLDR; actions become Tasks
- **Standalone CTA that belongs under an active SP** → attach via `success_plan_id` (create) or `CtaGroupId` (update)
- **Creating SP + CTAs but skipping the Timeline Update context anchor** → always post the Update activity attached to the SP
- **Hardcoding picklist values** instead of `prepare_cta` / `prepare_sp` discovery
- **Putting draft email in CTA Comments** instead of Task description

Full anti-pattern catalog: `_shared/gainsight-output-best-practices.md` §10.

---

## Learnings

See `.learnings.md`.
