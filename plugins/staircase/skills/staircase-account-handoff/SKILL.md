---
name: staircase-account-handoff
description: "Builds a first-90-days onboarding brief for someone inheriting an account, from Staircase communication history. Triggers on \"I'm taking over [account]\", \"I just inherited [account]\", \"build me an onboarding brief for [account]\", \"handoff brief for [account]\", \"I'm the new owner on [account]\". Synthesizes stakeholders, why they bought, recent wins and challenges, open commitments, red flags, and first-30-day actions. Outputs a markdown brief."
user_type: ic
---

# Staircase Account Handoff

For the moment someone inherits an account by promotion, reorg, leave coverage, or normal rotation. This turns Staircase's communication history into a concrete first-90-days brief, so the new owner walks in with a real point of view instead of a cold company record. Output is a markdown brief, not a CRM write.

## Foundation references

Read these before composing the query if you have not in this session:
- `../staircase-mcp-expert/`: query mechanics and the Handoff Analysis data model (the richest, most structured analyst output).
- `../../_shared/staircase-output-best-practices.md`: the house style.

## When to use

**Trigger phrases:**
- "I'm taking over [account]" / "I just inherited [account]"
- "build me an onboarding brief for [account]"
- "handoff brief for [account]" / "new owner brief for [account]"
- "I'm the new owner on [account]"

**Optimized for:** Cowork (card + tabs) and Code (markdown + optional file). The brief is the deliverable the new owner uses on day one.

## Step 1: Resolve the account

Call `staircase_account_lookup(name=<account>)` first.

- **High-confidence single match:** proceed.
- **Multiple low-confidence matches:** STOP and ask which account. Do not guess.
- **No match:** tell the user; without communication data there is nothing to synthesize. Offer to run the skill once communications start flowing.

## Step 1.5: Pull the structured scaffold (cheap, deterministic)

Call `staircase_account_info(account_id)` once first. It returns, in one deterministic call: health / sentiment / engagement scores, risk level, expansion readiness + summary, renewal date, revenue (+ per-product ARR where synced), tier, journey phase, owner/CSM names, and (most relevant here) the **stored Handoff fields** (`Handoff strategic summary`, `Handoff primary objectives`) plus the AI Summary, Churn Risk, and Renewal summaries. When the Handoff analyst has fired, these give the new owner a factual spine before any narrative. (Note: on active accounts that were never formally handed off, the handoff fields may be empty (verified live); fall back to the Handoff Analysis query in Step 2.)

**Optional stakeholder roster (deterministic):** for the org chart, run a `stakeholder` report filtered `stakeholder.customer In [account_id]` with columns name, title, role, last_engagement. This returns the full contact roster reliably (verified: the account filter works). Use it for coverage/threading ("who exists, who's gone quiet"). It does NOT give reliable per-person *stance* (report tone defaults to Neutral); get champion/detractor stance from the Handoff Analysis in Step 2. Skip this on very large accounts where the roster is hundreds of rows unless the user wants the full map.

## Step 2: Run the Handoff Analysis query

"Sales handoff" is a first-class AI insight in Staircase, and the Handoff Analysis is its most mature, most structured output. Use it via `staircase_analyze_account`. This phrasing maps to that internal report type.

```
staircase_analyze_account(account_id, query="
Build a Handoff Analysis for <Account> from communication history. Return:
1. Account summary (60-second read: biggest risk + biggest opportunity)
2. Why they bought and their goals (original purchase rationale, the problem they were solving)
3. Key stakeholders (champions / decision-makers / detractors), each with role, sentiment evidence, and last activity
4. Recent wins and challenges (last ~90 days)
5. Current priorities and open commitments on both sides
6. Red flags to watch
7. Recommended first 30-day actions
Cite specific communications and distinguish evidenced from inferred.")
```

If you need the full 11-section structure (purchase context, onboarding readiness, expected outcomes, commitments with made-by/made-to), pull the richer Handoff template from the analyst data models in the foundation skill.

**Non-determinism:** re-run the same phrasing once or twice if thin; trust honest negatives.

**Optional evidence drill:** confirm a stakeholder's stance or a stated commitment with `staircase_fetch_evidence(<evidence_id>)`.

## Step 3: Note the window

Staircase reads ~90 days of communication. A handoff often needs the deeper backstory: the original deal, the multi-year relationship, the commercial terms. Say plainly in the brief that older history and all commercials should come from the CRM. This skill builds the communication-grounded layer of the handoff, not the commercial one.

## Step 4: Build the brief

```
# Handoff Brief: <Account>

**New owner:** <name or TBD> · **Window:** last ~90 days of communication · **Generated:** <date>
> Older history and commercials (ARR, renewal date, contract terms) come from the CRM. This brief is the communication-grounded layer.

---

## 1. 60-second read

<3-5 sentences. What the new owner needs in one minute. Lead with the biggest risk and the biggest opportunity.>

## 2. Why they bought

<Original purchase rationale and goals, direct from the communication synthesis. The problem they were solving, the bet they made.>

## 3. Stakeholders

### Champions
- **<name>**: role, sentiment evidence, last activity. <source>

### Decision-makers / sponsors
- **<name>**: ... <source>

### Detractors / friction points
- **<name>**: ... <source>

### Recent shifts (last ~90 days)
- <someone newly appearing, someone gone quiet>. <source>

## 4. Recent wins and challenges

**Wins**
- <win>. <source>

**Challenges**
- <challenge>. <source>

## 5. Open commitments

| Owner | Commitment | Since | Status |
|-------|------------|-------|--------|
| Us | <what we owe them> | <date> | <open> |
| Them | <what they owe us> | <date> | <open> |

## 6. Red flags

Numbered, ranked by severity, each with a one-line mitigation.

## 7. First-30-day actions

Concrete moves for the new owner's first month:
- Conversations to have (the live handoff with the prior owner, an exec intro).
- Threads to pick up (the open commitments above).
- Relationships to establish (the champions and any quiet stakeholders).

## 8. Open questions for the outgoing owner

Things the communications cannot answer. Ask these on the live handoff call. Examples: the real story behind a red flag, commercial context, history older than 90 days.

---

### Evidenced vs inferred
- **Evidenced:** <what the communications directly say>
- **Inferred:** <what you are interpreting>

### Sources
<evidence IDs or communication references>
```

### Format adaptations
- **Cowork:** lead with a card (the 60-second read), then tabs for stakeholders, wins/challenges, commitments, and the action plan. Evidenced-vs-inferred and sources as expandables.
- **Code:** full markdown to stdout, plus a saved file if the user wants one.

## House-style guardrails

- **Communication signals lead; the scaffold's commercial fields are usable.** Stakeholders, sentiment, commitments, wins, and risks come from communications. Renewal date, revenue, and per-product ARR come from `account_info` (CRM-synced); include them, flagging the CRM as authoritative for the contracted figure and for history older than the ~90-day window. Contract terms and seat counts still live in the CRM.
- **~90-day window, stated explicitly.** This is a handoff; the window limitation matters more here than anywhere else. Always flag what the CRM must supply.
- **Every stakeholder and commitment carries a source.** If you cannot source it, mark it inferred.
- **No CRM writes, no Success Plan creation.** This solo skill produces a markdown brief only. There is no approval gate because there is no write.
- **Open questions are part of the value.** What the communications cannot tell the new owner is exactly what they should ask the outgoing owner.

## Edge cases

| Situation | What to do |
|-----------|------------|
| Multiple low-confidence lookup matches | Stop, list, ask which account. |
| No communication data for the account | Cannot build. Tell the user; offer to run once communications start. |
| Account spans multiple entities (M&A, regional splits) | Note the entities; build at the level the lookup resolved, and flag the others. |
| Thin 90-day history but a long backstory | Build what you can; lean hard on section 8 (questions for the outgoing owner) and the CRM note. |
| User also wants the formal Success Plan | Out of scope for the solo plugin (no CRM writes). The brief's section 7 is the action starting point. |
