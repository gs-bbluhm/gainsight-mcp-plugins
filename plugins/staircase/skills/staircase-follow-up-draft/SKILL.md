---
name: staircase-follow-up-draft
description: "Drafts a follow-up email to a customer grounded in real Staircase interactions. Triggers on \"draft a follow-up to [account]\", \"write a follow-up email for [account]\", \"help me follow up with [account]\", \"draft an email to [account]\". Produces a ready-to-send DRAFT in the user's voice that references actual conversations, plus the source interactions to verify. DRAFT ONLY, never sends."
user_type: ic
---

# Staircase Follow-Up Draft

Turn the last ~90 days of communication into a warm, specific follow-up email the user can edit and send. It references real conversations (not generic pleasantries), addresses the open items, and comes with the source interactions so the user can verify before sending. This skill drafts. It never sends.

## Foundation references

Read these before composing the query if you have not in this session:
- `../staircase-mcp-expert/`: query mechanics, non-determinism handling.
- `../../_shared/staircase-output-best-practices.md`: the house style and the draft-do-not-send rule.

## When to use

**Trigger phrases:**
- "draft a follow-up to [account]" / "draft a follow-up email for [account]"
- "write a follow-up email for [account]"
- "help me follow up with [account]"
- "draft an email to [account]"

**Optimized for:** Cowork (draft in a card, copy-ready) and Code (draft to stdout, optional file).

## Step 1: Resolve the account

Call `staircase_account_lookup(name=<account>)` first.

- **High-confidence single match:** proceed.
- **Multiple low-confidence matches:** STOP and ask which account. Do not guess.
- **No match:** say so and ask for an alternate name.

## Step 2: Run the follow-up query

Use the validated **Draft a Follow-Up** prompt verbatim via `staircase_analyze_account`.

```
staircase_analyze_account(account_id, query="
Draft a follow-up email to <Account> based on my most recent interactions. First give me a two-line summary of what it needs to address (open items, commitments, any concern to acknowledge), then write the email: warm but concise, in my voice, referencing specifics from our actual conversations, with clear next steps. Show me the source interactions you drew from so I can verify before sending.")
```

**Non-determinism:** re-run the same phrasing once or twice if thin. If the account has almost no recent communication, say so rather than inventing specifics. A grounded draft beats a fabricated one.

**Optional evidence drill:** confirm a referenced detail with `staircase_fetch_evidence(<evidence_id>)` before it goes in the draft, so the email does not misquote a conversation.

## Step 3: Present the draft

Present it as a DRAFT for review. Do not claim it was sent. Do not send it.

```
# Follow-Up Draft: <Account>

**What this addresses:** <two lines: open items, commitments, any concern to acknowledge>
**Window:** last ~90 days · **Generated:** <date> · **Status: DRAFT, review before sending**

---

**To:** <suggested recipient(s) from the communications, if clear>
**Subject:** <suggested subject>

<Email body. Warm but concise. In the user's voice. References specifics from real
conversations. Ends with clear next steps. Plain text, no blockquote bars so it
copies cleanly into Gmail or Slack.>

---

### Sources I drew from (verify before sending)

| Date | Interaction | What I pulled from it |
|------|-------------|-----------------------|
| <date> | <email / meeting / ticket> | <the specific detail referenced in the draft> |

> Review and edit, then send from your own mail client. This skill does not send email.
```

### Format adaptations
- **Cowork:** present the draft in a copy-ready card with the sources as an expandable below. No send button, no send action.
- **Code:** draft inline in the response, sources table beneath, optional saved file.

## House-style guardrails

- **DRAFT ONLY. Never send.** No mail tool, no send action, no "sent" claim. The user reviews and sends themselves.
- **Inline draft, no `>` blockquote bars.** Blockquote markup copies badly into Gmail and Slack. Plain text.
- **Ground every specific.** Each concrete reference in the email maps to a real interaction in the sources table. If you cannot source a detail, leave it out.
- **In the user's voice, warm but concise.** Not flowery, not corporate boilerplate.
- **Keep commercial figures out of the draft.** Revenue, renewal dates, and usage numbers stay out of a customer-facing email unless the user asks for them; they are internal, and the CRM is authoritative for the contracted figures.
- **No em dashes** in the email body either.

## Edge cases

| Situation | What to do |
|-----------|------------|
| Multiple low-confidence lookup matches | Stop, list, ask which account. |
| Almost no recent communication to ground in | Say so; offer a short, honest check-in draft and flag that it lacks specific hooks. |
| User wants it sent | Decline to send; this skill drafts only. Hand them the copy-ready draft. |
| User wants a different tone or recipient | Regenerate with the adjustment; keep it grounded in the same sources. |
| Sensitive topic (security report, contract dispute) | Draft the relationship-level follow-up; do not offer to share a SOC 2 or commercial document. Note the relevant internal team handles that. |
