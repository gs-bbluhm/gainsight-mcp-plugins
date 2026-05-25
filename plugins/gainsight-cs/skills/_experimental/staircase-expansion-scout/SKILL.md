---
name: staircase-expansion-scout
description: Cross-portfolio expansion scout — surfaces accounts with active expansion signals, named upsell opportunities, and Staircase readiness score (1-5). Supports renewal-window, product, and industry intersections.
user_type: experimental
disable-model-invocation: true
---

# Staircase Expansion Scout

## Discovery

**Auto-trigger phrases:**
- "expansion opportunities"
- "expansion scout"
- "which accounts are ready to expand"
- "upsell pipeline from comms"
- "expansion plays for upcoming renewals"

**Validation history:** Primary query phrasing validated against real-org data — "explicit expansion signals or new product interest in the last 60 days" returns a portfolio-scale list of accounts with Expansion Summary, Opportunities, and Readiness (1-5) columns. Wrong-vocabulary phrasings ("readiness above 60") and combined-criteria queries return empty.

**Currently flagged experimental** — niche audience, parallel to staircase-at-risk-renewals.

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — validated phrasings + decompose-and-intersect
- `../staircase-mcp-expert/references/anti-patterns.md` — 15-cap clarification, OR not supported, determinism mitigations
- `../staircase-mcp-expert/references/field-catalog.md` — what's queryable

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)

---

Cross-account skill that surfaces the accounts most ready to expand, with named opportunities and readiness scores from Staircase. Pairs naturally with `staircase-at-risk-renewals` — same decompose-and-intersect pattern, different sentiment direction.

## Critical query-phrasing finding

**Use Staircase's internal vocabulary.** The query phrasing matters:

✅ "Which of my accounts have **explicit expansion signals** or **new product interest** in the last 60 days, such as upsell discussions, new product requests, or buying expansion."
→ Returns a portfolio-scale list with Expansion Summary, Expansion Opportunities, and **Readiness (1-5 scale)** columns.

❌ "Which accounts have expansion readiness above 60"
→ Returns "I am unable to retrieve accounts with a high expansion readiness score" — wrong scale lexicon.

❌ "Which accounts have positive sentiment AND are discussing new use cases"
→ Combined-criteria query, returns empty.

## Step 1: Define scope

Default: portfolio-wide. Adjust if user wants:
- Industry segment ("SaaS", "FinServ", etc.)
- Renewal-window intersection ("expansion plays for renewals in Q2")
- Readiness threshold ("only readiness 4 or 5")
- Specific product ("who's expressing interest in <product>?")

## Step 2: Primary query

```
staircase_ask("Which of my accounts have explicit expansion signals or
   new product interest in the last 60 days, such as upsell discussions,
   new product requests, or buying expansion?")
```

Parse the returned table. Columns include:
- Account Name
- Expansion Summary (narrative)
- Expansion Opportunities (specific products/services)
- Readiness (1-5)

## Step 3: Optional intersections (in parallel if multiple)

### Renewal-window intersection
```
staircase_ask("Which of my accounts have a renewal date in the next <N> days?")
```
Client-side join on account name. Returns the "expansion plays for upcoming renewals" subset — the highest-leverage segment.

### Product-interest filter
After primary query, filter the result client-side for accounts whose Expansion Opportunities mentions the target product (case-insensitive substring match).

### Industry filter
If Gainsight is enriched: `gainsight run_query` on company object filtered by industry, then intersect with the expansion list.

## Step 4: Enrich top N (default 5)

For the top N by Readiness (5 first, then 4):

```
staircase_account_lookup → account_id
staircase_analyze_account(account_id, query="
   For an expansion play: confirm the top 2 expansion opportunities,
   named decision makers and champions, the single most recent
   buying signal evidence, and the most concrete recommended next
   action a CSM should take. Cite evidence IDs.")
```

## Step 5: Optional Gainsight enrichment

For each enriched account:
```
gainsight resolve_customer + fetch_cta_list (DueDate >= today-90d)
```
Look for: existing expansion CTAs, current CSM owner, ARR, multi-product status.

## Step 6: Produce the report

### Output structure

```
# Expansion Scout Report — <date>

**Scope:** <portfolio-wide | renewal-window | etc.>
**Accounts with expansion signal:** <count>
**Readiness 5 (highest):** <count>
**Readiness 4:** <count>

## Headline

<2-3 sentences. Total estimated expansion ARR if knowable. Top theme.
The single highest-leverage play to run first.>

## Top Expansion Plays

| Rank | Account | Readiness | Top Opportunity | Renewal | Current CSM |

## Deep Dives (top 5)

### <Account>
- **Readiness:** <1-5>
- **Top opportunity:** <named product/service>
- **Named decision makers:** ...
- **Most recent buying signal:** <evidence ID>
- **Recommended next action:** ...

## Common Themes

Patterns across the expansion cohort. What products are showing the most pull. What customer profiles are most expansion-ready.

## Recommended Plays

Org-level moves. E.g.: "Run a focused POC outreach to the Readiness-5 cohort, anchored on the specific Expansion Opportunity surfaced for each."
```

## Edge cases

| Situation | What to do |
|-----------|------------|
| Primary query returns empty | Try alternate phrasings: "upsell discussions", "new product interest", "buying expansion" |
| Readiness column missing | Note in output; rely on the Expansion Summary narrative for ranking |
| User asks for "expansion readiness score" | Disambiguate: Staircase scale is 1-5, not 0-100 |
| User asks "which accounts are expansion-ready in industry X" | Combine primary query + industry filter via Gainsight (Staircase doesn't reliably filter on industry in `ask`) |

## Output Best Practices (when chaining into Gainsight writes)

This skill primarily READS from Staircase. If you chain into Gainsight writes (Opportunity CTAs on top expansion-ready accounts), follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Key rules: user approval gate before customer-facing writes, commitment discipline, HTML formatting, teammate-facing language (no synthesis labels like "save-into-expansion bonus"), reuse-vs-create discipline, org-specific discovery (Opportunity CTA Type may not exist in every org; fall back to closest match).

---

## Learnings

See `.learnings.md`.
