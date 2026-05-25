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

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Core rules:

1. **User approval gate** before customer-facing writes (every EBR pitch is customer-facing).
2. **Commitment discipline.** Email Tasks carry "Verify Before Sending" — every meeting commitment (proposed dates, attendees, agenda) needs CSM validation.
3. **HTML formatting** in rich-text.
4. **Teammate-facing, customer-focused.** No internal classification labels in customer surfaces.
5. **Evidence as readable references.**
6. **Reuse-vs-create.** Fetch existing.
7. **Cleanup discipline.**
8. **Org-specific discovery** of CTA Types (some orgs use "EBR" Type; others use Lifecycle + EBR Reason).

### Skill-specific emphasis

EBR scheduling outreach goes into Email-type Task descriptions. Verify Before Sending flags every meeting-specific commitment (proposed dates, room/Zoom link, agenda). EBR pitch defaults to PROPOSAL grade ("I'd like to propose a quarterly review"), not COMMITMENT grade ("Let's schedule for Tuesday at 10am"). CSM finalizes timing with the customer; the plugin drafts the invitation.

---

## Learnings

See `.learnings.md`.
