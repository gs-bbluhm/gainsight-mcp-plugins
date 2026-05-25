# gainsight-mcp-plugins

Claude Code plugins for Customer Success teams that pair the **Staircase AI MCP** (communication intelligence) with the **Gainsight CS MCP** (CRM state and write paths).

Single-prompt workflows for things that used to take 30 minutes of manual context-gathering: book pulse, account workspace, post-call processing, executive renewal radar, cross-portfolio pattern hunting.

---

## Plugins in this repo

| Plugin | What it is | Skills |
|--------|------------|--------|
| **`gainsight-cs`** | Customer Success operations plugin. CSMs, AMs, CS leaders, CS Ops. | 13 core (3 foundation + 6 IC + 4 exec) + 4 experimental |

More plugins planned: gainsight-px (Product Experience), gainsight-staircase-cross-product workflows.

---

## Install

### Step 1 — Add this marketplace

In Claude Code:

```
/plugin marketplace add gs-bbluhm/gainsight-mcp-plugins
```

### Step 2 — Install the plugin

```
/plugin install gainsight-cs@gainsight-mcp-plugins
```

### Step 3 — Verify

```
/plugin list
```

You should see `gainsight-cs` in the output. The plugin's skills become available immediately — start with `gainsight-mcp-setup` for the one-time onboarding (role-adaptive, ~2 minutes), then any other skill works.

### Updates

When new versions ship, run:

```
/plugin update gainsight-cs
```

The plugin tracks the latest commit on `main`, so every push is a new version users can pull.

---

## Prerequisites — MCP servers

These plugins are useless without the underlying MCPs. You'll need both connected in your Claude client (Claude Desktop or Claude Code). The two MCPs install differently — Staircase AI is an official Anthropic connector; Gainsight CS is a custom connector that requires admin OAuth setup on your Gainsight tenant.

### Staircase AI MCP — official Anthropic connector

The Staircase AI MCP is published in Claude's connector directory as **"Gainsight (Staircase AI)"**. No CLI commands or config files required.

**Prerequisites:**
- A Staircase AI account
- MCP access enabled at the platform level by your Staircase admin

**Connect:**

1. Open Claude → **Settings → Connectors → Browse connectors**
2. Search for *Staircase* and choose the **Gainsight (Staircase AI)** connector
3. Click **Connect** and authenticate with Google or Microsoft using your Staircase AI email
4. Set tool permissions to "Always allow" if you want a seamless workflow
5. Open a new chat and confirm Staircase AI appears in the connectors list

Reference: [Connect Staircase AI to LLMs Using MCP](https://support.gainsight.com/Staircase_AI/Staircase_AI_Features/Connect_Staircase_AI_to_LLMs_Using_MCP) (Gainsight support).

### Gainsight CS MCP — custom connector (admin setup required)

The Gainsight CS MCP is not yet an official Anthropic connector. It must be added as a **custom connector** in Claude, and your Gainsight admin must configure OAuth on the tenant first.

**Prerequisites — your Gainsight admin needs to:**
- Enable MCP access on your tenant
- Configure OAuth with PKCE in Gainsight (Administration → User Management → Authentication → OAuth Applications)
- Add these two callback URLs to the OAuth application:
  - `https://claude.ai/api/mcp/auth_callback`
  - `https://claude.com/api/mcp/auth_callback`
- Provide you (or you yourself, if you're the admin) with the Client ID, Client Secret, and your tenant's MCP server URL

**Connect (after admin setup is complete):**

1. Open Claude → **Settings → Connectors → Add custom connector**
2. Enter a name (e.g., "Gainsight CS")
3. Enter the server URL:
   ```
   https://<your-domain>.gainsightcloud.com/v1/ds-mcp/mcp
   ```
4. Paste the Client ID and Client Secret from your admin
5. Click **Connect** — Claude redirects you to Gainsight to authenticate
6. Log in with your Gainsight credentials. Claude confirms the connection.

Full admin setup instructions: [Set Up Gainsight CS MCP Server Integration](https://support.gainsight.com/gainsight_nxt/AI_Assistants/MCP_Integration/Admin_Guide/Set_Up_Gainsight_CS_MCP_Server_Integration) (Gainsight support).

> The Gainsight CS MCP will eventually be published as an official Anthropic connector. Until then, the custom-connector path above is the supported install method.

### Optional connectors that integrate well

The plugin's meeting-processor + handoff skills pull additional context from these if they're connected:

- **Notion MCP** (meeting notes connector) — for Granola/Zoom/manual meeting transcripts
- **Gmail MCP** — for email drafting + thread context
- **Calendar MCP** — for meeting scheduling + EBR coordination
- **Zoom MCP** — for direct recording / transcript access

These are nice-to-haves, not required.

---

## Quick start after install

1. **Run setup once:** prompt Claude with *"run gainsight-mcp-setup"* — a 2-minute role-adaptive onboarding that discovers your org's bespoke fields (segmentation, team-member assignment) and writes a persistent user profile. After this, every skill auto-applies your filter automatically.

2. **Use natural language for any skill.** Describe what you want — Claude matches your prompt to the right skill via its description. You don't need to remember skill names. The example prompts below are what users actually type.

3. **Drill down through chains.** Most workflows compose: book pulse → drill into top account → draft stakeholder outreach → write CTA. Each step is approval-gated.

---

## How invocation works

Skills in this plugin auto-trigger when your prompt matches their description. You typically don't need to name them.

- **Natural language is the default.** *"Show me my book pulse"* or *"draft an outreach to Ellen"* will find the right skill.
- **You can invoke explicitly by name.** *"Run gainsight-meeting-processor on this transcript"* forces the skill to load.
- **Experimental skills don't auto-trigger.** They have `disable-model-invocation: true` set, so you have to invoke them by name (e.g., *"run staircase-at-risk-renewals"*) if you want them.

---

## Skills inventory

### Foundation — onboarding + reference (3 skills)

Read by every other skill. The setup skill is the only one you typically invoke directly.

| Skill | What it does | Example prompt |
|-------|--------------|----------------|
| **`gainsight-mcp-setup`** | One-time role-adaptive onboarding. Discovers your org's team-member field, segmentation field, and required custom fields. Writes a persistent user profile so every other skill auto-applies your filter. | *"Run gainsight-mcp-setup"* |
| **`staircase-mcp-expert`** | Canonical reference for Staircase MCP query patterns, field catalog, anti-patterns, analyst data models. Other skills load this on demand. | Not invoked directly. |
| **`gainsight-cs-mcp-expert`** | Canonical reference for Gainsight CS MCP tool inventory, write-path patterns (CTA / Task / Timeline / SP), org-discovery procedures, anti-patterns. Other skills load this on demand. | Not invoked directly. |

### Individual contributor (IC) — daily workflows (6 skills)

For CSMs, AMs, anyone owning or assigned to accounts. After running `gainsight-mcp-setup`, these skills auto-scope to your book.

| Skill | What it does | Example prompts |
|-------|--------------|-----------------|
| **`gainsight-meeting-processor`** | Post-call workflow. Takes a transcript or meeting notes (Notion, Zoom, Granola, Fireflies, Gong, paste). Drafts Gmail recap + Timeline activity + Risk CTA + Success Plan updates + action items + win quotes. Nothing posts without approval. | *"Process this meeting transcript: [paste]"* · *"Run the meeting processor on my last call with [account]"* · *"What should I log in Gainsight from this meeting?"* |
| **`gainsight-csm-book-pulse`** | Weekly book triage. Unified fan-out query for your accounts + 6-tier composite priority scoring + insight flags (Account Dark, No QBR, Personnel Changes). Top 10 ranked with a watch list. | *"Give me my book pulse"* · *"Where should I focus this week?"* · *"Show me my top 10 priority accounts"* |
| **`gainsight-account-workspace`** | Daily working session on one account. Loads CTAs + SPs + Timeline + Renewal Center + Staircase situational context. Proposes up to 6 next moves. Drafts updates, posts on approval. | *"Open the workspace for [account]"* · *"What should I do for [account] today?"* · *"Move [account] forward"* |
| **`gainsight-account-handoff-onboarding`** | Inheriting an account. Pulls the Staircase Handoff Analysis (11-section structured output) + builds a first-90-days onboarding plan + drafts intro email to stakeholders. One-time per account. | *"I just inherited [account] — onboard me"* · *"Build a handoff plan for [account]"* |
| **`gainsight-stakeholder-connect`** | Stakeholder alignment analysis + personalized outreach drafts. Uses Personnel Changes flag + Risk Analysis stakeholder section. Single-account or book-scope. | *"Draft outreach to [stakeholder] at [account]"* · *"Which of my accounts lost a key stakeholder recently?"* · *"Reconnect plan for [account]"* |
| **`gainsight-no-qbr-ebr-scheduler`** | Surfaces accounts flagged "No QBR" and drafts personalized EBR outreach anchored on each account's active themes. Quarterly cadence. | *"Schedule QBRs for accounts that haven't had one"* · *"Which accounts need an EBR?"* · *"Draft EBR outreach for [account]"* |

### Executive — portfolio strategic workflows (4 skills)

For CS leaders, CROs, VPs. Monthly to quarterly cadence. Tier-stratified, theme-aware, briefing-grade output.

| Skill | What it does | Example prompts |
|-------|--------------|-----------------|
| **`gainsight-exec-renewal-radar`** | Tier-stratified renewal intelligence across the 120-day renewal window. Per-tier ranked play list with risk + expansion classification + cross-account theme detection. | *"Show me my Strategic-tier renewal radar"* · *"What renewals are at risk in the next 120 days?"* · *"Per-tier renewal play list"* |
| **`gainsight-renewal-priority-planner`** | Move-the-needle renewals. Composite movability score (renewal proximity + ARR + risk + readiness + tier). Pulls full Risk + Expansion Analyses on top-15. | *"Plan my top 15 renewals"* · *"Where can I move the needle on renewals this quarter?"* |
| **`gainsight-exec-churn-retrospective`** | Quarterly churn review. Pattern themes across recent churns + per-account Churn Analysis + gap-finding for churns missing analysis. | *"Run the churn retrospective for last quarter"* · *"What themes are driving churn?"* · *"Which churned accounts are we missing analysis on?"* |
| **`gainsight-exec-pattern-hunter`** | Cross-portfolio thematic intelligence. Groups 15 accounts by emergent themes (friction signals, win narratives, expansion language, executive engagement). Customer quotes with evidence IDs. | *"Find patterns across my portfolio about [theme]"* · *"What are customers saying about [topic]?"* · *"Pattern hunt for friction signals across enterprise accounts"* |

### Experimental — opt-in only (4 skills)

These live in `_experimental/` with `disable-model-invocation: true`. They don't auto-trigger. Invoke explicitly by name if you want them.

| Skill | What it does | Why it's experimental |
|-------|--------------|------------------------|
| **`gainsight-daily-cockpit`** | CSM daily focus surface — Gainsight new/open CTAs + Staircase persistent signals + per-account drill-downs. | Overlaps with `gainsight-account-workspace`; consolidation candidate. |
| **`staircase-at-risk-renewals`** | Cross-portfolio at-risk renewal report with health, sentiment, risk evidence per account. | Subsumed by `gainsight-exec-renewal-radar` in most flows. Functional, kept to avoid skill duplication in auto-invocation. |
| **`staircase-expansion-scout`** | Cross-portfolio expansion scout — accounts with active expansion signals + readiness scoring. | Overlaps with `gainsight-exec-renewal-radar`. |
| **`staircase-reference-finder`** | Find customer reference candidates for a target account or use case. | Partial; waiting on a portfolio-similarity primitive in the Staircase MCP. |

---

## What this enables (concrete examples)

| Prompt | What happens |
|--------|--------------|
| *"Process this Granola transcript: [paste]"* | `gainsight-meeting-processor` drafts Gmail recap + Timeline activity + Risk CTA + Success Plan updates + action items + win quotes. Nothing posts without approval. |
| *"Give me my book pulse"* | `gainsight-csm-book-pulse` runs a unified fan-out + 6-tier composite priority scoring + insight flags. Top 10 ranked with watch list. |
| *"Show me at-risk renewals across Strategic tier in the next 120 days"* | `gainsight-exec-renewal-radar` runs the tier-stratified view with per-account Risk × Expansion merge classification. |
| *"Find patterns across my portfolio about [theme]"* | `gainsight-exec-pattern-hunter` runs a 15-account intentional fan-out for cross-portfolio thematic intelligence with evidence IDs. |
| *"Draft outreach to [stakeholder] anchored on the merge findings"* | `gainsight-stakeholder-connect` produces a personalized email draft with tone discipline (specifics over generalities, customer-focused). Approval-gated. |

---

## Architecture (briefly)

The plugin follows a three-tier model:

- **Foundation skills** — MCP-mechanics knowledge that other skills read on demand (`staircase-mcp-expert`, `gainsight-cs-mcp-expert`, `gainsight-mcp-setup`)
- **IC skills** — individual contributor workflows for CSMs / AMs / anyone with accounts assigned via a team-member field
- **Exec skills** — portfolio strategic workflows for CS leaders / CROs / VPs
- **Experimental** — usable but not production-grade; live in `_experimental/` with auto-invocation disabled

Each workflow skill is described at ~200 chars in its frontmatter (Claude's discovery surface), with a `## Discovery` section in the body for auto-trigger phrases + validation history. References to dense MCP mechanics live in foundation skills and load on demand.

For the field-level mapping between Staircase and Gainsight CS, the canonical chain (Staircase reads → Claude synthesizes → Gainsight writes), and the decision matrix on which MCP owns which question, see [`plugins/gainsight-cs/_shared/mcp-cross-walk.md`](./plugins/gainsight-cs/_shared/mcp-cross-walk.md).

---

## Repository layout

```
gainsight-mcp-plugins/
├── .claude-plugin/
│   └── marketplace.json          ← Marketplace manifest
├── plugins/
│   └── gainsight-cs/             ← The plugin
│       ├── .claude-plugin/plugin.json
│       ├── skills/
│       │   ├── gainsight-cs-mcp-expert/
│       │   ├── staircase-mcp-expert/
│       │   ├── gainsight-mcp-setup/
│       │   ├── gainsight-meeting-processor/
│       │   ├── gainsight-csm-book-pulse/
│       │   ├── gainsight-account-workspace/
│       │   ├── gainsight-account-handoff-onboarding/
│       │   ├── gainsight-stakeholder-connect/
│       │   ├── gainsight-no-qbr-ebr-scheduler/
│       │   ├── gainsight-exec-renewal-radar/
│       │   ├── gainsight-renewal-priority-planner/
│       │   ├── gainsight-exec-churn-retrospective/
│       │   ├── gainsight-exec-pattern-hunter/
│       │   └── _experimental/    ← 5 skills with model-invocation disabled
│       ├── _shared/
│       │   ├── gainsight-output-best-practices.md
│       │   └── mcp-cross-walk.md
│       └── README.md
├── README.md                     ← This file
├── LICENSE                       ← MIT
└── .gitignore
```

---

## Support and contributions

- **Issues:** open a GitHub issue on this repo
- **Questions:** reach out to Brady Bluhm ([bbluhm@gainsight.com](mailto:bbluhm@gainsight.com))
- **Contributions:** PRs welcome — please open an issue first to discuss the change

---

## License

MIT — see [LICENSE](./LICENSE). Use, fork, modify, distribute freely.

---

## About

Built and maintained by [Brady Bluhm](https://github.com/gs-bbluhm) (bbluhm@gainsight.com), Senior PM at Gainsight (Staircase AI). The plugin started as personal CS-tooling experiments in May 2026 and was opened to the public ahead of Pulse 2026.
