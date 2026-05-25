---
name: gainsight-exec-pattern-hunter
description: Cross-portfolio thematic intelligence. Groups 15 accounts by emergent themes — feature requests, friction signals, win narratives, expansion language, competitive mentions — with evidence IDs.
user_type: exec
---

# Staircase Pattern Hunter

## Discovery

**Auto-trigger phrases:**
- "what patterns are emerging"
- "what themes are showing up across my book"
- "common feature requests this quarter"
- "what friction signals repeat"
- "what wins are being expressed"

**Purpose:** Portfolio-wide thematic view grounded in actual customer language. Staircase MCP cross-account queries support up to ~15 accounts in a single grouped-theme query with evidence IDs.

**Optimized for:** Cowork (theme card with expandable account lists) and Code (full markdown report). Cowork is the primary optimization target.

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

Cross-portfolio thematic intelligence. Looks across up to 15 accounts to surface common patterns in feature requests, friction signals, win narratives, expansion language, or competitive mentions — with evidence IDs anchoring each theme.

## Why this skill exists

Staircase MCP supports a grouped-theme query that returns themes across ~15 accounts with evidence IDs. This skill packages that capability into a CSM-leadership-friendly workflow.

## Use cases

| Question the user is asking | Skill scope |
|---|---|
| "What are the top feature themes in my book this quarter?" | Feature-request theme detection |
| "What integration or admin friction is showing up repeatedly?" | Engineering signal — where to invest |
| "What value language is appearing in our expansion conversations?" | Marketing input / sales playbook |
| "Which competitors are being mentioned across accounts?" | Competitive intelligence rollup |
| "What's the common language in our renewal saves?" | Save-play library input |
| "What ROI claims are customers articulating themselves?" | Voice-of-customer evidence |

## Step 1: Frame the theme target

Ask the user (or infer from the trigger) what kind of patterns they want surfaced:

- **Feature requests** — what customers are asking for
- **Friction signals** — where the product or experience is breaking down
- **Win narratives** — what's working that customers articulate
- **Expansion language** — buying intent and product pull
- **Competitive mentions** — which alternatives surface
- **Risk language** — common churn signals

If unclear, default to the broadest useful framing: feature requests + friction signals.

## Step 2: Run the validated pattern query

```
staircase_ask("Across 15 of my customers, identify common patterns or
   themes in <signal type> from the last <N> days. Group by theme
   and list the accounts under each.")
```

Returns grouped themes with affected accounts and evidence IDs per theme.

### Optional scope filter (still single-dimension)

If the user wants the scan focused (e.g. "across my top 15 expansion accounts" or "across my at-risk renewals"), add that scope into the query but **do not combine multiple criteria** — that hits the same combined-query failure pattern documented across the plugin.

✅ "Across 15 of my customers showing expansion signals, identify common themes in feature requests..."
❌ "Across 15 of my customers with health > 60 AND renewals in next 90 days AND active expansion, identify themes..." (combined-criteria — fails)

## Step 3: Optional account enrichment

For 1-3 accounts the user wants to drill into:

```
staircase_account_lookup(name=<account>) → account_id
staircase_analyze_account(account_id, query="
   For pattern follow-up: deeper context on <theme>. What did
   <Account> specifically say or request? Who's driving it?
   Cite evidence IDs.")
```

Skip enrichment if the theme map alone is enough.

## Step 4: Optional Gainsight enrichment

For the named-stakeholder + ARR-sized version of the report (the executive-friendly version):

```
For each account in the theme map:
  gainsight resolve_customer(name=<account>) → company GSID
  gainsight run_query on company — pull Arr, RenewalDate, CSM
```

Group ARR per theme to size each theme's opportunity.

## Step 5: Produce the report

### Output structure

```
# Pattern Hunter Report — <signal type> across portfolio

**Scope:** <broad portfolio | top 15 X accounts | etc.>
**Window:** Last <N> days
**Accounts examined:** 15
**Themes detected:** <count>
**Highest-volume theme:** <name>

## Headline

<2-3 sentences. The single biggest pattern. Total ARR if sized. The one move it suggests.>

## Themes

### 1. <Theme Name> — <count> accounts (<total ARR if sized>)

<2-3 sentence theme description>

- **<Account>** — <what they specifically said>
- **<Account>** — <what they specifically said>
- ...

**Evidence:** <ID list with one-line context per ID>
**Recommended next move:** <action-oriented suggestion>

### 2. <Theme>

...

## Cross-Theme Observations

<Patterns across themes. e.g. "AI/automation appears in 5 of 9 themes — the
underlying customer ask is a unified intelligence layer, not nine
separate features.">

## Recommended Plays

1. <Highest-leverage move>
2. <Second move>
3. ...
```

### Cowork formatting
Theme cards with account lists expandable per theme. Evidence-ID chips link out to Staircase.

### Code formatting
Full markdown to stdout + artifact at `pattern-hunter-<topic>-<date>.md`.

## Worked example (shape of output)

Query: "Across 15 of my customers, identify common patterns or themes in their feature requests or product feedback from the last 60 days."

A typical return is ~6-9 themes, each with affected accounts and evidence IDs. Common theme types:
1. **AI / Automation / In-Product Guidance**
2. **Admin UX / Integration / Configuration Friction**
3. **Reporting / Analytics / Health Scoring**
4. **Customer Education / Enablement / Learning Experience**
5. **Customization / Segmentation / Product Configuration**
6. **Success Planning / Value Tracking / Outcome Measurement**
7. **Localization / Accessibility / Multilingual Support**
8. **Governance / Permissions / Security Controls**
9. **Operational / Commercial Issues**

Cross-theme observation worth surfacing: any account that appears in 4+ themes — either deep engagement (positive) or scattered priorities (worth checking).

## Edge cases

| Situation | What to do |
|---|---|
| Theme query returns empty | Try a more specific scope ("expansion accounts", "at-risk accounts") instead of broad portfolio |
| One account appears in 4+ themes | Flag it explicitly — either highly engaged or scattered. Worth a follow-up. |
| Garbled Unicode in account names | Known data-quality issue (commonly observed with non-Latin-script account names). Note in output; do not fail. |
| User wants to see beyond 15 accounts | Document the cap; recommend running the skill twice with different scopes to compare. |
| Evidence IDs are sparse (< 3 across all themes) | Confidence is lower — flag in output. Themes are still valid but less directly attributable. |

## Limitations to document for DS

- 15-account cap is the documented upper bound. Patterns across larger sets aren't possible in a single query.
- "Group by industry" doesn't work — industry metadata isn't queryable (filed in reference-finder feature request).
- Sentiment-trajectory grouping is fragile — works as a single-dim query but not when combined with theme detection.
- The same query phrased differently can return different account sets (sampling variability) — re-run for stability when stakes are high.

## Output Best Practices (when chaining into Gainsight writes)

This skill primarily READS from Staircase. If you chain into Gainsight writes (Timeline activities sharing pattern findings with the team, CTAs on accounts that surfaced under specific themes), follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Key rules: user approval gate, commitment discipline, HTML formatting, teammate-facing language, reuse-vs-create discipline, org-specific discovery.

---

## Learnings

See `.learnings.md`.
