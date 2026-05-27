---
name: gainsight-account-workspace
description: Single-account workbench for CSMs — "work on [account]," "what should I do for [account]," "drive [account] forward." Pulls everything you need for one account, recommends next moves, drafts updates you approve before anything posts.
user_type: ic
---

# Gainsight Account Workspace

## Discovery

**Auto-trigger phrases:**
- "work on [account]"
- "what should I do for [account]"
- "open [account]" / "pull up [account]"
- "drive [account] forward"
- "[account] situation" / "where are we with [account]"

**Validation history:** The "everyday workbench" companion to gainsight-meeting-processor (post-call) and gainsight-account-handoff-onboarding (one-time-for-a-handoff). The highest-frequency working surface in the plugin — touches all three Gainsight write paths (CTAs, Timeline, SP updates).

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

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
- `../gainsight-cs-mcp-expert/references/write-path-patterns.md` — canonical CTA + Task + Timeline + SP recipes with HTML templates
- `../gainsight-cs-mcp-expert/references/anti-patterns.md` — G3.1-G3.11 gotchas, custom field requirements, HTML formatting

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)

**Rendering discipline (for Cowork app-feel):**
- `../mcp-app-design/references/patterns.md` — tab structure, action tee-up sequence, preference question cards, working mode picker, color/badge semantics

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

The daily workbench for a CSM working a single account. Less time-boxed than the meeting processor (which handles one call) and less front-loaded than the handoff plan (which is a one-time briefing). This is **the skill you run when you're about to spend 30 minutes on an account and want to land changes in Gainsight before you close the tab.**

## Step 0: Resolve and load

```
A. staircase_account_lookup(account_name) → account_id
B. gainsight resolve_customer(search_name) → company GSID + relationships
```

If multiple relationships, default to Company-level. Surface options for the user to focus.

## Step 1: Parallel state load

```
C. gainsight fetch_cta_list (DueDate >= today-90d, IsClosed=false)
   → open CTAs with status, priority, type, owner, due date
   ⚠️ Always date-filter to keep payload bounded
D. gainsight fetch_success_plan_list (CompanyId, IsClosed=false)
   → active plans with PercentComplete, OverdueCtas
E. gainsight fetch_timeline_activity_list (recent 5-10)
   contextual_user_query="recent communications, decisions, commitments for <account>"
   ⚠️ Soft-fail expected; degrade gracefully if it returns error
F. gainsight run_query on company (Name, ARR, RenewalDate, Stage, Tier, IndustryName, SegmentId)
   → commercial backbone
G. staircase_analyze_account(account_id, query="
   Current state of <Account>: top 2-3 risks, sentiment trajectory,
   stakeholder shifts in last 30 days, open commercial discussions,
   expansion signals, anything urgent the CSM should act on this week.
   Cite evidence IDs.")
```

## Step 2: Situation read

Synthesize a **30-second account read** before any action proposals:

```
> <Account> · ARR $<amt> · Renewal <date> (<N days out>) · Stage <stage>
> Staircase sentiment: <trajectory in plain language>
> Open CTAs: <count> (<overdue>) · Active Success Plans: <count> (<%>complete avg)
> What's hot right now: <1-2 sentence narrative grounded in Staircase + CTA freshness>
```

## Step 3: Propose next moves

Group recommendations into 3 buckets. **Do not exceed 6 total recommendations** — the point is decisive action, not an overwhelming list.

### A. CTA dispositions (1-3)
For each open CTA, decide:
- **Update**: change status, add a comment, push due date, change priority
- **Close**: mark resolved with a closure note
- **Escalate**: bump priority or reassign owner
- **Hold**: explicitly defer with a reason

Each recommendation includes the **specific edit** (status → "Work in Progress", comment text drafted, etc.) and the evidence/rationale.

### B. Success Plan objective updates (1-2)
For each active plan with objectives touched by recent activity or Staircase signal:
- Status change (On Track / At Risk / Off Track / Complete)
- Next step text
- Comment with attribution

### C. New activity to log (1-2)
- Timeline activity drafted from recent Staircase synthesis
- Optional: new CTA proposed if an unaddressed risk/opportunity surfaced

## Step 4: Present the workbench

**Cowork rendering:** Surface as a tabbed app per `mcp-app-design/references/per-skill-mappings.md` (look up this skill's chrome) (4 tabs: State / Recommended Actions / Existing Work / Briefing). Lead with the header card (account stats), never with prose. Use sortable tables + action tee-up sequence (one card at a time, approve/edit/skip buttons). Inline choice cards for preference questions. NEVER dump a markdown wall.

**Code fallback:** Scannable markdown — structured headers, emoji-badged tables, batch-mode action queue with approval syntax.

### In Claude Cowork
A multi-tab card:
- **Now** tab: the 30-second read + headline recommendation
- **CTAs** tab: each CTA with proposed edit and a checkbox
- **Success Plans** tab: each plan with proposed updates
- **New Activity** tab: drafted Timeline content + optional new CTA
- **Approve & Apply** footer button — applies all checked items at once

### In Claude Code
Full markdown to stdout + artifact at `account-workspace-<account>-<date>.md`. Each section ends with a clear approval prompt:

```
Approve to apply:
[A1] Update "Renewal Risk" CTA: status → "Work in Progress", append comment
[A2] Update "Launch <product>" objective: status → "At Risk"
[B1] Log Timeline activity: "Working session <date> — ..."

Reply with `approve A1,A2,B1`, `approve all`, or `edit A1` to revise.
```

## Step 5: Apply on approval

For each approved item:
- CTA updates → `manage_cockpit_actions(action="update", ...)`
- Success Plan updates → `manage_success_plan_actions(action="update", ...)`
- New Timeline activity → `create_timeline_activity(...)`
- New CTA → `manage_cockpit_actions(action="create", ...)`

Confirm each post with the resulting Gsid and a one-line acknowledgement.

## Step 6: Wrap-up

End with a brief follow-on suggestion: "Now run `gainsight-meeting-processor` after your <next meeting>" or "Schedule a renewal-prep working session for <date>." Short, actionable.

## Edge cases

| Situation | What to do |
|-----------|------------|
| No open CTAs | Note in situation read. Suggest creating an Activity-type CTA from Staircase signal |
| 50+ open CTAs | Show top 10 by recency + priority. Flag "CTA hygiene" as itself a recommendation. |
| No active success plan | Note in situation read. Suggest creating one if renewal < 120 days out. |
| Timeline fetch fails | Note in section, proceed without it |
| Staircase analyze returns thin data | Lower confidence on the situational read; lean more on Gainsight data |
| User wants to skip recommendations and just see state | Run Step 2 + show all raw data, skip Steps 3-5 |

## Cross-skill links

- After a customer call → run `gainsight-meeting-processor`, then `gainsight-account-workspace` to action what came out
- New CSM on this account → run `gainsight-account-handoff-onboarding` once, then `gainsight-account-workspace` as the daily companion
- Account looking at-risk → `gainsight-account-workspace` is where the CSM does the actual save work after `gainsight-exec-renewal-radar` (or `_experimental/staircase-at-risk-renewals`) surfaces the account

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

Multi-write context — all three write paths possible. Apply gates consistently. Most common pattern: drafting an update on existing artifacts vs creating new. **Cleanup discipline matters most here** — always fetch existing artifacts FIRST, surface stagnant items to the user with cleanup recommendations, then propose new writes. A clean working surface enables real focus.

### Failure modes from prior sessions to avoid

- **Action content in CTA description instead of Tasks** → CTA description stays TLDR; actions become Tasks
- **Standalone CTA that belongs under an active SP** → attach via `success_plan_id` (create) or `CtaGroupId` (update)
- **Creating SP + CTAs but skipping the Timeline Update context anchor** → always post the Update activity attached to the SP
- **Hardcoding picklist values** instead of `prepare_cta` / `prepare_sp` discovery
- **Putting draft email in CTA Comments** instead of Task description

Full anti-pattern catalog: `_shared/gainsight-output-best-practices.md` §10.

---

## Learnings

`.learnings.md` — populated after first real-account test (build-tested, real-account test deferred to next session).
