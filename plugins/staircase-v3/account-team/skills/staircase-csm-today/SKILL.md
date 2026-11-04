---
name: staircase-csm-today
description: "Your daily what-needs-me list from Staircase AI: the top 5 actions across your book grouped by when to act, first move up top, each teed up to act (the customer email drafted, the Slack ask to your own team written, a meeting or hold proposed, an escalation framed). It reads the threads behind the top rows before trusting them. Use for 'what needs me today', 'what's waiting on me', 'which of my accounts have gone quiet', 'which of my accounts are at risk', 'did any of my champions leave', 'who could I ask for a reference', 'plan my week', 'what changed in my accounts this week', 'write my weekly update', 'I'm back from PTO, what did I miss', 'what happened since Oct 20' and 'I'm taking over <name>'s book'. Say done, not mine or snooze on an item and it stays off your list. Not for one account in depth (staircase-account-brief), a renewal forecast (staircase-renewals), a recap of one call (staircase-follow-up), or creating CTAs and Timeline entries. Needs the Staircase AI connector."
license: MIT
compatibility: "Needs the Staircase AI MCP connector. Works in Claude Code, Claude Desktop, Cowork and claude.ai. The scoring script and the dismissal file need a runtime that runs Python and writes files (Claude Code); elsewhere the skill runs a labeled reduced ranking and keeps dismissals in a pasted state line."
metadata:
  version: "3.0.0-alpha.1"
  layer: "persona"
  pack: "account-team"
---

# Staircase CSM Today

A CSM opens the day with a full book and no time. This skill answers "what needs me today" with the first move in one line and five actions grouped by when to act, ranked by a rule it shows on `why`, each one ready to go: the email drafted, the internal ask written, the meeting proposed. It runs the shared engine in `references/action-priority.md` (stage 1 scores the book from reports, stage 2 reads the threads behind the shortlist) and picks each action with `references/action-types.md`. It never restates either file: read them, follow them, and use this skill for what they leave open (modes, the read, the list, the drafts, dismissals).

Stage 1 alone is never the answer. In the engine's dry run, the report-only ranking put 3 wrong rows in a top 12 and missed 3 of the final top 8. Every list in this skill comes after the stage 2 read.

## Read these, at these moments

| File | When |
|---|---|
| `references/scope.md` | Before the first scoped call (book resolution, statuses, the scope line) |
| `references/data-rules.md` | Before the first report (Dates first) |
| `references/action-priority.md` | Before stage 1 (rank rule, score, triggers, pulls, stage 2, suppression, list shape, ledger) |
| `references/action-types.md` | Before teeing up any item |
| `references/evidence.md`, `references/delivery.md`, `references/plain-words.md` | Before the first answer (surface, layers, verbs, states, the user's words) |
| `references/trust.md` | Before any draft |
| `references/company-profile.md` | Once per session (weights, list size, thresholds, teams, exclusions, resources) |
| `references/safe-to-ask.md` | Before a references-lane row |

The pack build also copies three core skills in; this skill uses two of them (`references/staircase-voice.md` is not used here): `references/staircase-account-brief.md` (a one-account brief, with its prep and takeover lenses) and `references/staircase-follow-up.md` (a meeting recap). Read one only when the user picks an item that needs it ("brief <account>", "recap draft", "takeover brief"). If a file is missing, offer the ask that triggers the skill ("catch me up on <account>", "I just got off a call with <account>").

## 1. Before the first call

1. **Connector.** Staircase tool names end in `staircase_run_report`, `staircase_get_recipe` and so on; the prefix differs by install. If none are present, stop with the no-connector state in `delivery.md` (in Claude Code add the command: `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`).
2. **Clock.** Read the local date and time with a tool (`date`) when one runs, else use the date the conversation gives. Local today anchors every window (`data-rules.md`, Dates). It prints as "data as of <time>" in How I built this.
3. **Recipe.** `staircase_get_recipe` with `portfolio_resolution`. Ask for `churn_signal_resolution` later, and only when a fresh-risk or open-situation row reaches the top 5 and the action turns on save versus closure. Never use `staircase_analyze_account`.
4. **Metadata,** once per session, never pasted. The payload is about 100k characters; when the runtime saves it to a file, query that file with a tool (`jq`) and never read it whole. Take `current_user_id`, the user-reference role fields, the Active option id, and the insight and event ids in `argument_options`. Any insight or event id the engine names that is absent goes in `--drop` and is named in the trail.
5. **Company profile.** Weights, `list_size`, thresholds, `teams`, `exclusions` and `resources`. `not set` means the engine default, and the answer says "default".
6. **Dismissals.** In Claude Code the script reads `~/.staircase/ledger.jsonl` itself. Elsewhere, look for an `ST-STATE` line the user pasted in this conversation and apply it.

## 2. Route the ask to a mode

| The user says | Mode | What changes |
|---|---|---|
| "what needs me today", "what's waiting on me", "what am I missing", "my list" | Today | The full engine, every lane |
| "which of my accounts have gone quiet", "who haven't I talked to in a while" | Lane: gone quiet | `--lane quiet`; quiet and one-sided chase only |
| "which of my accounts are at risk" (plural) | Lane: risk | `--lane risk`; live accounts stay in (it is a state list); prints risk coverage and the unassessed low-health accounts. One account ("is X at risk") goes to the account brief |
| "did any of my champions leave", "who's new at my accounts" | Lane: stakeholder change | `--lane stakeholder`; every farewell event in 30 days is read |
| "who could I ask for a reference", "any happy customers I could ask" | References lane | Section 6, on the whole book |
| "plan my week", "what changed in my accounts this week", "how's my book", "write my weekly update" | Week | Section 8 |
| "I'm back from PTO", "what did I miss", "what happened since <date>" | Since | Section 9 |
| "I'm taking over <name>'s book" (a book, not one account) | Takeover | Section 10. One account goes to the account brief |
| `done 2`, `not mine 3`, `snooze 1 until Friday` (also "4 is wrong", accepted, never taught; "they asked us to stop contacting them", accepted) | Clear | Section 11 |
| `draft 7`, `draft all`, `more`, `show hidden`, `why`, `why 2`, `brief <account>` | Expand | Tee up an extras row or put drafts in the user's Slack or Gmail drafts; show the next rows; list the items the user cleared; print the trail (section 12); brief one account |

Any mode accepts "for <name>'s book" (a manager or a tester): resolve that person with the recipe's single-user step, say whose accounts they are in How I built this ("<name>'s 28 active accounts where they're the CSM"), and pass their user id as `--scope-id`. On such a run: the headline, items and drafts speak to that person as "you" (the list is written for them), and the proof lines name them; drafts are signed with their name; a customer waiting is "waiting on our side", never that person's lapse, and no reply time is shown per person (`trust.md`, people are never ranked); What I couldn't see says these are the threads you can see, so <name> may see more; times print in the signed-in user's zone, labeled; no morning-push offer. "What changed" belongs to this skill for book holders; "who do I owe a reply" and "keep me posted" belong to the follow-up skill.

## 3. Scope

- The user's book through `portfolio_resolution` (single user: fingerprint, picking rule, COUNT check). Never `customer.owner` by default. When the recipe's picking rule ORs several role fields, pass each as its own `--role-field`; when it picks one dominant field, the others stay out and What I couldn't see names them with their counts and the phrase that adds them ("Not included: 9 accounts where you hold another role, say 'include my other roles'"). Active only (`scope.md`, statuses), said as "your 28 active accounts". Leave out `exclusions` and say how many in the trail.
- First run with no saved scope: the first-run state in `delivery.md` ("I found 28 accounts where you're the CSM. Is that your book?"), then the list.
- No book (every role-field count is 0): say so in one line and offer "for <name>'s book", or "accounts you've emailed or met in the last 30 days" through `staircase-ask`. This skill ranks books.
- Name the CSM: the recipe's user row gives `user.full_name`. In threads, that name's messages are "you"; any other participant of type User is a teammate.

## 4. Stage 1: score the book

1. Build the configs with the script (they follow the pulls in `action-priority.md`, with label equal to key so the CSV headers match what the script reads):
   `python3 -I scripts/score.py pulls --role-field <field id from metadata, customer.<field>> --user-id <the book holder's user id> --today <local today> [--since <date>] [--drop <ids>]`
   Pull B also carries the stored health band (`customer.buckets.health`: the week header, and the expansion gate, where only Low blocks), the parent account's id (`customer.parent`: a parent and child in the book make one item) and the account's page (`customer.url`: link the account name on its item).
2. Run every config it prints (A, B, C1, C2, EV, COUNT) in parallel with `staircase_run_report`, each with a one-sentence `intent`. Save each `csv` to its own file in a scratch folder exactly as returned. EV is the book's `lifecycle_event` report for the window, with top-level `arguments.dateRange` set: it gives the event ids that fresh-risk and stakeholder rows need, book-wide, in one call.
3. Check: each pull reads `complete: true` and COUNT equals the rows of A; a mismatch is named in `Seen:`. The configs fetch the whole book in one page of up to 1,000 rows, unsorted, because sorting a customer report on `customer.id` is silently ignored and paging on it can drop or repeat rows. A book over 1,000 accounts is out of this skill's range: say so.
4. On `code: timeout` (or `invalid_config` saying the report takes too long): never resend it. For A, rerun `pulls --split-a` and run A1 and A2. For any other pull, split its columns in half once. Say so in `Seen:`.
5. Rank: `python3 -I scripts/score.py rank --today <local today> --now <the current time in UTC, YYYY-MM-DDTHH:MM> --a <A files> --b B.csv --c1 C1.csv --c2 C2.csv --ev EV.csv --scope-id <book user id> [--mode week|since|takeover] [--lane <lane>] [--since <date>]` (`--now` is read as UTC, like every stored time; a local time there shifts the 48-hour and 7-day windows by the zone offset; leave it out and the script uses the machine clock) (add `--ledger <path>` only to point at a ledger other than `~/.staircase/ledger.jsonl`). It prints the meetings strip, the ranked candidates with stakes, urgency and attention, their fingerprints, the stage 2 shortlist (reply rows and other rows) with each account's page, and what it left out or changed (ledger, do not contact, quiet folded into a meeting, related accounts made one item, live two-way, no trigger).
6. **No script runtime** (chat, Cowork without Python): reduced mode from `action-priority.md`, "Scoring with no script", labeled in How I built this with that file's sentence. Build the same pulls from the column list there (the exact configs are in `scripts/score.py` for reference) and detect triggers with the trigger table. Shortlist: pinned rows first; then by trigger class in this order: renewal decision, reply needed, meeting follow-up, fresh risk, meeting prep (renewal in 180 days, risk 4 or 5, or a customer thread open; the rest of this week's meetings are read in week mode and raised by what the read finds), open situation, stakeholder change, renewal checkpoint, quiet and one-sided chase, expansion, record check; within a class, stakes tier first (1: renewal inside 60 days or risk 4 or 5; 2: renewal inside 120 days or risk 3; 3: the rest), then renewal date, then risk. On live two-way accounts drop quiet, chase and checkpoint items only (`action-priority.md`, Suppression); an account that meets in the window folds its quiet or chase into the meeting. Run stage 2 on the top 14. After the read, hand-score the confirmed rows (15 or fewer, per `action-priority.md`) with the score formula, taking value from the account's revenue rank in the book (top third 0.83, middle 0.5, bottom third 0.17, blank or 0 is 0.5), and order the list by that score.

## 5. Stage 2: read before you list

Follow "Stage 2" in `action-priority.md` for the shortlist the script printed (the top 14 plus every reply and pinned row, and in week mode every account that meets this week: at most 20, or 26 in week mode, read in calls of up to 20 accounts). Concretely:

1. `staircase_list_communications` for the reply rows, `date_range` the last 30 days as an explicit array, `per_account_limit` 6; and one more call for the other rows, the last 90 days, `per_account_limit` 6. Set `limit` to accounts x 6 on each call (`data-rules.md` rule 17: the default 100 drops rows past 16 accounts). Rows come newest first, so a busy account still shows its last few days, and a quiet or checkpoint row shows its last real exchange (a 14-day read shows nothing for a trigger defined on 21 to 90 days of silence). Up to 20 accounts per call.
2. `staircase_list_communications` with the `event_ids` (from EV) of the shortlist's farewell, organization_personnel_change, churn, churn_risk and exceptional_negative events, plus the `exceptional_positive` events of up to 2 references-lane candidates.
   2b. For those references candidates (at most 2 accounts), one more `staircase_list_communications` call over the last 45 days, `per_account_limit` 6: the safe-to-ask conversation read.
3. `staircase_fetch_evidence` in batches of up to 20 ids, at most two calls, filled in this order: the thread or call each top-5 draft will quote; then `mixed` email threads on reply rows where the reply depends on who wrote last, highest stakes first. What does not fit stays a summary: never quote it. In the answer it reads "per the call notes" or "per the email summary"; the trail marks its evidence id "summary only".
4. `staircase_account_info` for each top-5 row whose action turns on a stored analysis (open situation, fresh risk, renewal decision): the risk, churn or renewal analysis, named as stored.
5. One `stakeholder` report on the top 8 accounts, run once the read has settled the order: filter `stakeholder.customer` In those ids and `stakeholder.type` In [the Human option id from metadata]; columns `stakeholder.customer`, `stakeholder.name`, `stakeholder.email`, `stakeholder.title`, `stakeholder.last_engagement`, `stakeholder.last_reach_out`; plus `stakeholder.last_engagement` on or after today minus 179 days (contacts who engaged in the last 180 days); sort by `stakeholder.last_engagement` descending, then `stakeholder.name` (a sort on an id field is silently ignored); one page of 100 (say so in `Seen:` when it has more). It gives the draft addresses and the touch budget for proactive items (`stakeholder.last_reach_out` counts any outbound, so it is a proxy), and the title behind each quote: match the quoted message's sender (its `participants`) to these rows by email, then by exact name, and pass `speaker_name` and `speaker_role` (`data-rules.md` rule 28). No match or no title: the name alone.

Then decide each row with the trigger table in `action-priority.md`:

| Row | Keep it when | Otherwise |
|---|---|---|
| Customer waiting (reply) | The thread's last message is from a customer contact (Stakeholder), nothing from our side came later on that thread or on a split thread (a later outbound to the same contact with the same subject, ignoring "Re:" and "Fwd:"), and it is a real ask: not a solicitation, a newsletter, an automated notice or thanks | Drop it, or reclassify the account by what the read shows. Class the ask for its urgency: escalation, billing or commercial 1.0; technical, a data request or a how-to 0.8; scheduling or a resource share 0.6. A scheduling ask whose proposed date already shows as the account's next meeting (`next_mtg`) is handled: the Checked line |
| Meeting follow-up | A summary or transcript exists, nothing went to its participants since, and it was not rescheduled | Drop it. No recap without a transcript or the user's notes |
| Meeting prep | The read shows what the meeting is for: a business review (EBR, QBR, value review), a renewal or pricing talk, an executive or a new contact attending (titles from the stakeholder report), an open ask or a blocker in the latest threads, or a calendar invite whose subject names one of these. Re-score at urgency 0.8 when it is within 48 hours, 0.6 later this week. The draft is 3 to 5 agenda lines from what the read found; a quiet spell the script folded in becomes one of them ("raise the quiet since 5 Oct") | A routine sync with nothing open stays on the meetings line only. Never the Checked line while an ask or a blocker is open: an open blocker before tomorrow's meeting is the item |
| Fresh risk, stakeholder change | The event's threads show a real departure, arrival or risk, and which side it is on (ours or theirs, one product or the account) | A false event drops to the Checked line ("Checked, nothing needed now", section 12). An acknowledged one with a dated next step already set drops there too, naming the step; acknowledged with no next step stays, and the action is save or manage closure |
| Renewal decision | The threads show the decision is still open | A recorded outcome stays as a renewal decision (urgency 0.9) with the action "close it out", plus the CRM fix |
| Quiet, one-sided chase | No two-way exchange since the stage 1 dates (customer last engaged over `quiet_days`, default 21, ago), the contacts are still there, and the last "engagement" was a person, not a newsletter or an automated mailbox | Drop it |
| Renewal checkpoint | No renewal conversation in the read since the checkpoint opened, and no outcome recorded | A known non-renewal becomes a renewal decision with the action "close it out"; a signed renewal drops to the Checked line (plus a CRM fix when the date is stale) |
| Open situation (risk 4 or 5, no fresh event) | The stored analysis and the 90-day read show a live problem with no dated next step | A dated next step in motion drops to the Checked line, unless pinned |
| Expansion ready | No open problem in the read and nothing commercial already moving with the account executive | An inbound commercial ask makes it a reply; anything open drops it |
| Record check | The stale date itself is never ranked; the account's other triggers (a risk 5 open situation, a reply) still rank, and their item names the stale date. Stale-date branch (renewal passed more than 30 days ago): zero threads in 90 days. Revenue-0 branch: the field reads 0 while the threads show a paying customer | Drop it; a record check is never above a live item on the same account. Stale dates with threads are never items: the script lists them for the record-check line |
| Risk heard in the read, no event behind it (a competitor chosen, a product they pay for now dropped, a decision-maker's complaint; a deal we lost for a product they never bought is a note for whoever owns that deal, not a risk) | The words are in a fetched message or a call summary, dated | Reclassify the account as a fresh risk (urgency 0.85 inside 14 days, else 0.6), labeled "from the emails, not a Staircase warning", with your confidence. It outranks a teammate handling it: the item names the teammate who holds the thread |

- **Pinned rows.** A renewal inside 60 days (or passed in the last 30) on a risk 4 or 5 or ChurnRisk account is marked pinned by the script (`action-priority.md`, list shape). It stays on the list (top 5, Also worth a look, or the Closing line) even when the read shows the save or the closure in motion: the action is the next step. Only the ledger removes it. The pin guarantees its place on the list, not first place: section 6 groups it.
- **Settled losses go to the Closing line** (`action-priority.md`, list shape), pinned or not: a written non-renewal or churn notice that holds (fetched, or in the stored churn analysis), a closure being managed, or offboarding finished while the account still reads Active (the CRM fix rides on the same line). One line each: what closes, when, and who has the commercial steps, from the renewal-owner field. Such an account stays in the ranked list only while the user owns a dated step: a customer waiting on them, a meeting with them in the window, an export or offboarding task, or a product that stays (then the item is about the product that stays).
- **Do not contact.** The script marks accounts the user asked us not to contact. Their remaining items get internal actions only (a Slack to the renewal owner or the team, a close-out, a CRM fix); a reply to a thread the customer started stays a reply. Never a proactive customer draft on them, and How I built this says how many accounts carry it.
- **Related accounts.** The script makes a parent and its child one item; read both, and name both in the heading ("Lumen Freight (with Lumen Group, its parent account)"). The draft goes to the contacts of whichever account the read shows is talking.
- **Covered by a teammate:** a teammate (another User) wrote after the customer on that same thread, or the customer addressed the teammate and the topic is theirs (a renewal owner's terms thread, a support engineer's ticket). One clause in the Checked line, "<name> is handling it", not an item. When the customer's last message there is over 2 business days old and the account renews in 120 days or sits in the top third of the book, it becomes an Also-worth-a-look row instead: a Slack nudge to that teammate. A thread where the customer wrote last and addressed the book holder is waiting, whatever teammates wrote elsewhere.
- **Add what the counts missed.** A customer waiting in a thread read for another reason becomes that account's item when it outranks the reason it was read for.
- **Before dropping an account, test its next trigger.** When the read drops an account's top trigger, weigh the next one in its Also column against the table above before the account leaves the list (a dropped record check can leave a live risk 5 open situation behind it).
- **Re-score a reclassified row** as 100 x stakes (from the script) x the new trigger's urgency, with attention only for proactive triggers. A confirmed reply takes its urgency from the ask class in the trigger table, dated by the first unanswered customer message on that thread (a re-ping today on a 12-day-old ask is 12 days old; the script's "under 1 day" flag is account level). A genuinely same-day ask that is not commercial, billing or an escalation takes the trigger table's x 0.7, and never takes the customer-waiting slot (the suppression table's "waits"). Never re-multiply rows you did not reclassify.
- **Reply fingerprints.** For each confirmed reply the fingerprint is `<account_id>|reply_needed|<thread_key>@<the customer's last message time, UTC, YYYY-MM-DDTHH:MM, from the fetched message>` (the date alone when the thread was not fetched). Ledger lines carry the dismissal time, so a customer message later the same day counts as newer. Run `python3 -I scripts/score.py check --today <today> --scope-id <id> --fp <fp> <fp> ...` on them and drop what it suppresses.
- **Events not read.** Step 2 reads the events behind the shortlist's kept items. A farewell or risk event behind a trigger the script dropped (live two-way) stays unread, even on a shortlisted account; name it in What I couldn't see ("Not opened: possible contact departures at <accounts> → `check departures`"), never as a finding.
- **Base rate before absence** (`evidence.md`): "no renewal discussion" or "no decision-maker touch" needs the share of the book that carries the field first.

## 6. Build the list

- **One item per account,** in the engine's order after the read. Tags are plain words (`plain-words.md`): Waiting on you, Renewal, At risk, Quiet, Contact change, Meeting, Growth. A tag goes in a heading only when the move does not already say it.
- **The customer-waiting slot.** If customers are confirmed waiting on the book holder (not covered by a teammate) and none reached the top 5 on priority, the longest-waiting one takes 5th place, whatever the account's value. If one is already in the top 5, nothing moves. Ties go to the longer wait, then the nearer renewal.
- **The top 5** (`list_size.full_items`) are full items. Then **Also worth a look:** up to 7 one-line rows (`list_size.more_options`). Say how many more exist and offer them (`more`); never drop rows silently.
- **Group by when.** The top 5 print in these groups, in this order. Inside "Do today" the earliest deadline leads (a meeting's start time; for a customer waiting, the longest wait), then the engine's order; inside the other groups the engine's order holds. Numbers run 1 to 5 in the order shown, so the headline's first move is item 1. An empty group does not print. Every pinned row's heading ends "(don't miss: renews <date>, high risk)", in whichever group it falls.

| Group | Goes there |
|---|---|
| Do today | A pinned row the read has not settled (it can still be saved); a customer confirmed waiting on the user with a commercial, escalation or technical ask (a scheduling ask or a resource share goes to This week unless its date is today or tomorrow); a meeting today; anything whose deadline is today or tomorrow, so the message has to go today |
| Prep for <day> | A meeting item (agenda or prep) whose meeting falls later in the window; one group per day |
| This week | The rest of the top 5 |

A row the read has settled into a loss is not in the top 5: it goes to the Closing line (section 5), and the next row moves up.

- **Meetings** (next 48 hours in today mode, 7 days in week mode): a `### Meetings` section after the extras, one bullet per day, with "(item n)" beside an account that has an item. The time is the account's next meeting with anyone on our side (`customer.event.next_event`), not the user's calendar: say so once. Cross-check the strip against the rows: an item or extras row whose account meets in the window says so in a bullet ("They also meet with us Thu 12:00"). A meeting the read raised (section 5) is also an item; its draft is 3 to 5 agenda lines from the open asks, sources in words, and the full brief on `brief <account>`.
- **References,** at most 2 rows, only when it has a candidate: an `exceptional_positive` event in the last 14 days on an account that passes the stored gates (`safe-to-ask.md` check 1). Only candidates get the 45-day read (step 2b) and the speaker and ask-budget checks. One line, "**Could be a reference:** <account>, <the praise and its date> → `draft the ask`", or "on hold: <reason>". An account that fails check 1 is not a candidate and is not read. The user is the CSM, so the CSM check is theirs: the fitting ask is drafted on `draft the ask`, and a quote is never publishable without written consent. On the references ask itself, run safe-to-ask over the whole book (10 accounts read at most) and rank as it says.
- **Two lines under the extras,** each only when it has rows: **CRM may be out of date:** the record-check line (`action-priority.md`, list shape), ending "→ `draft the CRM fix`". **Checked, nothing needed now:** the rows the read dropped, each with its reason in a few words, and "<name> is handling it" for covered rows.

## 7. Tee up every item

Pick the action with the situation table in `action-types.md` and prepare what its evidence column names. For the top 5:

- **Recipients.** Customer email: the contacts who wrote or attended, by name (fetched messages carry `sender_name` only), with the address from the stakeholder report; when no address is there, write the name and "(address not in Staircase)". Slack ask: the colleague who wrote our side's last message on that thread or topic, naming the role-field holder too when it is someone else ("Slack Danica, cc Tré, the renewal owner"); when that last message is the user's own, the item is the user's next step, not a Slack. With no colleague on the thread: the person in the account's role fields (`customer.<role_field>.full_name`, one small report for the top 5 accounts, fields from `role_map` in the profile; when not set, a field whose label names the job, shown as "(my guess for the <job>)") or the team in `teams`. The user's manager is `user.manager` on the user's own row. Unknown: write `<who>` and say so.
- **Order.** When the customer reply depends on an internal answer, the Slack ask is the draft and a quick "working on it" reply sits under it as its own labeled block ("**Draft 1, reply to <name>**").
- **Dates and times** in drafts and items are in the user's local zone (a message at 18:00 local on 2 Nov is 2 Nov, even when its UTC date is 3 Nov).
- **The draft itself:** short, in plain words, citing only what that recipient said or was present for, shaped per `delivery.md` (Act). No roadmap, prices, terms or dates the user did not give. Ours carry names; theirs read "you mentioned". A next step no thread names is labeled "my suggestion" outside the block. Meeting proposals carry 2 to 3 times only when a calendar connector shows them, else "a few times that work for you this week".
- **Sources** in an item read as sender, date and channel ("Priya's email, 2 Nov"). Evidence ids go to the trail (`why 2`), never under or inside a draft.
- **Where the drafts go.** As text in the answer. With a mail or Slack connector, `draft 1` puts it in the user's Gmail or Slack drafts and `draft all` does every one; say so once in the Drafts heading. Nothing is sent, posted or invited without the user's yes, each time (`trust.md`). With Gainsight CS connected, an open CTA with the same reason turns the item into "advance this task"; the ranking never depends on it.
- **Extras rows** name the move and its verb in code style ("check-in email → `draft 8`"). Draft on ask.

## 8. Week mode ("plan my week", "what changed this week", "how's my book")

Run stage 1 with `--mode week`: every meeting in the next 7 days is a candidate and is read in stage 2 (an EBR, a pricing call or a new executive is what CSMs plan a week around, and only the read can tell one from a routine sync); renewal checkpoints reach 180 days (the value review); the renewals line stays 120 days. The answer is the today shape over the week, with three changes:

1. The headline counts the week ("**5 things need you this week.** First: ...").
2. After the Checked line: `### Meetings this week`, one bullet per day, "(item n)" beside accounts with an item; then `### Renewals in the next 120 days`, one bullet, soonest first. Health bands, event counts and the quiet count go to the trail; the risk coverage goes in What I couldn't see. Scores are current values, not changes over the week: never write a trend.
3. **Your weekly update** is the last draft, and one line above the drafts says so ("**Also ready:** your weekly update for <manager>, at the bottom."). A Slack draft to the user's manager (from `user.manager`), 6 to 8 lines in the user's voice: wins (dated: a renewal closed, a very positive note quoted only from fetched text), what I'm watching and what I'm doing about it, renewals coming, where I need help. Facts only from this run's reads; their evidence ids go to the trail. The user sends it.

## 9. Since mode ("back from PTO", "since <date>")

- The window starts at the date the user gives, at most 90 days back (the thread read caps there; say so if they ask for more). Pass `--since <date>` to both `pulls` and `rank`: Pull B and EV widen to the absence, so a customer who wrote on day one of it still counts as waiting.
- The headline says what changed while they were out and the first move. **While you were out** follows the extras (the scan stays first): up to 10 accounts by stakes, one line each with what happened (dated events, customer emails, meetings held without the book holder, meaning their name is not among the meeting's User participants, renewals that passed), from the script's per-account digest and the stage 2 read. Teammates who covered: "<name> handled it".
- Reply rows read from the since date; threads read out of `total_count` for each busy account go to the trail.

## 10. Book takeover ("I'm taking over <name>'s book")

- Scope: the outgoing person's book through the recipe (single user), or the accounts the user lists. Run stage 1 with `--mode takeover` (stakes first, with a bump for a customer waiting or a fresh event), then the stage 2 read on the top 14.
- Rank rule for this mode (verbatim on `why`, one clause in How I built this): "Ranked by what is at stake (renewal nearness, risk, value within the book), with a customer waiting or a fresh event moved up."
- **Take these first** (the top 5), each a bold heading line and bullets (`delivery.md`, Chat layout): why first in the heading; what is open now, dated, as the first bullet; the last bullet "- **Ready:** three questions for <outgoing owner> and an intro email to <main contact>, held until you confirm the change is announced → `draft n`" (`trust.md`, held drafts). The questions and the held email sit with the drafts. The account brief's takeover lens on ask ("I'm taking over <account>").
- **The rest,** one bullet each, ordered by renewal date: "- **<account>** · renews <date> · <risk in words> · last two-way <date> · <n> open threads".
- Never quote the outgoing owner's own emails to the customer.

## 11. Clearing items

The user says `done 2`, `not mine 3` or `snooze 1 until Friday`, numbered from the latest list in this conversation; "4 is wrong" is accepted, never taught (`delivery.md`, Verbs). Record it and confirm in one plain line ("Done: <account> stays off your list until something new happens there."). Clearing covers the account's situation as the user saw it, not only the one trigger: the script hides every item on that account until something newer than the dismissal happens (the customer writes again, a new event, a meeting, the next renewal checkpoint) or the snooze ends. "Not mine" on the whole account hides it for good. The ledger is the signed-in user's own: on a "for <name>" run it changes only that user's view of the book.

| Said | State, reason | Also |
|---|---|---|
| done | done, done | Nothing more. Sync lag is why "done" must stick: the reply may not have reached Staircase yet |
| not mine (the item) | dismissed, not_mine | If a teammate owns it, offer a one-line Slack to them. When the item rests on a stored field, offer the CRM fix note: the field, its value, its date, what the threads show |
| not mine (the account) | dismissed, not_mine, fingerprint `<account_id>\|*\|*` | The book may be wrong: offer the CRM fix note to the admin (`action-types.md`), naming the role field |
| wrong (accepted) | dismissed, wrong | As "not mine" on the item |
| snooze until <date> | snoozed, not_now, until the date | Resolve "Friday" to a date and print it |
| "they asked us to stop contacting them", "don't contact <account>" (accepted, never taught) | dismissed, do_not_contact, fingerprint `<account_id>\|*\|*` | Confirm: "<account>: no customer messages from me; internal steps only. Say 'ok to contact <account>' to lift it." |
| undo, take back, ok to contact | lifted, the same fingerprint (and the reason, when lifting one kind only) | Confirm what came back |
| "<account> and <account> are one" | linked, fingerprint `<account_id>\|*\|*` with `--with <the other id>` | They show as one item from the next run |

- **Claude Code:** `python3 -I scripts/score.py ledger --today <today> --fp <fingerprint> --state <state> --reason <reason> [--until <date>] [--with <id>] --scope-id <book user id>`. It appends to `~/.staircase/ledger.jsonl`. The next run's `rank` reads it before ranking, and `check` covers reply threads in stage 2.
- **Elsewhere:** print the state line from `action-priority.md` (under 300 characters, every active entry) under the To act line, introduced as "Paste this line next time so I remember what you cleared:", and apply a pasted line before ranking.
- How I built this says how many items are hidden because the user cleared them, and "show hidden" lists them.

## 12. Answer shape

Follow `delivery.md` (Work a list: the four layers and their budgets, verbs, states; Chat layout: where the eye goes) and `plain-words.md` above the proof lines. Three levels only: `###` sections, a bold line per item, bullets. No `#` or `##`. In order:

1. **Headline,** 30 words at most: the count in bold, then the first move (item 1), its deadline, what is ready, with the verb in code style. On a first run (no cleared items yet), one italic tip line under it: "*Tip: reply with a number and a word, like `draft 1` or `done 3`. Plain words work too.*" It stops once the user has used any verb.
2. **The top 5,** grouped by when under `###` headings (section 6), each a bold line and up to 3 bullets: `**1. <Account>** · <the move as a verb>, <the deadline>`. The bullets say what happened, who, when, and a meeting in the window, one fact a bullet. A tag goes first and only when it changes the move (`- *Don't miss: renews 14 Nov at high risk.*`). A customer's words are one quote line nested under the bullet they back (`> "exact words" · *Name, Title, when*`), at most one an item, fetched text only, the name and title from the stakeholder record (the name alone when there is no title). The last bullet is the move: ``- **Ready:** <the kind of draft and the recipient> → `draft 1` ``, with the also-offer on the same bullet ("Also: ... → `brief <account>`"). The rank factors decide the order; they print in words only on `why 1`.
3. **Also worth a look,** one bullet per row numbered on from 6 (``- **6. Lumen Freight** · what is going on. The move → `draft 6` ``). Then, each only when it has rows, a bold label with bullets (Could be a reference, CRM may be out of date, Checked, nothing needed now) or a `###` section (the meetings, and the mode's extras: week: Renewals in the next 120 days; since: While you were out; takeover: the rest). Week mode (section 8) keeps this layout: Meetings this week and Renewals in the next 120 days are `###` sections, and "Also ready: your weekly update for <manager>, at the bottom" is an italic note.
4. **Drafts,** after a rule (`---`), under `### Drafts` with one italic line ("*Nothing is sent. `draft 1` saves one to your Slack or Gmail drafts; `draft all` does every one.*"), numbered to match the items, each a bold label line and then the code block with only the message, per `delivery.md` (Act).
5. **Proof,** after a rule, two bold-label paragraphs. **How I built this:** whose accounts in words ("your 28 active accounts where you're the CSM"), the dates read, how much was read ("I read 14 accounts closely and 18 email threads in full"), "grouped by when to act, then by what's at stake, who's waiting and for how long, and how quiet the account is", the hidden count, the reduced-ranking sentence when it applies, "data as of <time>". **What I couldn't see:** emails Staircase can't see and the user's calendar; the coverage gap that changes a decision ("risk is scored on only 6 of your 22 accounts, so a quiet account isn't a safe one"); what was not opened and the roles not included, each with the phrase that opens it, in code style ("`include my other roles`").
6. **To act** (`delivery.md`, Verbs, every verb in code style); outside Claude Code the state line follows when anything is cleared, then the board offer when it earns one, in italics with `board` in code style (the board, below).

Example (invented accounts, dates and names; the full sample is `evals/sample-output.md`):

````markdown
**5 things need you today.** First: Copperline, waiting since 29 Oct on a licensing question, meets with us at 15:00 today. Your Slack to Lee is ready (`draft 1`).

### Do today

**1. Copperline** · get Priya a licensing answer before the 15:00 call
- Priya asked on 29 Oct whether a support seat uses a paid license. Nobody has answered, and she wrote again this morning:
  > "Can you confirm before we add the next team?" · *Priya Shah, Operations Manager, 08:12 today*
- **Ready:** a Slack to Lee Moreno (renewal owner), plus a "sorry for the wait" reply to Priya → `draft 1`

### This week: closures to hand off

**5. Orchard Health** · close out the analytics product; the core product stays
- *Don't miss: renews 30 Nov at high risk.*
- They declined a 3-month extension on 27 Oct, and the transition runs to 26 Nov. The notice covers one product, not the account.
  > "We'll keep the core platform, but analytics ends with this term." · *Owen Achebe, Director of Clinical Systems, 27 Oct*
- **Ready:** a Slack to the account team on the close-out and the contact for the product that stays → `draft 5`

*(Items 2 to 4, Also worth a look and the meetings follow in the same shape.)*

---

### Drafts

*Nothing is sent. `draft 1` saves one to your Slack or Gmail drafts; `draft all` does every one.*

**Draft 1: Slack to Lee Moreno**
```
Does a support seat at Copperline use a paid license? Priya asked on 29 Oct and again today, before they add the next team. I meet them at 15:00 and want to bring an answer.
```

---

**How I built this:** your 22 active accounts where you're the CSM; emails and calls 4 Oct to 2 Nov, meetings to 4 Nov. I read 14 accounts closely and 18 email threads in full. Grouped by when to act, then by what's at stake, who's waiting, and how quiet the account is. Data as of 2 Nov 16:47.

**What I couldn't see:** emails Staircase can't see, and your calendar. Risk is scored on only 6 of your 22 accounts, so a quiet account isn't a safe one.

**To act:** `draft 1` saves it to your Slack or Gmail drafts · `done 4` or `snooze 5 until Friday` clears one · `not mine 3` · `why 2` shows the reasoning. Plain words work too.
````

**The trail** prints on `why` (and in Claude Code also goes to `~/.staircase/runs/<date>-staircase-csm-today.md`): `Rank rule:` the `action-priority.md` sentence verbatim (takeover: section 10's; on a "for <name>" run, "your book" reads "<name>'s book"), `Scope:` (`scope.md`), `Window:` every window as dates, `Seen:` (accounts and threads read out of total, blank fields, base-rate drops, anything that timed out or was split, hidden count), `Covered by:`, `Read, no action:` with reasons, `As of:` (latest touch seen), `Sources:`, then each item's evidence ids. `why <n>` prints that item's stakes, urgency and attention in words with its evidence ids and stored fields. Every `Seen:` mention in this file is a trail line.

**The board, on ask** (`delivery.md`, rule 3). Build `assets/action-board.html` only when the user asks ("board") or has said yes before. Otherwise, when the list has 5 or more items and 3 or more drafts, end the answer with the one offer line, once per conversation. To build it, copy the file and rewrite only its `board-data` JSON block from this answer (the schema is in the comment above that block). The chat answer stays complete; the board is a second copy.

No revenue figures. Account names, never ids alone. No em dashes. A quick follow-up (`draft 7`) skips the proof lines.

## 13. The morning push

Offer it once, after a first good run: "Want this every weekday at 7:00?" Only on the user's yes, set up a personal routine on their own session (in Claude Code, `/schedule`). The push is this answer cut to 12 lines (the headline, each top-5 heading with its Ready line, and the To act line), reads the ledger first, creates the top 5 drafts in Gmail or Slack as drafts (never sends), says "data as of <time>", and posts nothing on a quiet day. One push per person per morning, never more (`delivery.md`, scheduled runs).

## 14. What this skill adds, and the gap each rule covers

| Rule | Server gap it covers |
|---|---|
| A script builds the pulls and scores the book; a labeled reduced mode elsewhere | No `action_priority` recipe; scoring 30 rows by model arithmetic drops high-risk renewals (F19) |
| The book's event report runs in stage 1 | Fresh-risk and stakeholder rows need event ids for the read and the ledger; `last_lifecycle_event_date` gives dates only |
| Stage 2 read of the shortlist, every run | No last-sender or `awaiting_reply_since` field; open-thread counts miss and mislabel waits (F45, F46) |
| Fetch `mixed` threads before saying a customer waits | Thread direction is per thread, not per last message |
| Live two-way accounts drop proactive items; automated mailboxes and newsletters are not engagement | No human-only two-way touch date |
| The local ledger and the `ST-STATE` line | Nothing server-side records what was surfaced or dismissed (F44) |
| Recipients from role fields, guessed and flagged when the profile maps none | Role fields are tenant labels; no standard "account executive" field |
| No recap or follow-up item without a transcript or notes | Held versus rescheduled is not recorded (T8) |
| Book pulls in one unsorted page of up to 1,000 rows, checked with COUNT | Sorting a customer report on `customer.id` is silently ignored, so paging on it can drop or repeat rows |
| Other rows read 90 days, newest 6 threads | Quiet, chase and checkpoint triggers are defined on 21 to 90 days of silence; a 14-day read shows nothing |
| A dismissal hides the account until newer evidence | Per-trigger fingerprints let a dismissed account return under another trigger the next morning |
| Draft addresses from a stakeholder report | Fetched messages carry `sender_name` only |
| Risk heard in a read becomes a fresh-risk item | A competitor chosen or a product dropped in a call raises no lifecycle event |
