# Staircase MCP: Report Recipes

The canonical report for each core question. A recipe is not the shortest query that answers the question; it is the column set that gives you enough context to make the right call-outs. Every config here was run live against a production org before it was written down.

## Contents
- How to use a recipe (placeholders, conventions)
- `scope.membership`: whose book is this (the first-call contract)
- `book.context`: a book of business, ready for triage
- `renewal.window`: upcoming renewals with the signals that decide them
- `risk.cohort`: the at-risk set, with who is (and isn't) engaged
- `expansion.pipeline`: opportunities by confidence and momentum
- `lifecycle.evidence`: signal to communications to quotes
- `account.360`: one account, fully loaded
- `team.rollup`: a team's books, risk, and workload in one call
- `stakeholder.coverage`: role gaps and stale executive relationships
- `voc.pain_profile`: what a cohort is talking about
- `churn.retro`: what we lost and why

## How to use a recipe

**Placeholders.** `<book_owner_field>` is a customer field whose `referencedEntity` is `user`, resolved by `scope.membership` (it may be `owner` or an org-specific role field; never assume). `<user_id>` is `current_user_id` from `staircase_report_metadata`, or a teammate's `user.id`. `<window>` is a DateRange enum such as `[PastMonth]`, `[Past3Months]`, or `[PastYear]`. `<account_id>` comes from `staircase_account_lookup`. `<manager_user_id>` is the `user.id` of a team's manager. `<role:decision_maker>`, `<role:executive_sponsor>`, `<role:champion>`, and `<role:departed>` are lists of this org's stakeholder role names, mapped once and cached as `org.role_map` in the profile (role names are configurable: a champion role may be called "Adoption Champion", and "Contract Signer" may be a second decision-maker role).

**Conventions every recipe follows.**
- Scope a book with `{"field":{"id":"customer.<book_owner_field>"},"operator":"In","values":[<user_id>]}`. The name form `customer.<book_owner_field>.full_name In ["<name>"]` also works when you only have names.
- Scope a team in one filter by following the book field to its manager: `customer.<book_owner_field>.manager In [<manager_user_id>]`. The same path works from other roots (`stakeholder.customer.<book_owner_field>.manager`, `lifecycle_event.customer.<book_owner_field>.manager`).
- Add `customer.status In ["Active"]` unless the ask is about churned accounts or one named account.
- Add the profile's `scope.filter` (a portfolio slice such as a product line or region) to every recipe when it's set, and swap `customer.revenue_converted` for `scope.revenue_field` in revenue columns and totals. On multi-product accounts, account-level risk can concern a different product than the slice: read `lifecycle_event.products` on recent events before attributing it.
- A Reference column returns a raw integer id. Always select the name alongside it (`customer.name`, or `<entity>.customer.name` on other roots) and give the id column an explicit label such as "Account id", or its header collides with the name column.
- Label every column. Aggregation columns without distinct labels collide.
- Paging: sort, then page with `pagination`, and put the entity id last in `sortBy` so pages neither drop nor repeat rows. Exception: sorting by `lifecycle_event.id` is ignored today, so for events narrow the window instead (anti-patterns.md R13).
- Check the base rate before flagging an absence. Before calling out "no QBR booked" on each row, COUNT the org's active accounts with `customer.next_qbr_date Defined`; if almost none have one, say so once as a systemic gap (R17).
- Verbose text columns (`customer.summary`, `customer.risk.analysis`, `customer.expansion.summary`, `customer.churn.synopsis`, `lifecycle_event.direct_quotes`) cost tokens and hit `row_cap` sooner. Pull them for a shortlist, not the whole cohort.
- Collection fields (`lifecycle_event.signals`, `.direct_quotes`, `.products`, `.comm_types`, `customer.churn.issues`) are returnable, but their contents are never filterable (a few accept a presence test such as `Defined`). Filter in the report on something else, then cluster the Collection client-side.
- If `staircase_get_playbook` is available and lists a topic that matches the ask, read it first and prefer it where it differs.

---

## `scope.membership`: whose book is this

**Answers:** "my accounts", "my book", "is this person a book carrier", and which field links a person to their accounts. Run it once per org, before the first book-scoped question, and cache the answer.

**Build it from metadata.** List every `customer.*` field whose `referencedEntity` is `user` (always includes `customer.owner`; many orgs add CSM, renewal-owner, or specialist fields). Add one child COUNT column per field.

```json
{"entity": "user",
 "columns": [
  {"field": {"id": "user.full_name"}, "key": "name", "label": "Name"},
  {"field": {"id": "user.title"}, "key": "title", "label": "Title"},
  {"field": {"id": "user.manager.full_name"}, "key": "mgr", "label": "Manager"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.owner", "aggregation": "COUNT"}, "key": "f1", "label": "As owner"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<role_field_2>", "aggregation": "COUNT"}, "key": "f2", "label": "As <role_field_2>"}
 ],
 "filter": {"operator": "And", "conditions": [{"field": {"id": "user.id"}, "operator": "In", "values": [<user_id>]}]},
 "sortBy": []}
```

**Reading it.**
- One field with a real count: that field is the book. Don't ask.
- Two or more fields with real counts: ask one question that names the fields and counts ("You're the owner on N accounts and the renewal owner on M. Which book is this about?").
- No field: not a book carrier. Check their reports (`user.manager In [<user_id>]`) with the same child COUNTs: if the reports hold books, use team scope (via `team.rollup`); if they hold none, use portfolio scope. Never hand someone an empty team book.

**Why it works:** the same child COUNT that powers rollups answers membership directly, so scope resolution needs no guessing and no label matching. Population counts alone never decide between two real role fields; the person's intent does.

---

## `book.context`: a book of business, ready for triage

**Answers:** "what's on my plate", "where should I focus this week", "show me my book". Carries every input the priority composite (query-patterns.md) needs, so the book can be scored without a second pull.

```json
{"entity": "customer",
 "arguments": {"dateRange": "[Past3Months]"},
 "columns": [
  {"field": {"id": "customer.id"}, "key": "id", "label": "Account id"},
  {"field": {"id": "customer.name"}, "key": "name", "label": "Account"},
  {"field": {"id": "customer.tier.name"}, "key": "tier", "label": "Tier"},
  {"field": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": true}}, "key": "rev", "label": "Revenue"},
  {"field": {"id": "customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "customer.buckets.health"}, "key": "health", "label": "Health"},
  {"field": {"id": "customer.buckets.engagement.score"}, "key": "eng", "label": "Engagement"},
  {"field": {"id": "customer.buckets.sentiment.score"}, "key": "sent", "label": "Sentiment"},
  {"field": {"id": "customer.buckets.open_items.numeric_score"}, "key": "open", "label": "Open items score"},
  {"field": {"id": "customer.risk.risk_level"}, "key": "risk", "label": "Risk"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "MAX", "aggregatedField": {"id": "lifecycle_event.date"},
             "condition": {"operator": "And", "conditions": [{"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]}]}},
   "key": "lastCR", "label": "Last churn-risk fired"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [
               {"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]},
               {"field": {"id": "lifecycle_event.date"}, "operator": "InRange", "value": "[Past3Months]"}]}},
   "key": "cr", "label": "Churn-risk events 90d"},
  {"field": {"id": "customer.expansion.readiness_level"}, "key": "exp", "label": "Expansion readiness"},
  {"field": {"id": "customer.expansion.momentum_indicator"}, "key": "mom", "label": "Expansion momentum"},
  {"field": {"id": "customer.last_engagement"}, "key": "lastEng", "label": "Last engagement"},
  {"field": {"id": "customer.last_dm_touch"}, "key": "dm", "label": "Last decision-maker touch"},
  {"field": {"id": "customer.email.organization_last_sent"}, "key": "weLast", "label": "Last email from us"},
  {"field": {"id": "customer.email.customer_last_sent"}, "key": "theyLast", "label": "Last email from them"},
  {"field": {"id": "customer.event.next_event"}, "key": "nextMtg", "label": "Next meeting"},
  {"field": {"id": "customer.next_qbr_date"}, "key": "qbr", "label": "Next QBR"},
  {"field": {"id": "customer.relationship_score.multi_threaded"}, "key": "mt", "label": "Multi-threaded"},
  {"field": {"id": "customer.relationship_score.stakeholders_count"}, "key": "stk", "label": "Stakeholders"},
  {"field": {"id": "customer.ticket.submitted_count", "arguments": {"filter.user": {"operator": "And", "conditions": []}, "productId": []}}, "key": "tix", "label": "Tickets 90d"},
  {"field": {"id": "customer.url"}, "key": "url", "label": "Staircase link"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "customer.<book_owner_field>"}, "operator": "In", "values": [<user_id>]}]},
 "sortBy": [{"columnKey": "renew", "direction": "Asc"}, {"columnKey": "id", "direction": "Asc"}]}
```

**Why these columns.**
| Column | The call-out it enables |
|---|---|
| Renewal + Risk + Next QBR + Next meeting | "Renews in 30 days, risk 5, no QBR and no meeting booked": the most urgent pattern in any book. Check the QBR base rate first; when almost no account has one booked, make it one book-level call-out, not a flag on every row |
| Last churn-risk fired + Churn-risk events 90d | Whether the risk is fresh (fired last week) or stale (fired months ago and never re-confirmed). Risk level alone says an analyst fired at some point; these say when and how often |
| Last decision-maker touch | "The decision maker hasn't been touched in months and the renewal is weeks away" |
| Last email from us vs from them | "We keep reaching out; they stopped replying" (silent risk) |
| Renewal in the past on an Active account | Data hygiene: the renewal date was never updated, so every renewal view is wrong for it |
| Multi-threaded false + Stakeholders | Single-threaded exposure; pair with renewal proximity |
| Engagement, Sentiment, Open items, Tickets 90d | The remaining inputs to the priority composite |
| Expansion readiness + momentum with Risk | Save-into-expansion candidates (query-patterns.md); a cooling expansion on a healthy account |
| Staircase link | An "open in Staircase" action on every row of the rendered app |

**Cost:** cheap; no verbose text columns. Add `customer.summary` only for the top 10. The report-level `dateRange` applies to the windowed columns (tickets).

**Follow-on:** for accounts with a fresh churn-risk fire, run `lifecycle.evidence` on them before calling them at risk. **Renders as:** Book Cockpit.

---

## `renewal.window`: upcoming renewals with the signals that decide them

**Answers:** "what's renewing this quarter", "which renewals need attention", the Renewal Radar.

```json
{"entity": "customer",
 "columns": [
  {"field": {"id": "customer.id"}, "key": "id", "label": "Account id"},
  {"field": {"id": "customer.name"}, "key": "name", "label": "Account"},
  {"field": {"id": "customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "customer.tier.name"}, "key": "tier", "label": "Tier"},
  {"field": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": true}}, "key": "rev", "label": "Revenue"},
  {"field": {"id": "customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "customer.risk.risk_level"}, "key": "risk", "label": "Risk"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "MAX", "aggregatedField": {"id": "lifecycle_event.date"},
             "condition": {"operator": "And", "conditions": [{"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]}]}},
   "key": "lastCR", "label": "Last churn-risk fired"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [
               {"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]},
               {"field": {"id": "lifecycle_event.date"}, "operator": "InRange", "value": "[Past3Months]"}]}},
   "key": "cr", "label": "Churn-risk events 90d"},
  {"field": {"id": "customer.buckets.health"}, "key": "health", "label": "Health"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "MAX", "aggregatedField": {"id": "lifecycle_event.date"},
             "condition": {"operator": "And", "conditions": [{"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["renewal_discussion"]}]}},
   "key": "lastComm", "label": "Last commercial discussion"},
  {"field": {"id": "customer.last_dm_touch"}, "key": "dm", "label": "Last decision-maker touch"},
  {"field": {"id": "customer.event.next_event"}, "key": "nextMtg", "label": "Next meeting"},
  {"field": {"id": "customer.next_qbr_date"}, "key": "qbr", "label": "Next QBR"},
  {"field": {"id": "customer.relationship_score.multi_threaded"}, "key": "mt", "label": "Multi-threaded"},
  {"field": {"id": "customer.expansion.readiness_level"}, "key": "exp", "label": "Expansion readiness"},
  {"field": {"id": "customer.expansion.momentum_indicator"}, "key": "mom", "label": "Expansion momentum"},
  {"field": {"id": "customer.url"}, "key": "url", "label": "Staircase link"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "customer.renewal_date"}, "operator": "InRange", "value": "[Next90Days]"}]},
 "sortBy": [{"columnKey": "renew", "direction": "Asc"}, {"columnKey": "id", "direction": "Asc"}]}
```

Add the `<book_owner_field>` scope condition for a personal view; leave it off for a leader's view. To surface only the renewals that need attention, add `customer.risk.risk_level GreaterOrEqual 4` or rank the full window with the priority composite.

**Why these columns.**
| Column | The call-out it enables |
|---|---|
| Last commercial discussion (MAX date of `renewal_discussion` events) | "Renews in 3 weeks and nobody has discussed terms since spring": the unspoken-renewal risk |
| Last churn-risk fired + events 90d, with Risk | A risk score with fresh evidence behind it, vs a stale score |
| Next meeting + Next QBR | No meeting and no business review booked before the renewal. Check the org's QBR base rate first: when almost no account has a review booked, it's a systemic habit gap (reviews aren't being booked ahead, or aren't titled "QBR", "EBR", or "Business Review"), not a per-account signal, and Next meeting carries the per-account call-out |
| Last decision-maker touch | The person who signs hasn't been engaged |
| Expansion readiness + momentum | Defend, grow, or both: the play for each renewal |
| Book owner | Who to talk to (context only) |

**Label note:** `renewal_discussion` displays as "Commercial discussion" in many orgs. Event types are partly org-specific; read the `lifecycle_event.type` options from metadata and use the option ids.

**Book owner is context, never a ranking.** Show who carries each account so the reader knows who to talk to; never sort or total by person to imply performance (analysis-methodology.md, anti-libel framing).

**Follow-on:** for renewals with a fresh churn-risk fire or a stale commercial discussion, run `lifecycle.evidence` on the account's full recent timeline to surface pricing asks, deadlines, and blocking constraints (in live testing, one "exit intent" signal turned out to be a price discrepancy on the order form days before renewal). **Renders as:** Renewal Radar.
---

## `risk.cohort`: the at-risk set, with who is (and isn't) engaged

**Answers:** "which accounts are at risk", "where are we blindsided", "where have we gone quiet".

```json
{"entity": "customer",
 "columns": [
  {"field": {"id": "customer.id"}, "key": "id", "label": "Account id"},
  {"field": {"id": "customer.name"}, "key": "name", "label": "Account"},
  {"field": {"id": "customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "customer.tier.name"}, "key": "tier", "label": "Tier"},
  {"field": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": true}}, "key": "rev", "label": "Revenue"},
  {"field": {"id": "customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "customer.risk.risk_level"}, "key": "risk", "label": "Risk"},
  {"field": {"rootEntityPath": "customer", "childEntity": "lifecycle_event", "referenceField": "lifecycle_event.customer", "aggregation": "MAX", "aggregatedField": {"id": "lifecycle_event.date"},
             "condition": {"operator": "And", "conditions": [{"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]}]}},
   "key": "lastCR", "label": "Last churn-risk fired"},
  {"field": {"id": "customer.last_dm_touch"}, "key": "dm", "label": "Last decision-maker touch"},
  {"field": {"id": "customer.event.next_event"}, "key": "nextMtg", "label": "Next meeting"},
  {"field": {"id": "customer.email.owner_sent_count", "arguments": {"dateRange": "[PastMonth]", "aggregateParentChild": false, "productId": []}}, "key": "own", "label": "Owner emails 30d"},
  {"field": {"id": "customer.email.organization_sent_count", "arguments": {"dateRange": "[PastMonth]", "aggregateParentChild": false, "productId": [], "filter.user": {"operator": "And", "conditions": []}}}, "key": "org", "label": "Org emails 30d"},
  {"field": {"id": "customer.email.customer_last_sent"}, "key": "theyLast", "label": "Last email from them"},
  {"field": {"id": "customer.relationship_score.multi_threaded"}, "key": "mt", "label": "Multi-threaded"},
  {"field": {"id": "customer.url"}, "key": "url", "label": "Staircase link"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
  {"operator": "Or", "conditions": [
    {"field": {"id": "customer.risk.risk_level"}, "operator": "GreaterOrEqual", "value": 4},
    {"field": {"rootEntityPath": "customer", "childEntity": "insight", "referenceField": "insight.customer", "aggregation": "EXISTS",
               "condition": {"operator": "And", "conditions": [{"field": {"id": "insight.type"}, "operator": "Equal", "value": "ChurnRisk"}]}},
     "operator": "Equal", "value": true}]}]},
 "sortBy": [{"columnKey": "rev", "direction": "Desc"}, {"columnKey": "id", "direction": "Asc"}]}
```

**Why these columns.**
| Column | The call-out it enables |
|---|---|
| Org emails 30d with Last decision-maker touch | "Activity is not access": heavy email volume with no executive contact in years, on a top-revenue at-risk account |
| Owner emails vs Org emails | Owner low, org high: the account owner is absent while support or others carry it. Both near zero: nobody is talking to an at-risk account |
| Last churn-risk fired | Fresh (this week) vs stale risk |
| Revenue + Renewal + Tier | Rank by money and time, not by risk score alone |
| Risk OR ChurnRisk insight | Catches accounts flagged by the insight but not yet scored, and scored but not flagged |
| Book owner | Who to talk to (context only) |

`owner_sent_count` counts the `customer.owner` field's sends, which may not be `<book_owner_field>`; label it "Owner emails" and say so when they differ.

**Book owner is context, never a ranking.** Show who carries each account so the reader knows who to talk to; never sort or total by person to imply performance (analysis-methodology.md, anti-libel framing).

**Follow-on:** `lifecycle.evidence` for the top of the list, reading the full timeline before calling anything "leaving". **Renders as:** Risk Radar.
---

## `expansion.pipeline`: opportunities by confidence and momentum

**Answers:** "where can we expand", "which opportunities are real", "expansion plays for my book".

```json
{"entity": "expansion_opportunity",
 "columns": [
  {"field": {"id": "expansion_opportunity.customer.name"}, "key": "acct", "label": "Account"},
  {"field": {"id": "expansion_opportunity.customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "expansion_opportunity.offering"}, "key": "offer", "label": "Offering"},
  {"field": {"id": "expansion_opportunity.summary_line"}, "key": "sum", "label": "Summary"},
  {"field": {"id": "expansion_opportunity.category"}, "key": "cat", "label": "Category"},
  {"field": {"id": "expansion_opportunity.momentum_state"}, "key": "mom", "label": "Momentum"},
  {"field": {"id": "expansion_opportunity.confidence_level"}, "key": "conf", "label": "Confidence"},
  {"field": {"id": "expansion_opportunity.decision_maker"}, "key": "dm", "label": "Decision maker"},
  {"field": {"id": "expansion_opportunity.timeline_indicator"}, "key": "when", "label": "Timeline"},
  {"field": {"id": "expansion_opportunity.budget_status"}, "key": "budget", "label": "Budget"},
  {"field": {"id": "expansion_opportunity.competitive_mention"}, "key": "comp", "label": "Competitive mention"},
  {"field": {"id": "expansion_opportunity.customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "expansion_opportunity.customer.risk.risk_level"}, "key": "risk", "label": "Account risk"},
  {"field": {"id": "expansion_opportunity.customer.buckets.health"}, "key": "health", "label": "Account health"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "expansion_opportunity.customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "expansion_opportunity.confidence_level"}, "operator": "In", "values": ["High", "Medium"]}]},
 "sortBy": []}
```

**Why these columns.**
| Column | The call-out it enables |
|---|---|
| Confidence x Momentum | High + Heating = pursue now; High + Cooling = a slipping opportunity to rescue |
| Account risk and health (two hops through the customer reference) | High confidence on an at-risk or unhealthy account needs the Risk x Expansion merge before anyone pitches |
| Competitive mention | A competitor is already in the conversation for this expansion |
| Renewal | Time the expansion ask to the renewal conversation |
| Decision maker, Budget, Timeline | Whether the opportunity is actionable or aspirational |
| Book owner | Who to talk to (context only) |

One account can have several opportunity rows; never assume one row per account. `opportunity_value` is prose, never sum it. Scope to a book with `expansion_opportunity.customer.<book_owner_field> In [<user_id>]`. **Renders as:** Expansion Workbench.
---

## `lifecycle.evidence`: signal to communications to quotes

**Answers:** "why is this account at risk", "what did they actually say", "what did we promise", "who is replacing us".

**Step 1, the events** (root `lifecycle_event`):
```json
{"entity": "lifecycle_event",
 "columns": [
  {"field": {"id": "lifecycle_event.id"}, "key": "eid", "label": "Event id"},
  {"field": {"id": "lifecycle_event.customer"}, "key": "aid", "label": "Account id"},
  {"field": {"id": "lifecycle_event.customer.name"}, "key": "acct", "label": "Account"},
  {"field": {"id": "lifecycle_event.customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "lifecycle_event.customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "lifecycle_event.customer.risk.risk_level"}, "key": "risk", "label": "Account risk"},
  {"field": {"id": "lifecycle_event.type"}, "key": "type", "label": "Type"},
  {"field": {"id": "lifecycle_event.date"}, "key": "date", "label": "Date"},
  {"field": {"id": "lifecycle_event.signals"}, "key": "signals", "label": "Signals"},
  {"field": {"id": "lifecycle_event.comm_types"}, "key": "comm", "label": "Channels"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "lifecycle_event.customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "lifecycle_event.type"}, "operator": "In", "values": ["churn_risk"]},
  {"field": {"id": "lifecycle_event.date"}, "operator": "InRange", "value": "<window>"}]},
 "sortBy": [{"columnKey": "date", "direction": "Desc"}]}
```
Scope with `lifecycle_event.customer.<book_owner_field> In [<user_id>]`, a team with `lifecycle_event.customer.<book_owner_field>.manager In [<manager_user_id>]`, or one account with `lifecycle_event.customer In [<account_id>]` (drop the type filter for the account's full timeline). The Type column renders as a raw token (for example `EventTypeId(raw=churn_risk)`); map it to its label from the metadata options. Sorting by event id is ignored today, so don't page ties on date: narrow the window until one page holds the result, and dedupe by event id (anti-patterns.md R13).

**Step 2, triage the Signals client-side.** Signals are the sharpest early-warning primitive in Staircase, but they are a Collection, so cluster them yourself. Use hard-stop signals (concrete exit actions, migration in progress, auto-renewal opt-out, contract ultimatums, a named competitor replacement) to decide which events to read first, not to conclude intent: a signal records what was discussed, not why. Pull the account's full recent timeline (all event types) so a churn-risk event sits next to the commercial discussions and positive messages around it. The signal vocabulary is org-generated; read the values you get rather than assuming a fixed list.

**Step 3, the communications:** `staircase_list_communications(event_ids=[...])`, up to 20 ids per call. Each row gives the channel, date, `account_id`, participants (typed User for your team, Stakeholder for theirs), and for emails a `summary` and a `direction` (inbound, outbound, or mixed); meetings return a `call_summary` plus `issues[]` and `action_items[]`. Check `total_count`, `complete`, and `dropped_group_ids` and say how much you read.

**A row is the whole thread as of its latest message**, not the moment the signal fired. Compare the row's date with the event date: when the thread moved on (an ultimatum on Monday, the customer booking the renewal call on Wednesday), the trajectory is the finding. When the summary and the signal disagree, fetch the evidence and read it.

**Step 4, the quotes:** summaries are not quotable. Pass the `evidence_id`s you need to `staircase_fetch_evidence(ids=[...])` for verbatim text; request transcripts only with a `transcript_query`.

**What this chain unlocks:**
| Use | How |
|---|---|
| Risk dossier in their words | churn_risk events, top signals, meeting issues, fetched quotes |
| Commitment ledger | `action_items[]` across a book's recent meeting rows. Items are plain sentences that name the actor ("Jordan to send the updated deck", "Acme Corp to confirm user counts"): split ours vs theirs by matching that leading name against the row's participants (User or Stakeholder) or the account name, and mark any item you can't attribute as unassigned |
| Competitive displacement | events carrying a competitor-replacement signal, then the competitor named in the communications |
| Coverage accountability | `participants` of type User on at-risk threads: who from your side is present, and who isn't |
| Advocacy | `exceptional_positive` events, then the communications, for evidence-backed references |

**Renders as:** Account 360 (evidence timeline) and the drill-down in Risk Radar.

---

## `account.360`: one account, fully loaded

**Answers:** "catch me up on this account", "prep me for this meeting", "hand this account over".

A composition of verified pieces, in this order:
1. `staircase_account_lookup` for the id.
2. The account row: `book.context` columns with `customer.id In [<account_id>]` (no status filter), plus the verbose fields for this one account: `customer.summary`, `customer.risk.analysis`, `customer.expansion.summary`, `customer.handoff.strategic_summary`.
3. The roster: `stakeholder` root, `stakeholder.customer In [<account_id>]`, columns `stakeholder.name`, `.title`, `.role.name`, `.last_engagement`, `.last_reach_out`, `.touch_frequency`, `.email_stats.last_received`.
4. The timeline: `lifecycle.evidence` with `lifecycle_event.customer In [<account_id>]`, all types, `<window>` of `[Past3Months]`, then `staircase_list_communications` on the most recent events.
5. Open expansion: `expansion.pipeline` with `expansion_opportunity.customer In [<account_id>]`.
6. Only if the ask needs narrative judgment (stance, the play): `staircase_analyze_account`, grounded in the evidence ids from steps 4 and 5.

**Renders as:** Account 360.

---

## `team.rollup`: a team's books, risk, and workload in one call

**Answers:** "how is my team doing", "who is overloaded", "prep my 1:1 with a teammate".

**First, find the team's book field.** Run `scope.membership` with `user.manager In [<manager_user_id>]` in place of the single-user filter. Teams usually carry their books on one field, with a few accounts on a second; use the dominant field below and mention the other.

```json
{"entity": "user",
 "columns": [
  {"field": {"id": "user.full_name"}, "key": "name", "label": "Name"},
  {"field": {"id": "user.title"}, "key": "title", "label": "Title"},
  {"field": {"id": "user.mailbox_connected"}, "key": "mbx", "label": "Mailbox connected"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<book_owner_field>", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [{"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]}]}},
   "key": "book", "label": "Book size"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<book_owner_field>", "aggregation": "SUM",
             "aggregatedField": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": false}},
             "condition": {"operator": "And", "conditions": [{"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]}]}},
   "key": "bookRev", "label": "Book revenue"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<book_owner_field>", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [
               {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
               {"field": {"id": "customer.risk.risk_level"}, "operator": "GreaterOrEqual", "value": 4}]}},
   "key": "riskN", "label": "At-risk accounts"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<book_owner_field>", "aggregation": "SUM",
             "aggregatedField": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": false}},
             "condition": {"operator": "And", "conditions": [
               {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
               {"field": {"id": "customer.risk.risk_level"}, "operator": "GreaterOrEqual", "value": 4}]}},
   "key": "riskRev", "label": "At-risk revenue"},
  {"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<book_owner_field>", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [
               {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
               {"field": {"id": "customer.renewal_date"}, "operator": "InRange", "value": "[Next90Days]"}]}},
   "key": "ren", "label": "Renewing 90d"},
  {"field": {"id": "user.effort.effort_hours", "arguments": {"dateRange": "[PastMonth]", "filter.customer": {"operator": "And", "conditions": []}}}, "key": "eff", "label": "Effort hrs 30d"},
  {"field": {"id": "user.event_stats.total_hours", "arguments": {"dateRange": "[PastMonth]", "filter.customer": {"operator": "And", "conditions": []}}}, "key": "mtg", "label": "Meeting hrs 30d"},
  {"field": {"id": "user.email_stats.response_time_hours", "arguments": {"dateRange": "[PastMonth]", "filter.customer": {"operator": "And", "conditions": []}}}, "key": "rt", "label": "Response time hrs"}
 ],
 "filter": {"operator": "And", "conditions": [{"field": {"id": "user.manager"}, "operator": "In", "values": [<manager_user_id>]}]},
 "sortBy": []}
```

**Why these columns.**
| Column | The call-out it enables |
|---|---|
| Book size, Book revenue, At-risk accounts and revenue, Renewing 90d | Each person's exposure, computed server-side with no client-side join |
| Effort, Meeting hours, Response time | The dual-signal overload test in analysis-methodology.md. Effort and meeting hours cover all of a person's accounts, not only this book |
| Mailbox connected | A teammate whose mailbox isn't connected makes their whole book look dark, which is a setup fix, not a risk |

**Read it carefully.**
- **Pooled users are a segment, not a person.** Shared placeholder users (a scaled or digital program pool) can carry hundreds of accounts with no effort, no title, and no mailbox, and `user.is_auto` doesn't flag them. Show a pool as its own row and leave it out of per-person comparisons and averages.
- **Zero on the team's field isn't "unassigned."** Check the person's other role fields before saying they carry no book.
- **Normalize before comparing.** A 3-account book and a 30-account book aren't comparable per hour.
- **This is for coaching a team, never for ranking people.** Show load and exposure so a manager knows where to help; don't sort or total by person to imply performance (analysis-methodology.md).

**Renders as:** Team Roster.

---

## `stakeholder.coverage`: role gaps and stale executive relationships

**Answers:** "who's missing a decision maker", "where have we lost exec coverage", "which key contacts have gone cold". Two reports: role coverage per account, then the stale executives behind it.

**Map the roles first.** Every org has three built-in roles that can't be renamed: "Decision Maker", "Champion", and "Executive Sponsor". Staircase's own signals (`customer.last_dm_touch`, the decision-maker and champion insights) count only those exact names. Orgs add their own roles too, including look-alikes. Pull the role list once (root `stakeholder_role`, `stakeholder_role.name` plus a child COUNT of `stakeholder` through `stakeholder.role`), map any look-alikes and the org's departed role to the concepts, confirm with the user, and cache the mapping as `org.role_map`. When a built-in role holds almost no one while a look-alike holds many, count both for coverage and say that Staircase's signals don't see the look-alike: retagging those people to the built-in role makes the signals work.

**(a) Role coverage** (root `customer`, one row per account):
```json
{"entity": "customer",
 "columns": [
  {"field": {"id": "customer.id"}, "key": "id", "label": "Account id"},
  {"field": {"id": "customer.name"}, "key": "name", "label": "Account"},
  {"field": {"id": "customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "customer.risk.risk_level"}, "key": "risk", "label": "Risk"},
  {"field": {"rootEntityPath": "customer", "childEntity": "stakeholder", "referenceField": "stakeholder.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [{"field": {"id": "stakeholder.role.name"}, "operator": "In", "values": <role:decision_maker>}]}},
   "key": "dm", "label": "Decision makers"},
  {"field": {"rootEntityPath": "customer", "childEntity": "stakeholder", "referenceField": "stakeholder.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [{"field": {"id": "stakeholder.role.name"}, "operator": "In", "values": <role:executive_sponsor>}]}},
   "key": "es", "label": "Executive sponsors"},
  {"field": {"rootEntityPath": "customer", "childEntity": "stakeholder", "referenceField": "stakeholder.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [{"field": {"id": "stakeholder.role.name"}, "operator": "In", "values": <role:champion>}]}},
   "key": "ch", "label": "Champions"},
  {"field": {"rootEntityPath": "customer", "childEntity": "stakeholder", "referenceField": "stakeholder.customer", "aggregation": "COUNT",
             "condition": {"operator": "And", "conditions": [{"field": {"id": "stakeholder.role.name"}, "operator": "In", "values": <role:departed>}]}},
   "key": "gone", "label": "Marked departed"},
  {"field": {"id": "customer.last_dm_touch"}, "key": "dmT", "label": "Last decision-maker touch"},
  {"field": {"id": "customer.url"}, "key": "url", "label": "Staircase link"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "customer.<book_owner_field>"}, "operator": "In", "values": [<user_id>]}]},
 "sortBy": [{"columnKey": "renew", "direction": "Asc"}, {"columnKey": "id", "direction": "Asc"}]}
```
Add a column for the org's default or unknown role to show how much of the roster is untagged. For a renewal view, add `customer.renewal_date InRange [Next90Days]`.

| Column | The call-out it enables |
|---|---|
| Decision makers = 0 near a renewal | "Renews in weeks and nobody on record signs": ask the customer who does |
| Executive sponsors = 0 across a cohort | Usually a tagging gap, not a relationship gap: a role-cleanup action for the team |
| Champions = 0 with departed > 0 | The champion may have left and nobody replaced them |
| Last decision-maker touch | A tagged decision maker nobody has talked to |

**(b) Stale executives** (root `stakeholder`, one call for every seniority term):
```json
{"entity": "stakeholder",
 "columns": [
  {"field": {"id": "stakeholder.customer"}, "key": "aid", "label": "Account id"},
  {"field": {"id": "stakeholder.customer.name"}, "key": "acct", "label": "Account"},
  {"field": {"id": "stakeholder.customer.renewal_date"}, "key": "renew", "label": "Renewal"},
  {"field": {"id": "stakeholder.name"}, "key": "who", "label": "Stakeholder"},
  {"field": {"id": "stakeholder.title"}, "key": "title", "label": "Title"},
  {"field": {"id": "stakeholder.role.name"}, "key": "role", "label": "Role"},
  {"field": {"id": "stakeholder.last_engagement"}, "key": "eng", "label": "Last engagement"},
  {"field": {"id": "stakeholder.last_reach_out"}, "key": "reach", "label": "Last reach-out"},
  {"field": {"id": "stakeholder.event_stats.next_scheduled_event"}, "key": "next", "label": "Next meeting"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "stakeholder.customer.status"}, "operator": "In", "values": ["Active"]},
  {"field": {"id": "stakeholder.customer.<book_owner_field>"}, "operator": "In", "values": [<user_id>]},
  {"field": {"id": "stakeholder.role.name"}, "operator": "NotIn", "values": <role:departed>},
  {"field": {"id": "stakeholder.last_engagement"}, "operator": "InRange", "value": "[PastYear]"},
  {"field": {"id": "stakeholder.last_engagement"}, "operator": "NotInRange", "value": "[Past3Months]"},
  {"operator": "Or", "conditions": [
    {"field": {"id": "stakeholder.title"}, "operator": "Contains", "value": "Chief"},
    {"field": {"id": "stakeholder.title"}, "operator": "Contains", "value": "Vice President"},
    {"field": {"id": "stakeholder.title"}, "operator": "Contains", "value": "VP"},
    {"field": {"id": "stakeholder.title"}, "operator": "Contains", "value": "Head of"},
    {"field": {"id": "stakeholder.role.name"}, "operator": "In", "values": <role:decision_maker> + <role:executive_sponsor>}]}]},
 "sortBy": [{"columnKey": "renew", "direction": "Asc"}, {"columnKey": "aid", "direction": "Asc"}]}
```
The engaged-in-the-past-year window is what makes this list useful: sorting all executives by oldest reach-out surfaces contacts from years ago who have most likely left. Senior titles are an org-wide population in the tens of thousands, so always scope to a book, a team, or a renewal window.

| Column | The call-out it enables |
|---|---|
| Last engagement vs Last reach-out | Reach-out recent but engagement old: "we keep writing, they stopped answering" |
| Renewal with no Next meeting | A lapsed executive on a near-term renewal with nothing booked |
| Role empty or unknown on a senior title | A likely decision maker or sponsor who was never tagged |

The roster is reliable; per-person sentiment tone in this entity is not (it defaults to neutral), so get stance from `staircase_analyze_account`. **Renders as:** the coverage panel in Account 360 and Renewal Radar.

---

## `voc.pain_profile`: what a cohort is talking about

**Answers:** "what are at-risk accounts complaining about", "top themes this quarter", "rising issues".

`<cohort filter>` is a customer condition tree, for example the at-risk set:
`{"operator":"And","conditions":[{"field":{"id":"customer.status"},"operator":"In","values":["Active"]},{"field":{"id":"customer.risk.risk_level"},"operator":"GreaterOrEqual","value":4}]}`, a book (`customer.<book_owner_field> In [<user_id>]`), or a team (`customer.<book_owner_field>.manager In [<manager_user_id>]`).

**Call 1, pain and reach in the cohort:**
```json
{"entity": "parent_topic",
 "columns": [
  {"field": {"id": "parent_topic.id"}, "key": "id", "label": "Topic id"},
  {"field": {"id": "parent_topic.negative_sentiment", "arguments": {"dateRange": "[Past3Months]", "commType": [], "filter.customer": <cohort filter>}}, "key": "neg", "label": "Negative"},
  {"field": {"id": "parent_topic.accounts_count", "arguments": {"dateRange": "[Past3Months]", "commType": [], "filter.customer": <cohort filter>}}, "key": "accts", "label": "Accounts"}
 ],
 "sortBy": [{"columnKey": "neg", "direction": "Desc"}]}
```
**Call 2, volume and trend** (same shape, run in parallel): `parent_topic.total_count` and `parent_topic.absolute_growth_percentage` with the same arguments. Join the two on Topic id.

**Keep it to two cohort metrics per call.** Every `filter.customer` column recomputes the cohort; with a large cohort, three or more such columns time out (the error arrives as `invalid_config`, see anti-patterns.md R16). Unscoped topic metrics and small cohorts tolerate more.

| Column | The call-out it enables |
|---|---|
| Negative, sorted | What this cohort is unhappy about, ranked |
| Accounts | Breadth: one loud account vs a pattern across many |
| Growth (a fraction: 0.08 means up 8% on the previous period) | Rising vs fading themes. Weight growth by absolute volume so a small-base spike doesn't dominate |
| Mentions | The denominator for the negative share |

**Known gap (verified 2026-09-25):** topic reports return numeric topic ids with no name column, and semantic search returns topic names but not ids, so there's no join between them. Until names return, rank with the report and name the themes through `staircase_semantic_search` (topic channel, `parent_topics` filter with the standard parent names listed in that tool's description, `topic_sentiments: ["negative"]`). Say in the output that theme names come from the search layer.

---

## `churn.retro`: what we lost and why

**Answers:** "churn retrospective", "what did we lose last quarter and why".

```json
{"entity": "customer",
 "columns": [
  {"field": {"id": "customer.id"}, "key": "id", "label": "Account id"},
  {"field": {"id": "customer.name"}, "key": "name", "label": "Account"},
  {"field": {"id": "customer.<book_owner_field>.full_name"}, "key": "who", "label": "Book owner"},
  {"field": {"id": "customer.tier.name"}, "key": "tier", "label": "Tier"},
  {"field": {"id": "customer.revenue_converted", "arguments": {"aggregateParentChild": true}}, "key": "rev", "label": "Revenue"},
  {"field": {"id": "customer.churn.churn_date"}, "key": "cd", "label": "Churn date"},
  {"field": {"id": "customer.churn.issues"}, "key": "iss", "label": "Churn issues"}
 ],
 "filter": {"operator": "And", "conditions": [
  {"field": {"id": "customer.status"}, "operator": "In", "values": ["Churned"]},
  {"field": {"id": "customer.churn.churn_date"}, "operator": "InRange", "value": "[LastQuarter]"}]},
 "sortBy": [{"columnKey": "cd", "direction": "Desc"}, {"columnKey": "id", "direction": "Asc"}]}
```

**Coverage first.** Not every churned account has a churn analysis. Run two scalar COUNTs (all churned in the window, then the same filter plus `customer.churn.issues Defined`) and state the analyzed share, so reason percentages are read against it rather than the whole cohort. The accounts with `customer.churn.issues NotDefined` are the ones that need a manual read.

**Reasons.** `churn.issues` is a Collection of reason phrases: cluster them client-side into reason themes and attach lost revenue per theme. Add `customer.churn.synopsis` for the shortlist.

**Destinations.** For who replaced us, run `lifecycle.evidence` with types `["churn","churn_risk"]` on the churned accounts and read the competitor-replacement signals and the communications behind them.

**Book owner is context, never a ranking.** Never present churn by person as performance.
