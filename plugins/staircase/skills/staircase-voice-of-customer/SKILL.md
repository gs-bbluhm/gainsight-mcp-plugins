---
name: staircase-voice-of-customer
description: "Voice-of-Customer / cohort intelligence: what customers are actually saying, quantified. Report-first: a cohort-scoped topic profile (which themes, how loud, how negative, and which are rising), drilled into the specific child-topic reasons, then grounded in verbatim quotes with evidence. Works for any cohort (whole book, a tier, a team, at-risk accounts, a renewal window), the topic engine no CRM has. Triggers on \"voice of customer\", \"what are customers saying\", \"what are customers saying about [topic]\", \"VoC on [topic]\", \"customer feedback on [topic]\", \"what themes are rising\", \"what's driving negative sentiment\", \"top customer complaints\", \"cohort intel\"."
user_type: exec
allowed-tools: mcp__visualize__show_widget, mcp__visualize__read_me
---

# Staircase Voice of Customer (cohort intelligence)

What are customers saying, as a measured profile, not a vibe. This is the capability a CRM cannot replicate: a topic / sentiment / volume / trend profile for **any cohort × window × channel**, drilled from the big theme down to the specific reason, and anchored in the customers' own words. The engine is the `parent_topic` entity (deterministic counts, sentiment, and period-over-period trend), the child-topic drill (`semantic_search` topic channel), and evidence quotes.

## Foundation & portability (read first)
A **workflow skill on top of `staircase-mcp-expert`**. That foundation owns the query mechanics (the `parent_topic` cohort-scoping via the `filter.customer` argument, the VoC drill in `../staircase-mcp-expert/references/advanced-report-patterns.md`, the argument system). This skill composes them into the VoC workflow. Read it before composing queries.
- `../../_shared/staircase-output-best-practices.md`: house style, evidence discipline, no CRM writes.
- **Portability:** standard primitives only: the **canonical parent topics** every Staircase org has (Support & issues, Commercial & contracts, Feature requests, Implementation & projects, Risk & dissatisfaction, Customer success & relations, Security & compliance, Organizational changes, Competitors, Expansion opportunities, Advocacy & value realization, Product knowledge, Meeting scheduling), never a hardcoded org-specific topic. No `_c` fields. **Trend fields are flag-gated** per org: probe `absolute_growth_percentage`; if null, degrade to current-period volume + negative rate and say trends are unavailable. If the org is itself a vendor instance, ignore its internal/product-feedback topics and report only the canonical customer-facing parents.

## Step 0: Topic + cohort + window
- **Cohort (the differentiator):** VoC is only as sharp as its scope. Default = whole active book, but the power is a *specific* cohort: a tier, a team (owner set), the at-risk accounts (`insight EXISTS ChurnRisk` ∨ `risk.risk_level >= 4`), a renewal window, the churned set. Ask or infer which cohort; the topic profile changes completely by cohort. Pass it as the `filter.customer` argument on every topic metric.
- **Topic:** optional. **Open VoC** ("what are customers saying") → rank all canonical parents (Step 1) and surface the dominant + rising-negative themes. **Topic VoC** ("...about X") → go straight to the named parent and drill (Steps 2-3).
- **Window:** default `Past3Months` (the `dateRange` argument); the trend compares it to the prior period.

## Step 1: Quantify the cohort topic profile (deterministic)
`parent_topic` report, each metric carrying the cohort scope. Columns: `parent_topic.id` (a numeric topic id: topic reports currently return no names, so name each theme through the Step 2 search, which returns parent and child topic names, and say so in the output), `total_count`, `negative_sentiment`, `accounts_count`, and the trend trio `current_period_volume`, `previous_period_volume`, `absolute_growth_percentage`. Arguments on each metric: `dateRange` (window), `commType` (channels), `filter.customer` (the cohort).
Rank on three axes, not one:
- **Negative volume** (`negative_sentiment`): where the pain concentrates.
- **Negative rate** (`negative_sentiment / total_count`): where a theme is almost always negative (in live testing, Risk & dissatisfaction ran mostly negative). A high rate on real volume is a red flag even at modest counts.
- **Growth** (`absolute_growth_percentage`): what's *rising*. A theme up 20% on a large base is the story; ignore big % swings on tiny bases.
Read the canonical parents only. The output of Step 1 alone answers "what are customers saying" for the open mode.

## Step 2: Children (drill the theme into its reasons)
A parent topic ("Support & issues") is a bucket; the **child topics** are the specific reasons. Get them with **one** `semantic_search` call that leads with **text terms plus topic terms together**: a few single-word text terms for the theme (text terms match conjunctively, so one word each) and several topic-phrase variations of the parent or theme, all in the same call, bounded to the Step-0 window (a text term needs an account scope or a date bound). Keep extra filters minimal. Do **not** stack `account_ids` + `parent_topics` + `topic_sentiments` on one call: the filters compound and over-filter to empty. When the cohort is a set of named accounts, pass their `account_ids` (pull the ids from a `customer` report first) with the text and topic terms in that same call and add nothing else; narrow to the parent and to negative sentiment Claude-side from each result's `parent_topic` / `topic_sentiment`. Each topic hit carries `child_topic`, `topic_sentiment`, `account_name`, and `evidence_id` (text hits carry no `child_topic`; use them as quote candidates). Aggregate the child topics and **keep only those appearing more than once** (`count > 1`): a child topic mentioned by one account is an anecdote, not a theme. Count distinct accounts per child topic; that's the breadth.

## Step 3: Quotes (ground it in their words)
The Step-2 snippets ARE the representative quotes, each with an `evidence_id`, an account, and a sentiment. Pick 1-3 per child topic that are verbatim and attributable. `fetch_evidence(<id>)` for the full thread when a snippet is too thin. For a deep read on one account that raised a theme strongly, `account_lookup` → `analyze_account` (stay within the parallel per-account analysis cap, 10 today). Always attach evidence ids; never surface a quote you can't anchor.

## Prioritize into a finding
VoC is only useful if it points somewhere. Close with the one or two themes that combine **volume × negative rate × growth** and name the action they imply: a product priority (recurring feature/capability gap), a comms fix (a misunderstanding), a program (a systemic friction), or a save motion (if the cohort is at-risk). Tie the finding to the cohort: "across your top-tier renewals, X is rising and it's a product gap" is worth more than a book-wide average.

## Output: the VoC read
```
# Voice of Customer: <cohort> · <window> (<date>)

**Scope:** <cohort> · **Window:** <window> · **Channels:** <all / named>
> Reflects communications in the window, not a survey. Trends shown where the org enables them.

## Headline
<2-3 sentences: the dominant theme, the fastest-rising negative, and the one action it implies for this cohort.>

## Theme profile (ranked)
| Theme | Items | Negative | Neg rate | Trend | Accounts |
|-------|-------|----------|----------|-------|----------|
| Support & issues | <items> | <negative> | <neg %> | <trend %> | <accounts> |
| Risk & dissatisfaction | <items> | <negative> | <neg %> | <trend %> | <accounts> |

## <Top theme>: the reasons (child topics, count > 1)
| Reason (child topic) | Accounts | Sentiment | Representative quote (evidence) |
|----------------------|----------|-----------|---------------------------------|
| <child topic> | Acme, Globex, … | negative | "<verbatim>" (<evidence_id>) |

## What's rising
<the themes with real growth × negative rate, and what each predicts.>

## Finding & action
<the one or two themes worth acting on, each tied to a product / comms / program / save move, with an owner.>

---
## Sources
- Staircase `staircase_run_report`: cohort-scoped `parent_topic` profile (volume, negative sentiment, period trend)
- Staircase `staircase_semantic_search`: child-topic drill + representative quotes; `staircase_fetch_evidence` for full text
```

**Format adaptation:** inside Claude, render the interactive VoC dashboard (below). In Cowork, lead with the theme-profile table (volume/neg/trend bars) then the child-topic reasons + quote cards. In Code, markdown + optional `voc-<cohort>-<date>.md`. No CRM writes.

## Interactive dashboard (inside Claude)
Render via `show_widget` (same design system as the other cockpits; call `read_me` first). Shape: a **ranked theme bar-list** (each canonical parent as a bar sized by volume, colored by negative rate, with a small ▲/▼ trend badge), a cohort selector / filter, and **click a theme → expand inline** (accordion, not a top panel) to its child-topic reasons (count>1) with the representative quotes and evidence chips. A "rising negatives" filter surfaces the growth×neg-rate themes. Keep it read-only; the deep-dive button `sendPrompt`s Claude to pull fresh quotes for a chosen theme.

## Edge cases
| Situation | What to do |
|-----------|------------|
| No cohort given | Default whole active book, but say so and offer the sharper cuts (tier / team / at-risk / renewal window). |
| Trend fields null | Org hasn't enabled trends: rank by negative volume + rate; note trends unavailable. Don't fabricate direction. |
| A child-topic search returns nothing scoped | Scoped topic-only search can come back empty: keep the account_ids, text terms, and topic terms in the same call with no other filters, or widen the window. |
| Instance/internal topics dominate (vendor's own org) | Ignore them; report only the canonical customer-facing parents. |
| A "theme" is one account | count>1 rule: that's an anecdote; note it separately, don't elevate it to a theme. |
| User wants ARR-weighted VoC | Name the accounts per theme; weight by ARR from the CRM (Staircase holds the communication signal, not the contract). |
