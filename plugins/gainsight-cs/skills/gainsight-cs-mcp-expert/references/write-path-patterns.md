# Gainsight CS MCP — Write Path Patterns

Canonical recipes for every customer-facing Gainsight write. Use these as templates — adapt the content, keep the structure.

**Read before writing.** The output discipline rules in `_shared/gainsight-output-best-practices.md` (v1.1) ALWAYS apply: user approval gate, commitment discipline (proposal language, not commitment language), HTML formatting, teammate-facing customer-focused content, Verify Before Sending on Email tasks, reuse before create, cleanup before create.

---

## The canonical Take Action chain (~8 MCP calls, 5-8s)

The end-to-end pattern, validated against real-org data:

```
1. resolve_customer(name) ............... company_id
2. resolve_user(name) ................... owner_id
3. fetch_cta_list(company_id, IsClosed=false, DueDate GTE today-90d, page_size=25)
                                          → REUSE check: is there an existing CTA covering this?
4. fetch_success_plan_list(company_id)
                                          → REUSE check: active SP we should update vs. create new?
5. manage_cockpit_actions(mode='prepare_cta')           → type_id
6. manage_cockpit_actions(mode='prepare_cta', type_id) → status_id, priority_id, reason_id, playbook_id
7. ┌── USER APPROVAL GATE ─────────────────────────────┐
   │ Surface the planned artifact (TLDR, key choices,  │
   │ commitments being drafted). User approves OR edits.│
   └────────────────────────────────────────────────────┘
8. manage_cockpit_actions(mode='create_cta', ...)       → cta_id
9. create_timeline_activity(company_id, cta_id, custom_field_values={"Status": <Y/R/G>}, content=HTML)
10. (Optional) manage_cockpit_actions(mode='create_cta_task', cta_id, ...)
    × N tasks (one per discrete action)
11. (Optional, only if SP threshold met) manage_success_plan_actions(mode='create_sp', ...)
```

---

## Recipe 1 — Risk CTA + Linked Timeline

**Use case:** Customer-facing risk being managed. Save play. The most common artifact type.

### Step A — Prepare
```
manage_cockpit_actions(mode='prepare_cta')
  → pick Type: Risk (or Renewal Risk if explicit churn-intent, ROI Risk if value scrutiny)
manage_cockpit_actions(mode='prepare_cta', type_id=<Risk>)
  → pick Reason: Renewal Risk | ROI Risk | Stakeholder Risk | Adoption Risk | Competitor | Other
  → pick Priority: Critical | High | Medium | Low
  → pick Status: New (start state)
  → optional: pick Playbook if one matches (often not)
```

### Step B — Approval gate (mandatory)

Present to user:
- **Goal:** 1 sentence
- **Type / Reason / Priority chosen:** 3 picks + 1-line rationale each
- **Commitments being drafted:** list any customer-visible promises (with Verify Before Sending tags if Email-type Task)
- **Reuse check:** "I see existing CTA X — should I update it instead?" (if applicable)

### Step C — Create

```
manage_cockpit_actions(
  mode='create_cta',
  company_id=<gsid>,
  type_id=<Risk gsid>,
  reason_id=<Renewal Risk gsid>,
  priority_id=<High gsid>,
  status_id=<New gsid>,
  owner_id=<CSM gsid>,
  due_date='YYYY-MM-DD',
  name='<Account> Renewal Execution (<Stakeholder1>, <Stakeholder2>)',
  comments='<HTML — see template below>'
)
```

**CTA `comments` HTML template:**
```html
<p><strong>TLDR.</strong> One-line situation + immediate next move.</p>
<p><strong>Status.</strong> Concise state — what's happening with the customer right now.</p>
<p><strong>Next move.</strong> One line. Point to Tasks for action list; point to the linked Timeline entry for full context.</p>
<p><em>See Tasks (below) for the action playbook. See linked Timeline entry for stakeholder map + evidence.</em></p>
```

### Step D — Linked Timeline activity

```
create_timeline_activity(
  company_id=<gsid>,
  cta_id=<cta gsid from Step C>,
  activity_type='<from get_activity_types_config — typically "Internal Note" or "Update">',
  subject='<TLDR of the situation>',
  content='<HTML — see template below>',
  custom_field_values={"Status": "Yellow"},  # If your org requires a Status custom field (org-bespoke); values vary
  date='YYYY-MM-DD'
)
```

**Timeline `content` HTML template (CTA-attached context):**
```html
<p><strong>Customer state.</strong> 2-3 sentences — what's true about the customer right now. Customer-focused, teammate-facing. No internal synthesis language ("Risk × Expansion merge", "Recency Tiebreaker", "Save-then-Expand classification") — give the team the situation, not your process.</p>
<p><strong>Key stakeholders.</strong></p>
<ul>
  <li><strong>Name (Title):</strong> Their current state, engagement posture, recent sentiment signal.</li>
  <li><strong>Name (Title):</strong> ...</li>
</ul>
<p><strong>Evidence (recent communications).</strong></p>
<ul>
  <li><strong>Email (YYYY-MM-DD, Name):</strong> Paraphrased content. No comm_##### IDs.</li>
  <li><strong>Meeting (YYYY-MM-DD):</strong> Paraphrased content.</li>
</ul>
<p><strong>What we know about the renewal/expansion play.</strong> 1-2 sentences. Customer language only.</p>
```

**Anti-patterns for Timeline content:**
- Don't repeat the Tasks (they're already there)
- Don't expose internal classification labels ("Save-then-Expand," "Skeptical Read")
- Don't include `comm_Email_#####` or `comm_Calendar_#####` IDs — they paste as plain text, not clickable (G3.11)
- Don't use `\n` — use HTML `<p>`, `<ul>`, `<br>` (G3.9)

---

## Recipe 2 — CTA Task with accelerator content

**Use case:** Each Task is ONE discrete action under the CTA. Description carries the accelerator (draft email body, talking points, discovery questions, best-practice notes).

### Prepare + Create
```
manage_cockpit_actions(mode='prepare_cta_task') → task type options
manage_cockpit_actions(
  mode='create_cta_task',
  cta_id=<from Recipe 1>,
  task_type='<Action | Email | Call | Other>',
  name='<Imperative-verb action — e.g., "Send AI addendum decision package to <stakeholder>">',
  description='<HTML accelerator content>',
  owner_id=<who does this>,
  due_date='YYYY-MM-DD',
  custom_field_values={"Status": "Open"}  # check via discovery
)
```

### Naming pattern
- ✅ "Send AI addendum decision package to <stakeholder>"
- ✅ "Draft CRO ROI memo for <executive>"
- ❌ "AI addendum" (not an action)
- ❌ "Follow up with customer" (vague)

### Description HTML templates by Task type

**For Action-type Tasks:**
```html
<p><strong>What this does.</strong> 1 sentence.</p>
<p><strong>Steps.</strong></p>
<ol>
  <li>Step 1.</li>
  <li>Step 2.</li>
</ol>
<p><strong>Best practice.</strong> 1-2 lines of internal CS guidance — what to watch for, what's worked before.</p>
```

**For Email-type Tasks (proposal-language, Verify Before Sending mandatory):**
```html
<p><strong>Draft email — VERIFY BEFORE SENDING.</strong></p>
<p><strong>To:</strong> name@email.com</p>
<p><strong>Subject:</strong> [Proposed subject line]</p>
<hr>
<p>Hi [Name],</p>
<p>[Body paragraph 1 — proposal language, not commitment language. "We're proposing X" not "We will X". "I'd like to suggest" not "I commit to".]</p>
<p>[Body paragraph 2.]</p>
<p>[Sign-off]</p>
<hr>
<p><strong>Verify Before Sending checklist.</strong></p>
<ul>
  <li>[ ] Confirm any commitments named in this draft are authorized by [Product / Eng / Leadership]</li>
  <li>[ ] Confirm dates / deliverables match what we can actually do</li>
  <li>[ ] Confirm tone is right for this stakeholder's preferences</li>
  <li>[ ] Confirm recipient list (cc / bcc as needed)</li>
</ul>
```

**Why Verify Before Sending matters (G3.10 context):** ad-hoc Tasks created via `create_cta_task` can't pre-load into Gainsight's email composer today. CSM copy-pastes manually. The checklist guards against AI overcommitment in customer-visible text.

---

## Recipe 3 — Success Plan (only when threshold met)

**Threshold to create a NEW SP** (from `_shared/gainsight-output-best-practices.md` §5):
1. ≥3 strategic CTA recommendations
2. Clear outcome goal
3. Measurable success criteria
4. Multi-week strategic motion (not a single-touch action)

**If threshold NOT met:** create a CTA + Tasks. No SP.

**If threshold met AND no active SP exists:** proceed below.

**If threshold met AND active SP exists:** UPDATE the existing SP. Don't create a new one. The reuse-vs-create rule.

### Pre-create cleanup gate
```
fetch_success_plan_list(company_id) → check:
  - Active SPs (status=Active)?  → prefer UPDATE
  - Past-due SPs?                → surface for cleanup
  - Stale-update SPs (>90 days)? → surface for cleanup
```

### Prepare + Create
```
manage_success_plan_actions(mode='prepare_sp')
  → pick SP Type from org's type list (commonly 5-25 types). Examples:
    - Renewal Success Plan
    - ROI / Value Realization (often per-product)
    - <Onboarding variants>
    - <Org-bespoke templates>
  → pick Status: typically Active

manage_success_plan_actions(
  mode='create_sp',
  company_id=<gsid>,
  type_id=<SP type gsid>,
  status_id=<Active gsid>,
  owner_id=<CSM gsid>,
  due_date='YYYY-MM-DD',
  name='<Outcome-oriented name — e.g., "<Account> Save-then-Expand Renewal Plan">',
  comments='<HTML plan info — outcome goal, success measurement, key stakeholders>'
)
```

### SP `comments` HTML template
```html
<p><strong>Outcome goal.</strong> 1 sentence. What success looks like at SP close.</p>
<p><strong>Success measurement.</strong> How we'll know we got there. Specific.</p>
<p><strong>Strategic stakeholders.</strong></p>
<ul>
  <li><strong>Name (Title):</strong> Their role in this plan.</li>
</ul>
<p><strong>Approach.</strong> 2-3 sentences on the strategic motion. Reference the CTAs that drive the plan.</p>
```

### First-CTA pattern: Discovery / Customer Interview CTA
The first CTA in a new SP is often a discovery touchpoint with 5-7 standardized questions in Task descriptions. Helps confirm outcomes + measures with the customer.

```
Task 1: Open with renewal-context check-in (script in description)
Task 2: Confirm top business outcomes for the next contract period
Task 3: Identify primary value drivers from current usage
Task 4: Surface unaddressed gaps or open commitments
Task 5: Confirm sponsors + decision-makers for renewal
Task 6: Agree on success criteria for the SP outcome
Task 7: Schedule next sync
```

**If a Staircase Handoff Analysis already exists for the account, do NOT re-ask what's already known.** Adapt the Discovery CTA to validate Handoff findings rather than re-discover from scratch.

---

## Recipe 4 — UPDATE existing CTA / SP (reuse over create)

The reuse path. Always preferred when an existing artifact is close enough.

### When to UPDATE vs CREATE

| Situation | Action |
|---|---|
| Existing open CTA covers same risk/opportunity | UPDATE comments + add Tasks |
| Existing active SP is active + recent | UPDATE objectives + add CTAs to it |
| Existing Timeline activity covers same event | UPDATE rather than duplicate |
| Genuinely new strategic motion not covered by existing artifacts | CREATE |

### UPDATE CTA
```
manage_cockpit_actions(
  mode='update_cta',
  cta_id=<existing>,
  comments='<HTML — APPEND not replace; preserve existing context>',
  # Optional: update status_id, priority_id, due_date as situation evolves
)
```

### UPDATE SP
```
manage_success_plan_actions(
  mode='update_sp',
  sp_id=<existing>,
  comments='<HTML — add new context, preserve outcome goal>',
  # Optional: extend due_date if scope grows; surface to user before extending
)
```

### Cascade behavior to remember (G3.7)
Closing a Success Plan auto-closes its open CTA objectives. Useful for cleanup workflows. Don't fight it; use it.

---

## Cleanup discipline (§12 of output best practices)

Before creating new artifacts, surface and offer to close stagnant ones:

```
fetch_cta_list(company_id, IsClosed=false) → flag any:
  - past-due > 90 days
  - last-update > 90 days
  - opened by users no longer at the company
```

Present to user. Let them confirm closure. Then proceed with new creates.

**Example pattern:** When you find multiple multi-year past-due CTAs owned by a former stakeholder, surface + close them before recreating fresh artifacts.

---

## Custom field values — handling org-specific requirements

**Discover-then-pass pattern:**

1. First write attempt with the standard params. If it succeeds: done. If it returns `"Missing required custom fields: 'X' (type: STRING, allowed values: [...])"`:
2. Read the error — it names the field and allowed values.
3. Retry with `custom_field_values={"X": <allowed value>}`.
4. **Document the requirement** for the session so subsequent writes pre-pass it.

**Common example (when an org requires a Status custom field):**
```python
custom_field_values={
  "Status": "Yellow"  # e.g., Green | Yellow | Red | N/A - Internal Update — values are org-bespoke
}
```

Goes on `create_timeline_activity` and sometimes on Tasks.

---

## Source
- `gainsight-mappings.md` (gainsight-meeting-processor references)
- `_shared/gainsight-output-best-practices.md` (v1.1 canonical output discipline)
- Validated against real-org write paths
- DS recs G3.1, G3.6, G3.7, G3.8, G3.9, G3.10, G3.11
