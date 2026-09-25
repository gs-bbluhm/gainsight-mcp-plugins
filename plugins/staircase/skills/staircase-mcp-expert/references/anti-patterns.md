# Staircase MCP: Reliability Rules and Rough Edges

The single source for the rules that keep answers correct. Read it when something fails, looks wrong, or comes back empty, and before an operation you haven't run before. Verified live 2026-09-25.

## Contents
- Reliability rules (R2-R17)
- The parallel analysis cap
- Anti-patterns by path
- Determinism and retries
- Two scales that must not be mapped
- Old patterns (resolved; kept so nobody relearns them)

## Reliability rules
| # | Rule | What to do |
|---|---|---|
| R2 | **Analyst scores are sparse by design.** `risk.risk_level` and `expansion.readiness_level` exist only where that analyst fired. | For "the at-risk set", filter to populated or high values. Never sort a mostly-null column and read the top. |
| R3 | **Stakeholder roster yes, stance no.** The `stakeholder` entity reliably returns names, titles, roles, recency, and touch cadence per account. Its sentiment tone defaults to neutral. | Use it for org charts and coverage. Get champion or detractor stance from `staircase_analyze_account`. |
| R4 | **`staircase_analyze_account` re-derives analyst content non-deterministically.** The same prompt can return different counts of reasons and stakeholders. | Treat it as narrative, not data. Ground every claim in evidence ids. For exact values use report fields; for expansion detail use the `expansion_opportunity` entity. |
| R5 | **Unscoped raw-text search times out.** | Themes go to the topic channel; text terms need `account_ids` or a date bound. Write each text term as a single word (terms match conjunctively). |
| R6 | **Multi-value filters: prefer `In`.** `Or` works in report filters, including `Or` of `Equal` on one field. `In` with a `values` array is still the cleanest form, and it works on String fields even though `filter_operators.byFieldType` doesn't list it there. | Use `In` for "any of these N values." Treat the operator map as advisory, not exhaustive; the backend is the validation authority. |
| R7 | **"My accounts" never scopes itself.** | Pass the resolved scope explicitly: `customer.<book_owner_field> In [<user_id>]`, from the first-call contract in SKILL.md. |
| R7b | **`customer.owner` is not always the CSM.** Its role is org-specific. In one production org the owner field held account managers and shared no accounts at all with the real CSM field. | Resolve the book field with `scope.membership` (report-recipes.md). Never default to `owner`; never pick a field by population statistics alone when a person appears in two. |
| R8 | **Retry only when the result says `retryable: true`.** Every result carries `outcome` (`success`, `no_data`, `error`), `code`, and `retryable`. | Retryable: retry once with the identical call. Not retryable: read `message`, fix the config, and try again. For narrative tools, a second attempt with alternate phrasing is fine; trust a clear "no evidence" answer. |
| R9 | **Collections are columns; their contents are never filters.** `lifecycle_event.signals`, `.direct_quotes`, `.products`, and `.comm_types` can't be filtered at all. A few Collections accept a presence test only: `customer.churn.issues Defined` works, but `Contains "<text>"` is rejected as unparsable. | Filter on something else (event type, date, account, or presence), then cluster the Collection values yourself. Pull verbose Collections (direct quotes) for a shortlist only. |
| R10 | **Reference columns return raw integer ids.** This includes `customer.id`, `<entity>.customer`, and topic ids. | Select the name alongside (`customer.name`, `<entity>.customer.name`, `customer.tier.name`, `user.manager.full_name`), and label the id column explicitly. Topic reports currently have no name column: name themes through `staircase_semantic_search` and say so. |
| R11 | **Empty is not always "none."** Not every org enables every insight or lifecycle event type, and reference fields (tier, journey, a role field) can be unpopulated. | Before building a lens on a rarer type or field, probe with a COUNT. When a lens is empty, say whether the type is unused in this org or genuinely clear. |
| R12 | **Lifecycle event types are org-specific.** Some are standard, some are the org's own, and display labels differ from option ids (for example `renewal_discussion` often displays as "Commercial discussion"). The `type` column currently renders a raw token such as `EventTypeId(raw=churn_risk)`. | Read the `lifecycle_event.type` options from metadata, filter by option id, and show the label. Never hardcode a list of event types. |
| R13 | **Paging needs a total order.** Sorting by `lifecycle_event.id` is silently ignored today, so lifecycle events have no reliable tiebreaker. | When paging, make the entity id the last `sortBy` entry (works on `customer.id`), or rows silently drop or repeat across pages. For lifecycle events, narrow the date window until one page holds the result, and dedupe by event id. For whole-population questions, use a COUNT or SUM instead of paging. |
| R14 | **Report size is not the limit; text width is.** Reports return full cohorts and page freely. Wide reports with long text columns hit `row_cap` sooner. | Keep verbose columns off cohort pulls; add them for the shortlist in a second call. |
| R15 | **`Contains` matches substrings, in any case.** A short token matches inside other words: "EBR" matches "Debrief" and company names that contain those letters. | Use whole words or multi-letter phrases ("Business Review", "Vice President"). Treat a short-token match as a candidate and check the value before counting it. |
| R16 | **A timeout can arrive as `invalid_config`.** A report that takes too long returns `code: invalid_config` with `retryable: false` and a message that it "takes too long to build". Cohort-filtered topic metrics hit this first. | Read the message, not just the code. Retry with fewer columns or a smaller cohort: at most two `filter.customer` metric columns per call, joined client-side on the entity id. |
| R17 | **Check the base rate before flagging an absence.** A field can be accurate and still almost always empty (in one org, only a handful of active accounts had a future business review booked). | Before flagging "no QBR" or "no decision-maker touch" row by row, COUNT how many accounts have the field `Defined`. If it's near zero, report one systemic gap instead of the same flag on every row. |

## The parallel analysis cap
Per-account analysis fans out in parallel with a cap of **10 accounts** today. The cap is on that fan-out, not on report size: a report returns the whole cohort. The workflow is long list, rank, then analyze the top accounts in batches of up to 10.

## Anti-patterns by path
| Anti-pattern | Instead |
|---|---|
| Building a list of accounts with `staircase_query` or `staircase_semantic_search` | A structured report. Retrieval tools return evidence, not complete lists |
| Asking a report to "rank by urgency" | Pull the raw fields and score them yourself (query-patterns.md) |
| Re-deriving in search a value the report schema exposes | Use the field. Search is for evidence the schema can't represent |
| Stacking `account_ids`, `parent_topics`, and `topic_sentiments` on one scoped search | Lead with text terms plus topic terms in one call; add filters one at a time only if the result is too broad |
| Filtering a Reference role field by a bare name | Filter by id (`In [<user_id>]`) or through the leaf (`.full_name In ["<name>"]`) |
| Treating `summary` from `staircase_list_communications` as a quote | Fetch the evidence id for verbatim text |
| Time-window deltas ("what changed in the last 24 hours") | Staircase reasons over persistent signals; compare two windows of the same metric instead. Score history (health or engagement over time) isn't in the report layer yet, so say a trajectory can't be shown rather than inferring one |
| Treating `meeting.is_scheduled` as "upcoming" | It is true for past calendar meetings too. Sort by `meeting.start_time` (column only, not filterable), or use `customer.next_qbr_date` and `customer.event.next_event` for what's booked |
| Hardcoding a custom field id, a tier name, or an event type | Discover it from metadata; cache it in the profile |

## Determinism and retries
- Structured reports are deterministic. If one returns fewer rows than expected, check the filter before assuming the data changed.
- A cohort pulled again weeks later can legitimately return a different count because the underlying population changed. That is drift, not flakiness; compare the membership, not just the count.
- Narrative tools (`staircase_analyze_account`, `staircase_query`) vary run to run. Use them for reasoning and evidence, never for exact counts.

## Two scales that must not be mapped
Portfolio `risk_level` and `readiness_level` are 1-5 categorical stages. Per-account `staircase_analyze_account` returns 0-10 maturity-style scores. They measure different things; never convert one into the other.

## Old patterns (resolved; kept so nobody relearns them)
- **Silent full-table results from a mis-keyed filter.** Unknown config keys and field paths now return an explicit error naming the bad path (verified 2026-09-25). Still sanity-check that a filtered report narrowed.
- **Same-field `Or` returning zero rows.** No longer reproduces as of 2026-09-25 on String and Picklist fields; `In` remains the preferred form.
- **"OR is unsupported."** That limit belonged to the prose question path, never to reports.
- **Lifecycle events only through an EXISTS filter.** `lifecycle_event` is a root entity now; the insight entity is still reached through EXISTS.
- **"The stakeholder entity can't filter by account."** It can (fixed 2026-08).
- **Mandatory field arguments.** Arguments are supported, with defaults; supply them when the question needs a specific window or scope.
- **`staircase_generate_report` as the default.** `staircase_run_report` is the default; generate is the fallback.
