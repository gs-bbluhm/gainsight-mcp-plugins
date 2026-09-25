---
name: staircase-account-deep-dive
description: "The richest single-account synthesis from Staircase communication data. Use when someone needs to get oriented on an account fast. Triggers on \"catch me up on [account]\", \"what's going on with [account]\", \"give me the latest on [account]\", \"deep dive on [account]\", \"where do we stand with [account]\". Produces a dated, evidence-cited catch-up: one-line status, the developments that matter, open threads, the sentiment trend, and the single next action."
user_type: ic
---

# Staircase Account Deep Dive

The "catch me up" workflow. One account, the last ~90 days of communication, synthesized into something you can read in two minutes and act on today. This is the default account read when someone just needs to know where things stand.

## Foundation references

Read these before composing the query if you have not in this session:
- `../staircase-mcp-expert/`: query mechanics, field catalog, non-determinism handling, analyst data models.
- `../../_shared/staircase-output-best-practices.md`: the house style every artifact follows.

## When to use

**Trigger phrases:**
- "catch me up on [account]"
- "what's going on with [account]"
- "give me the latest on [account]"
- "deep dive on [account]" / "brief me on [account]"
- "where do we stand with [account]"

**Optimized for:** Cowork (card + sections) and Code (markdown + optional file). This is the single most reliable Staircase surface, so it is the safest default.

## Step 1: Resolve the account

Call `staircase_account_lookup(name=<account>)` first to get an `account_id`.

- **High-confidence single match:** proceed.
- **Multiple low-confidence matches:** STOP and ask the user which account they mean. Do not guess.
- **No match:** tell the user plainly and ask for an alternate spelling or the parent company name.

## Step 1.5: Pull the structured scaffold (cheap, deterministic)

Call `staircase_account_info(account_id)` once before the narrative. It returns, in one deterministic call: health / sentiment / engagement scores, risk level, expansion readiness + summary, renewal date, revenue (+ per-product ARR where synced), tier, journey phase, last engagement / last touch, owner, and the stored analyst summaries (AI Summary, Churn Risk, Renewal). Use it to set the **status line and health framing on real numbers** and to decide what the catch-up should emphasize. Then `analyze_account` supplies the dated developments, open threads, sentiment *trend*, and evidence the scores alone can't tell you. (If the user only wants the fast factual snapshot, `account_info` may be enough on its own.)

## Step 2: Run the catch-up query

Use the validated **Catch Me Up** prompt verbatim via `staircase_analyze_account`. This is the prompt that passed 5/5 in live testing and returns dated, sourced, evidenced-vs-inferred output.

```
staircase_analyze_account(account_id, query="
Give me a complete catch-up on <Account> from the last 90 days of communication. Structure it as: (1) current relationship status in one line, (2) the 3-5 most important developments in chronological order with date and source, (3) open threads or unanswered asks on either side, (4) the overall sentiment trend and what's driving it, and (5) the single most important thing I should do next. Cite specific communications and distinguish evidenced from inferred.")
```

**Non-determinism:** if the answer comes back thin, re-run the same phrasing once or twice before switching wording. Trust an honest negative ("no usable evidence in the 90-day context") as real, not the engine hiding data.

**Optional evidence drill:** if a development is load-bearing and the user needs to verify it, pull the full text with `staircase_fetch_evidence(<evidence_id>)`.

## Step 3: Build the artifact

Synthesize into this structure. Lead with the answer, tables over paragraphs, sources attached.

```
# Catch-Up: <Account>

**Status:** <one line, e.g., "Engaged but high-risk ahead of an upcoming decision">
**Window:** last ~90 days of communication · **Generated:** <date>

---

## What happened (most recent first)

| Date | Development | Source |
|------|-------------|--------|
| <date> | <what happened, one line> | <email / meeting / ticket> |
| ... | ... | ... |

## Open threads

- **<open item / unanswered ask>**: who owes whom, since when.
- ...

## Sentiment trend

<2-3 sentences: direction (improving / flat / declining), since when, what is driving it. Cite the signal.>

## Do this next

**<the single most important next action>**: why, and who it is for.

---

### Evidenced vs inferred
- **Evidenced:** <what the communications directly say>
- **Inferred:** <what you are interpreting from limited or indirect signal>

### Sources
<evidence IDs or communication references behind the claims above>
```

### Format adaptations
- **Cowork:** lead with a card (status line + "Do this next"), then the developments table, with open threads and sentiment as sections. Offer the evidenced-vs-inferred split as an expandable.
- **Code:** full markdown to stdout, plus an optional saved file if the user asks.

## House-style guardrails

- **Lead with communication signals; the scaffold's commercial fields are fair game.** `account_info` surfaces health/sentiment/engagement scores, risk, expansion, renewal date and revenue (CRM-synced); use them, flagging the CRM as authoritative for the exact figure/date. Seat counts and product-usage still live outside Staircase.
- **~90-day window.** Anything older lives in the CRM. Say so if the user asks about earlier history.
- **Every claim carries a source.** If you cannot source it, mark it inferred.
- **One next action, not five.** The value of this skill is the single most important move.

## Edge cases

| Situation | What to do |
|-----------|------------|
| Lookup returns multiple low-confidence matches | Stop, list them, ask the user which one. |
| Account has near-zero communication in 90 days | Report the honest negative; suggest the CRM for older context. |
| User wants only risk, or only meeting prep | Route to `staircase-risk-check` or `staircase-meeting-prep`. |
| User asks "what just changed" specifically | This skill covers it: lead with the most recent dated developments and any shift in the sentiment trend. |
