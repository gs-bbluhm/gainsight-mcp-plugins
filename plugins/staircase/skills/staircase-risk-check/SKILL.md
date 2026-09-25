---
name: staircase-risk-check
description: "Reads the health and risk signals for one account from Staircase communication data. Triggers on \"risk check on [account]\", \"is [account] at risk\", \"health check on [account]\", \"any red flags on [account]\", \"how healthy is [account]\". Surfaces frustration and churn signals with the exact language and source, balancing strengths, the sentiment trajectory, and the top 1-2 actions this week."
user_type: ic
---

# Staircase Risk Check

A grounded health read for one account. Not a vibe and not a score: the actual frustration, disengagement, and churn signals in the communications, quoted with their source, balanced against the strengths, with a clear trajectory and the one or two things to do this week.

## Foundation references

Read these before composing the query if you have not in this session:
- `../staircase-mcp-expert/`: query mechanics, the Risk Analysis data model, non-determinism handling.
- `../../_shared/staircase-output-best-practices.md`: the house style. Note: in Staircase R/Y/G displays, yellow means average/neutral, never "concern".

## When to use

**Trigger phrases:**
- "risk check on [account]"
- "is [account] at risk" / "should I be worried about [account]"
- "health check on [account]"
- "any red flags on [account]"
- "how healthy is [account]"

**Optimized for:** Cowork (card + sections) and Code (markdown + optional file).

## Step 1: Resolve the account

Call `staircase_account_lookup(name=<account>)` first.

- **High-confidence single match:** proceed.
- **Multiple low-confidence matches:** STOP and ask which account. Do not guess.
- **No match:** say so and ask for an alternate name.

## Step 2: Run the risk query

Use the validated **Risk Check** prompt verbatim via `staircase_analyze_account`.

```
staircase_analyze_account(account_id, query="
Assess the health and risk signals for <Account> from the last 90 days of communication. Identify: (1) specific signals of frustration, disengagement, or churn risk with the exact language and source, (2) signals of strength or satisfaction, (3) the sentiment trajectory and since when, (4) stakeholder or responsiveness patterns that change the picture, and (5) a clear risk read with the top 1-2 actions this week. Distinguish evidenced from inferred.")
```

**Non-determinism:** re-run the same phrasing once or twice if thin; trust an honest negative as a real signal of low communication, not hidden data.

**Optional evidence drill:** for a quote that will drive a decision, pull the full surrounding context with `staircase_fetch_evidence(<evidence_id>)` so the user can verify it was not taken out of context.

## Step 3: Build the risk read

```
# Risk Check: <Account>

**Read:** <one line, e.g., "Elevated risk, declining since mid-quarter"> · **Trajectory:** <improving / flat / declining since <date>>
**Window:** last ~90 days · **Generated:** <date>

---

## Risk signals

| Signal | Exact language | Source |
|--------|----------------|--------|
| <frustration / disengagement / churn> | "<verbatim quote>" | <email / meeting / ticket> |
| ... | ... | ... |

## Strengths / what's working

- **<strength or satisfaction signal>**: "<quote if available>". <source>
- ...

## Sentiment trajectory

<2-3 sentences: direction and since when, plus any stakeholder or responsiveness pattern that changes the picture (a champion gone quiet, slowed replies, a new detractor).>

## Do this week

1. **<top action>**: why, and for whom.
2. **<second action, if warranted>**: ...

---

### Evidenced vs inferred
- **Evidenced:** <what the communications directly say>
- **Inferred:** <what you are interpreting from limited signal>

### Sources
<evidence IDs or communication references>
```

### Format adaptations
- **Cowork:** lead with a card (the one-line read + trajectory + top action), then the risk-signals table, strengths and trajectory as sections. Evidenced-vs-inferred expandable.
- **Code:** full markdown to stdout, optional saved file.

## House-style guardrails

- **Communication signals first.** Frame health and risk on communications. Revenue and renewal date come from the report fields when populated (the CRM is authoritative for the contracted figure); product usage lives in the CRM.
- **Quote, do not paraphrase, the risk language.** The exact words plus the source are what make this trustworthy.
- **Balance the read.** Always surface strengths too, so a single bad thread does not read as a crisis, and a quiet quarter does not read as health.
- **At most two actions.** Prioritize. The value is knowing the one or two moves that matter this week.
- **Honest negatives are findings.** "No risk signals in the 90-day window" is a real, useful answer.

## Edge cases

| Situation | What to do |
|-----------|------------|
| Multiple low-confidence lookup matches | Stop, list, ask which account. |
| No risk signals found | Report it as a positive-leaning honest negative; still note trajectory and any quiet stakeholders. |
| Risk is entirely commercial (pricing, contract terms) | Surface the communication signal of it; note the commercial specifics belong in the CRM. |
| User wants the full structured Risk Analysis | The deeper per-risk drill-down (reasons + playbook + stakeholders) is available; see the analyst data models in the foundation skill. |
