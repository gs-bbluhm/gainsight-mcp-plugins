---
name: gainsight-exec-churn-retrospective
description: Quarterly churn retrospective. Combines Gainsight Status=Churned authoritative list + Staircase pattern themes + per-account Churn Analysis.
user_type: exec
---

# Gainsight Churn Retrospective Analyzer

## Discovery

**Auto-trigger phrases:**
- "churn retrospective"
- "analyze recent churns"
- "what patterns drove churn"
- "churned accounts review"
- "post-mortem churn analysis"
- "find missed signals on churn"

**Purpose:** Quarterly retrospective combining authoritative Gainsight data (Status = "Churned", churn_date) with Staircase's pattern themes and per-account Churn Analysis structured output. The output also surfaces the gap of accounts that churned WITHOUT a Staircase Churn Analysis firing — feedback for trigger tuning.

**Optimized for:** Cowork (per-account drill cards + approval gates) and Code (full retrospective report). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Handoff, Expansion, Risk, Churn, Renewal, Summary)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

**Rendering discipline (for Cowork app-feel):**
- `../../_shared/cowork-output-patterns.md` — tab structure, action tee-up sequence, preference question cards, working mode picker, color/badge semantics

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

The CSM Ops quarterly ritual: review who churned, why they churned, what we missed, and where Staircase didn't catch the signal.

---

## Critical correction

"Churn Analysis" is a Staircase analyst that fires when a **verified churn** is detected — typically from Churn Notification communications. It is **retrospective**, not forward-looking. **It is not the same as Churn Risk** (which is predictive signal).

⚠️ **Churn Analysis doesn't always fire** even when an account has churned. The Staircase trigger requires a Churn Notification communication; many churns happen without one (silent non-renewal, M&A consolidation, etc.). The gap-finding mechanism in this skill identifies these accounts.

---

## Step 0: Scope

Default: last 90 days of churn.

User overrides:
- "Q2 <year>" / "last quarter" / "year-to-date"
- "Just enterprise" — tier filter applied in Step 1
- "Specific product" — e.g., a single product line — filter by Relationship Product type

---

## Step 1: Pull the authoritative churned-accounts list (Gainsight)

⚠️ **Gainsight is the source of truth for "who churned."** Staircase doesn't reliably enumerate churned accounts ("list churned accounts" query returns empty in many configurations).

```
gainsight run_query on company:
  select: Name, Gsid, Arr, ARR__gc, ST_ARR__gc,
          churn_date__gc, churn_primary_reason__gc,
          churned_to_competitor__gc, RenewalDate,
          CS_Segment__gc, type__gc
  where: Status EQ "Churned"
         AND (churn_date__gc GTE <window-start> OR
              (churn_date__gc IS NULL AND RenewalDate GTE <window-start>
               AND RenewalDate LT <today>))
  page_size: 50
```

Note the OR clause: if `churn_date__gc` is empty, use past-renewal-date as a fallback indicator. Surface these explicitly in the report as "no recorded churn date — inferred from past renewal."

---

## Step 2: Pull pattern themes (Staircase, 15-account scope)

```
staircase_ask("Across my recently churned customers, what are the
   common themes in the reasons for churn? Group by theme and list
   the accounts under each, with evidence IDs.")
```

Themes commonly returned (will vary based on the actual churn cohort):
1. Product fit / feature gaps
2. Cost / value perception
3. Operational / support quality
4. Organizational change / champion loss
5. Strategic re-platform / consolidation

Skill should not assume the theme list is fixed — let the data drive it.

---

## Step 3: Per-account Churn Analysis (parallel batches of 5, top N=10-15)

For each account from Step 1, run:

```
staircase_account_lookup(name=<account>) → account_id
staircase_analyze_account(account_id, query="
   Pull the AI Churn Analysis for <Account> (only fires if a verified
   churn was detected). Return:
   - Detected date
   - High-level summary: ARR impact, primary drivers, mitigation efforts,
     final outcome
   - Issues: bulleted list of specific problems
   - Missed signals: what should have been caught earlier
   - Supporting evidence IDs with dates

   If no Churn Analysis exists, respond: 'No Churn Analysis found.'")
```

The per-account output is structured (Why-churned + Issues + Missed signals + Outcome + dated Reference timeline) when the analysis fires — and the MCP is honest about returning "no analysis found" when it doesn't.

---

## Step 4: Identify the gap (churned without analysis)

Set difference: `Churned_in_Gainsight ∖ Has_Churn_Analysis_in_Staircase`

These are the accounts that:
- **Did churn** (Gainsight authoritative)
- **But Staircase didn't catch the signal** (no Churn Notification communication, OR the analysis hasn't run yet)

Surface them explicitly in the report. **This is the gap-finding mechanism the retrospective is built around.**

---

## Step 5: Produce the retrospective

**Cowork rendering:** Surface as a tabbed app per `_shared/cowork-output-patterns.md` §9 (4 tabs: Cohort / Patterns / Gaps / Recommendations). Lead with the header card (churn cohort stats), never with prose. Per-account/theme expandable cards; briefing-grade output, minimal direct posting. Inline choice card for "Drill into pattern?". NEVER dump a markdown wall.

**Code fallback:** Scannable markdown — structured headers, emoji-badged tables, batch-mode action queue with approval syntax.

### Output structure

```markdown
# Churn Retrospective — <window>

**Generated:** <date>
**Window:** <window>
**Total churned accounts (Gainsight authoritative):** <count>
**Total ARR lost:** $<sum>
**Accounts with Staircase Churn Analysis:** <count> (<%>)
**Accounts without Churn Analysis (gap):** <count>

---

## Headline

<2-3 sentences>
- Total ARR impact
- Top 1-2 themes driving churn (with account counts)
- The single highest-lesson finding (e.g., "all five product-fit churns shared the same product-area gap")

---

## Common Themes (Staircase pattern detection)

### 1. <Theme name> (<count> accounts, $<ARR sum>)

<2-3 sentence theme description>

- **<Account>** ($<ARR>, churned <date>) — <what specifically>
- **<Account>** ($<ARR>, churned <date>) — <what specifically>
- ...

**Lesson / recommendation:** <one-sentence org-level move>

### 2. <Theme name> (...)

...

---

## Per-Account Briefs (top N by ARR or strategic importance)

### <Account> — $<ARR> · Churned <date>

**Why churned (Staircase):**
<summary paragraph>

**Issues:**
- <bulleted>
- ...

**Missed signals:**
- <what should have been caught earlier — bulleted>
- <evidence: <ID> from <date>>

**Outcome:**
<final state — moved to competitor? consolidated? deprioritized?>

**Gainsight context:**
- Primary reason: <churn_primary_reason__gc>
- Churned to competitor: <churned_to_competitor__gc>
- Account team member: <discovered org-bespoke field>

---

## Gap Findings — Churned without Staircase Analysis

⚠️ <count> churned accounts have no Staircase Churn Analysis. These churns were not detected via a Churn Notification communication — either:
- The customer didn't send formal churn notification (silent non-renewal)
- The churn was via M&A consolidation
- The trigger heuristic missed the signal

| Account | $<ARR> | Churn date | Gainsight primary reason | Notes |
|---------|--------|-------------|----------------------------|-------|
| ... | | | | |

**Action:** For each, consider whether the AM/CSM should add a manual churn close-out note that Staircase can future-detect via training.

---

## Cross-Cohort Plays

Patterns across the cohort that suggest org-level moves:

1. **<Theme>** — <count> accounts cite the same factor. Recommended response: <play>.
2. ...

---

## Process improvements surfaced

If the gap (Step 4) is large (>30% of churned), surface:
- **Churn Analysis trigger improvements** — what communication patterns should also fire the analyzer?
- **Process improvements** — should we add a mandatory CSM close-out note that names "churn reason" in customer-facing comms?
```

### Format adaptation

- **Cowork:** themes as expandable cards; per-account briefs as drill-downs; gap section as a flagged callout.
- **Code:** full markdown + artifact at `churn-retrospective-<window>-<date>.md`.

---

## Edge cases

| Situation | What to do |
|---|---|
| `churn_date__gc` empty for everyone | Fall back to past-renewal-date heuristic — note in report |
| Staircase pattern themes return empty | Skill still works from per-account briefs; flag the missing portfolio view |
| Account has Status=Churned but resolve_customer in Staircase fails | Note in gap section; possible name-matching issue or Staircase doesn't have the account |
| Window has 0 churns | Celebrate. Report "no churns in the window" rather than failing. |
| Many churns (50+) | Surface top 10-15 by ARR for the per-account section; aggregate the rest in themes only |

---

## Why this matters

> "The CSM Ops quarterly question is 'what did we learn from the churns we couldn't save.' Plugin runs the retrospective in one prompt: authoritative list from Gainsight, themes from Staircase, structured per-account brief, AND the gap of churns that weren't caught by the analyzer. That last piece — *churned but no analysis* — is the trigger-tuning feedback loop that improves Staircase over time."

---

## Output Best Practices (when chaining into Gainsight writes)

Primarily READ. Produces a retrospective report (markdown). If chaining into Gainsight writes from the output (investigation CTAs on missing-analysis churns, knowledge-share Timeline activities), follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Key rules: user approval gate, PROPOSAL language, HTML formatting, no internal classification labels in customer surfaces, fetch existing first, org-specific discovery.

"Missing analysis" CTAs that surface trigger-tuning feedback for Staircase are typically INTERNAL investigation tasks (not customer-facing). The 8 best-practice rules still apply but the verification bar is lower for internal-only artifacts.

---

## Learnings

See `.learnings.md`.
