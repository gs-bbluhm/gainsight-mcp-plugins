---
name: gainsight-no-qbr-ebr-scheduler
description: Surface No-QBR accounts and draft personalized EBR-scheduling outreach anchored on account-specific context (risks, expansion signals, themes). Chains into QBR prep after scheduling.
user_type: ic
---

# No QBR → EBR Scheduler

## Discovery

**Auto-trigger phrases:**
- "schedule QBRs"
- "EBR outreach"
- "which accounts need a QBR"
- "No QBR pulse"
- "set up business reviews"
- "QBR scheduling assistant"

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas (15-cap, OR not supported, determinism)
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Summary, Risk, Expansion — used per-account in Step 2 EBR-context fan-out)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)
- `../gainsight-cs-mcp-expert/references/write-path-patterns.md` — canonical CTA + Task (Email type) + Timeline recipes with HTML templates
- `../gainsight-cs-mcp-expert/references/anti-patterns.md` — gotchas, custom field requirements, HTML formatting

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

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

For the CSM moment: when the No-QBR insight fires for an account, the skill drafts a personalized EBR-scheduling email using what Staircase knows about the account right now — recent risks, active expansion conversations, current themes — and chains into QBR prep + focus plan once the EBR is on the calendar.

The No QBR query returns accounts with QBR-pain narrative per account. Per-account AI Summary + Risk Analysis + Expansion Analysis provide rich EBR-pitch context. Cleanly bounded use case — small pool, high quality.

---

## Team-member field discovery (CRITICAL)

Staircase has a standard `Owner` field that's consistent across orgs. Most orgs also have custom team-member fields (e.g., `CSM`, `Account Manager`, `Renewal Owner`, or an org-bespoke variant) — these must be discovered via the Gainsight `get_object_metadata("company")` call. The `gainsight-mcp-setup` skill walks the user through this discovery once and caches the field name in the user profile.

In any query in this skill that filters by a CSM, substitute `<team-member-field>` with the field discovered during setup.

---

## Step 0: Scope

User specifies either:
- **Specific account** — "draft an EBR email for <account>"
- **CSM book** — "all No-QBR accounts in my book"
- **Full portfolio** — "all No-QBR accounts" (CS leadership view)

---

## Step 1: Pull No-QBR accounts

```
staircase_ask("Which of my accounts are flagged as No QBR?")
   → accounts with QBR-pain narrative + evidence IDs

(Optional filter to CSM's book:)
staircase_ask("List the accounts where the <team-member-field> is <CSM Name>...")
→ client-side intersect
```

---

## Step 2: For each No-QBR account, pull EBR-pitch context

In parallel batches (limit 5 at a time):

```
staircase_account_lookup(name=<account>) → account_id
staircase_analyze_account(account_id, query="
   For an Executive Business Review (EBR) scheduling pitch, return:
   - Top 2 active themes the customer cares about right now
   - Most recent risk signal or open thread (if any)
   - Most recent expansion signal or buying-intent (if any)
   - Named decision maker or executive sponsor (best person to invite)
   - One specific value-realization moment from the last 60 days that
     could anchor the EBR conversation
   - Evidence IDs supporting each.")
```

Plus Gainsight enrichment per account:
```
gainsight resolve_customer(name=<account>) → company GSID
gainsight run_query on company:
  select: Arr, ARR__gc, RenewalDate, Staircase_Last_Engagement__gc,
          Staircase_AI_Renewal_Analysis__gc
  where: CompanyId IN (<resolved GSIDs>)
```

---

## Step 3: Draft personalized EBR-scheduling email per account

Use the established email-format conventions. Each email anchors on the account-specific context Staircase surfaced.

### Email template

```
Subject: <Customer> — proposing an Executive Business Review

Greeting: Good <morning/afternoon>, <FirstName>,

Opening (2-3 sentences):
  "I wanted to propose we get an EBR on the calendar in the next
  few weeks. Specifically — <one-sentence why now, anchored on the
  Staircase context: an active expansion conversation, a recent
  risk thread, or a strategic theme they're actively working>.
  This feels like the right moment to step back and align on
  outcomes, strategic direction, and the path to renewal."

Suggested agenda (3-5 bullets — anchored on the EBR pitch context):
  - Review of <specific value moment Staircase identified>
  - Discussion of <recent theme they're working on>
  - Roadmap alignment on <area they've shown interest in>
  - <Risk thread, if active — frame as "addressing X together">
  - Next-quarter priorities

Logistics (1-2 sentences):
  "I'd suggest a 60-90 minute session. <FirstName>, would you have
  capacity in <suggested window>? I'm happy to send a few specific
  time options."

Closing line:
  "Looking forward to setting time aside to think strategically
  with you."
```

### Tone notes
- Anchor on Staircase context — don't propose generic agendas
- Reference the specific value moment, expansion thread, or risk topic
- Make the executive feel the meeting is for THEM (their priorities, their context)
- Keep agenda items to 3-5 — over-stuffing signals lack of focus
- Length: 8-12 sentences max — executives don't read long EBR pitches

---

## Step 4: Present the packet

**Cowork rendering:** Surface as a tabbed app per `mcp-app-design/references/per-skill-mappings.md` (look up this skill's chrome) (2 tabs: Accounts Needing EBR / Scheduled). Lead with the header card (EBR pipeline stats), never with prose. Use sortable tables + per-account scheduling card (one at a time, approve/edit/skip buttons). Inline choice cards for EBR scope selection. NEVER dump a markdown wall.

**Code fallback:** Scannable markdown — structured headers, emoji-badged tables, batch-mode action queue with approval syntax.

### Output structure

```markdown
# EBR Scheduling Pulse — <date>

## No-QBR accounts (<count>)

| # | Account | $<ARR> | Renewal | Last engaged | Champion / Sponsor | Why this EBR now |
|---|---------|---------|---------|---------------|---------------------|------------------|
| 1 | <account> | <ARR> | <date> | <date> | <name> | <one-line context from Staircase> |
| 2 | <account> | <ARR> | <date> | <date> | <name> | <one-line context from Staircase> |
| ... |

## Per-account EBR scheduling drafts

### 1. <Account>
**Why this EBR matters now:** <2 sentences from Staircase context>
**Recommended invitee:** <named executive sponsor>
**Suggested duration:** 60-90 min
**Anchor agenda item:** <specific value moment or theme>

**Drafted email:**
```
Subject: <Account> — proposing an Executive Business Review
[Full email body, ready to copy]
```

**Approve & post:**
- [ ] Create Gmail draft
- [ ] Edit before posting
- [ ] Skip this one

### 2. <Account>
...
```

### Format adaptation

- **Cowork:** per-account card with the email draft + edit/copy buttons; account context badges (ARR, renewal, sponsor) visible.
- **Code:** full markdown to stdout.

---

## Step 5: Optional close-out (approval-gated)

- Create Gmail drafts via `create_draft`
- Create CTAs in Gainsight: "EBR scheduling outreach sent — follow up in 7 days if no response"
- Log Timeline activity per account noting the outreach
- Once an EBR is scheduled on the calendar, chain into `gainsight-account-workspace` or future `gainsight-qbr-prep` skill for the prep work

---

## Step 6: Future chain — QBR prep + focus plan (post-scheduling)

When the EBR is on the calendar (detected via Calendar MCP or user input):

1. Run `gainsight-account-workspace` for the account → focus plan
2. Pull the full Risk Analysis + Expansion Analysis with all sections
3. Draft a one-pager pre-read with: agenda, account context, recent wins, open risks, expansion opportunities, success-plan progress
4. Generate slides via `gainsight-decks:branded-deck` (existing plugin) for the EBR presentation itself

This chain is the "EBR end-to-end" workflow — schedule, prep, present. The current skill handles only the scheduling motion; the prep + present steps reuse existing skills.

---

## Edge cases

| Situation | What to do |
|---|---|
| Account has had a QBR recently but is still flagged | Note the timing mismatch — may be flag refresh lag. Surface to user. |
| Executive sponsor unknown | Surface "needs sponsor identification" — recommend running the stakeholder-connect skill first |
| Renewal in next 30 days | Re-frame email as "renewal-prep EBR" rather than generic EBR |
| Account has critical risk flagged | Frame agenda around addressing the risk — don't pretend it's a routine review |
| No expansion or risk context | Default to value-realization + roadmap alignment — generic but appropriate |

---

## Why this matters

Every CSM has the "I owe these accounts a QBR" Post-it. The plugin pulls the accounts where Staircase has flagged No QBR, drafts a personalized EBR scheduling email per account anchored on what's actually live in their conversations, and surfaces the right executive sponsor to invite. The CSM has drafts in seconds instead of writing each email from scratch. Once the EBR is scheduled, the next skill in the chain runs the prep.

---

## Sources

- `gainsight-meeting-processor/references/email-format.md` — tone + structure
- `staircase-analyst-data-models.md` — Risk + Expansion query templates

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

EBR-scheduling CTA. Task description carries the full draft EBR-pitch email (personalized per account context, not boilerplate). Chain into QBR prep after scheduling lands. Verify Before Sending flags every meeting-specific commitment (proposed dates, room/Zoom link, agenda). EBR pitch defaults to PROPOSAL grade ("I'd like to propose a quarterly review"), not COMMITMENT grade ("Let's schedule for Tuesday at 10am"). CSM finalizes timing with the customer; the plugin drafts the invitation.

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
