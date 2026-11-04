# Safe to ask: can we ask this customer for a favor right now

Returns Ready, Hold (with the reason and evidence) or Pull for each account and contact, before any reference, case study, review, beta, peer intro or expansion ask. Used by the today list's references lane, the account brief's safe-to-ask lens, marketing advocates, beta recruiting and executive wins.

## Checks, in order

| # | Check | Ready needs | Otherwise |
|---|---|---|---|
| 1 | Stored gates | Status Active. Risk below 4 or not assessed (not assessed means read harder; "risk LessThan 4" drops blanks, so add an Or with NotDefined). No ChurnRisk insight. No `exceptional_negative`, `churn_risk`, `churn` or `farewell` event in 90 days (set `arguments.dateRange` and state it). Renewal more than 60 days out, unless the CSM says go | Pull: risk 4+, ChurnRisk, a churn event. Hold: renewal within 60 days, a departure |
| 2 | Conversation read | The last 45 days, at most 10 accounts a run: no open problem, escalation or commercial dispute | Hold, naming the thread (evidence id) |
| 3 | Speaker | The praise came from a customer-side participant (the fetched message's sender matches a Stakeholder), not our staff or a partner | Hold: speaker unconfirmed |
| 4 | Touch | No ask seen for that contact inside the ask budget; our recent outbound to them is not heavy; no CSM hold | Hold: recently asked, or the CSM said hold |

Health ranks; it does not gate. It removes most of an otherwise clean pool and does not read conversations.

## The praise

- Classes, best first: outcome achieved, product value, service, courtesy.
- Courtesy thanks and praise for fixing our own problem never rank as Ready. Onboarding praise is a promise, not an outcome.
- Fresh praise decays: ask within about 14 days.
- Ask budget (company profile may change): one ask per contact per 90 days, one per account per 30, separate from the CSM's touch budget.

## Output

| Account | Contact | Call | Their words (verbatim, evidence id) | Class | Open issues | Last ask seen | Fitting ask | CSM |
|---|---|---|---|---|---|---|---|---|

- Rank rule: Ready first; then outcome, product value, service; then the most recent praise; then the fewest asks seen.
- Next action: a Slack or email draft to the CSM ("planning to ask <contact> for <ask>; their note on <date>; anything I should know about open issues, renewal talks or recent asks? go or hold"). The ask to the customer waits for the CSM's go.
- A quote is never publishable without the customer's recorded written consent. "Feel free to quote me" is noted, not consent.
