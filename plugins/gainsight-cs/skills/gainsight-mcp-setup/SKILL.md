---
name: gainsight-mcp-setup
description: First-time setup. Asks who you are and what role you play, discovers your Gainsight org's bespoke fields (segmentation, team-member assignment, required custom fields, SP types), writes a persistent user profile, then runs a short role-tailored practice round so you immediately feel the unlock. Run this once per user per org. Other skills read the profile to auto-apply your filter — no more "filter for CSM = me" plumbing on every ask.
user_type: foundation
allowed-tools: mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__resolve_customer, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__resolve_user, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_object_metadata, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_picklist_values, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__get_activity_types_config, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__manage_cockpit_actions, mcp__88e9acda-6f39-4db2-a5df-89cfb4e1351d__manage_success_plan_actions, mcp__staircase-ai__ask, mcp__staircase-ai__staircase_account_lookup, mcp__staircase-ai__staircase_analyze_account, Read, Write, Edit
---

# Gainsight MCP Setup

## What this skill is for

The Gainsight CS + Staircase MCPs work, but every customer org names its fields differently. Without a one-time setup, every user has to repeat "filter for `CSM is <my name>`" on every ask. That's plumbing they shouldn't have to know.

This skill runs ONCE per user per org. It:
1. Asks who you are and what role you play
2. Discovers your org's bespoke fields (segmentation, team-member assignment, required custom fields, SP types)
3. Writes a persistent user profile
4. Runs a short role-tailored practice round so you feel the unlock immediately

After setup, every other skill reads the profile and applies your filter + role-aware defaults automatically.

## When to invoke

**Direct triggers:**
- "Help me set up the Gainsight MCPs"
- "I'm new to this plugin — what's the first thing I should do?"
- "Configure my filter / configure my role"
- "Why does every query make me re-type my CSM filter?"

**Auto-prompt triggers (from sibling skills):**
- Any IC-tier skill called when no user profile exists → "I don't see a user profile. Want to run `gainsight-mcp-setup` (2 minutes)?"

## Cowork UX priority

Every step is one question with clear options. AskUserQuestion-style branching at every decision point. No walls of text. The practice round at the end is interactive — user runs 2-3 worked examples and sees the unlock.

This skill is the canonical Cowork UX template for the plugin. Other skills should match its rhythm.

---

## The flow

### Step 1 — Identity

Ask:
- Your name? (full name as it appears in Gainsight / Staircase)
- Your work email?

Use `resolve_user(search_name)` against Gainsight to validate + get the user's GSID. If multiple matches, surface them with identity counts (Slack, Gong, Salesforce, Zendesk) and ask which is them.

### Step 2 — Role

Ask: "Which role best describes how you work with accounts?"

Options (AskUserQuestion):
- **Executive** — CS leader, CRO, VP. I work across the portfolio, not a specific book.
- **CSM** — I own / am assigned to a set of customer accounts. My job is health, adoption, retention.
- **AM** — Account Manager. Post-sale, retention + expansion focus. Often commercial-leaning.
- **Sales / AE** — Account Executive. I own accounts for new logos / renewals / expansion.
- **Admin** — CS Ops or Gainsight Admin. I work on schema, config, dashboards — not a personal book.
- **Other** — Tell me more about what you do.

Branch based on the answer.

### Step 3 — Branch: discover the user-filter field

#### Executive branch
- **Skip user-grain filter** — leaders work portfolio-wide.
- Optionally ask: "Do you want a default scope (e.g., a team or BU)?" — capture if yes.
- Move to Step 4.

#### CSM branch
- Read `../gainsight-cs-mcp-expert/references/org-discovery.md` (Section 2: team-member field discovery).
- Call `get_object_metadata("company")`.
- Scan for LOOKUP-to-gsuser fields + STRING name/email fields. Staircase's standard `Owner` field is universal across orgs. Custom team-member fields are bespoke per org — common names include `CSM`, `Account Manager`, `Renewal Owner`, `Account Owner`, `Primary_CSM__gc`, `CS_Lead__gc`, or an org-bespoke variant. Discover; do not assume.
- Surface 3-5 best candidates with one-line context each (e.g., "`CSM` (LOOKUP to user, 1200 accounts populated)").
- AskUserQuestion: "Which field captures your assignment?"
- Once chosen, capture the filter value:
  - For LOOKUP: user's GSID from Step 1
  - For STRING: user's name string
- Move to Step 4.

#### AM branch
- Same procedure as CSM branch, but the typical candidate field names differ. Look for: `Account_Manager__gc`, `AM`, `Account_Manager`, or org-bespoke variants.
- If both an AM field AND a CSM field exist, ask which captures THEIR assignment (some orgs have both).
- Move to Step 4.

#### Sales / AE branch
- Look for `Account_Owner__gc` (often SFDC-sync), `Opportunity_Owner__gc`, or sales-leaning custom fields.
- Capture filter values — may capture BOTH Account Owner + Opportunity Owner if relevant.
- Move to Step 4.

#### Admin branch
- Skip user-grain filter.
- Pivot to org-discovery practice — segmentation field, required custom fields, picklist audit.
- Move to Step 4.

#### Other branch
- Open-ended question: "Tell me how you relate to accounts in Gainsight."
- Surface all team-member-shaped fields from `get_object_metadata("company")`.
- Let user browse and pick. If none fit, capture role as-is and skip filter.

### Step 4 — Org discovery (everyone)

Run the rest of the org discovery from `../gainsight-cs-mcp-expert/references/org-discovery.md`:

1. **Segmentation field** — find the org's tier/segment field via `get_object_metadata("company")` + `get_picklist_values`. Surface candidates (`Tier`, `Segment`, `Customer_Tier__gc`, or org-bespoke variants). Let user pick.
2. **SP types** — call `manage_success_plan_actions(mode='prepare_sp')` and cache the type list.
3. **CTA types + reasons** — call `manage_cockpit_actions(mode='prepare_cta')` and cache.
4. **Activity types** — call `get_activity_types_config()` and cache. Surface any with required custom fields.
5. **Required custom fields on Timeline activities** — opportunistic; the first Timeline write attempt may fail and reveal them. Capture as discovered.

### Step 5 — Write the user profile

Write to `~/.gainsight-mcp/user-profile.md` (location pending Cowork validation; fallback documented in plugin README).

Profile schema:
```yaml
user:
  name: <full name>
  email: <work email>
  user_id: <Gainsight user GSID>
  role: <Executive | CSM | AM | Sales | Admin | Other>
  role_description: <optional free-text if "Other">

filter:
  field: <name of chosen team-member field, OR null for Exec/Admin>
  value: <user's name string or GSID depending on field type, OR null>
  field_type: <STRING | LOOKUP | null>
  secondary_field: <optional, e.g., for Sales who need both Account Owner + Opportunity Owner>
  secondary_value: <...>

org:
  segmentation_field: <name>
  segmentation_values: [list]
  timeline_required_custom_fields: <object — discovered as encountered>
  sp_types: [list cached from prepare_sp]
  cta_types: [list cached from prepare_cta]
  activity_types: [list cached from get_activity_types_config]

setup:
  completed_at: <ISO timestamp>
  plugin_version: <semver>
```

### Step 6 — Practice round (role-tailored)

The unlock moment. Run 2-3 worked examples customized to role.

#### Executive practice
1. **Portfolio at-risk:** Pull `gainsight-exec-renewal-radar` for the next 120 days. Show the tier-stratified output.
2. **Cross-account theme:** Run `gainsight-exec-pattern-hunter` on the top 15 prioritized accounts. Surface 3 themes.
3. **Optional:** Open one account's drill-down to show how Exec → IC handoff works.

#### CSM practice
1. **Book pulse:** Pull `gainsight-csm-book-pulse` using the just-configured filter. Show the prioritized ranking. "These are your top 5 this week."
2. **Drill-down on top account:** "Open the top account → what's the full picture?" Run `gainsight-account-workspace` on account #1.
3. **Draft an outreach:** Use `gainsight-stakeholder-connect` to draft an email to the named stakeholder. Show approval gate.

#### AM practice
- Same as CSM but slant practice examples toward renewal / commercial threads. Use `gainsight-renewal-priority-planner` instead of (or in addition to) book-pulse.

#### Sales practice
- Run a filtered list of accounts by their Account Owner. Show renewal opportunities + expansion signals. Optionally drill into one account's expansion analysis.

#### Admin practice
- Show the org-discovery results in a structured surface: segmentation field + values, required custom fields, SP type catalog. "Here's your org's bespoke surface — sibling skills now know this." Optionally validate one skill against the discovered schema.

### Step 7 — Close out

Show user:
- ✅ Profile written to `<location>`
- ✅ <N> bespoke fields discovered for your org
- ✅ <N> practice examples run successfully
- Next: try any of `<role-appropriate skill list>`. They'll auto-apply your filter.

Offer to surface the role-appropriate skill set as a quick-start menu.

---

## Re-running setup

If user re-invokes this skill:
- Read existing profile
- Surface what's currently configured
- Ask: "What do you want to update?" (role, filter, re-discover org fields, all)
- Branch into the relevant sub-flow

## How sibling skills consume the profile

Every non-foundation skill SKILL.md should carry this block in its Foundation references section:

```markdown
## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/<relevant>.md` — query patterns / field catalog / anti-patterns
- `../gainsight-cs-mcp-expert/references/<relevant>.md` — write paths / org discovery / anti-patterns

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)
```

## Cross-references

- **Staircase MCP foundation:** `../staircase-mcp-expert/` — query mechanics
- **Gainsight CS MCP foundation:** `../gainsight-cs-mcp-expert/` — write mechanics + org-discovery procedure (consumed verbatim by this skill)
- **Output discipline:** `../../_shared/gainsight-output-best-practices.md` — for any artifacts written during practice round

## Learnings

See `.learnings.md` for accumulated validation, edge cases, and role-flow refinements per session.
