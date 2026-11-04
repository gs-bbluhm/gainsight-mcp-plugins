# Staircase v3 (beta)

**Seven Staircase AI skills for Claude that turn your customer conversations into the next move, with the email, Slack ask or agenda already drafted.** Every answer says whose accounts it covers, what it read, and what it couldn't see. Nothing is ever sent or written for you: drafts only.

This is a beta. It changes often, and your feedback shapes it.

## Before you start

| You need | How |
|---|---|
| The Staircase AI connector | Claude, then Settings, Connectors, Browse connectors: search *Staircase*, pick **Gainsight (Staircase AI)** and sign in |
| Code execution on (Claude apps only) | Settings, Capabilities: turn on code execution. A few skills run a small scoring script |
| v2 turned off while you test | If you use the `staircase` 2.0 plugin or its skills, turn them off so only one version answers |

## Install

**Claude Code** (2.1.275 or later: one line per plugin)

```
/plugin install staircase-v3 --marketplace gs-bbluhm/gainsight-mcp-plugins
/plugin install staircase-v3-account-team --marketplace gs-bbluhm/gainsight-mcp-plugins
/plugin install staircase-v3-leaders --marketplace gs-bbluhm/gainsight-mcp-plugins
```

On an older Claude Code:

```
/plugin marketplace add gs-bbluhm/gainsight-mcp-plugins
/plugin install staircase-v3@gainsight-mcp-plugins
/plugin install staircase-v3-account-team@gainsight-mcp-plugins
/plugin install staircase-v3-leaders@gainsight-mcp-plugins
```

Already added this marketplace for v2? Run `/plugin marketplace update gainsight-mcp-plugins` first.

**Claude on the web, desktop or Cowork**

Download the zips you want from [`skill-zips/`](skill-zips/), then in Claude open Settings, Skills (under Capabilities or Customize), choose **Upload skill**, and add each zip. Each zip works on its own.

## What to try

| Skill | Zip | For | Try saying |
|---|---|---|---|
| **What needs me today** | `staircase-csm-today.zip` | CSMs, account managers | "What needs me today?" · "Plan my week" · "Which of my accounts have gone quiet?" |
| **Renewals** | `staircase-renewals.zip` | Whoever owns renewals | "Which renewals need work?" · "Prep my forecast call" |
| **Account brief** | `staircase-account-brief.zip` | Anyone walking into a call | "Prep me for my call with <account>" · "Catch me up on <account>" · "I'm taking over <account>" |
| **Follow-up** | `staircase-follow-up.zip` | Anyone who talks to customers | "I just got off a call with <account>" · "Who do I owe a reply?" |
| **Voice of the customer** | `staircase-voice.zip` | CS leaders, product, marketing | "What are customers saying?" · "Top feature requests in the last 90 days" |
| **Team view** | `staircase-manager-team.zip` | CS managers | "How's my team?" · "What's renewing on my team?" |
| **Ask Staircase** | `staircase-ask.zip` | Everyone, admins most | "How many accounts renew in the next 90 days?" · "Build me a report of high-risk renewals by tier" · "Set up Staircase for me" |

Start with "What needs me today?" or "Prep me for my call with <account>": they show the most in one answer.

## How answers work

- **The first line is the whole answer:** how many things need you and the first move.
- **The first run asks one question:** "I found 28 accounts where you're the CSM. Is that your book?" Say yes, or tell it your role.
- **Reply with a number and a word:** `draft 1` saves a draft to your Gmail or Slack drafts (when those connectors are on), `done 4` or `snooze 5 until Friday` clears one, `not mine 3`, `why 2` shows the reasoning. Plain words work too.
- **Every answer ends with two lines:** "How I built this" and "What I couldn't see".
- **Want something you can click through?** On a long list, say `board`.
- **Read-only:** it reads Staircase and never changes Staircase, your CRM, your email or your Slack.

## Tell us what you see

What helps most:

1. Was item 1 the right first move? If not, what should it have been?
2. Anything wrong, missing or out of date?
3. Did the drafts sound like you, and go to the right person?
4. Where did you have to stop and think?

Share it with Brady during office hours or in your Slack channel with the Staircase team. Please keep customer names and details out of issues on this repo: it is public.
