# Staircase MCP: Advanced Report Patterns

The report layer is a full analytics engine: windowed metrics, cohort scoping, related-record filters, per-group rollups. This file holds the reusable techniques. The canonical report for each question type lives in `report-recipes.md`; start there and come here when you need to adapt one. Verified live against a production org (2026-08-31, refreshed 2026-09-25).

## Contents
1. The argument system (windows, cohorts, channels)
2. Insight cohorts (the EXISTS form)
3. Lifecycle events and their signals
4. Windowed and computed-metric cohorts
5. Cohort-scoped topics
6. The voice-of-customer drill
7. Rollups and breakdowns (no groupBy)
8. The stakeholder entity
9. Hierarchies: teams and parent accounts
10. Technique-specific rough edges

## 1. The argument system
Many fields accept arguments (listed per field as `supportedArguments` in metadata). This is what makes a metric windowed, scoped, and channel-aware.
- **`dateRange`**: a rolling (`[PastMonth]`, `[Past3Months]`), calendar (`[ThisQuarter]`, `[LastQuarter]`), or fixed range. Set it once in the report's top-level `arguments` and metric columns inherit it. The same metric at `[PastMonth]` and `[Past3Months]` gives you velocity.
- **`filter.customer` / `filter.user`**: a full condition object that scopes a metric to a population. This is how a topic, email, or effort metric is computed for "my at-risk accounts" instead of the whole org. Pass `{"operator":"And","conditions":[]}` for "everyone".
- **`commType`**: channels, `[]` for all. **`productId`**: product scope on multi-product accounts, `[]` for all. **`aggregateParentChild`**: roll child accounts into the parent.

## 2. Insight cohorts (the EXISTS form)
Insights are current-state flags on an account, reached through a related-record filter (the insight entity is not a report root):
```json
{"field": {"rootEntityPath": "customer", "childEntity": "insight", "referenceField": "insight.customer", "aggregation": "EXISTS",
           "condition": {"operator": "And", "conditions": [{"field": {"id": "insight.type"}, "operator": "Equal", "value": "ChurnRisk"}]}},
 "operator": "Equal", "value": true}
```
The insight types: `ChurnRisk`, `ChurnDetected`, `CustomerDark`, `CustomerNoReachOut`, `CustomerUnresponsive`, `CustomerSingleThreaded`, `NoQBR`, `NoRenewalDiscussion`, `NoMeeting`, `NoNextMeeting`, `PositiveSentimentTrend`, `NegativeSentimentTrend`, `Farewell` (a contact leaving), `OrganizationPersonnelChange`, `TitleChange`, `ExecutivesNoTouch`, `DmNoTouch`, `DmNotDefined`, `DmNotEngaged`.

**Combine with `Or` for meaningful cohorts:**
- Coverage gaps: `NoQBR` or `CustomerSingleThreaded` or `ExecutivesNoTouch`.
- Champion risk: `Farewell` or `OrganizationPersonnelChange` or `TitleChange`.
- Disengagement: `CustomerDark` or `CustomerNoReachOut` or `CustomerUnresponsive`.

`insight EXISTS ChurnRisk` is not the same as `risk.risk_level` populated. The insight is the flag; the level is the analyst's score. Use the insight for "flag on" and the level for "how bad." Not every org enables every type (R11).

## 3. Lifecycle events and their signals
`lifecycle_event` is a root entity: one row per detected event, with `type` (a filterable picklist), `date`, `customer` (join through it: `lifecycle_event.customer.name`, `.customer.tier.name`, `.customer.<book_owner_field>`), and four Collection columns: `signals`, `direct_quotes`, `products`, `comm_types`.

- **The type vocabulary is org-specific.** Read the `lifecycle_event.type` options from metadata; some are standard, some are the org's own, and labels differ from ids (R12).
- **Signals are the sharpest early-warning primitive Staircase has.** Each event carries a set of granular signals (exit intent, a named competitor replacement, auto-renewal opt-out, budget pressure, a renewal-blocking constraint, and so on). They are a Collection, so filter by type and date, then triage client-side. Weight hard-stop signals (concrete exit actions, migration in progress, auto-renewal opt-out, contract ultimatums, competitor replacement) above expressed frustration or exit intent alone when deciding **what to read first**, but never label intent from signals alone. Signals record what was discussed, not why: in live testing, an event tagged "explicit exit intent, auto-renewal opt-out" turned out to be a customer asking for no-auto-renew contract language during an otherwise healthy, expanding renewal, with the real issue a price discrepancy on the order form. Read the timeline (every event type, not just churn risk) and the communications before concluding.
- **Roll events onto accounts** with a child aggregation from `customer`: COUNT of `churn_risk` events in a window, or MAX of `lifecycle_event.date` for the most recent `renewal_discussion` (the "when did we last talk terms" column). Both verified; see `book.context` and `renewal.window`.
- **Go from an event to the evidence** with `staircase_list_communications(event_ids)`, then `staircase_fetch_evidence(ids)` for verbatim text. The full chain is the `lifecycle.evidence` recipe.

## 4. Windowed and computed-metric cohorts
Metric columns are windowed and filterable, so a computed metric can define a cohort.
- **Neglected at-risk:** `insight EXISTS ChurnRisk` AND `customer.email.owner_sent_count` (with `dateRange: [PastMonth]` on the filter leaf's field) `LessOrEqual 2`. At-risk accounts the owner has gone quiet on.
- **Owner vs organization sends.** `customer.email.owner_sent_count` counts the `customer.owner` field's emails; `customer.email.organization_sent_count` counts everyone at your company. Low owner with high org means the owner is absent while others carry the account. Both low on an at-risk account means nobody is talking to them.
- **Velocity:** request the same metric at two windows and compare.

## 5. Cohort-scoped topics
Every `parent_topic` metric takes `dateRange`, `commType`, and `filter.customer`, so you can compute a topic profile (volume, negative volume, accounts, trend) for any cohort over any window: the best single "what's on this cohort's mind" query (`voc.pain_profile`).
- **Topic names are currently unavailable in reports.** `parent_topic.id` returns a numeric id and there is no name column. Rank with the report, then name themes through `staircase_semantic_search` (the topic channel returns parent and child topic names), and say where the names came from.
- Trend fields (`current_period_volume`, `previous_period_volume`, `absolute_growth_percentage`) are org-flag-gated; degrade gracefully. Weight growth by absolute volume so a small-base spike doesn't dominate. `trend_data_over_time` does not serialize to CSV.
- Use topics to rank and count themes, never to build account lists or to decide whether an issue is resolved.

## 6. The voice-of-customer drill
1. **Quantify:** the cohort-scoped `parent_topic` report (section 5).
2. **See the children:** `staircase_semantic_search` on the topic channel, which can run unscoped. Read `parent_topic` and `child_topic` from the results. Ignore child topics with a single item; the long tail of one-offs is noise.
3. **Get the quotes:** for an account-scoped cohort, single-word text terms plus `account_ids` and `per_account_limit`; for an org-wide theme, the topic channel with `topic_sentiments: ["negative"]`. When scoping to accounts, put text and topic terms in the same call and keep other filters minimal.
4. **Read in full:** pass `evidence_id`s to `staircase_fetch_evidence(ids=[...])`, up to 20 at a time.

Search also accepts a `filter` (a report condition tree that narrows the account population) and a `direction` filter (inbound or outbound, text terms only).

## 7. Rollups and breakdowns (no groupBy)
- **Breakdown:** make the group the root entity and add child-aggregation columns, each with `rootEntityPath`, `childEntity`, `referenceField`, and `aggregation` (COUNT, SUM, AVG, MIN, MAX). Give every column a distinct label.
- **Conditional aggregation:** each child-aggregation column can carry its own `condition`, so several differently filtered SUMs sit side by side in one report (a mini pivot: total revenue, at-risk revenue, churn-flagged revenue per tier). An EXISTS leaf on insight or lifecycle event can nest inside that condition.
- **Discovered role fields work as the `referenceField`.** Root `user`, child `customer`, reference `customer.<book_owner_field>` rolls up each person's book, and with a condition, their at-risk count and revenue, in one call (`team.rollup`, `scope.membership`).
- **One number:** a scalar `{"aggregation": "COUNT"}` (or SUM over a main-entity field) returns a single row. Prefer it to listing for whole-population questions.

## 8. The stakeholder entity
`stakeholder.customer In [<account_ids>]` returns an account's roster. Reliable: `name`, `title`, `role.name`, `last_engagement`, `last_reach_out`, `touch_frequency`, and per-person stats such as `email_stats.last_received`, `event_stats.last_attended_event`, `event_stats.call_attendance_ratio`. Unreliable: `sentiment.tone` (defaults neutral).
- **Exec coverage:** `title Contains "Chief"` (and VP, Director) across a cohort, sorted by `last_reach_out` ascending (`stakeholder.coverage`).
- **Cadence breaks:** sort by `last_reach_out` and compare against `touch_frequency`.

## 9. Hierarchies: teams and parent accounts
- **Teams:** `user.manager` is a filterable reference to another user, so "my team" is `user.manager In [<manager_user_id>]`, and `user.manager.full_name` shows the org chart in any user report.
- **Parent accounts:** `customer.parent` references the parent account. Use `aggregateParentChild: true` on revenue to roll children up, and group by parent when a customer has many child accounts.

## 10. Technique-specific rough edges
(General reliability rules live in `anti-patterns.md`.)
- `child_topic` is not a report entity; the search layer is the only window into it.
- Per-account topic drill (`customer.topic_communication.*`) needs a numeric `topicId`, and there is no resolver for topic names.
- There is no deterministic structured pull for a single analyst's full output; `staircase_analyze_account` re-derives it (R4). For expansion, the `expansion_opportunity` entity is the deterministic path.
- One account can have several `expansion_opportunity` rows; never assume one row per account when joining.
- Ticket count and comments are available at the account level (`customer.ticket.*`); ticket status of record lives in the ticketing system.
