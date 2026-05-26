---
name: gainsight-renewal-priority-planner
description: Prioritize upcoming renewals where CSM attention can most move the needle. Composite movability score (Risk + Expansion Readiness + ARR + renewal proximity + tier), then per-account deep-dives surfacing save-plus-expansion plays.
user_type: exec
---

# Gainsight Renewal Priority Planner

## Discovery

**Auto-trigger phrases:**
- "which renewals should I focus on"
- "prioritize my Q2 renewals"
- "where should I spend my time before renewal"
- "renewal priority planner"
- "top renewal plays this quarter"
- "move-the-needle accounts"

**Purpose:** Built for the leadership-perspective question: not "what's at risk" or "what could expand" in isolation, but "where will my effort generate the biggest renewal-cycle return." Combines Staircase Risk Analysis + Expansion Analysis with Gainsight commercials.

**Optimized for:** Cowork (ranked card + per-account drill-down + approval gates) and Code (full markdown report + artifact). Cowork is the primary optimization target.

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

The CSM leader's "where should I focus this quarter" skill. Combines Staircase Risk Analysis + Expansion Analysis with Gainsight commercials to identify the accounts where attention can most move the needle on renewal outcomes — both **saves** (high-risk accounts that are still movable) and **save-into-expansion** plays (accounts with both risk and expansion readiness in flight).

---

## Step 0: Frame the scope

Default scope: renewals in next 90 days.

User can override:
- "Q3 renewals" → next 90 days
- "Q4 renewals" → 91-180 days out
- "my book this fiscal year" → 365 days
- "high-touch accounts only" → add tier filter

If the user mentions specific accounts to focus on, short-circuit to per-account deep-dive only.

---

## Step 1: Pull the renewal window (single-dim list query)

```
staircase_ask("Which of my accounts have a renewal date in the next <N> days?")
   → 100-200+ rows: account name + renewal date
```

This works at scale (verified 200+ rows). If user wants a smaller filter ("top tier only"), narrow client-side using Gainsight tier enrichment in Step 3.

---

## Step 2: Pull risk + expansion signals (parallel single-dim queries)

Run these three queries in parallel. Each returns a list with account name + level/score.

```
A. staircase_ask("Which of my accounts have a Risk Analysis with risk
   level 3 or higher? List account name and risk level.")
   → risk-flagged list with risk-level scores

B. staircase_ask("Which of my accounts have strong expansion signals
   with named expansion opportunities and an expansion readiness rating?
   List account name, opportunities, and readiness 1-5.")
   → expansion-ready list with readiness scores
   ⚠️ MCP is non-deterministic on this query — if first attempt returns
      empty, retry up to 2 times with same phrasing.

C. (Optional) staircase_ask("Which of my accounts had a Churn Risk
   event detected in the last 30 days?")
   → recent-churn-risk list (when supported by current MCP version)
```

---

## Step 3: Gainsight enrichment (parallel per account)

For each account in the renewal window, pull from Gainsight:

```
gainsight resolve_customer(name=<account>) → company GSID
gainsight run_query on company:
  select: Arr, ARR__gc, ST_ARR__gc, RenewalDate, Stage,
          CS_Segment__gc, type__gc, CurrentScore,
          Staircase_AI_Renewal_Analysis__gc,
          Staircase_Account_Dark__gc,
          Red_Account__gc
  where: CompanyId IN (<resolved GSIDs>)
```

`Staircase_AI_Renewal_Analysis__gc` is a Gainsight-side text field synced from Staircase that may contain the prior AI Renewal Analysis if the account has been through a prior renewal cycle — useful learning signal.

---

## Step 4: Composite priority scoring

Compute a "movability" score per account. The thesis: highest-leverage accounts have both **risk to mitigate** and **expansion to capture** — the save-into-expansion zone.

```
movability_score =
   0.30 × renewal_proximity_score    (closer = higher; <30d=1.0, <60d=0.75, <90d=0.5, <180d=0.25)
 + 0.25 × log_normalized(ARR)         (larger account = higher leverage)
 + 0.20 × risk_level_movable          (risk 3-4 = 1.0, risk 5 = 0.6 (already-lost), risk <3 = 0.3)
 + 0.15 × expansion_readiness         (readiness/5 normalized; bonus +0.15 if also risk≥3)
 + 0.10 × tier_weight                 (enterprise=1.0, mid-market=0.6, SMB=0.3)
```

**The save-into-expansion bonus** (+0.15 if account has BOTH risk≥3 AND readiness≥3) is what surfaces the "move-the-needle" accounts. These are the highest-leverage plays — neither pure-save nor pure-expansion alone gives the same return.

Rank descending. Pick top 15.

### Anti-pattern correction
Don't put risk-5 (already-churning) accounts at the top. They're usually past the save window. Risk 3-4 + expansion readiness 3+ is the sweet spot.

---

## Step 5: Deep-dive top 15 (parallel batches of 5)

For each top-15 account, run **two queries in parallel** using the validated analyst data models from `references/staircase-analyst-data-models.md`:

```
Query 1 — Full Risk Analysis:
  staircase_analyze_account(account_id, query=<full Risk Analysis template>)
  → Risk reasons (with severity + timeline urgency), playbook actions
    (with timeline + owner role), stakeholders (with sentiment +
    engagement guidance)

Query 2 — Full Expansion Analysis:
  staircase_analyze_account(account_id, query=<full Expansion Analysis template>)
  → ARR potential, products, per-opportunity drill-down (category,
    AI confidence, budget, technical, action plan, questions)
```

Run in 3 parallel batches of 5 (10 total parallel MCP calls, ~30-60s runtime).

---

## Step 6: Produce the priority report

### Output structure

```markdown
# Renewal Priority Plan — <Window> (<count> renewals · $<total ARR> total)

**Generated:** <date>
**Scope:** <window>

---

## Headline

<2-3 sentences>
- Total ARR in window
- Top 3 highest-movability accounts (named) with one-line "why this one"
- The single biggest collective opportunity (e.g., "5 of 15 share the same expansion play and could be sprinted together")

---

## Top 15 — Priority Ranked

| # | Account | Renewal | ARR | Risk / Expansion | Movability | Primary play |
|---|---------|---------|-----|------------------|------------|--------------|
| 1 | ...     | ...     | ... | R4 / E5          | 0.87       | Save-into-expansion |
| 2 | ...     | ...     | ... | R3 / E4          | 0.81       | Pure expansion |
| 3 | ...     | ...     | ... | R5 / E2          | 0.74       | Save-only |
| ... |

---

## Per-Account Deep Dives (top 5-7, with full Risk + Expansion sections)

### <Account> — Renewal <date> · ARR $<amt> · Movability <score>

**Tier:** <enterprise/mid/SMB> | **Account team member:** <discovered org-bespoke field>
**Risk Level:** <X/5> · **Expansion Readiness:** <X/5>

#### Top Risks (from Risk Analysis)
- **[High] <risk title>** — <signal type tags>. Timeline urgency: <text>.
  *Evidence:* `comm_...`
- **[Medium] <risk title>** — ...

#### Top Expansion Opportunities (from Expansion Analysis)
- **<Opportunity name>** (Category: <cross-sell/services/upsell>, AI confidence: <H/M/L>, Budget: <P/U/C>)
  Action plan: 1. ... 2. ... 3. ...
  Decision maker: <named>
- **<Opportunity name>** — ...

#### Recommended 90-Day Play
<3-5 sentences combining the risk playbook and expansion action plan into a single sequenced narrative>
<Tag: SAVE / EXPAND / SAVE-INTO-EXPAND>

#### Key Stakeholders to Engage
- <Name>, <title>, <sentiment> — <engagement approach>
- ...

---

## Cross-Cohort Plays

Patterns across the top 15:

1. **<Theme>** (<count> accounts) — <named opportunity or risk type that recurs>
   - <account>, <account>, <account>
   - Coordinated play: <one-sentence org-level move>

2. **<Theme>** (<count> accounts) — ...

---

## Resource Allocation Recommendation

- **Executive touch needed (<count> accounts):** <names> — exec sponsor outreach this week
- **CSM-led save sprint (<count> accounts):** <names> — focused weekly cadence
- **AE-led expansion play (<count> accounts):** <names> — commercial conversation
- **Watch + protect (<count> accounts):** <names> — low-touch maintenance
```

### Format adaptation

- **Cowork:** lead with the ranked-card view (top 15 with movability score badges); expandable per-account cards for deep dives.
- **Code:** full markdown to stdout + artifact at `renewal-priority-plan-<date>.md`.

---

## Step 7: Optional follow-on actions (approval-gated)

After review, offer:
- **Create CTAs** for the top 15 accounts (Renewal Priority playbook)
- **Schedule reviews** with named executive sponsors via Calendar MCP
- **Save the plan to a notes destination** of the user's choice
- **Generate exec-friendly slide deck** via `gainsight-decks` plugin

Nothing posts without explicit user approval per item.

---

## Edge cases

| Situation | What to do |
|---|---|
| User wants narrower window (next 30 days only) | Tighten Step 1 filter. May surface <15 accounts — process all. |
| Renewal window has 200+ accounts | Apply tier filter in Step 3 to narrow before scoring. |
| Risk Analysis empty for an account | Use AI Summary fallback + flag "Limited Staircase signal" in score (lower confidence). |
| Expansion Analysis empty for an account | Score expansion component as 0; the account becomes save-only candidate. |
| Account has high risk (5/5) but no Risk Analysis surfaced | Risk Level 5 with no analysis usually means active churn. Move to closeout queue; not a save candidate. |
| MCP returns empty on retry | Note in output, move on. Don't block the run. |
| User wants <15 accounts (e.g., "just my top 5") | Honor it — runtime drops proportionally. |

---

## What this enables

1. **Plugin synthesis is real.** Combines Staircase Risk + Staircase Expansion + Gainsight commercials into a single ranked output that neither system gives you alone.
2. **The "save-into-expansion" pattern is a CSM-leadership insight.** Most renewal-prep tools surface one dimension. This combines them.
3. **The output is a real plan, not a report.** Per-account 90-day play, stakeholder engagement approach, cross-cohort patterns, resource allocation recommendation.

---

## Sources

- `references/staircase-analyst-data-models.md` — full Risk + Expansion query templates
- `references/staircase-advanced-patterns.md` — long-list-then-prioritize workflow
- `references/gainsight-mappings.md` — Gainsight company + relationship field names

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

Save-into-expansion candidates get merge-classification-driven CTA structure: Save-then-Expand → Risk CTA (primary) + Opportunity CTA (secondary, post-save). Skeptical Read → Risk CTA only. Expansion-as-Save → Opportunity CTA. Classification labels stay INTERNAL. Drop the "movability score" or "composite priority" labels from customer-facing fields. Translate the strategic insight into stakeholder-state language. Tasks within each CTA carry the per-account action playbook: Risk Analysis findings translated into prep tasks, Expansion Analysis translated into outreach drafts.

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
