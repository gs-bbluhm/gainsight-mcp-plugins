---
name: gainsight-cs-mcp-expert
description: Foundation skill for the Gainsight CS MCP. Catalogs the tools, the read + write patterns that work, the org-specific things you MUST discover (Segment field, required custom fields, team-member fields, SP types, CTA reasons), and the gotchas. Other skills reference this before composing Gainsight queries or writes. Read this whenever you're about to read or write Gainsight data and you haven't recently.
user_type: foundation
allowed-tools: mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__resolve_customer, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__resolve_user, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_object_metadata, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_picklist_values, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_records, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__run_query, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__fetch_cta_list, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__fetch_success_plan_list, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__fetch_timeline_activity_list, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__manage_cockpit_actions, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__create_timeline_activity, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__manage_success_plan_actions, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_activity_types_config, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__ask_scorecard
---

# Gainsight CS MCP Expert

## What this skill is for

The Gainsight CS MCP is how every customer-success skill in this plugin reads from and writes to Gainsight. The tools work, but the surface is uneven: required custom fields aren't always declared up front, picklists are org-bespoke, payloads need date filters or they blow the token budget, and the write paths follow a two-step prepare-then-create pattern that isn't obvious from the tool names alone.

This skill is the canonical reference for sibling skills. Read it (or its references) before composing Gainsight reads or writes you haven't done recently in this session.

## When to invoke

**Direct invocation triggers:**
- "How do I query Gainsight for X?"
- "What fields does the Company object have for renewal forecasting?"
- "What's the right CTA reason for a save-into-expansion case?"
- "Validate my Gainsight write payload before I send it."
- "What custom fields does my org require on Timeline activities?"

**Sibling-skill reference triggers** (these skills MUST read this before writing):
- `gainsight-meeting-processor` — before logging Timeline, CTA, SP updates
- `gainsight-account-workspace` — before any write back to Gainsight
- `gainsight-csm-book-pulse` — before applying CTA filters / pulling SP data
- `gainsight-mcp-setup` — for the user-filter-field discovery procedure
- Any `gainsight-exec-*` skill — before posting org-wide context
- `gainsight-account-handoff-onboarding` — before creating an inheriting SP

## Top patterns (the 5 things you'll do 80% of the time)

### 1. Resolve customer + user before any write
- `resolve_customer(search_name)` returns one or more `account_id` matches with confidence labels. **If multiple low-confidence matches come back, stop and ask the user which to use.** Do NOT guess.
- `resolve_user(search_name)` may return multiple matches for a common name. Pick the record with the most identities attached (Slack, Gong, Salesforce, Zendesk) as the disambiguation signal.
- See `references/tool-inventory.md` for both tools.

### 2. Discover the org's bespoke fields before assuming
Every customer org names their fields differently. **Never assume.** Mandatory discovery for each new install / session:
- **Segmentation / tier field** (could be `Tier`, `Segment`, or an org-bespoke variant like `Customer_Tier__gc`) → `get_object_metadata(object_name="company")` then `get_picklist_values` on the chosen field
- **Team-member assignment field** — Staircase has a standard `Owner` field that's universal across orgs. Most orgs also have one or more custom team-member fields (common names: `CSM`, `Account Manager`, `Renewal Owner`, `Account Owner`, or an org-bespoke variant). The custom ones are bespoke per org and MUST be discovered via `get_object_metadata("company")`. `gainsight-mcp-setup` walks the user through this once and caches the chosen field in the user profile.
- **Required custom fields on Timeline activities** (some orgs silently require a `Status` custom field or similar) → expect first-attempt failures, retry with named field. See G3.1 in `references/anti-patterns.md`.
- **SP types + CTA reasons + Activity types** — all org-specific picklists. Pull once per session, cache.
- Full procedure in `references/org-discovery.md`.

### 3. The two-step prepare + create pattern (canonical for writes)
For BOTH CTAs and Success Plans:
1. `mode='prepare_*'` → top-level type options
2. (CTAs) `mode='prepare_*'` with `type_id` → dependent picklists (status, priority, reason, playbook)
3. `mode='create_*'` with all resolved GSIDs

Same pattern for `manage_cockpit_actions` and `manage_success_plan_actions`. Encoded in `references/write-path-patterns.md`. Total cost per Take Action artifact set: ~8 MCP calls, ~5-8s wall-clock.

### 4. Use HTML formatting in rich-text fields
Plain-text `\n` newlines render as a single blob in Gainsight rich-text fields. **Always use HTML:** `<p>`, `<ul>`, `<li>`, `<ol>`, `<strong>`, `<br>`. Applies to CTA comments, Task descriptions, Timeline activity content, SP info fields. Filed as G3.9. See `references/write-path-patterns.md` for ready-to-use HTML templates.

### 5. Query payload guards (token budget)
- **`fetch_cta_list`** — MANDATORY `DueDate GTE <today-90d>` filter + `page_size: 25`. Without it, you get 58k+ characters back. The `select=` parameter is IGNORED — full records always.
- **`fetch_timeline_activity_list`** — soft-fail expected (returns generic error intermittently). Note in reconciliation, don't block the run.
- **`get_object_metadata`** — call ONCE per session per object. Responses are 100-183k characters. Cache in conversation context.
- All payload guards documented in `references/anti-patterns.md`.

## Anti-patterns (top 5; full list in references/anti-patterns.md)

| Avoid | Why |
|---|---|
| Calling `fetch_cta_list` without a date filter | Blows token budget — large accounts can return 58k+ characters |
| Assuming any team-member or tier field name is universal | Custom field names are bespoke per org. Only Staircase's standard `Owner` field is universal. Discover first. |
| Creating a new CTA when an existing open CTA covers the same topic | Spam. UPDATE the existing one instead. |
| Passing `entity_type=RELATIONSHIP` + `relationship_id` to `create_timeline_activity` | Rejected even with valid IDs. G3.6. Workaround: company-scoped + `cta_id` linking. |
| Posting plain-text `\n`-delimited content to rich-text fields | Renders as a wall of text. Use HTML. G3.9. |

## Reference library

| File | When to read |
|---|---|
| `references/tool-inventory.md` | Before calling any tool you haven't recently — full payload shapes, return shapes, gotchas per tool |
| `references/write-path-patterns.md` | Before any CTA / Task / Timeline / Success Plan write — canonical recipes with HTML templates |
| `references/org-discovery.md` | First call per new org. Discovers segmentation, team-member field, required custom fields, SP types, CTA reasons. Consumed by `gainsight-mcp-setup`. |
| `references/anti-patterns.md` | When something fails unexpectedly OR before unfamiliar operations. G3.1-G3.11 gotchas + workarounds + known gaps. |

## Org-discovery requirements

Before any production use against a new Gainsight org, the plugin (via `gainsight-mcp-setup` for first-time setup OR a manual discovery step for power users) must establish:

1. **Segmentation field on `company`** — call `get_object_metadata("company")`, look for picklist fields that smell like tier/segment, then `get_picklist_values`. Common names: `Tier`, `Segment`, or an org-bespoke variant. Values: typically `High Touch / Mid Touch / Tech Touch` or `Enterprise / Strategic / Scale`. Org-bespoke.
2. **Team-member assignment field on `company`** — same metadata call. Staircase's standard `Owner` field is universal. Custom team-member fields are bespoke per org — common names include `CSM`, `Account Manager`, `Renewal Owner`, `Account Owner`, or an org-bespoke variant. Discover; do not assume.
3. **Required custom fields on `activity_timeline`** — first write attempt may fail with `"Missing required custom fields: 'X'"`. The error message names the field + allowed values, so retry-with-correction works. Document the requirement for the session.
4. **SP types** — `manage_success_plan_actions(mode='prepare_sp')`. Orgs commonly have 5-25 types including product-specific or motion-specific variants. Cache.
5. **CTA reasons + types + statuses + priorities + playbooks** — pulled via `manage_cockpit_actions(mode='prepare_cta')` (top-level then per-type). Cache.

Full procedure in `references/org-discovery.md`.

## Cowork UX notes

These skills are optimized for Claude Cowork users — CSMs, AMs, leaders who would feel overwhelmed by Code mechanics. When composing operations:
- One question at a time when gathering input (AskUserQuestion-style branching)
- Approval gate BEFORE any customer-visible write — surface the planned artifact, let user confirm or edit
- Never dump huge markdown walls in inline cards
- Where Code and Cowork would diverge, Cowork wins. Code retains full functionality through the same skills (markdown-rendered) but it is not the optimization target.

## When to use Gainsight CS vs Staircase vs both

| User question | Primary MCP | Secondary |
|---|---|---|
| ARR / renewal date / owner | Gainsight (authoritative) | Staircase ARR sometimes surfaces |
| Customer said recently / sentiment | Staircase | — |
| Open CTAs / Cockpit / Success Plans | Gainsight | — |
| What changed in the last 24 hours | Gainsight (time-bounded CTA/Timeline filter) | — |
| Strategic state / persistent signals | Staircase | Gainsight has synced booleans on Company |
| Play for this account | Staircase `analyze_account` | Gainsight context |
| Patterns across portfolio | Staircase pattern-detection | — |
| Daily / weekly cockpit | Both combined | — |
| Draft outreach / create CTA / log Timeline / update SP | Gainsight (write) | Staircase (context only) |

Full mapping + chain walkthrough: `../../_shared/mcp-cross-walk.md`.

## Cross-references

- **Cross-walk doc:** `../../_shared/mcp-cross-walk.md` — field-level Staircase ↔ Gainsight mapping, 5-Phase chain walked end-to-end, org-bespoke discovery split.
- **Staircase MCP foundation:** `../staircase-mcp-expert/` — paired with this skill; Staircase reads → Claude synthesizes → Gainsight writes is the canonical chain.
- **Output discipline:** `../../_shared/gainsight-output-best-practices.md` (v1.1) — writing principles, commitment discipline, classification framework, cleanup discipline. Apply to every customer-facing write.
- **User profile:** `~/.gainsight-mcp/user-profile.md` (created by `gainsight-mcp-setup`) — name, role, filter field, filter value. Sibling skills read this to apply role-appropriate defaults.
