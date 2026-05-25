---
name: gainsight-daily-cockpit
description: CSM daily focus surface — Gainsight new/open CTAs (what needs me) + Staircase persistent signals (what's hot) + per-account analyze drill-downs (top 3 plays). Composite pattern Gainsight=now + Staircase=hot + analyze=play.
user_type: experimental
disable-model-invocation: true
---

# Gainsight Daily Cockpit

## Discovery

**Auto-trigger phrases:**
- "build my daily cockpit"
- "what should I focus on today"
- "what needs me"
- "morning briefing"
- "daily CSM standup"
- "what's hot in my book"

**Validation history:** Validated against real Gainsight data — `fetch_cta_list` with `CreatedDate >= today-2d` returns a manageable batch of new CTAs with deflection, churn risk, and retention-planning context. The composite pattern (Gainsight=now + Staircase=hot + analyze=play) holds. Currently flagged experimental — may consolidate with `gainsight-account-workspace` later.

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke; the standard Staircase `Owner` field is universal, but most orgs also have custom team-member fields like `CSM`, `Account Manager`, or `Renewal Owner` that must be discovered via `get_object_metadata("company")` — the setup skill caches the discovered field name in the user profile)

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)

---

The CSM's morning surface. Three sections, one query: **what needs me today, what's strategically hot, and the top 3 plays.**

Built on the validated composite pattern: Gainsight provides the time-bounded substrate (new CTAs, open risks, dates, owners, ARR), Staircase provides the persistent strategic layer (what's expanding, what's at risk across the book), and per-account analyze gives the play for the surfaced accounts.

**Validated against real-org data** — `fetch_cta_list` with `CreatedDate >= today-2d` returns the day's new CTAs with deflection, churn risk, and retention-planning context. The composite pattern (Gainsight=now + Staircase=hot + analyze=play) holds at portfolio scale.

---

## Step 0: Inputs

Mostly inferred. User can override:
- **Owner scope** — default is current user (CURRENT_USER literal in Gainsight). User can specify "my whole team" or another CSM's name.
- **Date window** — default last 2 days. "Daily" can be last 24h, "weekly" last 7d.
- **Tier filter** — default all. User can scope to "enterprise only" / "top tier" / a specific segment.

---

## Step 1: Pull "what needs me" (Gainsight, time-bounded)

Run these in parallel:

```
A. fetch_cta_list — new CTAs created in the window
   where: OwnerId EQ CURRENT_USER (or filtered owner)
          AND CreatedDate GTE <today-2d>
          AND IsClosed EQ false
   page_size: 25
   ⚠️ MANDATORY CreatedDate filter (token budget guard)

B. fetch_cta_list — open Risk-type CTAs (regardless of age) that need attention
   where: OwnerId EQ CURRENT_USER
          AND IsClosed EQ false
          AND TypeId__gr.Name EQ "Risk"
          AND DueDate LTE <today+14d>
   page_size: 15

C. fetch_cta_list — high-priority overdue CTAs
   where: OwnerId EQ CURRENT_USER
          AND IsClosed EQ false
          AND DueDate LT <today>
          AND PriorityId__gr.Name IN ("High", "Critical")
   page_size: 10

D. fetch_timeline_activity_list — recent customer-initiated activity (last 24h)
   contextual_user_query="customer-initiated communications in the last 24 hours"
   ⚠️ Soft-fail expected
```

---

## Step 2: Pull "what's strategically hot" (Staircase, persistent signals)

Two parallel Staircase queries — these reason about persistent signals, not time deltas. **Don't ask Staircase "what changed yesterday" — that returns empty.**

```
A. staircase_ask("Examine 15 of my customers showing the strongest
   expansion signals or new product interest in the last 60 days.
   For each, summarize: account, top opportunity, readiness, one
   named decision maker.")

B. staircase_ask("Examine 15 of my customers with the highest
   current risk signals. For each, summarize: account, top risk,
   severity, one named stakeholder driving the risk.")
```

Verified pattern: 15-account list+summarize with structured columns reliably returns rich rows with evidence IDs.

---

## Step 3: Identify the top 3 "plays for today"

Score the union of (Step 1 CTA accounts + Step 2 risk/expansion accounts) by:
- **Urgency** — overdue or due-this-week: +0.4
- **ARR** (when knowable from Staircase or Gainsight): +0.3 normalized
- **Customer-initiated activity in last 24h** (from Step 1.D if it returned): +0.2
- **Combined risk + expansion signal** (account appears in both Step 2 lists): +0.1

Pick the top 3. These are today's "plays."

---

## Step 4: Drill-down the top 3 (parallel `analyze_account`)

For each of the top 3 plays:

```
staircase_account_lookup(name=<account>) → account_id
staircase_analyze_account(account_id, query="
   What's the single most important action for the CSM to take on
   <Account> this week? Include: the precise context, the named
   stakeholder to engage, the recommended approach, and evidence IDs.")
```

Run in parallel.

---

## Step 5: Produce the cockpit

### Output structure

```markdown
# Daily Cockpit — <date> · <CSM name>

## At a glance
- <count> new CTAs since yesterday · <count> overdue · <count> open risk CTAs
- Staircase signal: <count> accounts showing expansion · <count> at-risk
- Customer activity in last 24h: <count> accounts had inbound communication

---

## What needs me (today)

| # | Account | What | Type | Priority | Due | Notes |
|---|---------|------|------|----------|-----|-------|
| 1 | <account> | "<concise CTA reason / risk narrative>" | Risk | High | Today | <ARR or deflection context> |
| ... | | | | | | |

(Top 5-10 from Step 1, ranked by urgency)

---

## What's strategically hot (this week)

### At risk
| Account | Risk | Severity | Named stakeholder |
|---------|------|----------|---------------------|
| ... | | | |

### Expanding
| Account | Top opportunity | Readiness | Decision maker |
|---------|------------------|-----------|------------------|
| ... | | | |

(Top 5 each from Step 2)

---

## Top 3 plays for today

### 1. <Account>
**Why this one:** <one-sentence rationale combining urgency + signal>
**The play:** <2-3 sentences from analyze_account drill-down>
**Engage:** <named stakeholder> via <channel>
**Evidence:** <ID list>

### 2. <Account>
...

### 3. <Account>
...

---

## What can wait
<3-5 lines summarizing the rest — accounts/CTAs not prioritized for today
but worth a glance>
```

### Format adaptation

- **Cowork:** lead with the "at a glance" line + top 3 plays as the focused card. "What needs me" + "What's hot" as expandable sections below. Optimize for 30-second scan.
- **Code:** full markdown to stdout + optional file artifact (filename like `daily-cockpit-<date>.md`).

---

## Step 6: Optional close-out actions (approval-gated)

- Mark CTAs the user identifies as stale → close them
- Bump priority on accounts in the top-3 plays that don't have a CTA yet
- Save the cockpit to Notion for tomorrow's comparison

---

## Edge cases

| Situation | What to do |
|---|---|
| Less than 5 new CTAs in window | Show fewer; don't pad with stale items |
| No risk or expansion signals from Staircase | Note explicitly. Could indicate quiet week or thin Staircase data. |
| User wants weekly cockpit not daily | Stretch window in Step 1 to 7 days, same Staircase queries |
| `fetch_cta_list` returns large payload | Confirm `CreatedDate` filter is set; reduce page_size further |
| Staircase queries return empty | Skip the "what's hot" section; cockpit still works from Gainsight CTAs alone |
| User wants a different CSM's cockpit | Replace CURRENT_USER with named owner (resolve via `resolve_user`) |

---

## Why this matters

The CSM's morning question is "what should I focus on today." That's three questions, not one: what's urgent in my queue, what's strategically hot in my book, and what's the play. This skill answers all three in a single pass. The same composite pattern — Gainsight for now, Staircase for hot, analyze for the play — powers most of the cross-account skills in this plugin.

---

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Core rules:

1. **User approval gate** before customer-facing writes.
2. **Commitment discipline.** PROPOSAL language. Email Tasks carry "Verify Before Sending."
3. **HTML formatting** in rich-text.
4. **Teammate-facing, customer-focused.** No internal classification labels in customer surfaces.
5. **Evidence as readable references.**
6. **Reuse-vs-create.** Fetch existing first.
7. **Cleanup discipline.** Surface stagnant CTAs every morning — the daily cockpit is the highest-frequency place to enforce cleanup.
8. **Org-specific discovery.**

### Skill-specific emphasis

Primarily READ-oriented (fetches CTAs + Staircase signals to surface what needs attention today). New CTA creation is rare. When updates happen, they're status changes or comment additions on existing CTAs as actions complete. Don't proliferate new artifacts. The daily ritual advances existing work, not "create more work." Use this skill as the daily cleanup checkpoint: surface what's stagnant and recommend closure.

---

## Learnings

See `.learnings.md`.
