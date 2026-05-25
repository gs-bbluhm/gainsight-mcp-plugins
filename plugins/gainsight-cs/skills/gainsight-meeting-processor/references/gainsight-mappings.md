# Gainsight Mappings

How transcript signals translate into Gainsight Timeline / CTA / Success Plan updates, with verified API field names.

## Object map — what to query for which signal

| Need | Object | API name | Key fields |
|---|---|---|---|
| Account profile | Company | `company` | `Name`, `Arr`, `ARR__gc` (CS), `ST_ARR__gc`, `RenewalDate`, `Stage`, `CSM`, `CurrentScore`, `Staircase_Overall_Health_Score__gc` |
| Open work | CTA | `call_to_action` | `Name`, `DueDate`, `StatusId__gr.Name`, `PriorityId__gr.Name`, `TypeId__gr.Name`, `ReasonId__gr.Name`, `OwnerId__gr.Name` |
| Strategic plans | Success Plan | `cta_group` | `Name`, `DueDate`, `PercentComplete`, `OpenCtas`, `OverdueCtas`, `SuccessPlanTypeId__gr.Name`, `StatusId__gr.Name` |
| Recent interactions | Timeline Activity | `activity_timeline` | Sentiment (R/Y/G), Risk Status, Trending, Meeting Type, NotesPlainText. ⚠️ `fetch_timeline_activity_list` returns generic failure intermittently — soft-fail expected. |
| Forecasted revenue | Company Forecast (Renewal Center) | `gs_company_forecast` | Renewable, Forecasted, GRR%, NRR%, Churn amount, Churn category, Modeled-as (Won/Open/Lost/Stretch), Fiscal quarter |
| Pipeline / Renewal opps | Opportunity | `gs_opportunity` | Stage, Type, ARR by product, **Renewal Stage** (incl. "Assumed Churn / More Likely to Churn"), Competitors, Champion, DS Likelihood Score |
| Survey responses | Survey Participant | `survey_participant` | Send/open/respond dates, NPS response (⚠️ `survey_response` for actual answer text returns 500) |
| People at the account | Company Person / Person | `company_person`, `person` | Role, advocacy status/tier, NPS per contact, certification, LinkedIn |

## Critical: query payload guards

Some Gainsight MCP queries blow the token budget if not constrained.

### `fetch_cta_list` — MANDATORY date filter

```
where: CompanyId EQ <gsid> AND IsClosed EQ false AND DueDate GTE <today-90d>
page_size: 25
```

Without `DueDate GTE`, a busy account can return 50k+ characters. The `select=` parameter is **ignored** by the API. It returns full records regardless. Use date filter as the load-control mechanism.

### `fetch_timeline_activity_list` — soft-fail expected

This tool returns a generic "Failed to fetch timeline activities" on a meaningful percentage of accounts without diagnostic info. Treat as soft-fail, note in reconciliation, do not block the run.

### `get_object_metadata` — call once per session

Metadata responses are 100-183k characters (Company: 183k, CTA: 100k, Relationship: 178k observed). Cache in conversation context; do not re-call within the same session.

## Staircase fields synced into Gainsight Company object

These let you read Staircase signals via the Gainsight MCP without round-tripping through Staircase. Useful when one MCP is unreachable or when you want a single-pull view.

| Field | Type | What it tells you |
|---|---|---|
| `Staircase_Overall_Health_Score__gc` | NUMBER | Current overall health (0-100) |
| `Staircase_Overall_Health_Score_Label__gc` | STRING | "High" / "Medium" / "Low" |
| `Staircase_Account_Dark__gc` | BOOLEAN | No communication signal — risk flag |
| `Staircase_No_Meetings_with_Account__gc` | BOOLEAN | Engagement gap |
| `Staircase_No_Renewal_Discussion__gc` | BOOLEAN | Renewal prep risk |
| `Staircase_No_QBR__gc` | BOOLEAN | Missing strategic touchpoint |
| `Staircase_AI_Renewal_Analysis__gc` | RICHTEXTAREA | AI-generated renewal risk narrative (read this for context!) |
| `Staircase_Open_Items_Score_Label__gc` | STRING | Unresolved-items signal |
| `Staircase_Last_Engagement__gc` | DATE | Recency of any ST-detected engagement |
| `Staircase_Last_ReachOut__gc` | DATE | Last outbound from our side |
| `Staircase_Submitted_Tickets__gc` | NUMBER | Support volume |
| `ST_Segment__gc` | PICKLIST | Staircase tier classification |
| `Date_of_Most_Recent_Flagged_Risk__gc` | DATE | When risk was flagged |
| `Date_Removed_from_Red_Account_List__gc` | DATE | When risk resolved |

## ST-product Relationship fields

For Staircase-product-specific calls (e.g., an account's "- ST" relationship type), pull from the Relationship object:

| Field | What it tells you |
|---|---|
| `ST_State__gc` | Paying / Onboarding / Shadow / Trial |
| `ST_Customer_Records_Purchased__gc` | Contracted volume |
| `ST_Active_Accounts__gc` | Actual usage (COGs driver) |
| `ST_Prospect_Accounts__gc` | Prospect accounts being tracked |
| `ST_Connected_Inboxes__gc` | Integration depth |
| `ST_Chats_Last_90_Days__gc` | Communication volume |
| `ST_Emails_sentreceived_Last_90_Days__gc` | Email volume |
| `ST_Meetings_Last_90_Days__gc` | Meeting volume |
| `ST_Ticket_Comments_Last_90_Days__gc` | Support interaction volume |
| `ST_Staircase_ID__gc` | Cross-system link to Staircase customer ID |

## Competitor intelligence

| Field | Use |
|---|---|
| `Verified_CS_Incumbent_Competitor__gc` | Locked-in CS competitor |
| `Verified_PX_Incumbent_Competitor__gc` | PX competitor |
| `Verified_CE_Incumbent_Competitor__gc` | CE competitor |
| `Verified_CC_Incumbent_Competitor__gc` | CC competitor |
| `competitors__gc` | Multi-select competitor field |
| `<Product>_Incumbent_Competitor_Renewal_Date__gc` | When competitor renews — timing of takeover window |

## Risk + segmentation

| Field | Use |
|---|---|
| `Red_Account__gc` | Risk cohort classification |
| `Current_Deployment_Score__gc` | Deployment health label |
| `CO_Segment__gc` | Company engagement model |
| `CS_Segment__gc`, `PX_Segment__gc`, `CE_Segment__gc`, `IN_Segment__gc` | Per-product segment |
| `type__gc` | Account type |
| `Gainsight_Edition__gc` | License edition |

## Call type → Activity Type

| Call type | Default Activity Type | Notes |
|---|---|---|
| Kickoff | `Onboarding Call` | |
| Planning session | `Planning Call` | |
| Platform session / training | `Training Call` | |
| QBR / EBR | `Executive Business Review` | Has rich required fields (Meeting Type, Risk Status, Exec present) |
| At-risk call | `Escalation Call` | |
| Renewal conversation | `Renewal Call` | |
| Cadence / weekly sync | `Meeting` | Default for ambiguous types |
| Ad-hoc | `Meeting` | |
| Closeout / handover | `Handover Call` | |
| Implementation review | `Implementation Review` | |
| Internal PM observation | `Internal Note` | |
| Async product intel | `Update` (Meeting Type: "Product Engagement") | |
| Verified Outcome captured | `Verified Outcome` | Requires Metric Type, Metric |

Call `get_activity_types_config` once per session for the canonical list — orgs customize this.

## Risk language → CTA priority + reason

| Transcript signal | CTA Priority | Reason field |
|---|---|---|
| "We're evaluating other vendors" / buyer-named competitor | High | `Competitor` (or `Renewal Risk` if at renewal) |
| "Lost confidence", "broken sync", "can't deploy" | High | `ROI Risk` |
| "Frustrated", "this isn't working", "delays" | Medium | `Other` or product-area-specific |
| Stakeholder churn ("X left the company") | Medium | `Stakeholder Risk` |
| "We may not renew" / explicit churn intent | Critical | `Renewal Risk` |
| Implementation blockers from customer side | Medium | `Adoption Risk` |

Pull org-specific CTA Types via `get_picklist_values` on `call_to_action.TypeId` — common: `Risk`, `Adoption Risk`, `Renewal Risk`, `Stakeholder Risk`, `Activity`, `Objective`, `CSQL`.

### PM-specific CTA fields (for product-side use)

| Field | Use |
|---|---|
| `Product__gc` | Tag to CS, ST, PX, CC, CE, or XProduct |
| `product_risk_status__gc` | Track resolution lifecycle (Understanding / Formulating / Sign-off / Delivered / Complete / Will Not) |
| `related_product_area__gc` | Cockpit, Integrations, Rules Engine, Dashboards, etc. |
| `Product_Owner__gc` | LOOKUP to gsuser |
| `Engineering_Owner__gc` | LOOKUP to gsuser |
| `Link_to_Enhancement_Request__gc` | URL to Linear/Jira |
| `Renewal_Risk_Reason__gc` | Budgetary / Technical / Competitor / etc. |

## Timeline activity content structure

For meeting-processor output, structure the Timeline Activity content as:

```markdown
**Summary**
<1-2 paragraph narrative>

**Wins**
- "<verbatim quote>" — <name>

**Risks / Open Threads**
- <risk> (Staircase evidence: <ID>)

**Decisions**
- <decision>

**Action Items**
- <action> — <owner>, due <date>

**60-Day Staircase Context**
- Sentiment trajectory: <improving / stable / declining / fragile>
- Top risks: <list, with evidence IDs>
- Open commercial discussions: <list>
```

Use custom_field_values when creating:
```
{
  "Meeting Type": "Product Engagement",
  "Status": "Green",           // R/Y/G
  "Discussed Product": ["ST"],
  "Internal Attendees": "<your name>",
  "External Attendees": "...",
  "Trending": "Positively"
}
```

## Wins → Success Plan objective update

If a transcript win maps to an open Success Plan objective:
- Status: `On Track` (or `Complete` if explicitly accomplished)
- Next step: 1 sentence describing the next milestone
- Comment: include the win quote with attribution

## Anti-patterns

| Avoid | Why |
|---|---|
| Creating a CTA for every action item | Spam — CSMs have backlog management already |
| Logging the entire raw transcript to Timeline | Wasteful — summarize |
| Mapping every neutral discussion to "Risk" | Inflates risk volume, reduces signal-to-noise |
| Marking Success Plan as `At Risk` based on one call's sentiment | Need pattern, not one data point |
| Creating a new CTA when an existing open CTA covers the same topic | **Update the existing one instead.** If there is already an open Risk CTA on the same topic, that's the right home for new commentary. Duplicating it would be noise. |
| Skipping Renewal Center / Opportunity check | These objects carry the explicit "Assumed Churn / More Likely to Churn" forecast stage, which can catch data-quality issues invisible from Staircase signal alone. |

## Known CS MCP gaps

- `survey_response` returns 500 — actual NPS response text inaccessible
- `scorecard_fact` returns 500 — per-measure scores inaccessible (scorecard definitions work)
- `company_person.Name` returns P_5005 — use `FirstName` / `LastName` or traverse `PersonId__gr`
- Timeline sentiment field is empty for most accounts (CSMs aren't filling it) — Staircase is the reliable sentiment source

