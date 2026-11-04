# Action priority: ranking what needs the user

The engine behind every "what needs me" list (today lists, renewals, team and executive views). It ranks actions for today, not accounts for the week. Stage 1 scores the whole scope from reports and makes a shortlist. Stage 2 reads the shortlist's threads and decides. Stage 1 alone is a shortlist, never the answer: in testing it put 3 wrong rows in a top 12 and missed 3 of the final top 8. What each item becomes, and what to prepare for it: `action-types.md`.

## The rank rule (verbatim on `why` and in the run log)

How I built this says it in one clause (`delivery.md`, Proof); `Seen:` and the other footer labels named in this file are trail lines.

"Ranked by what is at stake (renewal nearness, risk, value within your book), how urgent it is (who is waiting on what, and for how long), and attention (quiet or unanswered accounts rise; accounts in a live two-way conversation drop). Items already handled, covered by a teammate, or snoozed are left out."

## Score

Priority = 100 x Stakes x Urgency x Attention, capped at 100. One item per account (its highest). No trigger, no item: that account belongs in a weekly view, not today's list.

**Stakes** = 0.40 renewal + 0.35 risk + 0.25 value (weights from `company-profile.md` when set).

| Input | Field | Normalization |
|---|---|---|
| Renewal | `customer.renewal_date` | Passed in the last 30 days: 1.0, plus a renewal-decision trigger. Passed more than 30 days ago: a stale date (`data-rules.md` rule 25): 0.3 like a blank, no renewal-decision trigger, and the record-check line. 0 to 30 days: 1.0. 31 to 60: 0.8. 61 to 90: 0.6. 91 to 180: 0.35. 181 to 365: 0.15. Later: 0.05. Blank: 0.3, say "no renewal date" |
| Risk | `customer.risk.risk_level` | 5: 1.0. 4: 0.8. 3: 0.5. 2: 0.25. 1: 0.1. A ChurnRisk insight floors it at 0.8; a `churn_risk` event in 30 days floors it at 0.7. Blank: 0.2 + 0.5 x (1 - health/100), capped at 0.6, say "risk not assessed, health used". Health 0 or blank is no data: 0.3, say "risk not assessed, no health data" |
| Value | `customer.revenue_converted` | Percentile within the scope. Blank or 0: 0.5, say "revenue not set". Never print the figure |

**Urgency** comes from the trigger (table below). **Attention** applies to proactive triggers; reactive ones (reply, follow-up, prep, fresh risk, renewal decision) use 1.0.

| Attention state | Test | Multiplier |
|---|---|---|
| Dark | No vendor touch in 30 days, or never | 1.3 |
| Chasing | We touched in 14 days but no client engagement in 30; or 2+ of our threads open with no customer email in 7 days | 1.15 |
| Drifting | No touch in 15 to 30 days, or no client engagement in 21 | 1.15 |
| Live | Our touch in 3 days and client engagement in 7 | 0.75 |
| Recent | Our touch in 4 to 7 days | 0.9 |
| Normal | Anything else | 1.0 |

A reply candidate where someone on our side wrote after the customer (account level only) takes 0.6 until stage 2 settles it.

## Triggers

| Trigger | Stage 1 detects | Stage 2 confirms | Urgency |
|---|---|---|---|
| Reply needed | `customer.email.customer_open_threads` 1 or more (last 30 days) | The thread's last message is from a customer contact, no later outbound on that thread, not a solicitation or newsletter. Class the ask | Escalation, billing or commercial 1.0. Technical, a data request or a how-to 0.8, +0.1 after 2 business days. Scheduling or a resource share 0.6. Under 1 business day: x 0.7 unless escalation, billing or commercial, and never the customer-waiting slot. Thanks or FYI: drop |
| Meeting follow-up | `customer.event.last_event` in 72 hours; an organization email after it lowers it (x 0.6, account level) until stage 2 checks who it went to, and never drops it | Meeting row `call_summary`, `issues[]`, `action_items[]`; no outbound to its participants since; drop rescheduled meetings | 0.9 |
| Meeting prep | `customer.event.next_event` in 48 hours (7 days in week mode): every meeting is a candidate | What the meeting is for, from the latest threads and the invite: a business review (EBR, QBR, value review), a renewal or pricing talk, an executive or a new contact attending, an open ask or a blocker. Any of these makes it a prep item at the high urgency. A routine sync with nothing open goes to the meetings line, never to "Checked, nothing needed" | 0.5 today or tomorrow by the local calendar, 0.4 later in the week; 0.8 and 0.6 with stakes in the reports (renewal in 180 days, risk 4+, ChurnRisk, a customer thread open) or in the read |
| Quiet | `last_engagement` over `quiet_days` (21) and `last_touch` over 14, and no meeting in the prep window (a meeting folds the silence into its prep item: "raise it in the meeting") | No two-way thread in `quiet_days`; the contact is still there; the last "engagement" was a person, not a newsletter or an automated mailbox | 0.6 |
| One-sided chase | `last_touch` in 14 days and `last_engagement` over 30; or `organization_open_threads` 3+ with no client engagement in 10 days | Our unanswered threads and who sent them; no client engagement (a reply or a meeting attended) in 10 days; not an automated mailbox | 0.55 |
| Fresh risk | `churn_risk` or `exceptional_negative` event in 30 days | Read the event's communications: whole account or one product, already acknowledged, then `churn_signal_resolution`; save or manage closure (`action-types.md`) | 0.85 in 14 days; 0.6 in 15 to 30 |
| Risk heard in the read | Nothing: stage 2 only | A competitor chosen, a product they pay for now dropped (a deal we lost for a product they never bought is not a risk to this renewal), or a decision maker's complaint, dated in a fetched message or a call summary, with no event behind it | Reclassify as fresh risk: 0.85 in 14 days, else 0.6, labeled "from the emails, not a Staircase warning", with your confidence |
| Renewal decision | Renewal passed in the last 30 days with status Active, or renewal in 30 days | Renewal threads: a notice versus an outcome; the date versus the emails. A recorded outcome stays, with the action "close it out" and a record fix | 0.9 |
| Renewal checkpoint | Crossing 180, 120, 90 or 60 days (once each). At 121 to 180 days it is the value review that sets up the renewal conversation | A `renewal_discussion` event in 60 days lowers it (x 0.5), never closes it: read it to check it is about this renewal and still moving; decision maker touched where tagged | 0.4 at 180 (0.55 with NoRenewalDiscussion or risk 4+); 0.45; 0.55 under 60; 0.7 with NoRenewalDiscussion or risk 4+ |
| Stakeholder change | `farewell` event in 30 days | Departure, handover, new joiner or false alarm; which side (the event also fires on our side and on leave) | 0.75 in 14 days, 0.5 after; new joiner 0.4 |
| Expansion ready | Readiness 4+, Heating, a High-confidence Heating opportunity, risk 2 or lower (or no risk score and a health band of Average or High: Average is neutral, only Low blocks), no reply waiting | `expansion_signal_resolution`; an inbound commercial ask makes it a reply | 0.35 |
| Open situation | Risk 4+ or ChurnRisk with no fresh event | Stored risk analysis plus 90-day threads: save or closure | 0.6; 0.7 with renewal in 120 days |
| Record check | A stale renewal date (passed more than 30 days ago) on an Active account; or revenue 0 on an Active account | Zero threads in 90 days makes it an item (the account may have lapsed). Otherwise it is not an item: it goes to the record-check line (List shape) | 0.7, items only |

## Stage 1: the pulls

Start with the narrow pulls below, joined on `customer.id`; one wide report is not safe (12- and 17-column book pulls have timed out). On any pull's `code: timeout` (or `invalid_config` whose message says the report takes too long), split that pull in half once and say so; never resend a timed-out config. One `dateRange` per metric per call: two windows on one metric timed out even at 4 columns.

**Paging and counts.** Fetch each pull in one unsorted page (`pagination` 0 to 1,000) when the scope fits. A pull that must page sorts with `customer.name` as its last key and dedupes by `customer.id`. Never sort or page on `customer.id`: that sort is silently ignored, so pages drop or repeat rows with no error (`data-rules.md` rule 16). Every pull must read `complete: true`, and its row count must match one scalar COUNT on the same filter; name any mismatch in `Seen:`.

| Pull | Columns (each pull: `customer.id`, `customer.name`, the scope filter, Active) |
|---|---|
| A, state | `customer.renewal_date`, `customer.risk.risk_level`, `customer.buckets.health_score`, `customer.revenue_converted`, `customer.last_touch`, `customer.last_engagement`, `customer.last_reach_out`, `customer.email.customer_last_sent`, `customer.email.organization_last_sent`, `customer.event.last_event`, `customer.event.next_event` |
| B, threads | `customer.email.customer_open_threads`, `customer.email.organization_open_threads`, with top-level `arguments.dateRange` set to the last 30 days as an explicit array (`data-rules.md`, Dates); `customer.buckets.health` (the band); and two static columns: `customer.parent` (the parent account's id) and `customer.url` (the account's page in Staircase) |
| C1, insights and expansion | `customer.insight_detected` (ChurnRisk, Farewell, CustomerDark, NoRenewalDiscussion); `customer.expansion.readiness_level`; `customer.expansion.momentum_indicator`; a child COUNT of `expansion_opportunity` with High confidence and Heating momentum |
| C2, event dates | `customer.last_lifecycle_event_date` (churn_risk, churn, farewell, exceptional_negative, renewal_discussion) |

- Use only the insight and event ids metadata offers; drop and name the rest.
- Base-rate guard: a flag true on more than 80 percent of the scope, or on none, does not separate accounts. Drop it and name it (`evidence.md`).
- Over 300 accounts: score in a script. With no script, pre-filter with a COUNT-first condition (renewal in 120 days, or risk 4+, or a customer open thread).

## Stage 2: read the shortlist (12 to 14 accounts)

1. `staircase_list_communications` with the shortlist `account_ids` (up to 20 per call), `per_account_limit` 6 and `limit` set to accounts x 6 (`data-rules.md` rule 17). Reply-needed rows read the same 30 days as Pull B, so a customer waiting 15 to 30 days is still visible. Every other row reads the last 90 days: rows come newest first, so a busy account still shows its last few days, and a quiet, chase or checkpoint row shows its last real exchange (a 14-day read cannot confirm a trigger defined on 21 to 90 days of silence). That is two calls when both kinds are on the shortlist.
2. A `lifecycle_event` report with top-level `arguments.dateRange` set to the last 30 days, scoped to the shortlist; then `staircase_list_communications` with the `event_ids` of farewell, churn, churn_risk and exceptional_negative events.
3. `staircase_fetch_evidence` only for a thread whose direction reads `mixed` where a reply depends on who wrote last, and for the quote a picked draft needs.
4. `staircase_account_info` only for rows whose action turns on a stored analysis (open situation, fresh risk, renewal decision).
5. A `stakeholder` report on the shortlist accounts: `stakeholder.type` In [the Human option id] and `stakeholder.last_engagement` in the last 180 days, sorted by last engagement descending; columns name, email, title, `last_engagement`, `last_reach_out`. It is the source of draft addresses (fetched messages carry `sender_name` only) and of the per-contact touch budget below. Unfiltered, a few accounts fill a 100-row page with inactive people.

Confirm, reclassify or drop each row by the trigger table, and add what the counts missed (a customer waiting that the count did not show; a risk heard in the read).

## Suppression

| Rule | Test | Effect |
|---|---|---|
| Live two-way | The account is Live (attention table) | Quiet, chase and checkpoint items drop: the live conversation answers them. A contact change, an expansion signal and an open risk stay, at attention 0.75, with the action "raise it in this week's conversation". Our outbound alone never suppresses |
| Do not contact | A ledger entry with reason `do_not_contact` on the account (the user said the customer asked us to stop, or "don't contact <account>") | Customer-facing items drop (quiet, chase, checkpoint, contact change, expansion). Internal ones stay (a reply they started, a meeting they booked, fresh risk, a renewal decision, an open risk), and their action is internal only: a Slack to the renewal owner or the team, a close-out, a CRM fix. Never a proactive customer draft; a reply to a thread the customer started stays a reply. Lifted only by the user ("ok to contact <account>") |
| Reply sent | A later outbound on the same thread, from anyone on our side; or a split thread: a later outbound to the same customer contact with the same subject (ignoring "Re:" and "Fwd:"). Check both before calling a customer waiting: in one blind run a reply sent 9 minutes after the customer's follow-up sat on a split thread and read as "no reply" | Removed; when a teammate sent it, one "covered by <name>" line |
| Addressed to a teammate | The customer's last message asks a named teammate, on that teammate's topic (a renewal owner's terms, a support engineer's ticket) | One line naming the teammate, not the user's item. A thread where the customer wrote last to the user is waiting, whatever teammates wrote elsewhere |
| Covered by a teammate, proactive items only | The latest outbound on the topic in 14 days came from another internal user, and the customer is answering them. One conversation can span several threads: judge them together | One "covered by <name>" line, not an item. Never on reactive items (reply, follow-up, prep, fresh risk, renewal decision) or pinned rows, and never for the renewal owner's commercial threads when the user is the CSM on that renewal: that is their job |
| Open CTA (only when Gainsight CS is connected) | A same-reason open CTA with a task due in 7 days | Becomes "advance this task"; never a duplicate CTA. The ranking must hold without it |
| Snoozed or dismissed | A ledger entry for the account (Ledger, below) | The whole account stays hidden until something newer than the dismissal happens or the snooze ends |
| Touch budget, proactive only | 1 proactive touch per contact per 14 days; 3 per account per 30 (company profile may change) | The item becomes "raise it in the next meeting" |
| Same-day ask | A customer email under 1 business day old in a live thread | Its reply urgency takes x 0.7 (trigger table), and it never takes the customer-waiting slot, unless commercial, billing or an escalation |
| Read before listing | Stakeholder change and fresh risk | One digest line until read |
| Data guards | A future `last_touch` counts as now; automated mailboxes and the customer's own newsletters are not engagement | Stage 2 checks the latest inbound before calling an account engaged |

Only the ledger can remove a pinned row (List shape): live suppression, covered-by-a-teammate and the read never do.

## List shape

- The top 5 as full items, three lines each (`delivery.md`, Scan): the move and its deadline; what happened, dated, in plain words; `Ready:` the draft and its verb. The three factors in words ("renewal on 6 Dec; no risk score yet; our terms offer unanswered since 22 Oct") and the evidence ids print on `why <n>`.
- Lists group by when ("Do today", "Prep for <day>", "This week"). Inside "Do today", the earliest deadline goes first (a meeting's start time; for a customer waiting, the longest wait), then this engine's order; item 1 is the first move (`delivery.md`, Glance). Later groups keep this engine's order.
- Then up to 7 more as one line each, under "Also worth a look".
- **Pinned rows.** A renewal inside 60 days, or passed in the last 30, on a risk 4 or 5 or ChurnRisk account always stays on the list, marked "don't miss": in the top 5, Also worth a look, or the Closing line. The read may change its action (save, manage closure, close it out with a CRM fix) and its place, never its presence. One that can still be saved stays at the top.
- **Closing line.** An account whose loss is settled leaves the ranked list for one line under it: a written non-renewal or churn notice, a closure being managed, or offboarding finished while the account still reads Active. Each entry says what closes and when, and who has the commercial steps ("Orchard Health: the analytics product closes 31 Dec, notice 28 Oct; Dana has the commercial steps"). A product that stays is named on the same line ("the community product stays"). The account returns to the ranked list only while the user owns a dated step: a customer waiting on them, a meeting with them in the window, or an export or offboarding task, and then the item is that step, never the loss itself. In the blind test a CSM left all four churning accounts off her own list while ours ranked two of them first.
- **Related accounts.** A parent and its child account both in scope (`customer.parent`) make one item, named for both ("Lumen Freight (with Lumen Group, its parent account)"); the member with the pin, else the highest priority, stands for it, and both are read in stage 2. The user can also join two accounts Staircase does not link ("Lumen Freight and Lumen Group are one").
- Keep one "customer waiting" slot that ignores value, so a small account with a waiting customer still shows: only for a customer confirmed waiting on the user, not addressed to or covered by a teammate.
- Meetings in the next 48 hours sit on their own line per day after the extras; an item whose account meets in the window says so in its own line.
- **CRM line** ("CRM may be out of date"). Stale renewal dates (passed more than 30 days ago) on Active accounts with threads in the last 90 days: one line under the list, the count plus up to 8 names, "ask whether it closed and the date moved". Never ranked.
- End with the two proof lines and the To act line (`delivery.md`). The rank rule, scope, windows and as-of time (the latest `last_touch` or `customer_last_sent` seen) go to the trail on `why`; what was not visible that changes a decision goes in What I couldn't see.

| View | Scope | What changes |
|---|---|---|
| CSM | Their book | The full engine |
| Account manager | The renewal-owner or owner field the recipe picks | Renewal, expansion, commercial and decision-maker items; renewal window 120 days. In a CSM lens on a renewal someone else owns, actions route to the renewal owner |
| Manager | Their team, pooled lane apart | A manager-lens rule may replace the score: groups (a renewal decision; a fresh signal; exposed and quiet), printed as a sentence, ordered within a group by nearness of the renewal date. It is also the no-script mode for a team. An older passed renewal date on a risk 4 or 5 account may stay a renewal decision in this lens, and a pinned row the read shows signed may move to the Checked line, named. Each row is marked "on their list": yes when today's signals already put it at the top of the holder's own list (a renewal passed in the last 30 days or due in 30; a churn notice, churn risk or very negative message in 14 days; a meeting today or tomorrow; a meeting in the last 72 hours with no email from us since). It is a proxy: no server record of anyone's list exists. Counts by trigger or group. Never sort, count or compare people |
| Executive | Their slice | Only top-tenth stakes with a renewal decision, a chase on a renewal, a whole-account fresh risk, an executive stakeholder change or an escalation, where the CSM path is exhausted (2+ of our threads unanswered for 7+ days, already escalated, or their executive on the thread); 3 to 5 accounts |

## Ledger

Stateless first: a later outbound on the thread closes a reply; outbound to the meeting's participants closes a follow-up; a `renewal_discussion` event closes a checkpoint; any customer reply clears quiet and chase. Clearing sticks from day one: "done", "not mine" and "snooze until <date>" are taught; "wrong" is accepted as "not mine", never taught (`delivery.md`, Verbs).

- **A dismissal covers the account,** not one trigger: every item on that account stays hidden until something newer than the dismissal happens (the customer writes again, a new event, a meeting, the next renewal checkpoint) or the snooze ends. Per-trigger dismissals let both dismissed accounts in one test return the next morning under another trigger. "Not mine" on the whole account (fingerprint `<account_id>|*|*`) hides it until the user takes it back.
- Fingerprint: `<account_id>|<trigger>|<evidence key>`: a thread key, event id, checkpoint label or meeting start; `<type>@<YYYY-MM-DD>` where no event id is known; a reply's key adds `@<date of the customer's last message>`. The renewals skill writes `<account_id>|renewal_plan|<renewal date>` and `<account_id>|expansion_plan|<lane>`; since those keys do not change from event to event, a clear on them holds until something newer happens (an event dated after it, the renewal crossing 180, 120, 90, 60 or 30 days, or the snooze ending).
- **Across skills.** One ledger file serves both list skills. An entry from the other skill covers only its own family at account level: a renewal clear covers the renewal checkpoint and renewal decision items, an expansion clear covers the expansion item, and the reverse. "Not mine" on the whole account covers everything.
- **Do not contact.** "They asked us to stop contacting them", or "don't contact <account>", writes `<account_id>|*|*` with reason `do_not_contact` (accepted, never taught). It hides nothing on its own: it drops customer-facing items and turns the rest internal (Suppression). "OK to contact <account>" lifts it.
- **Undo.** "Undo 2", "take 3 back" or "ok to contact X" writes a line with state `lifted` and the same fingerprint (and the reason, when it lifts one kind only); it cancels the earlier lines it matches.
- Scope: every entry carries `scope`, the user id whose book the list ranked. A run reads only the entries for its own scope, so a "for <name>" run never hides items on the user's own book, or the reverse.
- Claude Code: append one line per dismissal to `~/.staircase/ledger.jsonl`, for example `{"fp": "<account_id>|reply_needed|<thread_key>", "state": "snoozed", "until": "YYYY-MM-DD", "reason": "not now", "at": "YYYY-MM-DD", "scope": "<user_id>"}`. Read it before ranking.
- Elsewhere: print a state line under 300 characters under the To act line (`ST-STATE <date> snz <account_id>.<trigger>><until>; dis <account_id>.<trigger>.<key>:<reason>`), introduced as "Paste this line next time so I remember what you cleared:", and read it back when the user pastes it.

## Scoring with no script

Where no script can run, a skill may hand-score with the formula at 15 rows or fewer. Above 15 rows, use reduced mode and say so in How I built this: "Ranked without the scoring script (none runs here), so the order is rougher." Reduced mode sorts by trigger class in this order: renewal decision, reply needed, meeting follow-up, fresh risk, meeting prep, open situation, stakeholder change, checkpoint, quiet and chase, expansion, record check; then renewal date, then risk. Keep pinned rows and run stage 2 as above. Never multiply scores by hand across more than 15 rows.
