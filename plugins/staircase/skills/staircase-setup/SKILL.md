---
name: staircase-setup
description: "Optional first-run welcome for the Staircase plugin. Confirms the Staircase MCP is connected, works out which accounts are the user's by computing which role fields they hold in this org (asking only when that is ambiguous), learns the org's custom setup, runs a short role-tailored practice round, and caches a profile every other skill reuses. Triggers on \"set up Staircase\", \"get started\", \"configure my scope\", \"which accounts are mine\", or when a skill finds no profile."
user_type: foundation
allowed-tools: Read, Write, Edit
---

# Staircase Setup

## What this skill is for
Every Staircase skill already resolves scope on its first call (the first-call contract in `../staircase-mcp-expert/SKILL.md`, step 0). This skill runs that same contract as a friendly first-run experience: it shows the user how they appear in Staircase, confirms anything ambiguous, and lets them feel the payoff with one or two real results. Nothing here is required; a user can skip straight to any workflow skill.

Rhythm: one question per step, clear options, no walls of text.

## The flow

### Step 1: Connect
Call `staircase_report_metadata`.
- **It works:** note `current_user_id`, the role fields (every `customer.*` field whose `referencedEntity` is `user`), and the `lifecycle_event.type` options. Move on.
- **No Staircase tools, or an auth error:** stop and explain how to connect. In Claude (web, desktop, Cowork), add Staircase AI as a connector in claude.ai connector settings. In Claude Code, run `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`, then authenticate. Offer to continue once it's connected.

### Step 2: Show them how they appear in Staircase
Run the `scope.membership` recipe (`../staircase-mcp-expert/references/report-recipes.md`) for `current_user_id`. Show a small table: name, title, manager, and the account count under each role field that isn't zero.

Then decide scope:
| What membership shows | What to do |
|---|---|
| One role field with accounts | That's their book. Say so in one line: "You're the <field label> on N active accounts; I'll use those as your accounts." |
| Two or more role fields with accounts | Ask one question: "You show up as <field A> on N accounts and <field B> on M. Which should 'my accounts' mean?" Offer both plus "both." |
| No role fields, and people who report to them hold books | Team scope. "You don't carry a book, but N people on your team do. I'll default to your team's accounts." |
| No role fields, and no reports who hold books | Portfolio scope. "You don't carry a book, so I'll default to the whole portfolio." |

Never assume the owner field is the CSM. It varies by org.

### Step 3: Confirm the role (one question, pre-filled)
Infer a role from the title and the scope (CSM, AM, Sales, Leader, Ops). Ask: "Looks like you work as a <role>. Right?" with the inferred role first plus the others. The role only tunes defaults: the practice round and which skills to suggest.

### Step 4: Write the profile
Write `~/.staircase-mcp/user-profile.md` (create the folder if needed): YAML front matter plus a two-line human summary.

```yaml
user:
  name: <full name>
  user_id: <current_user_id>
  title: <title>
  role: <CSM | AM | Sales | Leader | Ops | Other>

scope:
  method: <book | team | portfolio>
  book_owner_field: <the chosen role field id, or null>
  user_id: <whose book: usually the user>
  team_manager_id: <the user's id when method = team, else null>
  filter: <a report condition for the user's slice of the portfolio, or null>
  revenue_field: <the slice's own revenue field id, or null for customer.revenue_converted>
  routing_role: <the role field a leader routes work by, when several carry books, else null>

org:
  role_fields: [<customer.* fields whose referencedEntity is user>]
  lifecycle_types: [{id: <option id>, label: <display label>}, ...]
  role_map:          # stakeholder role names per concept; filled the first time a skill needs it
    decision_maker: [<role names>]
    executive_sponsor: [<role names>]
    champion: [<role names>]
    departed: [<role names>]
  checked_at: <ISO timestamp>

defaults:
  window: "[Past3Months]"

setup:
  completed_at: <ISO timestamp>
  plugin: staircase
  plugin_version: <from .claude-plugin/plugin.json>
```

### Step 5: Practice round (one or two real results)
Use the scope just saved.
- **CSM or AM:** run `book.context`, rank it with the priority composite (`../staircase-mcp-expert/references/query-patterns.md`), and show the top five with the one reason each is on the list. Then, for the top account that has a recent churn-risk event, run the `lifecycle.evidence` chain and show what the customer actually said and what was promised on the call. That's the moment to land: Staircase shows the why, in their words.
- **Sales:** run `expansion.pipeline` for their accounts and show the high-confidence, heating opportunities with the decision maker and timeline.
- **Leader:** run `renewal.window` without a personal scope and show the renewals in the next 90 days that carry risk or haven't had a commercial discussion recently.
- **Manager (team scope):** run `team.rollup` and show each person's book size and at-risk revenue.
- **Ops:** run scalar COUNTs of Active accounts with a next QBR booked and with a `ChurnRisk` insight, to show cohort sizing. A near-zero QBR count is itself the finding: business reviews aren't being booked ahead or titled so Staircase can see them.

Render per `../staircase-app-design/`. Keep it to one or two results; the point is the felt unlock, not a full report.

### Step 6: Close out
Tell them the profile is saved and what scope it uses, then suggest two or three skills for their role:
- **CSM or AM:** `staircase-book-triage`, `staircase-meeting-prep`, `staircase-risk-check`, `staircase-follow-up-draft`, `staircase-renewal-watchlist`.
- **Sales:** `staircase-expansion-scout`, `staircase-meeting-prep`, `staircase-account-deep-dive`.
- **Leader or manager:** `staircase-risk-radar`, `staircase-team-manager`, `staircase-1on1-prep`, `staircase-renewal-watchlist`, `staircase-churn-review`, `staircase-voice-of-customer`.

## Re-running setup
Read the existing profile, show the current scope and role, and ask what to change (scope, role, or refresh the org setup). Re-run only the affected steps. Refresh the `org` block if metadata no longer lists a cached role field.

## Cross-references
- **The contract this skill runs:** `../staircase-mcp-expert/SKILL.md` (step 0) and `../staircase-mcp-expert/references/report-recipes.md` (`scope.membership`).
- **Rendering:** `../staircase-app-design/`.
- **Output discipline:** `../../_shared/staircase-output-best-practices.md`.
