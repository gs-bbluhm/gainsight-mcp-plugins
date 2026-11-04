# Plain words: what the user sees

Read before any answer. The left column never appears above the proof lines (`delivery.md`). Field ids, enum values, scores and evidence ids belong on `why`, in the run log, in a doc appendix, or in report mode's footer and report setup. `_dev/scripts/check_output.py` fails an answer that breaks this.

## Scope and roles

| Not this | Say this |
|---|---|
| "book", "read as the signed-in user", "for <name>" | "your accounts", "you" |
| "CS CSM field", "<role> field", "role field" | "where you're the CSM"; drop "field" everywhere |
| "Renewal Owner field", "Owner field", "CSSC field" | "the renewal owner", "the account owner", "the support engineer (my guess)" |
| "include second fields", "union" | "include accounts where you hold another role" |
| "Scope: book, <name>, <field>, 28 accounts, Active only" | "your 28 active accounts where you're the CSM" |
| "slice", "engaged with" | "the Enterprise accounts", "accounts you've emailed or met in the last 30 days" |
| "company profile", "no role map is set" | "your admin hasn't said who handles this, so this is my guess" |

## Scores and Staircase reads

| Not this | Say this |
|---|---|
| "stored", "Stored:", "(stored)" | "Staircase shows", or drop |
| "Stored health: 18 Average, 7 High, 3 Low" | drop in lists; "health average" only when it matters |
| "health score is 0, which means no data", "health not scored" | "no health score yet" |
| "risk 5", "risk 4 or 5" | "high risk (5 of 5)" the first time, then "high risk" |
| "risk not assessed (health 64 used)", "unassessed" | "no risk score yet" |
| "AI Churn Risk Analysis", "AI Renewal Analysis", "AI Churn Analysis" | "Staircase's churn read", "Staircase's renewal read" |
| "ChurnRisk insight", "dark insight" | "Staircase flagged churn risk", "Staircase flagged it as quiet" |
| "CS Stage reads '7 Will Churn'" | "their CS stage reads 'Will Churn'" |
| "bottom third / top third of the book by revenue" | drop; "one of your larger accounts" only when it explains the order |

## Events

| Not this | Say this |
|---|---|
| `exceptional_positive`, `exceptional_negative` | "a very positive note", "a very unhappy note" |
| `churn_risk` event | "a churn warning" |
| `farewell` event | "a possible contact departure" |
| `renewal_discussion`, "last renewal discussion" | "last renewal conversation" |
| "checkpoint", "checkpoint at 117 days" | "renews 28 Feb: time to start the renewal conversation" |

## List words

| Not this | Say this |
|---|---|
| "trigger", "trigger class", "is the trigger", "lane" | drop; say what happened, or use a tag below |
| "Customer waiting" | "Waiting on you" |
| "Fresh risk", "Open situation" | "New risk", "Ongoing risk" |
| "Meeting follow-up", "Meeting prep" | "Recap owed", "Prep" |
| "Stakeholder change" | "Contact change" |
| "Gone quiet", "one-sided", "chasing" | "quiet since 5 Oct", "not answering us since 5 Oct" |
| "Expansion ready" | "Ready to grow" |
| "PINNED", "pinned" | "Don't miss" |
| "Why now:", "Read found:", "Action:" | drop the first two; "Ready:" for the third |
| "holding reply" | "a quick 'working on it' reply" |
| "covered", "Covered by:" | "<name> is handling it" |
| "Read, no action:" | "Checked, nothing needed now" |
| "live two-way, proactive items dropped" | "you're already talking with them" |
| "suppressed", "hidden by the ledger", "dismissals", "ledger" | "hidden because you cleared them"; never name the ledger |
| "Record check", "record fix" | "CRM may be out of date", "CRM fix" |
| "Suggestion" | "my suggestion; no email names it" |
| Plan codes ("D defend, M manage closure") | the play in words on each row; counts in a sentence ("2 need a save plan, 1 is closing") |

## Proof and sources

| Not this | Say this |
|---|---|
| "Rank rule:" sentence | "Ranked by what's at stake, who's waiting and for how long, and how quiet it is" (proof line only) |
| "Window: threads ... (reply rows) and ... (other rows)" | "emails and calls from 5 Oct to 3 Nov" |
| "Seen: 18 of 28 accounts read: 7 reply rows (41 of 104 threads)" | "I read 18 accounts closely and 19 email threads in full" |
| "fetched", "summary only", "not quotable", "per the summary" | quote only fetched text; otherwise "per the call notes" or "per the email summary" |
| `comm_Email_...`, `comm_Video_...`, "[n]", "E-3318" | "Dana's email, 3 Nov"; ids on `why 2` |
| "Customer said", "the customer wrote", "their contact" (on a quote) | the speaker's name and title from the stakeholder record: "Priya Shah, Operations Manager, 29 Oct"; the name alone when there is no title |
| "We said", "our side" (on a quote) | "you", or the colleague's first name and role: "Lee, renewal owner" |
| "As of: <time> (latest touch seen, <time> UTC)" | "data as of 09:30 MT" |
| "Sources: three report pulls ..." | drop; on `why` |
| "Ask class ... 0.8 plus 0.1", "priority 72", "Stakes 0.96" | drop; on `why 2`, in words: "high: the customer has waited 6 days and it renews in 72" |
| "judgment call, see the log" | the judgment, in one sentence |
| `user.manager`, `customer.event.next_event`, any dotted id | "your manager", "the next meeting Staircase shows" |
| "Saved spec (re-run this)" | "Want the report setup so you can run it again?" |
| "Reconciles: groups sum to N; COUNT is N" | report mode only; never in a list |
