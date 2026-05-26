# Gainsight CS Output Best Practices

**Audience:** Every skill in this plugin that writes to Gainsight (CTAs, Timeline activities, Tasks, Success Plans)
**Purpose:** Produce CS-accelerating artifacts, not data dumps. The plugin writes to Gainsight to make CSMs faster, not to log that work happened.

---

## ⚡ READ THIS FIRST — Execution checklist (run before every Gainsight write)

**These 10 rules account for 95% of plugin output quality. If you can't tick all 10 before a write, stop and rebuild.**

### Composition rules (apply while drafting)

- [ ] **CTA description = TLDR ONLY.** 1-3 sentences: what + why + pointer to Tasks. NEVER the action playbook. See §2A.
- [ ] **Tasks carry the actions.** Each CTA has ≥2 Tasks. Each Task = ONE discrete action with a clear stakeholder. See §2B + §3.
- [ ] **Task descriptions carry the accelerator.** Pre-drafted email body, agenda, discovery script, escalation template — not "draft an email." See §3A-C.
- [ ] **Timeline activity for context.** For any strategic motion, post a Timeline Update with TLDR / Findings / Stakeholders / Action sequence / Evidence, attached to the SP or CTA. See §4.
- [ ] **HTML, not Markdown.** Rich-text fields require `<p>`, `<ul>`, `<strong>`, `<br>`. Never `**bold**` or `- item`. See §1.
- [ ] **No em dashes. No AI-isms. No internal classification labels** in customer-facing fields. See §1 anti-patterns.

### Discipline rules (apply at the approval gate, before any tool call)

- [ ] **Fetch existing first.** `fetch_cta_list` + `fetch_success_plan_list` on the company. Surface stagnant artifacts. See §12.
- [ ] **Reuse-vs-create check.** If an open CTA covers the same signal → update, don't duplicate. See §8.
- [ ] **SP threshold honored.** Don't create a Success Plan unless ≥3 strategic CTAs + clear outcome goal + measurable success criteria. See §5B.
- [ ] **Approval gate with validation summary.** Surface the pre-write summary (below) to the user BEFORE any write call. Wait for explicit approval.

### Pre-write validation summary (paste-ready template)

Before any `create_sp` / `create_cta` / `create_cta_task` / `create_timeline_activity` call, surface this to the user:

```
Pre-write validation — <Account>

Artifacts about to land:
- [count] Success Plan(s) with Plan Info enriched (Target Completion Date, Priority, Success Definition)
- [count] CTAs · descriptions confirmed TLDR · [count] attached to SP
- [count] Tasks total · each carries accelerator content (drafts/agendas/scripts)
- [count] Timeline activity attached to [SP / CTA / company]

Discipline checks:
- Existing artifacts fetched: [count] stagnant CTAs, [count] active SPs reviewed
- Reuse-vs-create: [decision per existing artifact]
- SP threshold: [N CTAs ≥3 ✓ / N <3 — using standalone CTAs instead]
- Formatting: HTML confirmed, no em dashes, no internal labels in customer-facing fields

Ready to write?  [Approve all / Adjust / Hold]
```

**If any check fails, regenerate before writing. Never silently violate.**

---

## TLDR

Gainsight artifacts accelerate CSMs when they (1) lead with TLDR-quality summaries, (2) break actions into Tasks rather than walls of text, (3) use Timeline entries as the universal context-delivery mechanism, and (4) only create Success Plans when there's a real strategic plan with measurable outcomes. Never link to external `.md` files — context lives inline.

---

## 1. Writing principles for Gainsight rich-text fields

**The pattern:**
- **TLDR first.** 1-2 line lead. What is this, why does it matter, what's the immediate next move.
- **Scannable bullets over paragraphs.** CSMs scan, they don't read.
- **Concrete specifics.** Names, dates, numbers, dollar amounts. Never "the customer" / "soon" / "several."
- **Inline context only.** Never link to external `.md` files or any external doc. The CSM reading the entry should have everything they need right there.

### User approval gate before write + commitment discipline

**Before any Gainsight write that produces customer-facing content** (Task email drafts, Timeline entries that surface to teams, CTA Comments), the plugin must:

1. **Present a short plan to the user** covering:
   - Goal of this action set
   - Key strategic choices being made (e.g., "frame the AI addendum as separate from renewal," "loop in the CIO before commercial discussion," "pause scoped governance work")
   - Specific external commitments being drafted (cadences, ETAs, named promises, cross-team resourcing claims)
2. **Get explicit user approval** on the plan and the commitments before any write
3. **Then write**

**Commitment Discipline:**
- Never commit on cadence ("starting next week, weekly war room") without confirming the CSM has the capacity AND has secured the cross-functional resources
- Never speak for other teams ("Product/Engineering will deliver X by Y") without verifying internal commitment exists
- Never make time-bound promises ("ETA this week," "proof by Friday") without confirming the CSM owns the ETA-tracker
- Never claim governance decisions ("paused as scoped feature work") that require leadership sign-off
- **Default to PROPOSAL language** ("I'd like to propose...", "We can offer...", "Can we align on..."), not COMMITMENT language ("We will deliver...", "I'm getting you...", "Starting next week")
- In Email-type Tasks, include a **VERIFY BEFORE SENDING** checklist that flags every external commitment the CSM must validate before sending

**Why this matters.** AI drafts can quickly become overcommitments to the customer. The CSM is on the hook for what gets sent. The plugin's job is to draft the strategic FRAME and the language. The CSM owns commitments to customers. The approval gate keeps the strategic intelligence (multi-thread the renewal, separate AI addendum, contain via the right stakeholder) while preventing the AI from over-promising on operational specifics.

### Teammate-facing, customer-focused output (the highest-leverage principle)

Every artifact lands on a teammate's screen. Their job is to act on the customer situation, not read about how the analysis got produced.

**Strict rules:**

1. **Lead with customer state, not Claude's synthesis process.**
2. **Never expose internal classification labels** in customer-facing surfaces. "Save-then-Expand," "Engaged Frustration," "Skeptical Read," "Recency tiebreaker," "Composite classifications firing" are INTERNAL Claude artifacts. They guide WHAT the plugin writes. They do NOT appear in the output.
3. **Never reference "Risk Analyst" / "Expansion Analyst"** as separate sources, or describe how analyses diverged or aligned. Synthesize the differences. Present a unified stakeholder state. The teammate doesn't need to know two analyses ran — they need to know who's who and where the customer is.
4. **Don't repeat Tasks in Timeline content.** Tasks live on the CTA. Timeline delivers CONTEXT (customer state, stakeholder map, evidence, expansion landscape, what's at risk). Not the action plan.
5. **Evidence references must be readable.** Format: `Email (Person, date): paraphrased content` or `Meeting (date): paraphrased content`. Don't paste `comm_Email_#####` or `comm_Calendar_#####` IDs (not clickable in current Gainsight UI). Use "Email:" or "Meeting:" prefixes (not "Calendar:").
6. **CTA names and Task names** also follow rules 2-3. Drop internal labels. "Stakeholder containment with <Stakeholder A> + <Stakeholder B>" beats "Stakeholder containment — acknowledge engaged frustration with <Stakeholder A> + <Stakeholder B>."

### Critical: Gainsight rich-text needs HTML formatting, NOT plain-text newlines

Plain `\n` newlines render as a single solid blob in Gainsight's rich-text fields. Use HTML tags:

```html
<p>Paragraph 1.</p>
<p>Paragraph 2 with a blank line between.</p>
<p><strong>SECTION HEADER:</strong></p>
<ol>
  <li>Numbered item 1.</li>
  <li>Numbered item 2.</li>
</ol>
<ul>
  <li>Bullet item.</li>
  <li>Another bullet.</li>
</ul>
<p>Closing line.</p>
<p><br></p>
<p>(use empty paragraph with br for visual spacing between sections)</p>
```

**Applies to:** CTA Comments field, Task Description field, Timeline Activity Content field, Success Plan rich-text fields.

**Don't use:** Markdown (`**bold**`, `- bullet`, `# header`) — rendering is inconsistent. Always use HTML.

**Banned in Gainsight rich text (strict):**
- **Em dashes (—).** Use commas, colons, periods, or `...` instead. This is the #1 plugin violation to police.
- "It's not X, it's Y" reframing.
- Inflated importance: "pivotal," "transformative," "robust."
- Throat-clearing: "It's important to note," "It's worth considering."
- Hollow affirmations: "Certainly," "Absolutely."
- Conjunctive transitions: "Furthermore," "Moreover," "Additionally."
- Trailing -ing phrases: "...ensuring alignment."
- File path references: "see `<external-file>.md`."
- Markdown formatting (use HTML, not `**bold**` or `- bullet`).

---

## 2. CTA structure pattern

A CTA is the unit of CSM action. Structure it so the CSM understands the situation in 10 seconds and knows what to do in 30.

### 2A. Main rich-text field (Comments / Description)

Keep this CONCISE. The main field answers three questions:
1. **What is this?** (1 line — the headline)
2. **Why does it matter?** (1-2 lines — the stakes)
3. **What's the immediate next move?** (1 line — point to Tasks for the full action list)

**Pattern:**

```
TLDR: <one-line headline summarizing the situation and why it's a CTA>

CURRENT STATE: <2-3 lines on the customer signal driving this CTA>

NEXT MOVE: See Tasks below. Deeper context in linked Timeline entry on this CTA.
```

**What the main field should NOT do:** carry the whole action playbook, paste the merge analysis, list 8 paragraphs of evidence. That belongs in Tasks (actions) + Timeline activity (deep context).

### 2B. Tasks (sub-steps within the CTA)

Tasks ARE the action list. Break actions out of the description.

**Task naming:**
- Imperative verb + object + named stakeholder
- Good: "Send <Stakeholder> AI addendum decision package (Option A or B)"
- Bad: "AI addendum"

**Task description field** carries the accelerator content the CSM needs to do the work:
- Draft email body (full text, ready to send)
- Talking-point script for a call
- 5-7 discovery questions for a customer conversation
- Best-practice notes (internal — what's worked in similar situations)
- Recommended approach + watchouts

**Task fields:**
- **Owner:** the CSM doing the work (usually the CTA owner; sometimes routed to a teammate)
- **Due Date:** realistic + sequenced (Week 1 actions before Week 2)
- **Priority:** Normal unless time-critical
- **Status:** Not Started on creation

**One Task per discrete action.** A CTA with 4-5 sequenced actions = 4-5 Tasks. Not one mega-task.

### 2C. Linked Timeline activity (CTA-attached)

Use a Timeline activity attached to the CTA for the deeper context the main rich-text doesn't carry:
- The merge analysis findings
- Stakeholder map (named, with roles)
- Evidence trail (specific calls / emails referenced)
- Recommended approach with rationale

The Timeline entry is "more details" for the CSM who wants to go deeper. The CTA's main field stays light + scannable; the linked Timeline carries the depth.

### 2D. CTA Type / Priority / Status / Reason — selection rules

| Field | How to choose |
|---|---|
| **Type** | Match to merge classification: Save-then-Expand → Risk (primary) + Opportunity (secondary). Skeptical Read → Risk only. Expansion-as-Save → Opportunity. Onboarding → Lifecycle. Renewal motion → Risk (if risk present) or Lifecycle. |
| **Priority** | High if renewal <30d OR risk-severity 4-5. Medium if renewal 30-90d OR risk 3. Low otherwise. |
| **Reason** | Match the underlying signal. For renewal-execution issues use "Renewal Risk." For champion-attrition use "Loss/Change of Key Persona." Pull the actual reason from the merge analysis — don't default to "Other." |
| **Status** | "New" on creation. CSM advances through Org-specific statuses (New → On Track → Closed Success / Closed Unsuccessful). |

---

## 3. Task pattern best practices

Tasks are how the plugin moves work from "interesting analysis" to "ready to act in 90 seconds."

**Three task types and their description patterns:**

### 3A. Outreach task (most common)

Task name: "Send <Person> <Subject> (this week)"
Task description carries the FULL DRAFT EMAIL BODY. CSM opens, reviews, edits if needed, sends.

```
Email draft to <Person>:

Subject: <Subject>

Hi <Person>,

<body>

Thanks,
<CSM>
```

Include any commercial / legal terms inline. Don't make the CSM go fetch them.

### 3B. Discovery / interview task

Task name: "Customer interview: <topic> (questions in description)"
Task description carries 5-7 standardized discovery questions the CSM asks live.

```
Questions for <Person> in the next call:

1. <question targeting current state>
2. <question targeting priorities>
3. <question targeting gaps>
4. <question targeting decision criteria>
5. <question targeting success measurement>

Notes to capture: <fields the CSM should record>
```

### 3C. Internal-prep task

Task name: "Draft <artifact> for <internal recipient>"
Task description carries the structure + key data points the CSM uses to build the artifact.

```
<Artifact> structure for <recipient>:

Section 1: <what>
- Key data point: <specific number / fact>

Section 2: <what>
- Recommendation: <specific guidance>
```

Examples: CRO ROI memo, exec briefing doc, board update, churn risk escalation.

**Sequencing:** assign Due Dates that respect dependencies (interview before email-draft, ROI memo before exec conversation).

---

## 4. Timeline activity pattern

Timeline activities are the universal context-delivery mechanism. Most common skill output. Use generously.

### 4A. Three use cases

1. **Account-level activity** (no CTA, no SP) — general update for the team
   - "Q2 renewal outlook for <account>" / "Customer change-of-champion observed at <account>"
2. **CTA-attached activity** — deeper context for a specific CTA
   - Posted with `cta_id` parameter; appears on CTA's Timeline tab
3. **Success Plan-attached activity** — context / update for a specific SP
   - Posted with `success_plan_id` parameter; appears on SP's Timeline tab

### 4B. Writing format

**Subject:** 60-80 chars, TLDR-quality
- Good: "Risk × Expansion Merge — <Account> classified Save-then-Expand"
- Bad: "Update" / "Notes" / "FYI"

**Content structure:**

```
TLDR: <2-3 line summary of the finding/update>

FINDINGS:
- <key point 1>
- <key point 2>
- <key point 3>

STAKEHOLDERS:
- <Name>, <role>: <brief on engagement/sentiment>
- <Name>, <role>: <brief>

NEXT MOVES (this week):
- <action 1 — see linked CTA>
- <action 2>

EVIDENCE:
- <date email from <Stakeholder>, comm_Email_...>
- <date calendar, comm_Calendar_...>
```

Section headers in ALL CAPS scan well in Gainsight's rich text without depending on markdown.

### 4C. Required custom fields (org-specific)

Some orgs require custom fields on every Timeline activity (e.g., a `Status` custom field with values like Green / Yellow / Red / N/A - Internal Update). The MCP returns a usable error if a required field is missing; retry with `custom_field_values={"<Field>": "..."}`. Discover required fields per org and handle the error pattern.

| Status | When to use |
|---|---|
| Green | Account is in good shape; positive signal logged. |
| Yellow | Active risk being managed; CTA exists; CSM in motion. |
| Red | Crisis; immediate escalation needed. |
| N/A - Internal Update | Plugin-generated context that's neither a signal nor a status change. |

---

## 5. Success Plan methodology

A Success Plan is a strategic plan, not a template. **Never create an empty Success Plan.** The plugin must produce a real plan with measurable outcomes — or not create one at all.

### 5A. Pre-create checks (mandatory)

Before creating ANY new Success Plan:

1. Call `fetch_success_plan_list(filter on company_id)` to find existing SPs on the account.
2. If an active SP exists with similar scope: **UPDATE** the existing SP (add CTAs, update objectives) rather than creating a new one.
3. If an existing SP has a past due date or stale last-update: **RECOMMEND CLEANUP** to the user before creating new.
4. If no existing SP applies: get **EXPLICIT USER CONSENT** with a preview of what will be created (plan info content, ≥3 CTAs proposed, outcome goal, measurement).

### 5B. Threshold to create

Create a new Success Plan only when ALL of these are true:

- **≥3 strategic CTA recommendations** ready to fill the plan
- **Clear outcome goal** identified (specific customer-side change)
- **Measurable success criteria** defined (≥1 indicator the CSM can track)

If any of these are missing, do NOT create a Success Plan. Create the standalone CTA(s) instead.

A Success Plan can be a short-duration strategic motion (e.g., 3-week save sequence) — duration is not the gate. The gate is "real strategic plan with measurable outcome," not "long-running."

### 5C. Required structure

**Plan info fields** (filled with TLDR-quality context, not boilerplate):
- Customer Name
- Type (org-specific — Renewal Success Plan / Onboarding / Expansion Plan / etc.)
- Status (Active on creation)
- Due Date (realistic — usually 60-120 days out)
- Owner (the responsible CSM)

**Plan info text fields** (where applicable — varies by SP type):
- Outcome goal — what changes for the customer when this plan succeeds?
- Success measurement — how do we know it worked? (≥1 metric or behavioral indicator)
- Downsell risk facts / Multi-threading status / Executive sponsor — fill with concrete current state

**CTAs (the strategic steps):**
- **≥3 CTAs minimum** — each one is a meaningful step in the plan
- **First CTA is often a Discovery CTA** (see 5E below)
- Each CTA has Tasks per section 3 above
- Sequence CTAs by due date

**Timeline activities (context/updates on the SP):**
- One on creation: "Success Plan created — <plan rationale + outcome goal + measurement>"
- Subsequent updates as the plan progresses

### 5D. Outcome + measurement framework

The plugin must NOT hard-depend on any specific framework (O2, OKRs, etc.) — those vary per customer org and aren't accessible via MCP today.

**Plugin guidance for proposing outcome + measurement:**
1. **Read the customer's business context** (industry, product, common value patterns) from the Staircase Risk + Expansion analyses
2. **Propose a primary outcome** that reflects what the customer cares about (per their stated priorities in the analyses)
3. **Propose 1-3 measurable indicators** — could be product metrics (adoption %, active users), business metrics (renewal % executed, ARR retained, expansion ARR closed), or behavioral indicators (exec engagement frequency, stakeholder multi-thread count)
4. **Present to the CSM for confirmation** before finalizing — the CSM knows the customer's actual goals better than the AI

If the customer org has structured goal data in Gainsight (Customer Goals, Goal Library) that's accessible via MCP, prefer that over generated proposals. Today this data is NOT MCP-accessible (filed as G3.5 DS rec).

### 5E. Discovery CTA pattern (adaptive — informed by Staircase intelligence)

Most strategic Success Plans benefit from a Discovery CTA as the first step. The Discovery CTA confirms the plan's outcome goal + success measurement WITH the customer rather than assuming.

**The discovery is ADAPTIVE** — it depends on what Staircase already knows about the account. Before drafting questions, the plugin should query Staircase for available analyses and let those shape the conversation:

**Pre-discovery Staircase intelligence gathering (mandatory):**
1. **For onboarding context** — check for **Handoff Analysis** (`staircase_analyze_account` with handoff-focused query). If present, the account was recently sold and Staircase captured the pre-sales goals, sponsor context, and key commitments. The onboarding discovery becomes a VALIDATION SESSION (confirm what's already known + fill specific gaps).
2. **For renewal context** — check for **Risk Analysis** (changes the conversation tone), **Expansion Analysis** (informs what threads to explore), **AI Renewal Analysis** (if past renewal exists, what worked / what didn't), and run any custom queries for the specific account state. Then build discovery to fill gaps, validate signals, and surface what the analyses miss.

**Discovery CTA structure:**
- Type: pick from org's available types (Risk if present, Objective if present, Activity as fallback)
- Name: "Customer discovery: <topic> — confirm goals + validate intelligence"
- ≥1 Task per discovery section, each with adaptive questions

**Renewal-context discovery questions (canonical starting set — refine per Staircase intelligence):**
1. What outcomes have made our partnership valuable in the past 12 months?
2. What are your team's top 2-3 priorities for the next 6-12 months?
3. Where has our product underdelivered relative to your expectations?
4. Who are the executive sponsors and budget approvers for this renewal?
5. What would make this renewal a clear yes for you (specific terms / outcomes / proof points)?
6. Are there expansion areas (products, use cases, BUs) we should explore — or is this purely a renewal conversation?
7. What does success look like 90 days after renewal?

**Adaptive overlay — when Staircase Risk Analysis is present:**
- Replace question 3 with a more targeted version that probes the actual risk reasons (don't re-ask what we know)
- Add: validation question for each named risk reason — "We've heard X is a concern. Can you walk me through how you're thinking about it?"
- Validate stakeholder positioning from the Risk Analysis with the customer directly

**Adaptive overlay — when Staircase Expansion Analysis is present:**
- Add: validation question for each named expansion thread — "We've seen interest in X. Where does this sit on your priority list?"
- Probe gaps in the expansion analysis — "Are there areas we haven't discussed where you see future value?"

**Onboarding-context discovery questions (when Handoff Analysis is NOT available):**
1. What outcome led your team to choose our product?
2. What does the first 90 days success look like?
3. Who owns the rollout internally? Who are the stakeholders we'll work with?
4. What are the biggest risks to a successful rollout you see today?
5. What does "rolled out and working" mean — what specific behaviors do you want to see in your team?
6. What integrations / data sources are required for go-live?
7. How will we measure ROI together at 90 / 180 days?

**Adaptive overlay — when Staircase Handoff Analysis IS available:**
- Lead with VALIDATION: "Here's what we captured from your pre-sales conversations. Is this still right?" Walk through the Handoff Analysis sections (goals, commitments, stakeholders, blockers).
- Then ask GAP-filling questions for sections the Handoff Analysis didn't cover or that are likely stale
- Replace generic "what does success look like" with the specific Crawl/Walk/Run language from the Handoff Analysis if present
- This makes the discovery session a relationship-builder (not a re-interview) — customer sees the handoff was real, not paperwork

**Principle:** Staircase already knows a lot about the account. Discovery exists to validate + fill gaps, NOT to repeat questions the customer has already answered. The plugin's job is to know what's already known and frame the conversation around what's missing.

---

## 6. Account Signal Classifications (the framework that drives everything downstream)

**The framework:** Staircase signals tell a story about what's happening on an account right now. Rather than routing based on a single signal, the plugin **classifies** the account based on signal combinations. Each classification implies a templated set of Gainsight artifacts (CTA Type intent, Task playbook, Timeline pattern, SP threshold).

**Multi-classify by design.** Real accounts have multiple stories happening. An account can fire (e.g.) Save-then-Expand + Imminent Renewal simultaneously, or Save-then-Expand + Champion Departure. Classifications are not mutually exclusive. The plugin fires all that match; the CSM sees the composite picture.

### 6A. How classifications drive downstream artifacts

For each classification that fires:
1. **CTA Type intent** — what Type best fits (Risk, Opportunity, Lifecycle, Activity, Objective). Pick from the org's actual options per §7.
2. **Task playbook** — sequenced action steps with accelerator content (the structure that goes into Task descriptions per §3)
3. **Timeline pattern** — what context to capture (merge analysis, stakeholder map, intervention history)
4. **SP threshold check** — does this classification warrant a Success Plan, or is a standalone CTA sufficient (gates per §5)

### 6B. Classification families

#### Risk × Expansion family (codified in §5)
- **Expansion-as-Save** — expansion close IS the save play
- **Save-then-Expand** — save first, expansion contingent on stabilization
- **Skeptical Read** — expansion thread partially/fully fantasy; defensive save only

#### Champion / Stakeholder family

**Champion Departure — Multi-thread Emergency**
- **Trigger:** Account Personnel Changes flag + Single Threaded with Stakeholder flag
- **CTA Type intent:** Risk (high priority)
- **Task playbook:**
  1. Identify 3 alternative stakeholders via Staircase Risk + Expansion analyses
  2. Draft warm-intro outreach to each (task description = full email draft per §3A)
  3. Schedule transition meeting with departing champion + new sponsors
  4. Update relationship-state Timeline activity
- **Timeline pattern:** Departing champion context, new-stakeholder targets, relationship history
- **SP threshold:** Recommend if multi-thread is a >30-day motion with measurable outcome

**Stakeholder Reset — Relationship Rebuild**
- **Trigger:** Personnel Changes flag + new CSM transitioning onto the account
- **CTA Type intent:** Lifecycle (medium-high priority)
- **Task playbook:**
  1. Warm-handoff discovery call with previous CSM
  2. Customer-facing intro email from new CSM (description = draft)
  3. 90-day relationship-rebuild plan
  4. Identify 2-3 quick-win opportunities
- **Timeline pattern:** Inherit prior CSM's relationship history, document new CSM intro
- **SP threshold:** STRONGLY recommend — relationship rebuild is inherently strategic

**Quiet Departure — Track and Pivot**
- **Trigger:** Personnel Changes flag + no active engagement signals on the account
- **CTA Type intent:** Risk (medium priority — verification mode)
- **Task playbook:**
  1. Verify the departure via customer-side ping
  2. Identify successor if not already named
  3. Plan re-engagement campaign if departure confirmed
- **Timeline pattern:** Verification evidence
- **SP threshold:** Standalone CTA — escalate to SP only if re-engagement becomes strategic

#### Engagement family

**Dark Account — Reactivation Play**
- **Trigger:** Account Dark flag + no recent CSM reach-out
- **CTA Type intent:** Risk (high priority)
- **Task playbook:**
  1. Reach-out email with escalation ladder (draft in description)
  2. LinkedIn touchpoint if email unanswered (template in description)
  3. Exec-to-exec ping if 2-week silence
  4. Account-pause analysis if no response after 4 weeks
- **Timeline pattern:** Last engagement date, evidence of disengagement pattern
- **SP threshold:** Standalone CTA unless dark-account pattern persists across multiple recovery attempts

**Triple Quiet — Pattern of Disengagement**
- **Trigger:** Account Dark + No Reach Out + No QBR all fire on the same account
- **CTA Type intent:** Risk (highest priority — escalation territory)
- **Task playbook:**
  1. CSM-side check-in (verify No Reach Out is real, not a data artifact)
  2. Manager-led account review
  3. Multi-channel re-engagement campaign
  4. Escalation to leadership for resource decision (continue vs accept churn)
- **Timeline pattern:** Full disengagement pattern with timeline of last activities
- **SP threshold:** STRONGLY recommend — sustained reset motion needed

**CSM-Side Reach-Out Gap**
- **Trigger:** No Reach Out flag fires but customer is engaging (positive sentiment, ticket activity, calendar invites from customer)
- **CTA Type intent:** Activity (medium priority)
- **Task playbook:**
  1. Catch-up outreach acknowledging the gap (draft in description)
  2. Resume cadence
  3. Optional: flag CSM workload to manager
- **Timeline pattern:** Note the gap, acknowledge customer-side engagement was strong
- **SP threshold:** No SP — operational CTA only

#### Renewal family

**Imminent Renewal — Execution Path**
- **Trigger:** Renewal date <30 days + decision-maker actively engaged + no critical risk signals
- **CTA Type intent:** Risk (Renewal Risk reason, high priority)
- **Task playbook:**
  1. Confirm scope with decision-maker
  2. Right-size licensing reconciliation
  3. Send paper to procurement
  4. Track countersignature
  5. Post-close Timeline activity + transition into next-cycle SP
- **Timeline pattern:** Stakeholder state, commercial terms, decision history
- **SP threshold:** Often warrants SP if multi-week execution and stakeholder map is complex

**Renewal Sleepwalk**
- **Trigger:** Renewal <60 days + Account Dark OR engagement <30
- **CTA Type intent:** Risk (highest priority — immediate intervention)
- **Task playbook:**
  1. Emergency reach-out to last-known stakeholder
  2. Exec-to-exec escalation in parallel
  3. Air-cover request from leadership
  4. Discovery on what's changed
- **Timeline pattern:** Disengagement timeline + last-known commercial context
- **SP threshold:** Recommend SP for the recovery motion

**Renewal Discovery Gap**
- **Trigger:** Renewal <90 days + No Renewal Discussion flag fires (or no commercial activity evidence in 60+ days)
- **CTA Type intent:** Risk or Objective (Renewal Risk reason)
- **Task playbook:**
  1. Initiate renewal-discovery conversation with the canonical 7 questions (§5E)
  2. Confirm decision-maker + sponsor
  3. Capture commercial requirements + decision criteria
- **Timeline pattern:** Discovery findings + decision-tree forward
- **SP threshold:** Recommend SP — discovery → execution → close is inherently a strategic motion

#### Onboarding family

**Fresh Handoff — Validation Discovery**
- **Trigger:** Handoff Analysis present in Staircase + customer close <90 days
- **CTA Type intent:** Lifecycle or Objective
- **Task playbook:**
  1. Adaptive validation discovery (per §5E — review Handoff Analysis, validate with customer)
  2. Confirm pre-sales goals + commitments are still accurate
  3. Identify go-live blockers
  4. Establish 90-day success measurement
- **Timeline pattern:** Validation findings, contrast against Handoff Analysis baseline
- **SP threshold:** STRONGLY recommend — onboarding is inherently a strategic SP motion. This is the canonical SP-creation case.

**Stuck Onboarding — Acceleration Play**
- **Trigger:** Onboarding event present + low adoption signals + >60 days post-close
- **CTA Type intent:** Risk (medium-high priority)
- **Task playbook:**
  1. Diagnose adoption blockers (technical / persona / change-management)
  2. Replanning workshop with key stakeholders
  3. Targeted enablement plan
  4. New 30-60-90 milestone reset
- **Timeline pattern:** Original onboarding plan vs current state, blocker diagnosis
- **SP threshold:** Often UPDATE the existing onboarding SP (reset due dates + objectives) rather than create new

### 6C. Composite picture — multi-classify in practice

When the plugin scans an account's signals, it runs each classification's trigger check. ALL classifications that match fire. The output shows the composite picture so the CSM understands the multiple stories happening.

**Example A — Imminent renewal with expansion in play:**
- Save-then-Expand (Risk × Expansion merge)
- Imminent Renewal — Execution Path (renewal <30d, decision-maker engaged, no critical risk)
- **Composite read:** Renewal motion that doubles as save play; defer expansion to post-renewal

**Example B — Champion departure mid-renewal:**
- Save-then-Expand multi-thread (per-thread variation)
- Champion Departure — Multi-thread Emergency (Personnel Changes + Single Threaded)
- **Composite read:** Save the renewal AND immediately multi-thread off the departing champion to prevent collapse

**Example C — Fresh handoff with CSM transition:**
- Fresh Handoff — Validation Discovery (Handoff Analysis present + recent close)
- Possibly Stakeholder Reset (if CSM transitioning at the same time)
- **Composite read:** Run adaptive validation discovery AND warm-handoff from prior CSM in the same SP

### 6D. Codification path

**Codified today:** 5 families (Risk × Expansion + Champion/Stakeholder + Engagement + Renewal + Onboarding) = 14 classifications.

**Deferred:** Sentiment family (Sentiment Collapse, Quiet Health Decline), Churn family (Verified Churn, Churn Imminent), Advocacy family (Champion at Scale, Quiet Advocate), Whitespace family (Cross-product, Multi-BU) — codified as those use cases are validated empirically.

---

## 7. CTA Type taxonomy + how to think about it

**CTA types vary widely per org.** Don't hard-code a routing matrix. Instead, give Claude the available toolbox and a way to think about which fits the situation.

### 7A. What's likely to be present in any org

**Reliably present:**
- **Risk** — the only type that's effectively universal. When in doubt, default here.

**Commonly present (but not guaranteed):**
- Opportunity, Lifecycle, Activity, Objective, EBR

**Sometimes present (varies more):**
- CSQL (qualified expansion sales lead — a Gainsight capability but not exposed to MCP today in many orgs)
- Custom org-specific types (e.g., onboarding-specific, regional-team, retention-team-engagement, or sales-credit-style types — names vary widely per org)

### 7B. How to think about which Type to use

Use this thinking, not a rigid mapping:

1. **What's the work?** Risk mitigation, expansion motion, milestone-stage action, simple touchpoint log, outcome-tracking work, executive review motion, sales-qualified lead.
2. **Which Type in THIS org best fits that work?** Discover via `manage_cockpit_actions(mode='prepare_cta')`. Pick the closest match.
3. **If no clear match:** default to Risk for risk-mitigation work, or use the org's most generic Type (often Activity).

### 7C. Classification → CTA intent (not rigid Type routing)

The classification(s) that fire on an account tell you what KIND of CTA to create:

| Classification | CTA intent | Type preference (if available) |
|---|---|---|
| **Save-then-Expand** | Two CTAs: save motion (Risk) + post-save expansion (Opportunity) | Risk + Opportunity |
| **Expansion-as-Save** | One CTA capturing save + expansion as the same motion | Opportunity (or Risk if absent) |
| **Skeptical Read** | One CTA for defensive save. Do NOT chase the dismissed expansion thread. | Risk |
| **Champion Departure — Multi-thread Emergency** | Risk CTA for multi-thread motion + Timeline capturing relationship history | Risk (high priority) |
| **Stakeholder Reset — Relationship Rebuild** | Lifecycle CTA for warm-handoff motion | Lifecycle |
| **Dark Account / Triple Quiet** | Risk CTA for reactivation play | Risk (highest priority on Triple Quiet) |
| **CSM-Side Reach-Out Gap** | Activity CTA for catch-up motion | Activity |
| **Imminent Renewal — Execution Path** | Risk CTA + Tasks for paper-to-countersign sequence | Risk (Renewal Risk reason) |
| **Renewal Sleepwalk** | Risk CTA + emergency reactivation Tasks | Risk (highest priority) |
| **Renewal Discovery Gap** | Risk or Objective CTA + Discovery Task with canonical 7 questions | Risk or Objective |
| **Fresh Handoff — Validation Discovery** | Lifecycle/Objective CTA + adaptive validation Task | Lifecycle or Objective |
| **Stuck Onboarding — Acceleration Play** | Risk CTA for adoption-blocker diagnosis | Risk |

**Important:** Don't insist on the "preferred" Type. If the org doesn't have Opportunity, a Risk CTA named "<Account> post-renewal product evaluation" carries the same intent — naming + Tasks make the work clear.

### 7D. Tasks-as-playbook (the key acceleration mechanism)

The CTA Type sets context. **Tasks deliver the playbook.** The Task list within a CTA IS the action playbook — sequenced steps with the accelerator content (draft emails, talking points, discovery questions) in the descriptions.

A Risk CTA with 5 well-structured Tasks beats a "perfect Type" CTA with no Tasks every time. Don't get stuck on Type selection — get the Tasks right.

### 7E. Discover before assuming

Every write to Gainsight must discover the org's actual Types/Reasons/Statuses/Playbooks via `manage_cockpit_actions(mode='prepare_cta')` first. Never assume the canonical labels above exist verbatim. The plugin reads what's there, picks the closest match, and notes mismatch as a finding if no good match exists.

---

## 8. Reuse vs Create decision matrix

Before any write, check for existing artifacts.

| Situation | Action |
|---|---|
| Existing CTA on same risk/opportunity, status not closed | UPDATE the existing CTA (add Tasks, update Comments). Don't create duplicate. |
| Existing CTA closed but new related signal | CREATE new CTA, reference the closed CTA in the description. |
| Existing Success Plan active + similar scope | UPDATE the SP (add CTAs, update objectives). |
| Existing SP past due date or stale | RECOMMEND CLEANUP to user first; then update or create new per their direction. |
| Existing Timeline activity on the same event | UPDATE in place via `activity_id`. |
| Genuinely new strategic motion / new event | CREATE fresh. |

**The discipline:** fewer, better artifacts beat many redundant ones. CSMs ignore Gainsight feeds full of duplicates.

---

## 9. Skill-specific quick reference

When implementing the patterns above in specific skills:

| Skill | Most common write | Pattern emphasis |
|---|---|---|
| `gainsight-meeting-processor` | Timeline activity (account-level) + optional Risk CTA | Post-call recap → Timeline; risk surfaced → CTA with Tasks for follow-up |
| `gainsight-csm-book-pulse` | Risk/Opportunity CTAs from top-of-rank accounts | Step 6 close-out actions. Get user consent before write. |
| `gainsight-exec-renewal-radar` | Mostly briefing-grade. Optional handoff CTAs to CSMs. | Don't auto-write; surface "create these CTAs for CSMs" recommendations. |
| `gainsight-renewal-priority-planner` | Risk + Opportunity CTAs per movability ranking | Save-into-expansion candidates get the merge-classification-driven CTA structure. |
| `gainsight-stakeholder-connect` | Timeline activity + optional CTA with outreach Task | The outreach drafts are Task descriptions, not buried in Comments. |
| `gainsight-no-qbr-ebr-scheduler` | Lifecycle / EBR CTA with scheduling Task | The Task description = the draft EBR-pitch email. |
| `gainsight-account-handoff-onboarding` | Success Plan creation (with full discovery CTA structure) | The canonical "real Success Plan" use case. |
| `gainsight-daily-cockpit` | Read-mostly (CTA fetch) | Update existing CTAs as actions complete; don't proliferate. |
| `gainsight-account-workspace` | Multi-write context | All three write paths possible — apply patterns consistently. |

---

## 10. Anti-patterns (don't do these)

| Anti-pattern | Why | Use instead |
|---|---|---|
| **Stagnant CTAs and Success Plans** (the most common CS failure mode) | Old open CTAs and SPs pile up; CSMs lose focus; real priorities get buried in noise; the plugin compounds this if it doesn't enforce cleanup discipline | Plugin MUST fetch existing CTAs/SPs first, surface stagnation (past due dates, no updates >30 days), and recommend close/cleanup BEFORE creating new artifacts. See §11 below. |
| Empty Success Plan with no CTAs | Doesn't accelerate anyone; clutters the workspace | Don't create unless ≥3 CTAs + outcome + measurement |
| Wall-of-text CTA description with all actions inline | CSM has to parse it; can't act fast | TLDR + Tasks for actions |
| Linking to external `.md` files for "more details" | CSM doesn't have access; breaks the workflow | Inline the context, or put it in a linked Timeline entry |
| Generic CTA name like "Action needed" | Doesn't tell CSM what or why | Imperative verb + specific stakeholder/topic |
| Creating duplicate CTA when existing one is open | Clutters Cockpit; signals plugin isn't checking | Fetch first; update if existing |
| Auto-creating Success Plan from a single signal | Methodology violation per §5 | Use a single CTA instead |
| Defaulting to Reason: "Other" | Loses workshop-grade specificity | Pick from the org's actual options that matches the underlying signal |
| Putting draft email in CTA Comments instead of Task description | Comments field is for context; Tasks accelerate work | Email body → Task description |
| **Putting the action playbook in CTA Comments (description) instead of Tasks** ⚠ NEW | Bloats the description; CSM can't scan the situation in 10 seconds; actions get buried | Comments = TLDR only (situation + why it matters). Each discrete action → ONE Task with the accelerator content in the Task description. See §2A vs §2B. |
| **Creating a standalone CTA that belongs under an active SP** ⚠ NEW | Splits the strategic motion across surfaces; CSM has to jump between CTA list and SP to see the full picture; reset/cleanup gets harder | If the CTA is part of a strategic motion already covered by an active SP, attach it via `success_plan_id` (create) or `CtaGroupId` (update). Standalone CTAs are for tactical motions outside any plan. |
| **Creating a SP + CTAs but skipping the Timeline Update** ⚠ NEW | The SP shows tasks but no narrative context — teammate has no situational anchor when they open it | When the SP launches a strategic motion, post a Timeline Update (Type=Update) attached to the SP via `success_plan_id`. Carries TLDR / Findings / Stakeholders / Action sequence / Evidence. See §4. |
| Forgetting the Status custom field on Timeline activities | Write fails silently or with cryptic error | Always set `custom_field_values={"Status": "..."}` for orgs that require it |

---

## 12. Cleanup discipline (the discipline that makes everything else work)

**CTAs and Success Plans get stagnant — open status but no movement.** The clutter buries real priorities. The plugin must enforce cleanup discipline, not just create new artifacts on top of old ones.

### 12A. Pre-write cleanup check (mandatory)

Before ANY write to a company:

1. **Fetch open CTAs** for the company via `fetch_cta_list` (filter: IsClosed=false)
2. **Fetch active Success Plans** for the company via `fetch_success_plan_list` (filter: Status=Active)
3. **Identify stagnation:** CTAs past due, no comment updates >30 days, SPs past due date with no recent timeline activity
4. **Surface stagnation to the user BEFORE creating new** — present the stagnant artifacts with a recommended action (close, update, or repurpose)

### 12B. Cleanup actions the plugin can recommend or take (with approval)

| Stagnation signal | Recommended action |
|---|---|
| CTA past due >30d, no comment activity | Mark as Closed (Closed Invalid or Closed No Action — let user decide) |
| CTA past due <30d, work clearly ongoing | Update due date + add Timeline activity logging current state |
| Open CTA on the same risk signal as new CTA being created | Update existing rather than create duplicate |
| SP past due, low CTA completion, no recent activity | Recommend close as "Closed - Unsuccessful" or "Closed - Superseded" |
| SP active but objectives stale | Update objectives via `manage_success_plan_actions` + add Timeline activity capturing the refresh |

### 12C. Cleanup as part of every skill that writes

Each skill SKILL.md must include a "Pre-write cleanup" step that:
1. Fetches existing related artifacts
2. Reports stagnation to user
3. Recommends specific cleanup actions
4. Only proceeds with new creation after user has chosen how to handle existing artifacts

### 12D. Why this matters

A clean Cockpit = real focus = effective CSM work. A cluttered Cockpit means the next valuable artifact the plugin creates gets ignored too. The plugin's responsibility extends beyond "create good artifacts" to "maintain a clean working surface."

This is the discipline that compounds — every clean-up makes the next artifact more valuable, and every uncleared piece of stagnant work makes everything worth less.

---

## 11. Workshop teaching points (the durable lessons)

1. **"The plugin can write to Gainsight. The methodology decides what to write."** Write paths working ≠ workshop-grade output.
2. **"Tasks accelerate the CSM. Comments inform them. Timeline carries depth."** Three distinct roles, three distinct content patterns.
3. **"Never create a Success Plan without a real plan."** Empty templates are worse than no plan — they signal noise to the CSM.
4. **"Discover the org's CTA Types, Reasons, SP types, Timeline custom fields BEFORE writing."** Every org configures Gainsight differently. The plugin must discover, not assume.
5. **"Customer goals and value frameworks should ideally be MCP-accessible per-org."** Today they're not (G3.5). Plugin intuits outcomes from business context until that gap closes.

---

## Scope summary

§6 Account Signal Classifications is the upstream framework: 5 families (Risk × Expansion + Champion/Stakeholder + Engagement + Renewal + Onboarding) = 14 classifications, each with templated CTA Type intent + Task playbook + Timeline pattern + SP threshold. Multi-classify by design — accounts can fire multiple classifications simultaneously, and the composite picture is what informs the action plan.

Core principles baked in:
- SP threshold: gated by ≥3 strategic CTAs + outcome + measurement, not by duration
- CTA Type: principle-based thinking, not rigid mapping
- Discovery CTA: adaptive based on Staircase analyses already present
- Anti-patterns: stagnant-CTA/SP cleanup as the #1 CS failure mode (see §12 Cleanup discipline)

Every skill SKILL.md that writes to Gainsight references this doc + bakes in the patterns.

**Deferred classifications** (codify as use cases get validated): Sentiment family · Churn family · Advocacy family · Whitespace family.
