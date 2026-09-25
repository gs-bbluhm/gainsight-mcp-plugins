<!-- FOR HUMAN USERS ONLY. This file is an enablement guide for people, not an instruction set for Claude. -->

# Staircase Plugin: User Guide

This plugin brings Staircase AI's communication intelligence into Claude. Ask in plain language and Claude runs the Staircase queries the right way, then hands you a clean answer you can use or share.

## Prerequisite: connect the Staircase MCP

The plugin needs the Staircase AI MCP connected to Claude. Either:

- add Staircase AI as a connector in your claude.ai connector settings and authorize it, or
- in Claude Code, run `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp` and authenticate when prompted.

Running setup (next section) confirms the connection for you.

## Set up once (optional)

Say: **"Set up Staircase"** (or run `staircase-setup`). Claude confirms the Staircase connection and who you are, figures out which accounts are yours automatically, runs a quick test, and remembers your scope. Takes about two minutes. You can also skip it: the first question you ask resolves your accounts the same way, and after that "my accounts" just works.

## What you can ask

### For one account

| You want to... | Say something like... | Skill |
|---|---|---|
| Get up to speed fast | "Catch me up on Acme" | `staircase-account-deep-dive` |
| Prep for a meeting | "Prep me for my meeting with Acme" | `staircase-meeting-prep` |
| Check health and risk | "Risk check on Acme" | `staircase-risk-check` |
| Draft a follow-up | "Draft a follow-up email to Acme from my last call" | `staircase-follow-up-draft` |
| Take over an account | "Build me a handoff brief for Acme" | `staircase-account-handoff` |

### Across your book

| You want to... | Say something like... | Skill |
|---|---|---|
| Know what needs you this week | "What needs me this week?" | `staircase-book-triage` |
| See what is at risk | "Show me my portfolio risk" | `staircase-risk-radar` |
| Plan or forecast renewals | "Plan my renewals" / "Renewal forecast by segment" | `staircase-renewal-watchlist` |
| Learn from churn | "Churn retrospective for last quarter" | `staircase-churn-review` |
| Hear the voice of the customer | "What are customers saying about pricing?" | `staircase-voice-of-customer` |
| Find expansion | "Where do I have expansion opportunities?" | `staircase-expansion-scout` |

### For CS leaders

| You want to... | Say something like... | Skill |
|---|---|---|
| See your team's load and exposure | "Show me my team's roster" | `staircase-team-manager` |
| Prep a 1:1 with a teammate | "Prep me for my 1:1 with <teammate>" | `staircase-1on1-prep` |

Two foundation skills work behind the scenes and are not usually called directly: `staircase-mcp-expert` (how to query Staircase well) and `staircase-app-design` (how answers render as clean, app-like views).

## What makes the answers good

The plugin always scopes to the right accounts, asks for the evidence behind each point, separates what the communications actually say from what is inferred, and ends with a clear next step. It frames everything on what people said and did, because Staircase reads communications.

## What Staircase does not know

Staircase reads communications, not your CRM. It shows revenue and renewal dates when your org has them populated, but your CRM is authoritative for the contracted value and date, and seat counts and product usage live in the CRM. Ask Staircase what customers are saying, how engaged they are, and what's putting a renewal at risk; ask your CRM for the contract facts.

## A few tips

- Be specific. "Risk check on Acme" beats "risk".
- On portfolio questions, if an answer comes back thin, ask again. The cross-account engine occasionally needs a second run.
- Everything is a draft for you to review. The plugin never sends anything on your behalf.

## What you need

The Staircase MCP connected to Claude (see the prerequisite above). Optionally, a meeting-notes source and Gmail for richer meeting prep and follow-up drafts.
