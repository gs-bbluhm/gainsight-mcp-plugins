# gainsight-cs

Claude plugin bundling **Staircase AI + Gainsight CS** skills for Customer Success Managers, CS Operations, and Customer Success leadership. Designed to run in Claude Code CLI and Claude Cowork.

The plugin codifies the highest-leverage CSM workflows that combine Staircase's 90-120 day communication intelligence with Gainsight's CTAs, Success Plans, Timeline, Renewal Center, and Opportunities — so a single prompt does what previously took 30 minutes of context-gathering.

## How to start — run setup once, then use the skills

1. **Run `gainsight-mcp-setup` first.** Role-adaptive onboarding (Executive / CSM / AM / Sales / Admin / Other) that discovers your org's bespoke fields, captures your assignment filter, and runs a short practice round. ~2 minutes. After this, every other skill auto-applies your filter — no more "filter for CSM = me" plumbing on every ask.
2. **Then use the role-appropriate skills below.**

## Skills

Organized by `user_type`:

### Foundation skills (read by every other skill; not typically called directly)

- **`gainsight-mcp-setup`** — Role-adaptive onboarding. Discovers your org's bespoke fields (segmentation, team-member assignment, required custom fields, SP types), writes a persistent user profile, runs role-tailored practice round. Run once per user per org.
- **`staircase-mcp-expert`** — Canonical reference for HOW to query Staircase MCP. SKILL.md has tight orientation + top patterns; `references/` carries dense material (field catalog, query patterns + 6-tier priority methodology, anti-patterns including the critical 15-cap clarification, analyst data models).
- **`gainsight-cs-mcp-expert`** — Canonical reference for HOW to read + write Gainsight CS MCP. SKILL.md has orientation; `references/` carries tool inventory, write-path recipes (CTA + Task + Timeline + SP with HTML templates), org-discovery procedure, anti-patterns (G3.1-G3.11 gotchas).

### Core skills — IC / individual contributor with accounts (`user_type: ic`)

For CSMs, AMs, anyone owning or assigned to accounts via a team-member field.

- **`gainsight-meeting-processor`** — Post-call workflow. Modular call-recorder source (Notion, Zoom, Granola, Fireflies, Gong, paste). Produces Gmail recap, Timeline activity, risk CTA, SP updates, action items, win quotes. Multi-MCP fan-out. Nothing posts without approval.
- **`gainsight-csm-book-pulse`** — Focus on accounts in your book that need attention this week. Layers insight flags (No QBR, Account Dark, No Reach Out, Personnel Changes) over the 6-tier composite priority score.
- **`gainsight-account-workspace`** — Daily workbench for one account. Loads CTAs + SPs + Timeline + Renewal Center + Staircase situational context, proposes up to 6 next moves, posts updates on approval.
- **`gainsight-account-handoff-onboarding`** — Inheriting an account. Scans Staircase for Handoff Analysis, then builds a first-90-days onboarding plan from the 11-section structured output.
- **`gainsight-stakeholder-connect`** — Stakeholder alignment analysis + personalized outreach drafts. Uses Personnel Changes flag + per-account Risk Analysis stakeholder section.
- **`gainsight-no-qbr-ebr-scheduler`** — Surface No-QBR accounts, draft personalized EBR outreach anchored on each account's active themes.

### Core skills — Exec / leadership (`user_type: exec`)

For CS leaders, CROs, VPs — portfolio + strategic cadence.

- **`gainsight-exec-renewal-radar`** — Tier-stratified renewal intelligence (Strategic / Scale / Enterprise) across the 120-day renewal window. Cross-account theme detection across the prioritized list.
- **`gainsight-renewal-priority-planner`** — Move-the-needle renewals. Composite movability score (renewal proximity + ARR + risk + readiness + tier). Pulls full Risk + Expansion Analyses on top-15.
- **`gainsight-exec-churn-retrospective`** — Quarterly review: pattern themes across churns + per-account Churn Analysis + gap-finding for churns that lack Staircase analysis.
- **`gainsight-exec-pattern-hunter`** — Cross-portfolio thematic intelligence. Groups 15 accounts by emergent themes with evidence IDs. Validated against real-org data: friction signals and win narratives return rich cross-aggregation; some query types (e.g., feature-request counts) fall back to per-account themes.

### Experimental skills (`user_type: experimental`)

Live in `skills/_experimental/` with `disable-model-invocation: true` — Claude won't auto-pick them on fuzzy match. Users can still invoke explicitly by name.

- **`gainsight-daily-cockpit`** — Overlaps with `gainsight-account-workspace`; consolidation candidate.
- **`staircase-at-risk-renewals`** — Subsumed by `gainsight-exec-renewal-radar` in most flows. Validated as production-grade against real-org data; kept experimental to avoid skill duplication.
- **`staircase-expansion-scout`** — Overlaps with `gainsight-exec-renewal-radar`. Validated against real-org data.
- **`staircase-reference-finder`** — Partial; waiting on a portfolio-similarity primitive in Staircase.

## Canonical references (read these first when installing)

- **`_shared/gainsight-output-best-practices.md`** — Plugin-wide output discipline for every Gainsight write. User approval gate, commitment discipline, HTML formatting, teammate-facing language, reuse-vs-create, cleanup discipline. v1.1 includes the Account Signal Classification framework + Risk × Expansion merge.
- **`skills/staircase-mcp-expert/`** — Staircase MCP foundation. SKILL.md (orientation) + `references/{field-catalog, query-patterns, anti-patterns, analyst-data-models}.md`.
- **`skills/gainsight-cs-mcp-expert/`** — Gainsight CS MCP foundation. SKILL.md (orientation) + `references/{tool-inventory, write-path-patterns, org-discovery, anti-patterns}.md`.
- **`skills/gainsight-mcp-setup/`** — First-run onboarding. Role-adaptive flow + persistent user profile.

## Naming convention

- `gainsight-<skill>` for skills where Gainsight CS leads the workflow
- `staircase-<skill>` for skills where Staircase AI leads
- All skills exercise **both** MCPs; the prefix signals which system anchors the flow.

## Frontmatter conventions

Every SKILL.md uses standard Claude Code frontmatter (`name`, `description`, `allowed-tools`, optional `disable-model-invocation` on experimental skills) plus one plugin-internal field:

- **`user_type`** — `foundation` | `ic` | `exec` | `experimental`. Plugin-internal convention indicating who the skill is for. Claude Code ignores unknown frontmatter keys, so this is safe; we use it for our own organization + future filtering. Not part of the official Claude Code frontmatter spec.

If you fork this plugin and want to drop the convention, removing `user_type:` lines has no functional effect.

## Prerequisites

- **Staircase AI MCP** installed and authenticated
- **Gainsight CS MCP** installed and authenticated
- Optional: Notion MCP (meeting notes connector), Zoom MCP, Gmail MCP, Calendar MCP

## Installation

See the top-level [README](../../README.md) for marketplace install instructions.

## Build history

Initial release: May 2026. Real-org validation history is captured per-skill in `.learnings.md` files alongside each SKILL.md — what worked, what didn't, and refinement notes. Validated workflows include meeting-processor recap drafting, account-handoff onboarding plans, portfolio-scale at-risk-renewal and expansion-scout sweeps, competitive pulse rollups, and cross-portfolio pattern-hunter aggregations.

## Plugin-filed feature requests

- `skills/_experimental/staircase-reference-finder/references/staircase-feature-request.md` — Reference Matching + Portfolio Similarity (industry metadata, advocacy structured field, `staircase_find_similar` tool).

## Known limitations

### Staircase MCP
- Combined-criteria queries (A AND B AND C) return empty — decompose into single-dimension + intersect client-side
- Industry / segment filtering not supported in customer metadata
- `staircase_analyze_account` uses `query`, NOT `question`
- ~90-120 day data window (not extendable)
- Cross-account capacity: 15 accounts per query (raised from "a few" in May 2026)

### Gainsight CS MCP
- `fetch_cta_list` without DueDate filter blows token budget — MANDATORY date constraint
- `select=` parameter is ignored — date filter is the actual load-control
- `fetch_timeline_activity_list` returns generic failure intermittently — soft-fail expected
- `survey_response` returns 500 (definitions work, response text doesn't)
- `scorecard_fact` returns 500 (measure definitions work, scores don't)
- Metadata responses are 100-183k chars — cache per session

### Notion MCP (meeting notes)
- Use `notion-search` text query, not `notion-query-meeting-notes` with `account_name`
- Transcript lives at the inner URL fragment in `readOnlyViewMeetingNoteUrl`, not the outer meeting page
