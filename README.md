# gainsight-mcp-plugins

**AI-native workflows for Customer Success teams**, built on top of the Staircase AI and Gainsight CS MCPs.

This is a library of one-prompt workflows that handle the heavy lifting CSMs and CS leaders do every week: triaging your book, prepping for a meeting, drafting stakeholder outreach, running a renewal radar across your portfolio. Work that takes 30 minutes of clicking through tabs becomes a single conversation.

## Why this exists

CSMs with 20–30 accounts spend most of their week reactive — opening Gainsight to check CTAs, opening Staircase to read recent customer signals, switching to email to draft outreach, back to Gainsight to log a Timeline activity. By the time you've gathered context on one account, half the hour is gone.

When Claude has both MCPs connected, the gathering happens for you. You ask *"what should I work on this week?"* and you get a ranked book pulse with the specific next move per account, drafted email outreach, and ready-to-post CTAs — all approval-gated. Nothing posts to Gainsight without your sign-off.

## What you can do with it

A few examples of prompts that work after install:

- *"Give me my book pulse for this week"* → ranked list of accounts that need attention with the specific lever to pull on each
- *"Process this meeting transcript"* → drafted Gmail recap + Timeline activity + Risk CTA + Success Plan updates + action items, ready for one-click approval
- *"I just inherited [account] — onboard me"* → first-90-days plan built from the Staircase Handoff Analysis, stakeholder intros, ready-to-create Onboarding Success Plan
- *"Show me Strategic-tier renewals at risk in the next 120 days"* → tier-stratified renewal radar with cross-account themes, per-account risk and expansion classification
- *"Draft outreach to [stakeholder] at [account]"* → personalized email anchored on what Staircase actually knows about the relationship, in your voice
- *"Find patterns across my portfolio about [theme]"* → cross-account thematic intelligence with customer quotes and evidence

## Who it's for

- **CSMs and Account Managers** — daily and weekly workflows, post-call processing, stakeholder outreach, EBR prep
- **CS leaders, CROs, VPs** — portfolio strategic views, renewal radar, churn retrospectives, cross-account pattern detection
- **CS Operations** — book-shaping, methodology validation, output-quality enforcement

The plugin auto-adapts to your role. You run `gainsight-mcp-setup` once at install and the skills scope to what you do.

---

## Get started

**1. Install the plugin** (in Claude Code):

```
/plugin marketplace add gs-bbluhm/gainsight-mcp-plugins
/plugin install gainsight-cs@gainsight-mcp-plugins
```

**2. Connect the MCPs** if you haven't already — see [Connect the MCPs](#connect-the-mcps) below.

**3. Run setup once.** In Claude, type: *"Run gainsight-mcp-setup"*. It walks you through a 2-minute onboarding that adapts to your role and discovers your org's specific Gainsight fields. After this, every skill automatically scopes to your work.

**4. Try something.** Use any of the example prompts above. The right skill loads automatically — you don't need to remember skill names. Describe what you want in your own words.

For updates as new versions ship: `/plugin update gainsight-cs`.

---

## Connect the MCPs

The plugin needs both MCPs connected in your Claude client (Claude Desktop or Claude Code). They install differently.

### Staircase AI MCP — one-click connector

Published in Claude's connector directory as **"Gainsight (Staircase AI)"**.

1. Open Claude → **Settings → Connectors → Browse connectors**
2. Search *Staircase* and pick **Gainsight (Staircase AI)**
3. Click **Connect** and sign in with your Staircase AI email (via Google or Microsoft)

That's it. Full instructions: [Gainsight support — Connect Staircase AI to LLMs Using MCP](https://support.gainsight.com/Staircase_AI/Staircase_AI_Features/Connect_Staircase_AI_to_LLMs_Using_MCP).

> If you don't see the connector, your Staircase admin may need to enable MCP access for your org first.

### Gainsight CS MCP — custom connector (admin sets up once)

Not yet in Claude's official connector directory. Your Gainsight admin sets it up once for the tenant; then you connect it as a custom connector.

**Step 1 (admin, one time):** Your Gainsight admin follows the [Set Up Gainsight CS MCP Server Integration](https://support.gainsight.com/gainsight_nxt/AI_Assistants/MCP_Integration/Admin_Guide/Set_Up_Gainsight_CS_MCP_Server_Integration) guide. They configure OAuth and hand you three things: a Client ID, a Client Secret, and your tenant's MCP server URL.

**Step 2 (you):** Add it as a custom connector in Claude.

1. Open Claude → **Settings → Connectors → Add custom connector**
2. Name it (e.g., "Gainsight CS")
3. Paste the server URL: `https://<your-domain>.gainsightcloud.com/v1/ds-mcp/mcp`
4. Paste the Client ID and Client Secret from your admin
5. Click **Connect** and sign in with your Gainsight credentials

> Gainsight CS will eventually become an official Anthropic connector. Until then, this custom-connector path is the supported method.

### Optional connectors that enhance the experience

None are required, but the plugin's meeting-processor and outreach skills get more powerful with any of these connected:

- **[Microsoft 365 Connector for Claude](https://support.claude.com/en/articles/12542951-enable-and-use-the-microsoft-365-connector)** — official Anthropic connector covering Outlook (email + calendar), Teams, SharePoint, OneDrive. Free on all Claude plans.
- **Gmail + Google Calendar connectors** — for users in Google Workspace instead of Microsoft 365.
- **Notion connector** — surfaces Granola, Zoom, and Notion-captured meeting notes for the meeting-processor skill.
- **Zoom connector** — direct access to recordings and transcripts.

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
