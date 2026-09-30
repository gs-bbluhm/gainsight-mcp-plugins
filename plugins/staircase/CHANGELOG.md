# Changelog

## 2.0.0-beta.2 (2026-09-29)
- **Risk radar** scopes to the accounts you're responsible for and leads with the 90-day renewal slice (fresh vs chronic risk). Each account gets one of five churn states (saveable, notice given, partial, lost, verify) and a tag for which product the risk is about. Coverage leads with decision-maker touch, and the team view shows pooled users separately.
- **Your slice of the portfolio:** if you don't carry a book, set the slice you own once (a product line, segment, or region) and every skill applies it.
- **Stakeholder roles:** Decision Maker, Champion, and Executive Sponsor are built in, and Staircase's signals count only those exact names. Skills flag look-alike roles and suggest retagging.
- **Server playbooks:** skills fetch matching `staircase_get_playbook` topics first.
- **Two books:** when you hold accounts in two roles, skills use the main one and say which, instead of asking.

## 2.0.0-beta.1 (2026-09-25)

First release of `staircase` as a standalone plugin in this marketplace. It supersedes the earlier desktop-upload builds (1.x). Beta: the foundation is final; the workflow skills are going through a live validation pass and may change before 2.0.0.

### Foundation
- **Scope resolves itself.** On first use, one report finds which account field links you to your book (owner, CSM, renewal owner, or an org-specific role), so "my accounts" works without setup questions. It asks one question only when you sit on two books. People who don't carry a book get their team's view or the portfolio.
- **Report recipes.** A new library of canonical reports, one per core question (book, renewal window, at-risk cohort, expansion pipeline, lifecycle evidence, account 360, team rollup, stakeholder coverage, voice of customer, churn retrospective). Each column is chosen for the call-out it enables.
- **Evidence chain.** Lifecycle events, then `staircase_list_communications` (meeting issues and action items, participants typed as your team or theirs), then verbatim evidence. Signals decide what to read; they never establish intent on their own.
- **Reliability rules rewritten** for the current MCP: multi-value `In`, retry only when a result says `retryable`, Collections are columns not filters, reference columns return ids, lifecycle types are org-specific, check the base rate before flagging an absence, and more. Rules for problems the server has since fixed are retired.
- **Leaner.** The foundation loads about 30% fewer tokens; the tool descriptions now carry the config contract, and the skill carries routing, org discovery, and methodology.
- **Setup is optional.** `staircase-setup` is now a short welcome and practice round; every skill resolves scope on its own.

### Workflow skills
- Scoping uses your resolved book field everywhere (expansion scout, renewal watchlist, churn review, and the rest).
- Expansion scout reads the `expansion_opportunity` entity, including AI confidence.
- Examples and embedded app data are synthetic; org-specific fields are discovered at run time, never shipped.
- App output: tier chips derived from your data, a single Revenue field, "open in Staircase" links, and one visual language across skills.

### Requirements
- The Staircase AI connector (Claude connector directory: "Gainsight (Staircase AI)"), or `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`.

### Known limitations
- Topic reports currently return topic ids without names; voice-of-customer names themes through search and says so.
- Account score history (health or engagement over time) isn't available through the MCP yet, so skills show current scores only.
- Per-account analysis runs up to 10 accounts in parallel.
