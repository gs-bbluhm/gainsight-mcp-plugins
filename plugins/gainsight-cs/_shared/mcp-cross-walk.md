# MCP Cross-Walk — Staircase ↔ Gainsight CS

How the two foundation skills work together. Field-level mapping, the canonical chain, decision matrix, and org-bespoke discovery responsibilities.

**Read this when:** you're composing a skill that touches both MCPs, you're not sure which one owns a question, or you need to translate a value from one to the other.

**Pairs with:** `skills/staircase-mcp-expert/` + `skills/gainsight-cs-mcp-expert/`.

---

## The canonical chain

Every IC + Exec skill in this plugin follows the same shape:

```
Staircase reads → Claude synthesizes → Gainsight reads enrichment → Gainsight writes (approval-gated)
```

The split is:
- **Staircase = communication intelligence.** What customers said, sentiment trends, engagement recency, named stakeholders, AI analyses (Risk / Expansion / Handoff / Churn / Renewal / Summary). 90-120 day window.
- **Gainsight CS = authoritative CRM state + write paths.** ARR, renewal date, owner assignments, CTAs, Success Plans, Timeline activities, picklists. Org-bespoke schema.
- **Claude = the bridge.** Pulls signals, applies methodology (6-tier composite, Risk × Expansion merge), drafts artifacts, presents approval gate, writes back.

## Decision matrix — which MCP owns this question

| Question shape | Primary MCP | Secondary | Why |
|----------------|-------------|-----------|-----|
| "What's the ARR / renewal date / owner of X?" | Gainsight | Staircase ARR may surface | Gainsight is authoritative for commercial state |
| "What did the customer say recently?" | Staircase | — | Communication intelligence lives only here |
| "What sentiment / engagement / risk signal is current?" | Staircase | — | Staircase computes these from comms |
| "What's open in Cockpit / Success Plans / Timeline?" | Gainsight | — | Gainsight owns workflow state |
| "What changed in the last 24 hours?" | Gainsight | — | Time-bounded CTA/Timeline filter |
| "Strategic state / persistent signals (Account Dark, No QBR, etc.)" | Staircase | Gainsight has synced booleans on Company | Staircase computes; Gainsight syncs them as fields |
| "Play for this single account" | Staircase `analyze_account` | Gainsight CTA + SP context | Staircase summarizes; Gainsight shows what's in motion |
| "Patterns across portfolio / themes" | Staircase pattern-detection | — | 15-account intentional fan-out is unique to Staircase |
| "Daily / weekly cockpit for a CSM book" | Both combined | — | Staircase = signals, Gainsight = open work |
| "Draft outreach / create CTA / log Timeline / update SP" | Gainsight (write) | Staircase (context only) | All write paths land in Gainsight |
| "Score / rank / prioritize accounts" | Both — Claude composes the score | — | Neither MCP returns a composite; methodology lives in Claude |

## Field-level mapping

The most-used signals exist in both systems with different names. Gainsight has many Staircase signals **synced onto the Company object** — useful when one MCP is unreachable or when you want a single-pull view.

### Account header

| Concept | Staircase | Gainsight | Notes |
|---------|-----------|-----------|-------|
| Account name | `name` | `company.Name` | Resolve via `staircase_account_lookup` and `resolve_customer` |
| Account ID | `account_id` (integer) | `company.Gsid` (36-char string) | **Different shapes** — keep both in context |
| ARR | sometimes returned | `company.Arr` and/or a custom ARR field (e.g., `ARR__gc`) | Gainsight is authoritative; the custom override field name is org-bespoke |
| Renewal date | sometimes returned | `company.RenewalDate` | Gainsight authoritative |
| Owner / Team Member | `Owner` (standard ST) | `company.<team-member-field>` (org-bespoke) | **Always discover the team-member field per org via `get_object_metadata`.** Standard Staircase `Owner` is universal; everything else (CSM, Account Manager, Renewal Owner, or any org-bespoke variant) must be discovered. |
| Tier / Segment | not native | `company.<segmentation-field>` (org-bespoke) | Common names include `Tier`, `Segment`, `touch_model__gc`, but each org names this differently. Discover via `get_object_metadata` + `get_picklist_values`. |

### Health + sentiment

| Concept | Staircase | Gainsight |
|---------|-----------|-----------|
| Overall health | computed from comms | `Staircase_Overall_Health_Score__gc` (synced) + `Staircase_Overall_Health_Score_Label__gc` |
| Engagement recency | `last_engagement_date` | `Staircase_Last_Engagement__gc` (synced) |
| Last reach-out | `last_reachout_date` | `Staircase_Last_ReachOut__gc` (synced) |
| Sentiment trend | computed | `CurrentScore` + per-Timeline sentiment R/Y/G |

### Risk + expansion signals

| Concept | Staircase | Gainsight |
|---------|-----------|-----------|
| Risk level (1-5) | `risk_level` | not natively (read via Staircase) |
| Expansion readiness (1-5) | `expansion_readiness_level` | not natively |
| Account Dark | `is_account_dark` insight | `Staircase_Account_Dark__gc` (synced boolean) |
| No QBR | `is_no_qbr` insight | `Staircase_No_QBR__gc` (synced) |
| No Renewal Discussion | insight | `Staircase_No_Renewal_Discussion__gc` (synced) |
| No Meetings with Account | insight | `Staircase_No_Meetings_with_Account__gc` (synced) |
| AI Renewal narrative | from `analyze_account` | `Staircase_AI_Renewal_Analysis__gc` (RICHTEXTAREA, synced) |
| Most recent flagged risk | from analysis | `Date_of_Most_Recent_Flagged_Risk__gc` |

**The pattern:** Staircase computes the signal; Gainsight syncs many of them as queryable Company fields. For cross-account list filters, the synced Gainsight booleans are often faster than running 15 Staircase analyze_account calls. For drill-down narrative, go to Staircase.

### Stakeholders + activity

| Concept | Staircase | Gainsight |
|---------|-----------|-----------|
| Named stakeholders + sentiment | `analyze_account` (Risk / Expansion / Handoff) | `company_person`, `person` |
| Advocate / detractor status | derived from sentiment evidence | `person.Advocacy_Tier__gc` |
| Recent communications | `staircase_query` evidence IDs | `activity_timeline` (with caveats — see anti-patterns) |
| NPS response | not native | `survey_participant` (response text returns 500 in some configurations) |

### Work in flight

| Concept | Where it lives | Tool |
|---------|----------------|------|
| Open CTAs | Gainsight only | `fetch_cta_list` (with MANDATORY DueDate filter) |
| Success Plans | Gainsight only | `fetch_success_plan_list` |
| Tasks under CTAs | Gainsight only | `run_query` on `cs_task` |
| Timeline activities | Gainsight only | `fetch_timeline_activity_list` (soft-fail expected) |
| Renewal opportunities | Gainsight | `gs_opportunity` |
| Forecasted revenue | Gainsight | `gs_company_forecast` |

## The 5-Phase chain walked through

A generic walkthrough for the question: *"What should this CSM work on this week, and what action should they take on their top-priority account?"*

### Phase 1 — List Query

**Staircase:** unified fan-out for the CSM's book.

```
staircase_query("List the accounts where the <team-member-field> is <CSM Name>. For each include name, ARR, renewal date, health, sentiment, engagement, last engagement, last reach-out, risk level, expansion readiness, and Account Dark / No QBR / No Reach Out / Personnel Changes flags.")
→ N accounts in one call
```

`<team-member-field>` is the org-bespoke field name discovered via `gainsight-mcp-setup` and stored in the user profile. The standard Staircase `Owner` field works universally; a custom Gainsight field (CSM / Account Manager / etc.) is more commonly used when the user wants Gainsight-assignment scoping.

### Phase 2 — Prioritize

**Claude:** apply the 6-tier composite scoring (renewal urgency + engagement staleness + commercial value + health/sentiment + expansion + acute events + support intensity) with risk-weighted readiness skepticism on save-into-expansion candidates.

### Phase 3 — Context Gathering

**Staircase:** drill-down on the top-ranked account.

```
staircase_account_lookup("<Account Name>") → account_id
staircase_analyze_account(account_id, "Full Risk Analysis: drivers, evidence, stakeholders...")
staircase_analyze_account(account_id, "Full Expansion Analysis: opportunities, champions, signals...")
```

**Claude:** Risk × Expansion merge with recency weighting → classify subtype (Save-then-Expand / Expansion-as-Save / Skeptical Read).

### Phase 4 — Action Planning + Prep

**Gainsight:** check existing artifacts before composing any write.

```
resolve_customer("<Account Name>") → company_gsid
fetch_cta_list(CompanyId=company_gsid, DueDate=next 60d)
→ check if an existing open CTA already covers this risk/opportunity
run_query(cs_task, CTAId=existing_cta_gsid) → check existing task coverage
```

**Claude:** apply the reuse-vs-create discipline. If an existing artifact covers the same motion, UPDATE it rather than creating a duplicate.

### Phase 5 — Take Action

**Gainsight (approval-gated):** follow the two-step prepare pattern.

```
manage_cockpit_actions(mode='prepare_cta') → type options
manage_cockpit_actions(mode='prepare_cta', type_id=<chosen>) → status/priority/reason/playbook options
[APPROVAL GATE — present payload to user, confirm before writing]
manage_cockpit_actions(mode='create_cta', ...) → CTA gsid returned
create_timeline_activity(linked to CTA, with org-required custom fields set) → activity gsid returned
```

## Org-bespoke discovery — split between MCPs

Neither MCP returns universal schema. Discovery responsibilities split:

| Discovery task | Owner | How |
|----------------|-------|-----|
| Team-member assignment field (CSM / Owner / Account Manager / org-bespoke) | **Gainsight** | `get_object_metadata("company")` → pick the picklist or lookup field that scopes accounts to users |
| Segmentation field (Tier / Segment / touch model / org-bespoke) | **Gainsight** | `get_object_metadata("company")` + `get_picklist_values` |
| Required custom fields on activity_timeline | **Gainsight** | First-write failure error message names the field + allowed values |
| SP types (org-bespoke list) | **Gainsight** | `manage_success_plan_actions(mode='prepare_sp')` |
| CTA reasons / types / statuses / priorities / playbooks | **Gainsight** | `manage_cockpit_actions(mode='prepare_cta')` |
| Account-name fuzzy match | **Staircase** | `staircase_account_lookup` (high vs low confidence) |
| Active stakeholders + role + sentiment | **Staircase** | `analyze_account` Risk / Expansion / Handoff |
| Org's competitor list | **Gainsight org profile** | Not currently queryable via MCP — org profile entries don't yet expose as a filter dimension |

The user profile (`~/.gainsight-mcp/user-profile.md` from `gainsight-mcp-setup`) caches the bespoke field names + filter values so sibling skills don't re-discover every session.

## Cross-skill chain patterns

Composable chains the plugin supports:

| Chain | Use case |
|-------|----------|
| `gainsight-csm-book-pulse` → drill-down via Risk × Expansion merge → `gainsight-stakeholder-connect` → Gainsight CTA write | Weekly book triage → top-account action |
| `gainsight-exec-renewal-radar` → per-account `analyze_account` → optional `gainsight-renewal-priority-planner` | Tier-stratified leadership renewal view → per-account deep-dive |
| `gainsight-meeting-processor` → Timeline + CTA + SP fan-out | Post-call workflow |
| `gainsight-account-handoff-onboarding` → 11-section Handoff Analysis → SP creation | New CSM inheriting an account |
| `gainsight-exec-pattern-hunter` → 15-account intentional fan-out → per-account drill-downs | Cross-portfolio thematic intelligence |

## Anti-patterns (cross-MCP)

- **Don't run 15 Staircase per-account analyses when you only need ARR + renewal date.** Use Gainsight `run_query` on `company` instead — same data, cheaper, no 15-cap.
- **Don't pull Gainsight Timeline as your context source.** Use Staircase `analyze_account` for narrative. Gainsight Timeline is the WRITE target, not the primary read source (and `fetch_timeline_activity_list` soft-fails intermittently).
- **Don't write to Gainsight without the reuse check.** Existing CTAs covering the same risk should be UPDATED, not duplicated.
- **Don't assume any field name is universal.** The standard Staircase `Owner` field is universal; everything else (team-member assignment, segmentation, custom fields) is org-bespoke. Always discover via `get_object_metadata`.
- **Don't compose OR queries in Staircase.** Decompose into single-dimension queries and intersect client-side.

## Cross-references

- `skills/staircase-mcp-expert/` — full Staircase MCP foundation (SKILL.md + 4 references)
- `skills/gainsight-cs-mcp-expert/` — full Gainsight CS MCP foundation (SKILL.md + 4 references)
- `_shared/gainsight-output-best-practices.md` — write discipline for any Gainsight write
- `skills/gainsight-mcp-setup/` — one-time onboarding that runs the org-bespoke discovery + writes the user profile
