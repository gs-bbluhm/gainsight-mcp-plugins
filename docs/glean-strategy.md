# Staircase on Glean: paths to value for CSMs and CS leaders

*Draft 2026-09-30. Sources: the `staircase` and `gainsight-cs` plugins in this repo, and Glean's public docs and blog (linked at the end). Glean facts come from public pages, not a Glean tenant. Anything marked **[verify]** needs a sandbox test before we commit to it.*

## TLDR

1. **Fastest path (weeks): register the Staircase MCP in Glean as a remote MCP action pack, and ship our skills into Glean Skills.** Glean supports the open Agent Skills standard and imports from GitHub, and our plugin repo is already `SKILL.md`. Skills are in private beta, so we have to confirm access.
2. **The tools alone will underperform in Glean.** Our intelligence lives in the skills: the first-call contract, report recipes, the signal-to-evidence-to-quote chain. Glean's own MCP guidance says to keep servers small and single-purpose because tool selection degrades. So we should also move the recipes server-side, as outcome-shaped tools and `staircase_get_playbook` topics. That helps every host, not only Glean.
3. **Scheduled Glean Agents are the best fit for the CSM and leader rhythm.** Monday book triage goes to a CSM's Slack DM. The weekly risk radar goes to a leader's channel or inbox.
4. **Later, and only as a pilot: MCP Apps (our widgets inside Glean chat) and pushing Staircase "account brief" documents into Glean's index.**
5. **The positioning problem to settle first:** Glean already indexes the same Slack, email, and call content. "Search your customer comms" is not our wedge there. Our wedge is the structured analyst layer (risk, expansion, churn lifecycle events, health, topics across accounts) that returns deterministic reports rather than RAG answers.

## What Glean gives us to build on

| Surface | What it is | Fit for Staircase |
|---|---|---|
| **Remote MCP host** (Admin Console → Platform → Actions) | Admin registers a remote MCP server. Assistant and Agents call its tools under the end user's identity. Glean only supports centrally registered remote servers. Custom static and dynamic headers are supported. | **Primary path.** Works today. |
| **Skills** (private beta in Assistant) | Agent Skills standard. Personal skills by upload, chat, or GitHub import. Org skills published by admins. Up to 100 files and 10 MB. Daily upstream sync. Invoked by routing, name, `/slash`, or the composer menu. Skills can call MCP tools. | **Best fit for our existing skills.** |
| **Agents** (Auto mode, Workflow mode) | Agent builder with schedule triggers. Schedules are per user, max 10 active background agents per user, output to Slack or email. Independent Agents have their own identity for shared runs. | **Best delivery rhythm** (Monday, weekly, renewal window). |
| **MCP Apps** | Glean hosts MCP servers that return `ui://` resources, rendered in a sandboxed iframe in chat. Live partners: Mixpanel, Hex, Gamma, Box. | **Best demo value** for the cockpit and radar. Partner requirements not public **[verify]**. |
| **Glean's own MCP server** | Exposes search, chat, read_document, employee_search, user_activity, memory. Admins can create audience-specific servers. | Reverse direction (Claude or Cursor into Glean). Useful for customers on both, not our goal. |
| **Indexing API, Client API, Web SDK, Agent Toolkit** | Push custom datasources into Glean, call Glean programmatically, embed search and chat. | Indexing is the only one relevant to us (path 5). |
| **Glean's MCP directory** | 17 preloaded servers today. | A listing is a distribution channel worth pursuing. |

## The paths, ranked

### Path 1: Staircase as a Glean MCP action pack (do first)
- Admin adds `https://mcp.staircase.ai/mcp` under Platform → Actions. Users authenticate through Staircase OAuth (Google or Microsoft sign-in).
- **Risk [verify]:** Glean runs actions as the end user, so we need per-user OAuth to work through Glean. The Staircase owner-scoping ("my book") depends on `current_user_id`. A shared service credential would silently return the whole org, which is the dangerous failure our `book-triage` skill already guards against.
- **Risk:** 11 generic tools, where the main ones take a report config object. An LLM with no playbook will build poor reports. That is why Path 2 matters.
- Glean recommends one purpose per server. Create a **"Customer Success" custom server** with a curated subset: `report_metadata`, `run_report`, `analyze_account`, `account_lookup`, `account_info`, `fetch_evidence`, `semantic_search`, `get_playbook`.

### Path 2: Skills in Glean, plus server-side playbooks (do in parallel)
Our skills import cleanly in principle, but **16 of our SKILL.md files use constructs Glean won't have**:

| Claude-specific construct | Glean-side fix |
|---|---|
| `~/.staircase-mcp/user-profile.md` (cached scope) | Use Glean's `memory` tool, or re-resolve each session (one report call). |
| Relative refs like `../staircase-mcp-expert/` | Glean skills are self-contained. Bundle the expert references into each skill with a build step. |
| `allowed-tools: mcp__visualize__show_widget`, `sendPrompt` bridge | Drop for text output. Re-do as MCP Apps (Path 4). |
| `user_type`, `disable-model-invocation` frontmatter | Harmless if ignored. Confirm Glean's parser tolerates unknown keys. |

The bigger lever is server-side. Skills are in private beta and depend on Glean's routing picking them. If we move the intelligence into the server, it works in Glean, Claude, Copilot, and anything else:
- `staircase_get_playbook` topics for the first-call contract, book triage lenses, and renewal radar.
- A few **outcome tools** (`book_triage`, `account_brief`, `renewal_radar`, `risk_radar`) that run the recipe and return ranked, evidence-linked rows. That is the "Glean-shaped" server: 5 to 6 tools, each with one job.
- This is a product decision, not a packaging task. It costs engineering time and gives up some flexibility, so it needs your call.

### Path 3: Scheduled Agents (the rhythm layer)
| Agent | Persona | Trigger | Output |
|---|---|---|---|
| Monday book cockpit | CSM | Weekly, per-user schedule | Slack DM: "Do first" 3 to 5 accounts with one next move each |
| Renewal clock | CSM | Weekly | Renewals at 90, 60, 30 days with risk and the play |
| Pre-meeting brief | CSM | Triggered before a calendar event **[verify event trigger support]** | Brief in Slack or email |
| Weekly risk radar | Leader | Weekly, **Independent Agent** | Channel post with revenue at risk by segment and the blindsided watchlist |
| Team 1:1 prep | Leader | Weekly | Per-teammate brief |
| Quarterly churn review | Leader | Quarterly | Doc plus Slack summary |

Constraints: per-user schedules mean each CSM opts in, so adoption is a rollout problem. The 10-agent cap per user is fine. Runs that need manual confirmation fall back to email.

### Path 4: MCP Apps (pilot)
The interactive cockpit, risk radar, and team roster already exist as HTML widgets. They use the Claude `sendPrompt` bridge, so they need porting to the MCP Apps `ui/*` postMessage contract. This is the most visible thing we can show a Glean customer, but it depends on partner onboarding that is not documented publicly. Start the conversation with Glean now. Build after Paths 1 to 3 work.

### Path 5: Push Staircase briefs into Glean's index (hold, pilot only)
Index one synthesized "account brief" document per account so plain Glean search answers "what's happening with Acme" with no tool call. **Pros:** works for every Glean user, including people who never invoke a skill. **Cons:** staleness, permission mapping (who may see which account's brief), and Glean's own summarization overlapping ours. I could not confirm Indexing API details from public pages **[verify]**. Try it with one design-partner customer before building.

## Translating each Staircase skill

| Staircase skill | Glean form | Notes |
|---|---|---|
| `staircase-book-triage` | Skill + scheduled Agent | Flagship for CSMs. Keep the one-base-pull design. |
| `staircase-meeting-prep` | Skill | Pair with Glean's calendar and meeting context. Staircase adds both-sides commitments and sentiment. |
| `staircase-account-deep-dive`, `-risk-check` | Skills | Text-first. Evidence quotes matter more in Glean because users already trust Glean citations. |
| `staircase-follow-up-draft` | Skill | Uses Glean's Gmail or Outlook action to draft. **Approval-gated.** |
| `staircase-account-handoff` | Skill | Useful for the CSM-change moment. |
| `staircase-risk-radar` | Independent Agent + MCP App | Leader flagship. |
| `staircase-renewal-watchlist` | Agent | |
| `staircase-churn-review` | Quarterly Agent | |
| `staircase-voice-of-customer` | Skill | Strongest differentiator vs Glean's raw search: quantified topics across accounts. |
| `staircase-expansion-scout` | Skill + Agent | |
| `staircase-team-manager`, `-1on1-prep` | Skills | `team_engine.py` needs a home. Script execution in Glean skills is **[verify]**, and otherwise it moves server-side. |
| `gainsight-*` (writes to CTAs, Timeline, Success Plans) | Later wave | Needs the Gainsight CS MCP in Glean too. Glean's human-in-the-loop gate fits our approval-gated writes. |

## Suggested sequence

1. **Weeks 1 to 2, validate.** Stand up a Glean sandbox or a design-partner tenant. Register the MCP. Test per-user OAuth, owner scoping, and tool selection on the five asks from the README. Confirm Skills beta access and GitHub import.
2. **Weeks 2 to 6, ship the core.** Bundle three to four skills (book-triage, meeting-prep, deep-dive, risk-radar) into a Glean-ready package. Stand up two scheduled agents. Start the server-side playbook work in parallel.
3. **Weeks 6 to 10.** Customer Success custom MCP server, MCP directory listing, and the MCP Apps conversation with Glean.
4. **After that.** Path 5 pilot and the Gainsight CS write-path bundle.

## Where I would push back

- **"Glean customers just need the MCP connected" is wrong.** Without the recipes, the report-config tools are hard for a general LLM. Skills or server-side playbooks are the product here.
- **Do not build MCP Apps first.** It is the prettiest path and the least proven. A plain-text Monday DM that names the three accounts needing a CSM will show value faster.
- **Decide the positioning before the build.** If customers read this as "another Glean connector for Slack and email," we lose. The pitch is the analyst layer: risk, expansion, churn events, and topic trends computed from communications, with the evidence behind each call.

## Open questions for you

1. Do we have a Glean design-partner customer, or an internal Glean sandbox?
2. Is Staircase MCP OAuth going to work for Glean's per-user flow, and who on the engineering side can check?
3. Are you willing to invest in server-side outcome tools, given it changes the MCP's shape?
4. Does Gainsight have an existing Glean partnership channel we should go through for the MCP directory and MCP Apps?

## Sources

- [Glean Developer Platform](https://developers.glean.com/)
- [MCP in Glean (March 2026)](https://www.glean.com/blog/mcp-mar-drop-2026)
- [MCP Apps in Glean Assistant (April 2026)](https://www.glean.com/blog/mcp-apps-assistant-apr-drop-2026)
- [Glean release notes, April 22, 2026](https://docs.glean.com/release-notes/releases/2026-04-22-april-release)
- [Glean Skills docs](https://docs.glean.com/user-guide/assistant/skills) and [launch post](https://www.glean.com/blog/glean-skills-launch-2026)
- [Schedule triggers](https://docs.glean.com/agents/concepts/schedule-triggers)
- [Create MCP servers](https://docs.glean.com/administration/platform/mcp/create-mcp-servers)
- [Connect remote MCP servers to Glean](https://docs.glean.com/administration/tools/connect-remote-mcp-servers-to-glean)
- [MCP Apps overview](https://modelcontextprotocol.io/extensions/apps/overview)
