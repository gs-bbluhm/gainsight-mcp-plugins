---
name: staircase-meeting-prep
description: "Preps the user for an upcoming customer meeting using Staircase communication signals. Triggers on \"prep me for [account]\", \"I have a meeting with [account]\", \"meeting prep for [account]\", \"what should I know before my [account] call\", \"brief me before [account]\". Produces where-we-left-off, both-sides commitments, risks to be ready for, recent wins, who's who, and three talking points."
user_type: ic
---

# Staircase Meeting Prep

Walk into a customer meeting with a real point of view. One account, the last ~90 days of communication, turned into a prep sheet: where you left off, what each side owes the other, what to be ready for, and three talking points to drive the conversation.

## Foundation references

Read these before composing the query if you have not in this session:
- `../staircase-mcp-expert/`: query mechanics, non-determinism handling.
- `../../_shared/staircase-output-best-practices.md`: the house style.

## When to use

**Trigger phrases:**
- "prep me for [account]" / "prep me for my meeting with [account]"
- "I have a meeting with [account]"
- "meeting prep for [account]"
- "what should I know before my [account] call"
- "brief me before [account]"

**Optimized for:** Cowork (card + sections) and Code (markdown + optional file).

## Step 1: Resolve the account

Call `staircase_account_lookup(name=<account>)` first.

- **High-confidence single match:** proceed.
- **Multiple low-confidence matches:** STOP and ask which account. Do not guess.
- **No match:** say so and ask for an alternate name.

## Step 1.5: Pull the structured scaffold (cheap, deterministic)

Before the narrative query, call `staircase_account_info(account_id)` once. It returns, deterministically, in one call: health / sentiment / engagement scores, risk level, expansion readiness + summary, renewal date, revenue (and per-product ARR where synced), tier, journey phase, last engagement / last touch, owner and CSM names, and the stored analyst summaries (AI Summary, Churn Risk, Renewal). Use it to:
- anchor the **"where we left off"** and health framing on real numbers, not a re-derived guess;
- decide emphasis (a risk-4 account walks in defensively; an expansion-ready one, offensively);
- fill the commercial context (renewal date, ARR) the prep sheet needs, flagged as CRM-authoritative for the exact figure.

This is the factual spine. `analyze_account` (next) supplies the dated timeline, the both-sides commitments, stakeholder stances, and evidence that `account_info` does not.

## Step 2: Run the meeting-prep query

Use the validated **Prep My Meeting** prompt verbatim via `staircase_analyze_account`.

```
staircase_analyze_account(account_id, query="
I have an upcoming meeting with <Account>. Using the last 90 days of communication, give me: (1) where we left off and the most recent interaction, (2) open items and commitments on both sides, (3) risks or unresolved concerns to be ready for, (4) recent wins to reinforce, (5) who the key people are and where each stands, and (6) three specific talking points to drive the conversation. Cite sources and distinguish evidenced from inferred.")
```

**Non-determinism:** re-run the same phrasing once or twice if thin; trust honest negatives.

**Optional evidence drill:** verify a specific commitment or concern with `staircase_fetch_evidence(<evidence_id>)`.

## Step 3 (optional): Enrich from meeting notes

If a meeting-notes MCP is connected in this environment (for example a Notion meeting-notes tool, Granola, or similar), you may cross-reference the most recent recap for tone and any items Staircase did not surface. This is additive only. Do not hard-depend on it, and never block the prep sheet waiting on it. If no such tool is available, skip this step silently.

## Step 4: Build the prep sheet

```
# Meeting Prep: <Account>

**Last touch:** <date + what it was> · **Window:** last ~90 days · **Generated:** <date>

---

## Where we left off

<2-3 sentences. The most recent interaction and the state it left things in.>

## Open commitments

| Owner | Commitment | Since | Status |
|-------|------------|-------|--------|
| Us | <what we owe them> | <date> | <open / in progress> |
| Them | <what they owe us> | <date> | <open / waiting> |

## Be ready for

- **<risk or unresolved concern>**: what it is and why it may come up. <source>
- ...

## Wins to reinforce

- **<recent win>**: worth naming in the room. <source>
- ...

## Who's who

| Person | Role (apparent) | Where they stand |
|--------|-----------------|------------------|
| <name> | <role> | <positive / neutral / concerned + one-line evidence> |

## Three talking points

1. **<talking point>**: the angle and why it lands.
2. **<talking point>**: ...
3. **<talking point>**: ...

---

### Evidenced vs inferred
- **Evidenced:** <what the communications say>
- **Inferred:** <what you are interpreting>

### Sources
<evidence IDs or communication references>
```

### Format adaptations
- **Cowork:** lead with a card (where we left off + the three talking points), tabs or sections for commitments, risks, who's who. Evidenced-vs-inferred as an expandable.
- **Code:** full markdown to stdout, optional saved file.

## House-style guardrails

- **Lead with communication signals; use the scaffold's commercial fields when present.** Staircase surfaces health/sentiment/engagement scores, risk, expansion, renewal date and revenue via `account_info` (CRM-synced). Use them, and flag the CRM as authoritative for the exact contracted figure/date. Seat counts and product-usage still live outside Staircase.
- **~90-day window.** If the meeting hinges on older history, say it should come from the CRM.
- **Both sides of every commitment.** The skill's value is showing what you owe them, not just what they owe you.
- **Talking points are specific.** Tie each to a real signal, not a generic agenda item.

## Edge cases

| Situation | What to do |
|-----------|------------|
| Multiple low-confidence lookup matches | Stop, list, ask which account. |
| Thin communication history | Report honestly; lean on any meeting-notes enrichment if available; suggest the CRM. |
| User wants a renewal-specific prep | Note the renewal framing (relationship health, value delivered, concerns, expansion) and that commercials come from the CRM. |
| No meeting-notes MCP present | Skip step 3 silently; the Staircase prep stands on its own. |
