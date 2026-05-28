---
name: gainsight-meeting-processor
description: Post-call workflow for CSMs after a customer sync — "I just had a call with [customer]," "process my [customer] call," "[customer] meeting recap." Turns the meeting into a Gmail recap, Timeline entry, risk CTA, and SP updates.
user_type: ic
---

# Gainsight Meeting Processor

## Discovery

**Auto-trigger phrases:**
- "I just had a call with [customer]"
- "process my [customer] call"
- "post-call for [customer]"
- "[customer] sync recap"
- "[customer] meeting recap"
- "recap my [customer] call"

**Why this matters:** Headline workflow that exercises both Staircase AI and Gainsight CS MCPs together. The Staircase fan-out differentiates this from transcript-only post-call tools. Risk and sentiment claims are grounded in 60-90 days of communication data, not just the call.

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

Post-call automation for Gainsight CSMs. Takes a customer meeting and produces a complete review packet: recap email draft, Gainsight Timeline activity, risk CTA (if warranted), success-plan updates, action items, and win quotes — all reviewed before anything is posted to Gainsight or sent from Gmail.

**The golden rule:** generate every deliverable, present them for review, do not post or send anything until the user approves item-by-item.

This skill is the headline workflow that exercises **both Staircase AI and Gainsight CS MCPs together**. The Staircase fan-out is what differentiates it from transcript-only post-call tools — risk and sentiment claims are grounded in 60-90 days of communication data, not just the call we just had.

---

## Step 0: Inputs

Ask the user only for what you can't figure out:

1. **Customer name** — required
2. **Call date / time** — optional, defaults to "most recent"
3. **Call recorder source** — optional, defaults to checking sources in priority order (see Step 1)

If the user says "use my Notion meetings", "pull from Zoom", "I'll paste it", honor that.

---

## Step 1: Find the Transcript (Modular Adapter)

Try sources in this priority order. Stop as soon as you find a usable transcript:

1. **Already in the conversation** — pasted directly. Use it.
2. **Notion meeting notes** — the most reliable source when the Notion meeting connector is active.
   - Tool: `notion-search` with `query=<customer name>` + `filters.created_date_range.start_date=<3-7 days ago>`. **Do not use `notion-query-meeting-notes` with `account_name` — that returns generic meeting list, not customer-matched results.**
   - Once you have the page, fetch with `notion-fetch` using `include_transcript=true`. **NOTE:** the outer meeting page may return `Transcript omitted` — the real transcript lives at the URL fragment inside `readOnlyViewMeetingNoteUrl` (the part after `#`). If transcript is omitted on first fetch, extract the fragment ID and call `notion-fetch` again with that ID.
3. **Zoom** — `search_meetings(query=<customer name>, window=this_week)` → take most recent → `get_meeting_assets(uuid)` for transcript + AI summary + participants.
4. **Granola, Fireflies, Gong, etc.** — if their MCPs are loaded in the session, use them. Check tool list before assuming.
5. **Ask the user to paste** — last resort.

Extract: full transcript text, meeting date, participant names + emails, call type (kickoff / planning / platform session / QBR / at-risk / renewal / escalation / executive / cadence / ad-hoc / closeout).

**Recording link & passcode:** use `[INSERT RECORDING LINK]` and `[INSERT PASSCODE]` placeholders. The user verifies and inserts them manually.

---

## Step 2: Parallel Context Fan-Out

After the transcript is in hand, fire these in **parallel** — do not wait for one before starting the next.

**Use the empirically-validated query templates from `references/staircase-query-patterns.md`.** They beat ad-hoc phrasing across 6 months of testing.

```
A. staircase_account_lookup(name=<customer>)
   → account_id, confidence
   ⚠️ Common name variants typically resolve high-confidence on
      first call. If LOW confidence or no match: retry with suffix
      variants (Inc, LLC, Corp, Software, comma-separated). If
      multiple HIGH confidence results come back (e.g. a parent
      and a subsidiary), ask the user which account before
      proceeding.

B. staircase_analyze_account(account_id, query="
   Summarize <Customer>'s last 90 days including risks, sentiment,
   and renewal readiness. Include named stakeholders, evidence IDs,
   and any explicit churn or expansion signals.")
   → AI-synthesized narrative + evidence[] with 5 items max
   ⚠️ Parameter is `query`, NOT `question`.
   ⚠️ Use action-oriented phrasing ("Summarize", "Draft", "Identify").
      Action verbs outperform information-retrieval phrasing ("What
      are the current risks...") empirically.

C. staircase_analyze_account(account_id, query="
   Who are the key stakeholders at <Customer> and their engagement
   patterns? Identify champions, decision-makers, detractors, and
   recent stakeholder shifts with evidence IDs.")
   → Stakeholder map

D. gainsight resolve_customer(search_name=<customer>)
   → Company Gsid (and any relevant Relationship Gsids)
   ⚠️ Multiple relationships are common. Pick the one matching the
      context of the call (Product type for product-specific calls,
      Onboarding for kickoff/implementation, etc.). When in doubt,
      use the Company Gsid and note the relationship choice for
      the user to confirm.

E. gainsight fetch_cta_list — open CTAs
   where: CompanyId EQ <company_gsid> AND IsClosed EQ false
          AND DueDate GTE <today-90d>
   ⚠️ MANDATORY DueDate filter. Without it, a busy account can
      return 50k+ characters and blow the token budget. The
      `select=` parameter is ignored by the API. Date filter is
      the actual load-control.
   ⚠️ Set page_size=25.

F. gainsight fetch_success_plan_list — active plans
   where: CompanyId EQ <company_gsid> AND IsClosed EQ false

G. gainsight run_query on gs_company_forecast (Renewal Center) —
   CompanyId EQ <company_gsid>
   → Forecasted renewal amount, GRR/NRR%, churn amount + category,
     modeled-as (Won Flat / Open / Stretch / Lost)
   ⭐ Adds the explicit forecast signal that's missing from the
     transcript and Staircase narrative alone.

H. gainsight fetch_cta_list on gs_opportunity (renewal opps) —
   CompanyId EQ <company_gsid> AND Status IN (open stages)
   → Renewal Stage values like "Assumed Churn (3+ mo Overdue)",
     "More Likely to Churn" surface data-quality / risk-triangulation
     issues even on healthy-looking accounts.

I. gainsight fetch_timeline_activity_list — recent activity (limit 10)
   contextual_user_query="recent communications and meeting notes
   for <customer>"
   where: CompanyId EQ <company_gsid>
   ⚠️ This tool returns "Failed to fetch timeline activities" without
      detail on a meaningful percentage of accounts. Treat as soft-fail.
      Note in reconciliation; do not block the run.

J. Gmail search for prior recaps (optional, for tone calibration)
   query: "from:me to:<customer domain> subject:recap"
```

Cite Staircase evidence IDs (e.g. `comm_Email_19d8ca123fd3a40e`) whenever you make a quantitative or sentiment claim derived from Staircase. Don't fabricate evidence IDs.

---

## Step 3: Process the Transcript with Context Fused In

Read the full transcript. Extract:
- Topics discussed
- Decisions made
- Action items (internal + customer-facing) with owners + due dates
- Win quotes (verbatim customer language flagged as positive — "exactly what we needed", "this is a game-changer", "you've solved X for us")
- Risk signals (customer frustration, blockers, escalations, churn-adjacent language)
- Commercial signals (expansion mentions, renewal questions, competitor mentions)
- Next call / follow-up commitments

**Then fuse with Staircase context.** If Staircase says "sentiment improving but fragile" and the transcript reads as universally positive, **flag the discrepancy explicitly** — Staircase sees 60+ days, the call is one moment. Both are real signal.

When risk surfaced by Staircase isn't addressed in the call, flag it as an open thread.

---

## Step 4: Generate Deliverables

| # | Deliverable | Format | Destination on approval |
|---|-------------|--------|------------------------|
| 1 | **Gmail recap draft** | Plain text email body | `create_draft` in Gmail |
| 2 | **Gainsight Timeline activity** | Subject + activity_type + narrative content | `create_timeline_activity(company_id, ...)` |
| 3 | **Risk CTA preview** (only if risk flagged) | Subject, priority, reason, owner, due date | `manage_cockpit_actions` (create) |
| 4 | **Success Plan objective updates** (only if active plans exist) | Per-objective: status, next step, comment | `manage_success_plan_actions` (update) |
| 5 | **Action item list** | Table: Action / Owner / Due / Notes | Clipboard; optionally per-item CTA |
| 6 | **Win quotes** | Verbatim block with attribution | Reference only |
| 7 | **Staircase reconciliation note** | If transcript and Staircase signal diverge | Inline only |

### Email draft tone & structure

Adapt to call type. See `references/email-format.md` for full templates.

Universal structure (CSM tone — adaptable across QBRs, at-risk calls, and renewal conversations):

- Subject: `[Customer] & Gainsight – [MM/DD/YYYY] – [Call Type] recap`
- Greeting: first names for small/familiar groups, "team" for larger
- Opening: 1-2 sentences, specific to the call (never "thanks for your time")
- Recording block (with placeholders for link/passcode)
- Resources shared (if any)
- Action items by person (named paragraphs, not generic table)
- Scheduling / next steps
- Closing line — single warm sentence
- **No sign-off** (Gmail signature template handles it)

**No em dashes. No emojis. No filler openers.**

### Gainsight Timeline activity content

- **Subject**: `[Call Type] – [MM/DD/YYYY]`
- **Activity Type**: pick from `get_activity_types_config` — common: `Meeting`, `Call`, `Executive Business Review`, `Onboarding Call`. Default to `Meeting` if unsure.
- **Content** (markdown allowed):
  - 1-paragraph narrative summary
  - Wins (bulleted, with quotes)
  - Risks / open threads (bulleted)
  - Decisions (bulleted)
  - Action items (bulleted, with owner names)
  - Staircase context note (1-2 lines summarizing the 60-day sentiment if it adds signal beyond the call)

### Risk CTA

Only create when:
- Risk surfaced in the call AND Staircase confirms or doesn't contradict, OR
- Staircase flagged risk in the last 60 days AND the call didn't address it

Skip CTA creation if:
- Sentiment is universally positive on both sides
- Risk is theoretical / future-state (not current)

### Success Plan updates

Cross-reference active success plans with topics discussed. For each objective touched in the call:
- New status (On Track / At Risk / Off Track / Complete)
- Next step (1 sentence)
- Comment with attribution

Skip if no active success plans.

---

## Step 5: Present the Review Packet

**Canonical rendering reference:** `mcp-app-design/references/per-skill-mappings.md` (this skill's row) + `patterns.md` + `component-library.md`.

Detect surface FIRST. Cowork → tabbed app. Code → scannable markdown. Mode heuristics in patterns.md.

### Cowork rendering (primary optimization target)

**Layout: colored app header + tab nav with counts + Tab 1 (Summary) as DEFAULT landing. NEVER lead with prose. NEVER dump all artifacts inline as one scroll — that's the wall-of-content failure mode codified in `patterns.md` §12 anti-patterns.**

#### Colored app header (always-on, top of viewport)

Render the colored app header component (`component-library.md` §1) with:
- **Icon:** 📞
- **Title:** "Meeting Recap"
- **Persona:** the customer name (e.g., "Bennett Birch Supply")
- **Date:** "Sync · <date> · <duration> · <attendees>"
- **Brand:** `gainsight` (Gainsight CS blue `#1976D2`)

#### Tab navigation with counts

Render the tab nav component (`component-library.md` §4):

```
Summary · Email (1) · Gainsight (N) · Wins (N) · Briefing (N)
```

- "Summary" is the DEFAULT landing tab. No count.
- Email count = number of draft emails (typically 1)
- Gainsight count = Timeline activities + CTAs + SP updates combined
- Wins count = advocacy quotes + Verified Outcomes captured
- Briefing count = reconciliation notes + open observations + flagged gaps

#### Tab 1 · Summary (the default landing — TLDR + actions + signals at-a-glance)

**Render in this order:**

1. **TLDR paragraph** (2-3 sentences max) — what was the call, what came out, what's queued. Example: "35-min sync with Travis Villegas + Nicholas Newman. 23% CTR lift confirmed, bulk-import friction surfaced, sister-brand expansion intro requested. 4 action items, 3 writes queued for Gainsight."

2. **Compact signals strip** (signal-color stripes per `component-library.md` §2 modifiers):
   - Health · <N> · stripe by range (red <40, amber 40-60, green 60+, blue 80+)
   - Sentiment · <N> · same banding
   - Days to renewal · <N> · stripe red (<60), amber (60-120), green (>120)
   - Open CTAs · <N>
   - Active SPs · <N> · stripe red if zero AND renewal <90d

3. **Action items table** (5-7 rows max, more goes in expandable):

   | Action | Owner | Due | Linked artifact |
   |---|---|---|---|
   | <action> | <name> | <date> | → CTA / SP / Email |

   Each row's "Linked artifact" cell is a chip linking to the relevant Gainsight tab card.

4. **Win quote preview** (1-2 lines, expandable to full Wins tab):
   > "<verbatim quote>" — Travis Villegas, Marketing Lead

5. **Primary CTA button** at the bottom: `[ Approve all <N> writes ]` (fast-path for users who skim the tabs and just want to ship)

**Do NOT include guidance prose** ("Review packet is up. Three approval-gated writes queued — use the buttons...") on this tab. The tabs + buttons signal what's available without prose.

#### Tab 2 · Email (the Gmail recap draft)

Render the action proposal card (`component-library.md` §9) with `--email` variant:
- To / CC / Subject lines
- Full email body preview (collapsible if >250 words)
- VERIFY BEFORE SENDING checklist (every external commitment in the email gets a verify bullet)
- `[ Approve & create Gmail draft ] [ Edit ] [ Skip ]`

#### Tab 3 · Gainsight (Timeline + CTA + SP updates consolidated)

Sub-cards within the tab — these are all Gainsight writes so grouping them feels natural:

1. **Timeline activity card** (`--timeline` action card variant): subject, activity_type, content preview, `[ Approve & post ]`
2. **Risk CTA card** (`--cta` action card variant): name, type, priority, owner, due, why-bullets, Tasks (per `component-library.md` §6 drill-down pattern), `[ Approve & create in Cockpit ]`
3. **SP updates card** (`--sp` action card variant, ONLY if active SP exists): per-objective status change + comment, `[ Approve all SP updates ]`

Stacked vertically within Tab 3. Each sub-card stands alone with its own approval state.

#### Tab 4 · Wins (advocacy + Verified Outcome capture)

Two sub-sections:

1. **Advocacy quotes captured**:
   - Each as a callout (`component-library.md` §3, `--success` variant) with quote + attribution + capture-date
   - `[ Save to advocacy library ]` button per quote
   - If a stakeholder qualifies as a Reference Customer candidate (advocacy quote + verified outcome + named): show `[ Flag as Reference Customer candidate ]` button

2. **Verified Outcomes captured**:
   - Each with the concrete value + measurement + stakeholder attribution
   - `[ Save to outcome library ]` per outcome

#### Tab 5 · Briefing (Staircase reconciliation + observations)

Briefing-grade content — context anchors and gap-flagging, not action surfaces:

1. **Staircase reconciliation note** (`component-library.md` §3, `--info` variant):
   - Health / Sentiment delta between Staircase 90-day signal and today's call
   - Explanation of why the numbers diverge (if they do)
   - Evidence references with comm IDs

2. **Plan Info gaps** (where Gainsight company-record fields are sparse):
   - Renewal Risk Summary · empty? Flag.
   - Expansion Opportunity Summary · empty? Flag.
   - Key Outcomes Achieved · empty? Flag.
   - Each gap has a `[ Suggest update for Gainsight UI ]` button (UI write, not MCP).

3. **Open items not in action items**:
   - Customer-side commitments without owner clarity
   - Cross-team escalations needed
   - Each has contextual action button.

### Action tee-up sequence (the key behavioral pattern)

**Do NOT dump all artifacts as one scrollable wall on the landing tab.** The Summary tab gives the at-a-glance picture. Per-artifact details + approvals live in their respective tabs. This is the fundamental tabbed-app design pattern — landing = overview, tabs = depth.

When user approves a write in any tab (Email / Gainsight sub-card / SP / etc.):
1. Sticky pending-action footer (`component-library.md` §10) updates: `2 of 3 approved · [ Review all ] · [ Post all ]`
2. On final approve, all queued writes execute in order: Timeline → CTA → SP updates → email-to-Gmail-drafts
3. Confirmation card with Gsids + links per write that landed

### Code rendering (CLI fallback)

The legacy inline markdown structure still works for Code users. Keep it scannable:

```markdown
# 📞 Meeting Recap — <Customer> · <date>

## TLDR
<2-3 sentence summary>

## Signals
- Health <N> · Sentiment <N> · Days to renewal <N> · Open CTAs <N> · Active SPs <N>

## Action items
| # | Action | Owner | Due | Linked |
| 1 | ... | ... | ... | ... |

## Email recap draft
**To/CC/Subject:** ...

<full body>

## Gainsight writes
1. **Timeline activity** — <subject> [`approve 1`]
2. **Risk CTA** — <name> [`approve 2`]
3. **SP updates** — <objective list> [`approve 3`]

## Wins
- "<quote>" — <stakeholder>
- Verified outcome: <metric>

## Briefing notes
- Staircase reconciliation: ...
- Plan Info gaps: ...

Reply `approve all`, `approve 1,3` (selective), or `edit <#>` to revise.
```

Also write the full packet to `inbox/workshop/meeting-processor-<customer>-<date>.md` for disk access.

---

## Step 6: Approval Gate → Post

Wait for the user's approval signal. Only then call:
- `create_draft` (Gmail)
- `create_timeline_activity` (Gainsight)
- `manage_cockpit_actions` for CTA (if approved)
- `manage_success_plan_actions` for plan updates (if approved)

Report back each post with a confirmation line including the Gsid / draft ID.

---

## Step 7: Wrap-Up

Brief summary covering:
- What was posted (with links / IDs)
- What was skipped (and why)
- Anything ambiguous flagged for follow-up
- Reminder of where each item lives:
  - Email → Gmail draft (send manually)
  - Timeline → Gainsight customer 360 page
  - CTA → Cockpit
  - Success Plan → Plan page

---

## Edge Cases

| Situation | What to do |
|-----------|------------|
| No transcript found anywhere | Ask user to paste it |
| Multiple meetings for same customer this week | Ask which one, or use date hint from trigger phrase |
| Customer resolves to multiple Gainsight entities (company + relationships) | Default to Company Gsid. Note relationships for user confirmation if call topic suggests one (e.g. a product-specific relationship for product calls). |
| Staircase account_lookup returns "low" confidence | Show matches to user before calling `analyze_account` |
| Staircase account_lookup returns ZERO matches | Retry with common suffix variants: "Inc", "LLC", "Corp", "Software", ", Inc.", ", LLC". Also try alternate brand names if the company has them. |
| Staircase returns MULTIPLE high-confidence matches | This is correct behavior for parent + subsidiary relationships. Ask the user which account, or use the call context to disambiguate. |
| Renewal Center (gs_company_forecast) returns nothing | Either pre-renewal (Forecast Center not yet populated) or post-renewal. Note in reconciliation; skip the Forecast section. |
| Opportunity Renewal Stage shows "Assumed Churn" / "More Likely to Churn" but Staircase signal is positive | **This is a real triangulation finding.** Surface it explicitly. Either the CSM hasn't updated the opportunity stage, or Staircase is missing a signal. Flag for the user. |
| Staircase has no data for the account | Skip Staircase context section. Still produce all other deliverables. Flag in wrap-up. |
| Gainsight has no open CTAs or success plans | Skip those sections. Surface in summary. |
| Recording link/passcode unknown | Use `[INSERT RECORDING LINK]` / `[INSERT PASSCODE]` placeholders |
| Attendee emails missing | Use what's known; flag gaps |
| Action item has no owner | Mark "Owner: TBD" |
| No clear risk in call BUT Staircase flagged risk in last 60 days | Note in reconciliation; do not auto-create CTA unless user confirms |
| Call type unclear | Default to `Meeting`, ask if confident matters |

---

## Reference Files

- `references/email-format.md` — Email tone + per-call-type templates
- `references/staircase-query-patterns.md` — Verified working query patterns for `staircase_analyze_account` and `staircase_ask`
- `references/gainsight-mappings.md` — Call-type → activity_type, risk-language → CTA priority, Staircase signal → Success Plan status mappings
- `references/widget-design.md` — Cowork review widget HTML

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

### Skill-specific emphasis (post-call)

Primary writes: **Timeline Activity** (customer state captured, type=Meeting or Call) + **optional Risk CTA** (only if risk surfaced, with Tasks for follow-up + email draft in Task description carrying Verify Before Sending) + **Success Plan objective updates** (only when an existing SP applies). Break action items into discrete Tasks under any CTA created — never buried in Timeline content. Timeline = team context. CTA Tasks = action playbook.

### Failure modes from prior sessions to avoid

- **Action content in CTA description instead of Tasks** → CTA description stays TLDR; actions become Tasks
- **Standalone CTA that belongs under an active SP** → attach via `success_plan_id` (create) or `CtaGroupId` (update)
- **Creating SP + CTAs but skipping the Timeline Update context anchor** → always post the Update activity attached to the SP
- **Hardcoding picklist values** instead of `prepare_cta` / `prepare_sp` discovery
- **Putting draft email in CTA Comments** instead of Task description

Full anti-pattern catalog: `_shared/gainsight-output-best-practices.md` §10.

---

## Learnings

See `.learnings.md` for accumulated wins, misses, and refinements from real-account testing. Read it before generating deliverables to avoid known failure modes.
