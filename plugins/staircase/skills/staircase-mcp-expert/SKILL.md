---
name: staircase-mcp-expert
description: "Foundation skill for the Staircase AI MCP. Resolves the user's scope and the org's custom setup on first call, routes each ask to the right tool (structured reports for lists and rankings, the lifecycle-event evidence chain for why, per-account analysis for narrative), supplies context-complete report recipes for core questions, and encodes the analysis methodology. Every other Staircase skill reads this before composing a non-trivial Staircase query."
user_type: foundation
---

# Staircase MCP Expert

## What this skill is for
The Staircase MCP turns customer communications into account intelligence: health, sentiment, risk, expansion, lifecycle events with their signals, stakeholders, topics, and AI analyst output.

**The tool descriptions carry the config contract**: report shape, sorting and paging, date formats, argument types, error recovery. Read them; this skill does not repeat them. This skill carries what the tools can't know:
1. Who the user is in this org and which accounts are theirs (the first-call contract).
2. Which tool answers which kind of question (the router).
3. The report recipes that pull enough context for good call-outs (`references/report-recipes.md`).
4. The evidence chain from a signal to the customer's own words.
5. The methodology for ranking, rollups, and ratios.

This plugin reads and synthesizes. It never writes to a CRM.

## Step 0: the first-call contract (once per session, before the first real query)
1. **Connect.** Call `staircase_report_metadata`. If no Staircase tools exist or the call fails for auth, stop and tell the user to connect Staircase: a claude.ai connector, or `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`.
2. **Reuse the cache.** Read `~/.staircase-mcp/user-profile.md` if it exists. Reuse its scope unless the user asks to change it, or the cached field no longer appears in metadata.
3. **Resolve scope, don't ask for it.** Role fields are the `customer.*` fields whose `referencedEntity` is `user` (always `customer.owner`, often org-specific CSM, renewal-owner, or specialist fields). Run the `scope.membership` recipe: one report, rooted at `user`, filtered to `current_user_id`, with one child COUNT per role field.
   - One field with a real count: that is the book. No question.
   - Two or more: ask one question naming the fields and counts.
   - None: not a book carrier. If people report to them (`user.manager`) and those people hold books, use team scope; otherwise portfolio scope. A manager whose reports carry no accounts (a product or enablement leader, say) gets portfolio, never an empty team book.
   - Portfolio scope: ask once whether they're responsible for a slice (a product line, segment, or region). Save it as `scope.filter`, a condition every report adds, and `scope.revenue_field` when the slice has its own revenue field (for a product line, that product's revenue field of 1 or more). Scope to the person's responsibility by default; the whole org only when they have no slice or ask for it.
   - Never assume `customer.owner` is the CSM. Its role differs by org.
4. **Learn the org's vocabulary.** From the same metadata call, cache the `lifecycle_event.type` options (event types are partly org-specific, and labels differ from ids) and the role-field list. Stakeholder roles are configured per org too: the first time an ask needs Decision Maker, Executive Sponsor, Champion, or Departed, pull the role list (`stakeholder.coverage` in report-recipes.md), propose a mapping, confirm it once, and cache it.
5. **Write the profile** (`scope.method`, `scope.book_owner_field`, `scope.user_id`, `scope.filter` and `scope.revenue_field` when set, `org.role_fields`, `org.lifecycle_types`, `org.role_map` once mapped) so the next skill skips steps 3 and 4.

If `staircase_get_playbook` is available, read its `portfolio_resolution` topic first and prefer it where it differs.

## Route every ask
| The ask | The path |
|---|---|
| A list, filter, ranking, count, or total (accounts, contacts, opportunities, topics, events) | `staircase_run_report` using a recipe from `references/report-recipes.md`. `staircase_generate_report` only when the ask can't be mapped to fields |
| Why a signal fired, what they said, what we promised | The evidence chain: `staircase_run_report` over `lifecycle_event`, then `staircase_list_communications(event_ids)`, then `staircase_fetch_evidence(ids)` for quotes |
| A theme across accounts (a topic, competitor, product, error) | `staircase_semantic_search`: topics for concepts, single-word text terms for proper nouns, scoped to accounts or a date bound |
| The story on one account (stance, the play) | `staircase_account_lookup`, then `staircase_analyze_account`, grounded in fetched evidence |
| One account's stored facts | `staircase_account_info` |
| An open question with no report shape | `staircase_query` (never to build a list) |

Decompose compound asks into these primitives and assemble the answer yourself. One tool, one job.

## The tool surface
| Tool | Use it for | Not for |
|---|---|---|
| `staircase_report_metadata` | This org's schema: entities, fields, types, picklist options, `referencedEntity`, `current_user_id` | Anything else. Call once, cache |
| `staircase_run_report` | Deterministic structured reports: the default for anything list-shaped | Interpreting communications |
| `staircase_generate_report` | Natural-language reports when a config can't be built | The first choice |
| `staircase_list_communications` | Lifecycle events to their communications: summaries, meeting `issues[]` and `action_items[]`, participants typed User or Stakeholder (up to 20 event ids per call) | Quoting (summaries aren't quotable) |
| `staircase_fetch_evidence` | Verbatim content for up to 20 evidence ids; transcripts are opt-in, prefer a `transcript_query` | Discovery |
| `staircase_semantic_search` | Ranked evidence for a theme or term | Counting or ranking accounts |
| `staircase_account_lookup` | Account name to id | Finding accounts by topic |
| `staircase_account_info` | One account's stored fields | Cross-account questions |
| `staircase_analyze_account` | Narrative reasoning over one account's communications | Lists, exact counts |
| `staircase_query` | Open-ended questions with evidence | Lists, rankings |
| `staircase_get_playbook` (when present) | Server-authored recipes for listed topics; check first when the ask matches | |

## The five patterns you'll use most
1. **Context-complete reports, not thin lists.** Pick the recipe for the question; it names the columns that make the call-outs possible. Always select the name alongside any id, and label every column.
2. **Signal, then evidence, then quote.** Signals decide which evidence to read; they never establish intent on their own. Use hard-stop signals to prioritize, then read the communications before calling an account "leaving" (`lifecycle.evidence`). An "auto-renewal opt-out" can be a procurement request for standard contract language, not an exit.
3. **Long list, rank, drill.** Reports return the whole cohort; rank it yourself with the composite in `references/query-patterns.md` (the report does not compute abstract priority). Drill the top accounts with `staircase_analyze_account`, about 10 at a time.
4. **Rollups in one call.** Make the group the root (`tier`, `user`) and add child aggregations, including conditional COUNT or SUM and a discovered role field as the `referenceField` (`team.rollup`).
5. **Merge Risk and Expansion yourself.** The analysts run independently; reconcile them for save-into-expansion accounts (`references/query-patterns.md`).

## Rules that bite (full list in `references/anti-patterns.md`)
- **Empty is not always "none."** An org may not enable an insight or event type. Probe with a COUNT before building a lens on it, and say so when a lens is empty.
- **Analyst scores are sparse by design.** `risk_level` and `readiness_level` exist only where that analyst fired; the presence is the signal.
- **Collections are columns, not filters.** Signals, direct quotes, products, channels, and churn issues come back per row; filter on something else and cluster them yourself.
- **References return ids.** Add the name column. Topic reports currently return topic ids with no names; name themes through `staircase_semantic_search`.
- **Retry only when `retryable` is true.** Otherwise fix the config using the error message.
- **Never hardcode an org's custom field.** Discover it from metadata; prefer the standard field when one exists.

## Staircase vs the CRM
Staircase derives health, sentiment, risk, expansion, engagement, and stakeholder context from communications. `revenue` and `renewal_date` are queryable and usable when populated, but the CRM is authoritative for the contracted figure and date. Seats, product usage, and segment fields live in the CRM. Say so when an answer depends on a CRM-authoritative value.

## Reference library
| File | Read it when |
|---|---|
| `references/report-recipes.md` | Before composing any report: the canonical context pull per question type |
| `references/field-catalog.md` | You need a field id, or want to know what a field is good for |
| `references/advanced-report-patterns.md` | A task needs time windows, cohort scoping, insight cohorts, lifecycle events, topics, rollups, or stakeholders |
| `references/query-patterns.md` | Translating business language into a plan; the priority composite; the Risk x Expansion merge |
| `references/anti-patterns.md` | Something failed or looks wrong; before an unfamiliar operation |
| `references/analyst-data-models.md` | Before `staircase_analyze_account`: the analyst templates |
| `references/analysis-methodology.md` | Before any cross-person or cross-account rollup, ranking, or efficiency ratio |

## Cross-references
- **Rendering:** `../staircase-app-design/` for every user-facing output.
- **Output discipline:** `../../_shared/staircase-output-best-practices.md`.
- **Profile:** `~/.staircase-mcp/user-profile.md` (written by step 0 above; `staircase-setup` runs the same contract with a welcome and a practice round).
