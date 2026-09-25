# Staircase MCP: Field Catalog

The standard fields worth knowing, by the value they deliver. `staircase_report_metadata` is authoritative for any given org: it lists every field, its type, whether it is filterable, its supported arguments, picklist options, and for references, the entity it points to. Use this catalog to know what to reach for; use metadata to confirm it exists. Refreshed against a live org 2026-09-25.

## Contents
1. The 11 report entities
2. Identity, scope, and role fields
3. Commercial
4. Scores
5. AI analyst fields
6. Relationship and stakeholder counts
7. Engagement, recency, meetings, tickets
8. Effort and cost
9. Insight proxies (quick filters)
10. The other entities, field by field
11. Custom fields (discover, never ship)
12. What Staircase does not own

## 1. The 11 report entities
| Entity | One row per | Best for |
|---|---|---|
| `customer` | Account | Almost everything: lists, rankings, cohorts, rollup children |
| `lifecycle_event` | Detected event (churn risk, commercial discussion, renewal, personnel change, ...) | Dated signals and the evidence chain |
| `expansion_opportunity` | Individual expansion opportunity | Pipeline by confidence, momentum, category |
| `stakeholder` | Customer contact | Rosters, exec coverage, cadence |
| `user` | Your team member | Rosters, workload, book rollups, the org chart |
| `parent_topic` | Canonical theme | Cohort-scoped VoC ranking and trend |
| `meeting` | Meeting | Meeting summaries, recordings, scheduled meetings |
| `feedback` | Human correction of an AI answer | Quality signals on the AI layer |
| `tier`, `journey`, `stakeholder_role` | Reference value | Group-by roots for breakdowns |

## 2. Identity, scope, and role fields
| Field | Notes |
|---|---|
| `customer.id` | Reference: renders the raw account id. Label it explicitly and pair it with `customer.name` |
| `customer.name` | String, filterable, selectable. Use `Contains` for a named account |
| `customer.status` | Picklist (`Active`, `Prospect`, `Churned`). Default account lists to `Active` |
| `customer.owner` | Reference to `user`. Always present, but its role is org-specific: it is not necessarily the CSM (R7b) |
| Other role fields | Any `customer.*` field whose `referencedEntity` is `user` (CSM, renewal owner, specialist roles). Discover them from metadata; resolve which one is the book with `scope.membership` |
| `customer.parent` | Reference to the parent account; pair with `aggregateParentChild` |
| `customer.url` | Link to the account's page in Staircase: useful for "open in Staircase" actions in rendered output |
| `customer.crm_id`, `customer.sfdc_id` | Join keys to the CRM |

Filter a role field by user id (`In [<user_id>]`) or through its leaf (`customer.<book_owner_field>.full_name In ["<name>"]`), never by a bare name.

## 3. Commercial
| Field | Notes |
|---|---|
| `customer.revenue`, `customer.revenue_converted` | Number, filterable, aggregatable. `revenue_converted` is in the corporate currency; pass `aggregateParentChild` to roll children in. Usable when populated; the CRM is authoritative for the contracted figure |
| `customer.renewal_date`, `customer.contract_start_date` | Date, filterable. A past renewal date on an Active account is a data-hygiene call-out |
| `customer.tier` | Reference; select `customer.tier.name` for the label |
| `customer.journey` | Reference; select `customer.journey.name`. Often unpopulated (R11) |
| `customer.currency` | The account's native currency |

## 4. Scores
Each score has a numeric field and a label field. Yellow or "Average" is neutral, never a concern.
| Concept | Numeric | Label |
|---|---|---|
| Health | `customer.buckets.health_score` | `customer.buckets.health` |
| Engagement | `customer.buckets.engagement.numeric_score` | `customer.buckets.engagement.score` |
| Sentiment | `customer.buckets.sentiment.numeric_score` | `customer.buckets.sentiment.score` |
| Open items | `customer.buckets.open_items.numeric_score` | `customer.buckets.open_items.score` |
| Response time | `customer.buckets.response_time.numeric_score` | `customer.buckets.response_time.score` |

Sentiment volume: `customer.customer_sentiment.{positive,neutral,negative}`, and per channel under `customer.email.customer_sentiment.*` and `customer.message.customer_sentiment.*`. An org can add its own scores (they appear as `customer.buckets.<custom>.score`); discover them.

## 5. AI analyst fields
| Field | Type | Notes |
|---|---|---|
| `customer.risk.risk_level` | Number 1-5 | Present only when a churn risk fired (R2). 4-5 is the acute set |
| `customer.risk.analysis` | String | The risk narrative; verbose |
| `customer.churn.churn_date` | Date | Verified churn |
| `customer.churn.issues` | Collection | Churn reason phrases; presence-filterable (`Defined`), contents clustered client-side |
| `customer.churn.synopsis` | String | Retrospective narrative; verbose |
| `customer.expansion.readiness_level` | Number 1-5 | Present when expansion signals were detected |
| `customer.expansion.momentum_indicator` | Picklist | Heating, Steady, Cooling |
| `customer.expansion.readiness_drivers`, `.product_spread`, `.critical_timing`, `.executive_engagement`, `.recent_changes` | String | The why-now, the whitespace, when to strike, exec air cover, what moved |
| `customer.expansion.total_arr_potential` | String | A qualitative tier word, not a number; not filterable |
| `customer.expansion.summary` | String | Verbose narrative |
| `customer.expansion.customer_opportunities` | Collection | Opportunity titles; for detail use the `expansion_opportunity` entity |
| `customer.handoff.strategic_summary`, `.primary_objectives` | String, Collection | Present when the handoff analyst fired |
| `customer.renewal.synopsis` | String | Post-renewal retrospective |
| `customer.summary` | String | Always-available narrative; its first paragraph is a cheap preview |

Portfolio scores are 1-5; per-account `staircase_analyze_account` scores are 0-10. Never map between them.

## 6. Relationship and stakeholder counts
| Field | Notes |
|---|---|
| `customer.relationship_score.multi_threaded` | Boolean, **column only (not filterable)**. To filter single-threaded accounts, use the `CustomerSingleThreaded` insight (EXISTS) or pull the column and filter client-side |
| `customer.relationship_score.stakeholders_count` | Number, filterable. Named contacts on file |
| `customer.relationship_score.users_count` | Number, filterable |

`multi_threaded` reflects whether recent communication is spread across contacts; `stakeholders_count` is how many contacts are on file. An account can have several stakeholders and still be single-threaded if only one of them replies. Read `multi_threaded` alongside last-reach-out and last-email-from-them.

## 7. Engagement, recency, meetings, tickets
| Field | Notes |
|---|---|
| `customer.last_engagement`, `customer.last_reach_out`, `customer.last_touch`, `customer.last_dm_touch` | DateTime, filterable |
| `customer.next_qbr_date` | Date; empty means no business review booked |
| `customer.last_lifecycle_event_date`, `customer.insight_detected` | Quick recency and flag checks |
| `customer.email.organization_last_sent` / `.customer_last_sent` | Last email from your side / from theirs. The gap is the "have they gone quiet" signal |
| `customer.email.owner_sent_count`, `.organization_sent_count`, `.customer_sent_count` | Windowed counts: the owner field alone, your whole company, the customer. Labels in metadata include your company's name |
| `customer.email.organization_response_time_hours`, `.customer_response_time_hours`, `.organization_open_threads`, `.customer_open_threads` | Response debt on both sides |
| `customer.message.*` | The same split for chat |
| `customer.event.count`, `.total_hours`, `.owner_count`, `.last_event`, `.last_dm_event`, `.next_event` | Meetings; `next_event` empty means nothing scheduled |
| `customer.ticket.submitted_count`, `.comments_count`, `.last_opened`, `.organization_response_time_hours`, `.customer_response_time_hours` | Ticket volume and responsiveness at the account level |

## 8. Effort and cost
All Number, columns and aggregations only (not filterable), windowed by `dateRange`.
| Field | Notes |
|---|---|
| `customer.effort.team_effort_hours` | Your team's hours on the account in the window |
| `customer.effort.owner_effort_hours` | The owner field's hours |
| `customer.effort.team_effort_cost` | Cost of that effort |
| `customer.effort.team_effort_time_range_revenue` | Revenue for the same window: the correct denominator for efficiency ratios (analysis-methodology.md) |
| `customer.effort.team_effort_efficiency` | A server-computed efficiency rate; confirm its definition in your org before presenting it as a ratio |

## 9. Insight proxies (quick filters)
The `insight` EXISTS form (advanced-report-patterns.md section 2) is the precise way. These field filters are quick proxies:
| Insight | Proxy filter |
|---|---|
| No QBR | `customer.next_qbr_date NotDefined` (or in the past) |
| Account dark / no reach-out | `customer.last_engagement` or `customer.last_reach_out` older than N days |
| No next meeting | `customer.event.next_event NotDefined` |
| Upcoming renewal | `customer.renewal_date InRange "[Next90Days]"` |
| Fired churn risk | `customer.risk.risk_level Defined` (4-5 for acute) |
| Single-threaded | Use the `CustomerSingleThreaded` insight (the `multi_threaded` field is not filterable) |

## 10. The other entities, field by field
- **`lifecycle_event`**: `id`, `type` (picklist, org-specific options), `date` (filterable, MIN/MAX), `customer` (join), and Collections `signals`, `direct_quotes`, `products`, `comm_types` (not filterable).
- **`expansion_opportunity`**: `customer`, `offering`, `category` (picklist), `momentum_state` (picklist), `confidence_level` (picklist: High, Medium, Low), `opportunity_value` (prose, never sum), `decision_maker`, `timeline_indicator`, `budget_status`, `technical_status`, `user_count`, `competitive_mention`, `summary_line`, `detail_paragraph`, `analyzed_at`. Several rows per account are common.
- **`user`**: `full_name`, `title`, `department`, `email`, `manager` (reference to user), `has_access`, `is_auto`, `excluded_from_analysis`, `owned_accounts.count` and `.total_revenue` (by the owner field), windowed stats `email_stats.*`, `event_stats.*`, `message_stats.*`, `ticket_stats.*` (each takes `dateRange` and `filter.customer`), and `effort.effort_hours` (column only). Filter real people with `has_access = true` and `is_auto = false`.
- **`stakeholder`**: `customer`, `name`, `title`, `email`, `role` (select `role.name`), `type`, `touch_frequency`, `last_engagement`, `last_reach_out`, per-person `email_stats.*`, `event_stats.*` (including `call_attendance_ratio` and `next_scheduled_event`), `message_stats.*`, `ticket_stats.submitted_count`, and `sentiment.*` (tone is unreliable, R3). Orgs can add their own stakeholder fields.
- **`parent_topic`**: `id` (numeric; there is currently no name field), and cohort-scoped metrics `total_count`, `accounts_count`, per-channel counts, `positive_sentiment`, `neutral_sentiment`, `negative_sentiment`, `sentiment_score`, and trend fields.
- **`meeting`**: `customer`, `summary` and `meeting_summary` (filterable text), `start_time` (column only), `duration_hours`, `meeting_provider`, `call_media`, `has_recording`, `is_scheduled`.
- **`feedback`**: `created_at`, `user`, `comment`, `old_value`, `new_value`, `display_type`, `comm_type`. A ready-made quality signal for AI answers.
- **`tier`, `journey`, `stakeholder_role`**: `id` and `name`; use as roots for breakdowns.

## 11. Custom fields (discover, never ship)
Every org adds its own fields (ids ending `_c`, sometimes `__c`): per-product revenue, extra role fields, segments, stages, priority flags. They exist only in that org. In a skill:
- Discover them from metadata at runtime; cache what matters in the profile.
- Refer to them with placeholders (`<book_owner_field>`, `<custom_field>_c`), never by a concrete id.
- Prefer the standard field whenever one exists (`customer.revenue` over a per-product revenue field).

## 12. What Staircase does not own
Seat or license counts, product usage and adoption, industry and segment classification (unless the org syncs them as custom fields), and ticket status of record. Staircase reasons over persistent signals, not "what changed in the last day." Revenue and renewal dates are present and usable, but the CRM is authoritative for the contracted figure; say so when an artifact depends on it.
