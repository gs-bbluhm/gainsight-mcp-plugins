# Gainsight CS MCP — Tool Inventory

Every tool, what it does, what to pass, what comes back, and the gotchas. Read this before calling a tool you haven't called recently.

Tools are grouped: **Discovery** (read metadata) → **Resolve** (find IDs) → **Read** (pull records) → **Write** (CTA / Timeline / SP).

---

## Discovery — schema + picklists

### `get_object_metadata(object_name)`
Returns the full field catalog for an object. Use to discover bespoke field names (Segment field, team-member field, required custom fields).

- **Cost:** 100-183k characters per call (Company: 183k, CTA: 100k, Relationship: 178k). **Call once per object per session and cache.**
- **Use for:** finding which fields exist on `company`, `call_to_action`, `cta_group` (Success Plan), `activity_timeline`, `relationship`.
- **Returns:** field name + type + picklist GSID (if applicable).

### `get_picklist_values(object_name, field_name)`
Returns the allowed values for a picklist field. Use after `get_object_metadata` identifies the field.

- **Use for:** discovering tier/segment values, CTA type / status / priority / reason values, SP type values, Timeline activity custom field allowed values.

### `get_activity_types_config()`
Returns the org's full list of Timeline activity types (Meeting, Onboarding Call, EBR, Renewal Call, etc.) plus their custom fields. **Call once per session.** Orgs customize this heavily.

### `ask_scorecard(...)`
Read-only access to scorecard structures. **Limitation:** `scorecard_fact` (per-measure scores) returns 500. Definitions work; live scores don't.

---

## Resolve — name → GSID

### `resolve_customer(search_name, entity_type="company")`
Resolves a customer name to one or more `account_id` matches.

- **Confidence labels:** "high" / "low" — usable.
- **Multiple low-confidence matches:** STOP and ask the user. Do NOT guess.
- **Example:** `resolve_customer(search_name="<Account Name>")` → `<account GSID>` (high confidence, one call).

### `resolve_user(search_name)`
Resolves a user name to one or more user GSIDs.

- **Disambiguation:** when multiple matches come back, pick the record with the most identities attached (Slack, Gong, Salesforce, Zendesk) — those identity counts are a reliable signal of the active user.
- **Example:** a common first name may return multiple matches; pick the user with the most identities attached.

---

## Read — pull records

### `get_records(object_name, where, fields, limit)`
Generic read against any object. Used for direct field pulls.

- **Use for:** pulling Company.RenewalDate / ARR / CSM / health scores in one shot, by GSID or by filter.

### `run_query(...)`
The structured-query interface. Supports complex `where` clauses + joins-like lookups via `gr.` traversal (e.g., `StatusId__gr.Name`).

- **Use for:** book-of-business pulls, tier × renewal-window queries, CSM-scoped reads.

### `fetch_cta_list(where, page_size)`
List CTAs for a company.

- **MANDATORY guard:** `where: CompanyId EQ <gsid> AND IsClosed EQ false AND DueDate GTE <today-90d>` + `page_size: 25`.
- **Without DueDate filter:** large accounts can return 58k+ characters. The `select=` parameter is **IGNORED** — full records always.
- **Date filter is the load-control mechanism.**

### `fetch_success_plan_list(company_id)`
List active + recent Success Plans for a company.

- **Use ALWAYS before creating a new SP** — the canonical reuse-vs-create gate.
- Returns active SPs, due dates, last update timestamps. Past-due + stale-update SPs are cleanup candidates.

### `fetch_timeline_activity_list(...)`
List Timeline activities.

- **Soft-fail expected.** Returns generic "Failed to fetch timeline activities" intermittently. Note in reconciliation, do NOT block the run.

---

## Write — CTA / Timeline / Success Plan

### `manage_cockpit_actions(mode, ...)`
The CTA + CTA Task write tool. **One tool, many modes.**

**Modes for CTAs:**
- `mode='prepare_cta'` (no type_id) → returns ~19 CTA Type options (Risk, Adoption Risk, Renewal Risk, Stakeholder Risk, Activity, Objective, CSQL, EBR, Lifecycle, ROI Risk, etc.)
- `mode='prepare_cta'` (with type_id) → returns dependent picklists: ~34 reasons, 4 priorities, 9 statuses, ~44 playbooks for that type
- `mode='create_cta'` (all GSIDs resolved) → CREATE
- `mode='update_cta'` (cta_id + fields) → UPDATE

**Modes for CTA Tasks:**
- `mode='prepare_cta_task'` → returns Task type options (Action, Email, Call, etc.)
- `mode='create_cta_task'` (cta_id, task params) → CREATE a Task under a CTA
- `mode='update_cta_task'` (task_id, fields) → UPDATE

**Required params for `create_cta`:** company_id, type_id, status_id, priority_id, reason_id, owner_id, due_date, name. Optional: comments (HTML), playbook_id, success_plan_id, relationship_id, custom_field_values.

**For Relationship-scoped CTAs:** include `entity_type="RELATIONSHIP"`, `relationship_id`, `relationship_type_id` (org-bespoke GSID — discover via metadata). Relationship CTAs work — Timeline activities don't (G3.6 workaround).

### `create_timeline_activity(...)`
The Timeline activity write tool.

**Required:** company_id, activity_type, subject, content (HTML), date.

**Often-required custom_field_values:** org-bespoke. Some orgs silently require a custom field (e.g., a `Status` STRING with values like `Green / Yellow / Red / N/A - Internal Update`). First attempt may fail with a clear error naming the missing field; retry-with-correction works. G3.1.

**To link to a CTA:** pass `cta_id`. Activity appears on BOTH Company timeline AND the CTA's Timeline tab.

**To link to a Success Plan:** pass `success_plan_id`.

**Anti-pattern:** Do NOT pass `entity_type="RELATIONSHIP"` + `relationship_id`. Returns "Relationship not found" even with valid IDs that CTA creation accepted. G3.6. Workaround: use company-scoped + `cta_id` linking.

### `manage_success_plan_actions(mode, ...)`
The Success Plan write tool. Same prepare-then-create pattern as CTAs.

**Modes:**
- `mode='prepare_sp'` → returns SP type options + statuses. Orgs commonly have 5-25 types (Renewal Success Plan, value-realization variants, onboarding variants, and org-bespoke templates). Org-specific.
- `mode='create_sp'` → CREATE. Required: company_id, type_id, status_id, owner_id, due_date, name. Optional: comments, custom_field_values.
- `mode='update_sp'` (sp_id + fields) → UPDATE objective fields, due dates, comments, status.

**Pre-create gate:** ALWAYS call `fetch_success_plan_list(company_id)` first. If an active SP exists, prefer UPDATE over CREATE. The plugin's `_shared/gainsight-output-best-practices.md` §5 mandates ≥3 CTA recommendations + clear outcome + measurable success criteria before creating a new SP.

**Cascade behavior (positive, G3.7):** Closing an SP auto-closes its open CTA objectives. Useful for cleanup workflows. Document and rely on it.

---

## Known gaps (read these before assuming an integration exists)

- **Email composition on Tasks** — G3.10. `cs_task` has hints (`IsEmailSent`, `ToEmailtype`, `PlaybookTaskId` → `cockpit_template`) but no fields exposed for subject/body/recipient. Email Tasks instantiated FROM playbooks carry email pre-loaded; ad-hoc Tasks via `create_cta_task` don't. Plugin can only put email content in description; CSM copy-pastes from there. **Highest-impact future unlock.**
- **Standalone CTA → SP linking** — G3.8. Can attach SP at CTA-creation time via `success_plan_id`; cannot link existing standalone CTA to existing SP after the fact. Workaround: re-create the CTA inside the SP context.
- **Survey response text** — `survey_response` returns 500. Actual NPS verbatim is inaccessible. Use Staircase for sentiment evidence instead.
- **Per-measure scorecard scores** — `scorecard_fact` returns 500. Scorecard definitions work; live measure values don't.
- **`comm_#####` evidence IDs** — G3.11. From Staircase analyses, paste as plain text in Gainsight rich text. Not clickable. Workaround: paraphrase + use `Email (date, person): content` / `Meeting (date): content` format. Don't embed raw `comm_#####` IDs in customer-facing fields.

---

## Source

- `gainsight-mappings.md` (original location: `gainsight-meeting-processor/references/`, retained there as artifact source)
- Validated against real-org data
- DS recs G3.1-G3.11 (Gainsight MCP feature recommendations)
