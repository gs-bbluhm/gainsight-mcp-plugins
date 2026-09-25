# Staircase MCP: Query Patterns

How to turn a business ask into a query plan, and how to rank and reconcile what comes back. The canonical report for each question type is in `report-recipes.md`; this file is the translation layer and the scoring methodology.

## Contents
- Step 1: identify the scope
- Step 2: map the business term to a field or signal
- Step 3: compose the plan (report first)
- The production cross-account workflow
- The priority composite
- The Risk x Expansion merge

## Step 1: identify the scope
| The user says | Scope |
|---|---|
| "my accounts", "my book" | The resolved book: `customer.<book_owner_field> In [<user_id>]`, from the first-call contract (SKILL.md step 0). Never assume the owner field |
| "my team" | `user.manager In [<user_id>]` for the roster, then each person's book through the same role field |
| "high-touch", "enterprise", a tier | `customer.tier.name` (discover the org's tier names from data, don't assume them) |
| "this quarter", "next 90 days" | A renewal or event window (`InRange "[Next90Days]"`, `[ThisQuarter]`) |
| "across our customers" | Portfolio-wide, Active accounts |
| A named account | `staircase_account_lookup` for the id, then `account.360` |

## Step 2: map the business term to a field or signal
| Business term | Field or signal (see field-catalog.md) |
|---|---|
| "at risk" | `risk.risk_level >= 4`, or the `ChurnRisk` insight, or recent `churn_risk` lifecycle events |
| "leaving", "about to churn" | Hard-stop Signals on recent `churn_risk` events (concrete exit actions, migration in progress, auto-renewal opt-out) |
| "expanding", "upsell" | `expansion.readiness_level`, `expansion_opportunity` by `confidence_level` and `momentum_state` |
| "stale", "quiet", "dark" | `last_engagement` / `last_reach_out` older than N days; the `CustomerDark` insight |
| "they stopped replying" | `email.customer_last_sent` well behind `email.organization_last_sent` |
| "no QBR" | `next_qbr_date` empty; the `NoQBR` insight |
| "single-threaded" | The `CustomerSingleThreaded` insight (the `multi_threaded` field is column only) |
| "renewing soon" | `renewal_date InRange "[Next90Days]"` |
| "nobody's talked terms" | Most recent `renewal_discussion` event date (child MAX) |
| "champion left" | `Farewell`, `OrganizationPersonnelChange`, or `TitleChange` insights; personnel-change lifecycle events |
| "negative trend" | `customer_sentiment.negative`, the `NegativeSentimentTrend` insight, low sentiment score |
| "what are they saying about X" | `staircase_semantic_search` (evidence, not counts) |
| "what did we promise" | Meeting `action_items[]` via `staircase_list_communications` |

Custom concepts (a "priority account" flag, a segment) are usually custom fields: discover them in metadata per org.

## Step 3: compose the plan (report first)
| Question shape | Plan |
|---|---|
| "List X with properties Y and Z" | One report with every property as a filter. Don't decompose; reports combine `And` and `Or` |
| "Top N by priority" | Pull the raw fields, score with the composite below, then drill the top N |
| "How many / how much" | A scalar COUNT or SUM, or a breakdown with the group as root |
| "Why is X happening" | The evidence chain (`lifecycle.evidence`) |
| "What are accounts saying about T" | `staircase_semantic_search`, scoped to the accounts from a report |
| "Which themes, how many accounts each" | A `parent_topic` report (`voc.pain_profile`) |
| "Tell me the story of one account" | `account.360`, then `staircase_analyze_account` if narrative judgment is needed |

## The production cross-account workflow
1. **Pull the cohort** with the recipe for the question (one report, all filters, all context columns). Confirm the row count is plausible.
2. **Score it** with the composite below.
3. **Pull evidence** for the top of the list: `lifecycle.evidence` for the accounts with recent events.
4. **Drill** the top accounts with `staircase_analyze_account`, 10 at a time.
5. **Synthesize** into the output the skill defines, rendered per `staircase-app-design`.

## The priority composite
The canonical "where should I focus" score, fully computable client-side. When an input is missing for this org or session, drop that tier, renormalize the remaining weights, and say so in the output.

```
priority =
  0.20 x renewal urgency
+ 0.18 x engagement health
+ 0.15 x commercial value
+ 0.15 x health and sentiment
+ 0.12 x expansion and open items
+ 0.10 x recent acute events
+ 0.10 x support intensity
(cap at 1.0)
```

- **Renewal urgency (0.20):** days to renewal (under 30 = 1.0, 60 = 0.75, 90 = 0.5, 180 = 0.25, else 0), blended with `risk_level / 5`.
- **Engagement health (0.18):** days since last engagement / 30 and days since last decision-maker touch / 21 (each capped at 1.0; decision-maker silence weighs more), plus the inverted engagement score.
- **Commercial value (0.15):** `log10(revenue) / 7`, blended with a tier weight you derive from the org's own tiers (highest tier 1.0, lowest 0.3).
- **Health and sentiment (0.15):** `(100 - health) / 100` and `(100 - sentiment) / 100`.
- **Expansion and open items (0.12):** `readiness_level / 5` (upside) and `(100 - open items score) / 100`.
- **Recent acute events (0.10), boosts only:** +0.15 for a `churn_risk` event in the last 30 days (+0.05 more if it carries a hard-stop signal), +0.10 for an extremely negative message event, +0.10 for a personnel change, +0.05 for an active no-QBR, dark, or single-threaded insight. Pull these as child COUNTs in the same report.
- **Support intensity (0.10):** `customer.ticket.submitted_count` and `.comments_count` in the window, normalized across the cohort.

**Save-into-expansion bonus:** accounts with `risk_level >= 3` AND `readiness_level >= 3` get +0.10. These are the highest-leverage plays.

**Risk-weighted readiness skepticism:** when risk is at least 3, discount the expansion contribution (risk 4 or more: x 0.5; risk 3: x 0.75). The expansion analyst doesn't see the risk analysis.

## The Risk x Expansion merge
The risk and expansion analysts run independently; neither sees the other. For accounts with `risk_level >= 3` AND `readiness_level >= 3`, reconcile them yourself. This is internal reasoning: never show the classification labels in a customer-facing artifact.

1. **Recency.** Compare the most recent evidence behind each analysis; the fresher one gets more weight.
2. **Pull both.** Risk: reasons, severity, stakeholders, mitigations (`staircase_analyze_account`). Expansion: the account's `expansion_opportunity` rows (confidence, momentum, decision maker, budget, timeline).
3. **Reconcile stakeholders.** The same person may read as a detractor in one and a sponsor in the other; prefer the framing the most recent evidence supports.
4. **Test each opportunity.** Does the risk credibly threaten this specific opportunity? Yes means save before expand; no means expand despite risk.
5. **Classify each opportunity separately**, then roll up to the account.
6. **Classify the account:**
   - **Expansion as the save:** the risk is real, but the sponsor's appetite for more is the path forward.
   - **Save, then expand:** resolve the risk first; the expansion lands after.
   - **Skeptical read:** the expansion signal contradicts recent risk evidence; weight it low and focus on the save.
7. **Plan:** three to five actions grounded in the classification. For customer-facing output, show the account state, the stakeholder map, and the plan only.
