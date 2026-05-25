---
name: gainsight-exec-renewal-radar
description: Tier-stratified exec renewal radar across a 120-day window. Scores accounts via 6-tier composite + save-into-expansion bonus, detects cross-account themes, produces per-tier brief.
user_type: exec
---

# Executive Renewal Radar

## Discovery

**Auto-trigger phrases:**
- "exec renewal radar"
- "tier-stratified renewal view"
- "renewals at risk across enterprise/strategic/scale"
- "120-day renewal radar"
- "leadership renewal briefing"
- "what should leadership focus on this quarter"

**Purpose:** A leadership-perspective renewal view ranked per tier, with cross-account theme detection and per-tier resource allocation recommendations. Sibling to `gainsight-csm-book-pulse` (CSM-grade) and `gainsight-renewal-priority-planner` — intentionally different audiences.

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Handoff, Expansion, Risk, Churn, Renewal, Summary)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

Tier-stratified, exec-grade view of the upcoming renewal-window-of-attention. Different audience from the CSM book pulse — exec output is briefing-grade, strategic, and surfaces org-wide patterns + resource allocation, NOT per-account action drafts.

---

## Audience and design intent

This is the **leadership skill** counterpart to `gainsight-csm-book-pulse`.

- **CSM book pulse** answers: *"Where do I, the CSM, spend my time this week?"* — operational, per-account, action-drafting.
- **Exec renewal radar** answers: *"Where should the CS leadership team allocate attention and resources this quarter?"* — strategic, cross-account, pattern-detecting.

Both skills use the same 6-tier composite methodology. The DIFFERENCE is the output design and the action class: exec output is briefing-grade and informs subsequent CSM-level actions.

---

## The 5-Phase Cross-Account Method (canonical pattern)

This skill follows the canonical architecture documented in `staircase-mcp-expert` Part 5.

| Phase | What happens | Exec-specific framing |
|---|---|---|
| **1. List Query** | Tier × renewal-window single-dim query | Filter by tier value + renewal-date-next-120d |
| **2. Prioritize** | 6-tier composite + save-into-expansion bonus | Same methodology as CSM, but ranked **per-tier** |
| **3. Context Gathering** | Cross-account theme detection across prioritized list | Patterns in risks, expansion threads, stakeholder shifts |
| **4. Action Planning** | Org-wide recommendations + per-tier resource allocation | NOT per-account drafts — strategic plays |
| **5. Take Action** | Briefing-grade output + optional handoff CTAs | Mostly briefing; minimal direct posting |

---

## Step 1: Pull tier × renewal-window lists (parallel)

### Step 0 (MANDATORY) — Discover the org's tier-equivalent field

**"Tier" is a concept, not a fixed field name.** Different orgs name it differently. **The skill must discover the field before querying.**

#### Common field names to probe (in order of likelihood):

| Field name candidates | Notes |
|---|---|
| `Tier` | Some Gainsight orgs use a literal Tier field |
| `Segment`, `CS_Segment__gc`, `PX_Segment__gc`, `Customer_Segmentation__gc` | **Most common in Gainsight orgs.** Multi-product orgs often have per-product Segment fields |
| `touch_model__gc` | Common touch-model field — values like "High Touch", "Mid-Touch", "Tech Touch" |
| `Account_Type__gc`, `Customer_Tier__gc`, `Engagement_Model__gc` | Variations |

#### Discovery procedure

```python
# 1. Pull company object metadata via Gainsight CS MCP
get_object_metadata(object_name="company",
                    context="What is the tier/segment field on company?")

# 2. Scan returned fields for tier-concept candidates (Tier, Segment, touch_model, etc.)

# 3. For the chosen field, get the actual picklist values
get_picklist_values(object_name="company", field_name="<discovered_field>")
   # → returns [{value: <GSID>, label: "High Touch (<10/CSM)"}, ...]

# 4. Use the LABEL values (not GSIDs) in subsequent Staircase queries
```

The conceptual frame: **"High-touch / Mid-touch / Low-touch (Tech-touch)."** Even when the field is named differently, the values usually map to that mental model.

---

### Step 1: Query per discovered tier value

For each picklist value discovered in Step 0:

```
staircase_query("List the accounts where <field-label> is '<value>'
   with renewal dates in the next <N> days. For each include name,
   ARR, renewal date, health score, risk level, expansion readiness
   level, sentiment score, engagement score, AND indicate whether
   currently flagged with Account Dark, No QBR, No Reach Out,
   Single Threaded with Stakeholder, Account Personnel Changes.")
```

**Use the unified book+flag fan-out pattern.**

**Alternate path (more robust for compound filters):** use Gainsight `run_query` to pull the tier-filtered + renewal-window list FIRST (deterministic), then call Staircase per-account for analyst-level depth.

### Anti-pattern: don't rely on Staircase pattern-matching arbitrary tier phrases

Don't ask Staircase for "Strategic tier" or "Enterprise tier" as if those are universal field values. Staircase pattern-matching against arbitrary tier phrases is unreliable. **Always discover the actual field + values via Gainsight first, then feed the real label values into Staircase.**

### Why this matters

> "The tier concept is universal, but the field name and the values vary by org. We see it called Tier, Segment, touch_model, Customer_Type, or Engagement_Model in different Gainsight instances. Multi-product orgs often have a Segment per product. The skill discovers the org's field at runtime — it doesn't assume 'Enterprise' exists. Conceptually, almost every org maps to high-touch / mid-touch / low-touch."

This is **the same insight as the standard `Owner` vs org-bespoke team-member fields teaching** — Staircase's `Owner` field is universal and consistent across orgs; everything else (CSM, Account Manager, Renewal Owner, Tier/Segment, Account Type) is CRM-synced and varies per org. Discover at runtime via `get_object_metadata`; never hardcode.

---

## Step 2: Apply 6-tier composite priority per tier

Same methodology as `gainsight-csm-book-pulse` (see `staircase-mcp-expert` Part 5):

- TIER_1 renewal urgency (×0.20)
- TIER_2 engagement health (×0.18)
- TIER_3 commercial value (×0.15)
- TIER_4 health + sentiment (×0.15)
- TIER_5 expansion + open items (×0.12)
- TIER_6 acute events (×0.10)
- TIER_7 support intensity (×0.10)
- **Save-into-expansion bonus +0.10** for Risk ≥3 AND Readiness ≥3

Rank within each tier separately — exec briefing surfaces top 5-10 per tier (not a single combined list).

---

## Step 3: Cross-account theme detection + Risk × Expansion Merge (per-account, mandatory for save-into-expansion candidates)

### 3A. Cross-account theme detection (exec-grade pattern)

After ranking, scan the prioritized list per tier for shared patterns:

```
staircase_query("Across <Tier> accounts renewing in the next 120 days,
   identify common themes in risk reasons, expansion opportunities, or
   stakeholder concerns. Group findings by theme and list the affected
   accounts under each.")
```

This phase is what makes the output EXEC-grade — patterns inform resource allocation (e.g., "5 of top 10 share AI governance concerns — coordinate legal response").

### 3B. Risk × Expansion Merge (MANDATORY for save-into-expansion candidates)

**Architectural finding:** Risk Analysis and Expansion Analysis are produced by INDEPENDENT analyst agents that DO NOT reference each other. Acting on either alone produces a distorted picture. The skill MUST run both AND merge.

For every account in the top 10 per tier that meets save-into-expansion criteria (Risk ≥3 AND Readiness ≥3):

1. Run Risk Analysis (focused, exclude expansion observations) — see canonical query in `gainsight-csm-book-pulse/SKILL.md` Step 4B.1
2. Run Expansion Analysis (focused, exclude risk observations) — see Step 4B.2
3. Apply the canonical Risk × Expansion Merge prompt to reconcile the two analyses
4. Classify the account: **Expansion-as-Save** / **Save-then-Expand** / **Skeptical Read**
5. Adjust the composite-bonus accordingly (full +0.10 for the first two; downgrade to +0.03 for Skeptical Read)

**Why the merge matters:** Risk Analyst and Expansion Analyst can characterize the same stakeholder differently — one may describe a person as a "detractor" while the other describes them as a "primary executive sponsor." The merge produces an honest, sequenced action plan instead of a naive "Risk 5 × Readiness 5 = aggressive expansion play" misread.

**Exec output framing:** Merge classification per top-tier account informs RESOURCE ALLOCATION:
- Expansion-as-Save accounts → CSM hours go into closing the expansion as the renewal play
- Save-then-Expand accounts → exec sponsor air-cover for the save phase, expansion deferred to post-renewal
- Skeptical Read accounts → defensive save only; do NOT chase expansion thread

**Theme types to surface:**
- Risk-reason themes: pricing pressure, integration friction, security/compliance gaps, exec sponsor churn
- Expansion themes: shared product interests, multi-BU expansion, AI/automation requests
- Stakeholder themes: champion-attrition clusters, single-threaded risk

---

## Step 4: Per-tier exec brief (the output)

### Output structure

```markdown
# Executive Renewal Radar — Next <N> Days · <Date>

## Portfolio at a glance

- <Strategic count> Strategic accounts renewing · $<total Strategic ARR>
- <Scale count> Scale accounts renewing · $<total Scale ARR>
- Save-into-expansion candidates org-wide: <count> ($<save-ARR>)
- Accounts at critical risk (health <30, Risk ≥4): <count>

---

## Strategic Tier — Top 10 (ranked by composite)

| # | Account | Score | Renewal | Health | ARR | Risk/RD | Theme | Headline |
|---|---|---|---|---|---|---|---|---|
| ... | | | | | | | | |

### Cross-account themes (Strategic)
- Theme A — <accounts affected>
- Theme B — <accounts affected>

### Exec recommended plays (Strategic)
1. <Org-wide play>
2. <Coordinated outreach where 3+ share a theme>
3. <Resource allocation recommendation>

---

## Scale Tier — Top 10

[Same structure]

---

## Enterprise Tier — Top 10

[Same structure, OR document gap if tier query returns empty]

---

## Cross-tier patterns

- <Themes that span tiers>
- <Reps / regions / products with concentration>

---

## Resource allocation recommendation (the executive ask)

- **CSM hours to allocate per tier this quarter:**
  - Strategic: <count> save-into-expansion plays × <hours each>
  - Scale: <count> bulk save / coordinated outreach
- **Exec sponsor pulls** (where CSMs need leadership air-cover):
  - <Account A — exec ask>
- **Coordinated comms motions:**
  - <Where 3+ accounts share a theme — issue org-wide enablement>
```

### Format adaptation

- **Cowork:** lead with portfolio-at-a-glance dashboard tile; per-tier expandable cards; theme + recommendation footer
- **Code:** full markdown to stdout + artifact at `executive-renewal-radar-<date>.md`

---

## Step 5: Optional close-out (approval-gated, briefing-mostly)

Exec output is briefing-grade. Direct posting is minimal:

- Optional: create top-tier renewal CTAs in Gainsight for the CSM team to action
- Optional: generate exec-talking-point packs per top-5 account for QBR / 1:1 prep
- Optional: trigger `gainsight-csm-book-pulse` for the affected CSMs to drill into per-account action

---

## Edge cases

| Situation | What to do |
|---|---|
| Tier value returns empty | Verify tier name via Gainsight `get_picklist_values` for Tier field. Document in artifact. |
| Tier list truncates mid-response | Narrow window (60-90 days), or request fewer fields, or ask for top-N explicitly |
| Account appears in multiple tier queries | De-duplicate; use the highest-priority tier classification |
| Risk Level field is null but renewal <30 days + RD ≥4 | Apply Risk-null fallback: +0.10 composite escalation |
| Renewal date already past | Differentiate in-flight (<30d past) from sync-stale (>30d past) — verify Gainsight Status field |
| Composite anomaly (health >75 + Risk ≥3) | Flag for investigation rather than auto-trust the ranking |

---

## Why this matters

> "The CSM book pulse asks 'where do I, as a CSM, spend my time?' The executive renewal radar asks 'where should the leadership team allocate attention this quarter?' Same composite methodology, different output design. The radar pulls the renewal window in a single query, detects shared themes across accounts (e.g., AI governance concerns clustering across multiple accounts), and recommends coordinated org-wide motions — not per-account drafts. That's the CSM-vs-Exec design intent of the plugin."

---

## Sources

- `staircase-mcp-expert` SKILL.md — canonical methodology
- `staircase-analyst-data-models.md` — per-account drill-down queries (Risk, Expansion)
- `gainsight-csm-book-pulse/SKILL.md` — sibling skill (CSM-grade counterpart)
- `gainsight-renewal-priority-planner/SKILL.md` — sibling skill (per-account composite movability)

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md` — the plugin-wide canonical reference. Core rules:

1. **User approval gate.** Present a short plan (goal + key strategic choices + specific external commitments). Get explicit user approval before any write.
2. **Commitment discipline.** Default to PROPOSAL language. Email-type Tasks carry a "Verify Before Sending" checklist.
3. **HTML formatting** in rich-text fields. Use `<p>`, `<ul>`, `<ol>`, `<strong>`, `<br>`.
4. **Teammate-facing, customer-focused content.** No internal classification labels (Save-then-Expand, Skeptical Read, Engaged Frustration, Recency tiebreaker, Composite classifications, etc.) in customer-facing surfaces.
5. **Evidence as readable references.** `Email (Person, date)` / `Meeting (date)`. No `comm_#####` IDs.
6. **Reuse-vs-create discipline.** Fetch existing CTAs and SPs first.
7. **Cleanup discipline.** Surface stagnant artifacts before creating new.
8. **Org-specific discovery.** Discover the org's tier-equivalent field (Tier / Segment / touch_model / etc.) via Gainsight metadata. Discover CTA Types / Statuses / Reasons via `prepare_*` calls. Never hardcode values.

### Skill-specific emphasis

Step 5 Take Action is **BRIEFING-grade by default**. The exec output is a markdown brief, not a Gainsight write. Auto-write only when the exec explicitly approves handoff CTAs for the CSM team to action. When creating those CTAs, apply the full 8 rules + approval gate. Tier-stratified output (per-tier ranked plays) is part of the briefing; don't push those rankings into Gainsight unless the exec asks for it.

---

## Learnings

See `.learnings.md`.
