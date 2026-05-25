<!-- FOR HUMAN USERS ONLY — Claude should not read or load this file. It duplicates context already in SKILL.md. -->

# Gainsight Meeting Processor — What You Can Do

Process a customer meeting into ready-to-review deliverables: a recap email, a Gainsight Timeline activity, a risk CTA (if needed), success-plan updates, action items, and win quotes. Nothing posts until you approve.

The skill exercises **Staircase AI + Gainsight CS together** so the output reflects what's been happening in the account for the last 60 days, not just the call we just had.

## Getting Started

Just talk naturally. Name the customer and the skill handles the rest.

> "Process my call with <account>"
> "Run the post-call workflow for <account>"
> "Do the meeting processor for <account> from yesterday"

If you want to specify the source of the transcript:

> "Use my Notion meetings"
> "Pull from Zoom"
> "I'll paste the transcript"

## What You Get

- **Email recap draft** in your tone, with action items addressed by person
- **Gainsight Timeline activity** with summary, wins, risks, decisions, action items, and 60-day Staircase context
- **Risk CTA preview** only if risk was surfaced (no spam)
- **Success Plan objective updates** if the call touched active plans
- **Action item list** for reference and sharing
- **Win quotes** verbatim with attribution
- **Reconciliation note** when the call and Staircase's 60-day signal disagree

## What Posts on Approval

- Gmail draft created (not sent — you send manually)
- Gainsight Timeline activity logged to Customer 360
- CTA created in Cockpit (if approved)
- Success Plan updates applied (if approved)

## Supported Transcript Sources

The skill detects which call recorder you have connected:
- Notion meeting notes (default if your Notion meeting connector is active)
- Zoom (search by customer name, this week)
- Granola, Fireflies, Gong (if their MCPs are loaded)
- Paste (always available fallback)

## Tips

- The skill defaults to "most recent" meeting. To pin a specific one, say the date: "process my call with <account> from May 19".
- If you have multiple Gainsight relationships under one Company, the skill defaults to the Company-level. It'll flag relationship options for product-specific calls (e.g. a product-specific relationship for product discussions).
- The recording link and passcode are left as placeholders. You verify and paste them before sending.
