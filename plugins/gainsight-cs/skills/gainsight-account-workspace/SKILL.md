---
name: gainsight-account-workspace
description: Daily working session on a single account. Loads Gainsight (CTAs, success plans, Timeline, ARR, renewal) and Staircase situational context, recommends next moves, drafts updates, posts only on approval. The everyday workbench between meetings.
user_type: ic
---

# Gainsight Account Workspace

## Discovery

**Auto-trigger phrases:**
- "work on [account]"
- "what should I do for [account]"
- "open the workspace for [account]"
- "show me the [account] situation"
- "move [account] forward"

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

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Core rules:

1. **User approval gate** before customer-facing writes.
2. **Commitment discipline.** PROPOSAL language. Email Tasks carry "Verify Before Sending."
3. **HTML formatting** in rich-text. `<p>`, `<ul>`, `<ol>`, `<strong>`, `<br>`.
4. **Teammate-facing, customer-focused.** No internal classification labels in customer surfaces.
5. **Evidence as readable references.**
6. **Reuse-vs-create.** Fetch existing first.
7. **Cleanup discipline.** Surface stagnant artifacts before creating new.
8. **Org-specific discovery.**

### Skill-specific emphasis

This skill touches all three Gainsight write paths (CTAs, Timeline, Success Plan updates) and is the highest-frequency working surface in the plugin. **Cleanup discipline matters most here** — always fetch existing artifacts FIRST, surface stagnant items to the user with cleanup recommendations, then propose new writes. A clean working surface enables real focus.

---

## Learnings

`.learnings.md` — populated after first real-account test (build-tested, real-account test deferred to next session).
