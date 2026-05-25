# Gainsight CS MCP — Anti-patterns + Gotchas

Read this when something fails OR before unfamiliar operations.

Organized by failure type: **payload guards** (token-budget failures), **silent requirements** (org-bespoke fields), **inconsistencies** (tools that behave differently than expected), **known gaps** (things you can't do today), **content-discipline anti-patterns** (things you CAN do but shouldn't).

---

## Payload guards (token-budget failures)

### ⚠️ `fetch_cta_list` without date filter blows the token budget

Large accounts can return 58k+ characters in one call. The `select=` parameter is **IGNORED** — the API returns full records regardless of what you ask for.

**Mandatory pattern:**
```
fetch_cta_list(
  where="CompanyId EQ <gsid> AND IsClosed EQ false AND DueDate GTE <today-90d>",
  page_size=25
)
```

The `DueDate GTE` filter is the actual load-control mechanism. The `page_size=25` cap is belt-and-suspenders.

### ⚠️ `get_object_metadata` is expensive — cache it

Single calls return 100-183k characters:
- Company: 183k
- CTA: 100k
- Relationship: 178k
- Activity Timeline: ~50k
- Success Plan: ~30k

**Pattern:** Call once per object per session. Cache in conversation context. Do NOT re-call within the same session for the same object.

### ⚠️ `fetch_timeline_activity_list` soft-fails intermittently

Returns generic `"Failed to fetch timeline activities"` without diagnostic info. Observed intermittently across multiple accounts.

**Pattern:** Treat as soft-fail. Note in reconciliation. Do NOT block the run. Fall back to Staircase if Timeline activity context matters.

---

## Silent requirements (org-bespoke fields that aren't surfaced)

### ⚠️ G3.1 — Timeline activity required custom fields aren't declared in tool description

Some orgs silently require a custom field (e.g., a `Status` STRING field with values like `Green / Yellow / Red / N/A - Internal Update`) on every Timeline activity.

First write attempt fails with:
```
"Missing required custom fields: 'Status' (type: STRING, allowed values: [...])"
```

**Workaround:** Tool returns a usable error message naming the field + allowed values. Retry-with-correction works:
```
custom_field_values={"Status": "Yellow"}
```

**Pre-emptive discovery (preferred):** call `get_object_metadata("activity_timeline")` and `get_activity_types_config()` once per session to discover required custom fields up front. See `org-discovery.md`.

### ⚠️ Org-specific fields are bespoke EVERYWHERE

- **Segmentation/tier field** — `Tier`, `Segment`, `Customer_Tier__gc`, or org-bespoke
- **Team-member assignment field** — Staircase's standard `Owner` field is universal; custom variants like `CSM`, `Account_Manager__gc`, `Renewal Owner`, etc. are org-bespoke
- **Required custom fields on Timeline activities** — varies
- **SP types** — vary in count and naming per org (commonly 5-25 types)
- **CTA reasons** — vary per org (often 20-40 per type)

Never assume a custom field name. Always discover via `get_object_metadata` + `get_picklist_values`.

---

## Inconsistencies (tools that behave unexpectedly)

### ⚠️ G3.6 — Timeline activity rejects `entity_type=RELATIONSHIP` even with valid relationship_id

Observed inconsistency:
- Creating a Risk CTA with `entity_type=RELATIONSHIP` + `relationship_id` + `relationship_type_id` → SUCCESS
- Immediately calling `create_timeline_activity` with the same `entity_type=RELATIONSHIP` + `relationship_id` → FAILED with `"Relationship not found"`

The relationship_id is valid (CTA creation accepted it seconds before). Tools are inconsistent.

**Workaround:** Use company-scoped Timeline activity + link to the relationship-scoped CTA via `cta_id`. The activity then appears on the Company timeline AND under the CTA's Timeline tab — functionally equivalent to a relationship-scoped activity for surface purposes.

### ⚠️ The `select=` parameter on `fetch_cta_list` is IGNORED

Whatever you pass, the API returns full records. Use `DueDate GTE` filtering instead to constrain payload size.

### ✅ G3.7 — Closing an SP auto-closes its open CTA objectives (positive, document and use)

Validated against real-org data: closing a stagnant Success Plan auto-closes its open CTA objectives (the response includes `ClosedCtas: N`).

**Useful for cleanup workflows.** When you close an SP, you don't need to also iterate through its CTAs to close them — cascade handles it. Document explicitly so plugins can rely on it.

---

## Known gaps (can't do today; flagged for future)

### ⚠️ G3.5 — Value frameworks + goal libraries are not MCP-accessible per-org
Gainsight has customer goals + goal library + playbooks features. They are NOT exposed through the CS MCP today. Plugin AI must intuit outcomes from business context rather than leverage customer-defined value frameworks. **Future priority for Value Analyst + MCP roadmap.**

Plugin guidance: stay framework-agnostic. AI infers outcomes from industry/product/usage context and proposes measurable indicators. If the org's Gainsight has playbooks data accessible (some do, via different endpoints), leverage it; otherwise generate sensibly with the customer's input via a Discovery CTA.

### ⚠️ G3.8 — Cannot link an existing standalone CTA to an existing Success Plan
Today the plugin can attach an SP at CTA creation time via `success_plan_id`, but there's no way to take an existing standalone CTA and link it to an existing SP. Multi-account workflows accumulate orphan CTAs that should logically belong to an active SP.

**Workaround:** When you discover this need, the option is to (a) leave the CTA orphan and add new CTAs inside the SP, or (b) re-create the CTA inside the SP context and close the orphan. Both are imperfect. Surface the limitation to the user.

**Suggested fix:** add `update_cta_link_to_sp` operation OR expose `CtaGroupId` as updatable on `update_cta`.

### ⚠️ G3.9 — Rich-text fields need HTML; `\n` doesn't render as a newline

Plain-text `\n`-delimited content renders as a single blob in Gainsight rich-text fields. Discovered the hard way against real-org Tasks.

**Pattern:** Use HTML formatting:
- Paragraphs: `<p>...</p>`
- Bullet lists: `<ul><li>...</li></ul>`
- Numbered lists: `<ol><li>...</li></ol>`
- Bold: `<strong>...</strong>`
- Line breaks: `<br>`
- Horizontal rule: `<hr>`

**Suggested fix:** tools should auto-detect plain-text input and wrap in `<p>` tags before submission, OR tool descriptions should prominently note this.

### ⚠️ G3.10 — Email composition fields on Tasks are NOT exposed (BIGGEST plugin acceleration unlock)

`cs_task` has hints of email integration:
- `IsEmailSent`
- `ToEmailtype`
- `DynaMetadata`
- `PlaybookTaskId` linking to `cockpit_template`

But no fields exposed for composer subject / body / recipient / from / cc / bcc.

Email Tasks instantiated FROM playbooks carry the email composer pre-loaded; ad-hoc Tasks via `create_cta_task` don't.

**Current workaround:** Plugin puts the draft email content in the Task description (HTML-formatted, with Verify Before Sending checklist). CSM copy-pastes into their email client manually.

**Suggested fix:** Expose `task_email_subject`, `task_email_body` (HTML), `task_email_to`/`cc`/`bcc`, `task_email_template_id` on `create_cta_task` / `update_cta_task`. OR expose a `compose_task_email(task_gsid, ...)` mapping to Gainsight's email service. **This is the highest-impact CS-workflow acceleration if exposed.**

### ⚠️ G3.11 — `comm_#####` evidence IDs from Staircase paste as plain text in Gainsight rich text

Today, `comm_Email_#####` and `comm_Calendar_#####` IDs from Staircase analyses paste as plain text into Gainsight rich text fields. Not clickable.

**Current workaround:** Use `Email (YYYY-MM-DD, Name): paraphrased content` and `Meeting (YYYY-MM-DD): paraphrased content` format. Don't embed raw `comm_#####` IDs in customer-facing fields.

**Suggested fix:** Render `comm_#####` IDs as account-anchored links to the underlying communication (or as embedded Staircase widget).

### Other gaps

- **`survey_response` returns 500** — actual NPS verbatim is inaccessible. Use Staircase sentiment evidence instead.
- **`scorecard_fact` returns 500** — per-measure scorecard values inaccessible. Definitions work; live values don't.
- **`company_person.Name` returns `P_5005`** — use `FirstName` + `LastName` or traverse `PersonId__gr`.
- **Timeline sentiment field is empty for most accounts** — CSMs aren't filling it. Staircase is the reliable sentiment source.

---

## Content-discipline anti-patterns (things you CAN do but shouldn't)

These are about WHAT to write, not how the MCP works. Full canonical guidance in `_shared/gainsight-output-best-practices.md`.

| Avoid | Why |
|---|---|
| Creating a CTA for every action item | Spam — CSMs have backlog management already. Group actions into Tasks under one CTA. |
| Logging the entire raw transcript to Timeline | Wasteful — summarize into the Timeline content template (Customer state, Stakeholders, Evidence, Next play) |
| Mapping every neutral discussion to "Risk" | Inflates risk volume, reduces signal-to-noise. Use Activity or Lifecycle types for non-risk touchpoints. |
| Marking Success Plan as `At Risk` based on one call's sentiment | Need pattern, not one data point |
| Creating a new CTA when an existing open CTA covers the same topic | UPDATE the existing one. Duplicating creates noise; appending to the existing CTA keeps the history intact. |
| Creating an empty Success Plan | Per §5: ≥3 CTA recommendations + outcome goal + success criteria + multi-week motion required before SP creation. Otherwise just create a CTA + Tasks. |
| Skipping Renewal Center / Opportunity check on at-risk accounts | These objects carry "Assumed Churn / More Likely to Churn" forecast stages — surfaces forecast-vs-reality data quality issues |
| Posting internal classification labels in customer-facing Timeline content ("Save-then-Expand", "Skeptical Read", "Risk × Expansion merge", "Recency Tiebreaker") | Customer-facing fields are teammate-facing AND customer-focused. Give the team the customer state, not Claude's synthesis process. |
| Drafting Email-type Tasks without Verify Before Sending checklist | Prevents AI overcommitment to customers. Mandatory per §1 of output best practices. |
| Posting `comm_Email_#####` / `comm_Calendar_#####` evidence IDs in customer-facing fields | They paste as plain text, not clickable. Paraphrase as `Email (date, name): content` instead. (G3.11) |

---

## Source

- `gainsight-mappings.md` (anti-patterns section + payload guards)
- `_shared/gainsight-output-best-practices.md` (v1.1 content discipline)
- Validated against real-org data on multiple accounts
