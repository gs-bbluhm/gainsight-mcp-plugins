---
name: staircase-follow-up
description: "Follow-up work for anyone who talks to customers, owner or not. Drafts the recap email after a meeting, with both sides' commitments, from the transcript or your own notes (no transcript, no invented recap). Finds who you owe a reply or follow-up to across the customers you emailed or met. Keeps you posted on accounts you were copied on or brought into, in about 10 lines. Writes coverage notes before time off, and the owed list when you are back. Use for 'I just got off a call with X', 'recap my meeting with X', 'follow up on today's calls', 'who do I owe a reply', 'what follow-ups am I behind on', 'keep me posted on accounts I'm copied on', 'I'm out next week, write coverage notes', 'I'm back from PTO, who do I owe'. Drafts appear in the answer; a Gmail draft only on your yes. Not for one account in depth (staircase-account-brief), what needs you across your book (staircase-csm-today), or logging calls and CTAs in Gainsight CS (the Gainsight CS plugin does that). Needs the Staircase AI connector."
license: MIT
compatibility: "Needs the Staircase AI MCP connector. Gmail, Slack and Gainsight CS connectors are optional. Works in Claude Code, Claude Desktop, Cowork and claude.ai."
metadata:
  version: "3.0.0-alpha.1"
  layer: "primitive"
---

# Staircase Follow-up

Follow-up work for anyone with customer contact, whether or not they own the account. Four modes: a recap after a meeting, what you owe, staying in the loop, and time off (out and back). The server owns the mechanism: tool descriptions and recipes (`staircase_get_recipe`) say how to read one account and how to find a person's communications. This skill adds what they leave out: how "you" are found in a thread, what counts as owed, what a recap may say, and when to stop and ask for notes. Section 10 lists each rule with the server gap it covers.

Read each reference at the moment named; they are short.

| File | Read it |
|---|---|
| `scope.md` | Before the first scoped call: the engaged-with filter (copy it as written), statuses, the scope line |
| `data-rules.md` | Before the first report: the Dates section first; rules 1, 4, 16, 17 and 21 bite here |
| `evidence.md` | Before the first answer |
| `trust.md` | Before any draft |
| `action-types.md` | When an item needs an internal ask before the customer reply, and for the next action |
| `delivery.md`, `plain-words.md` | Before the first answer: surface, layers, verbs, states, the user's words |
| `company-profile.md` | Once per session: exclusions, automated senders, teams |

## 1. Before the first call

1. **Connector.** Staircase tool names end in `staircase_run_report`, `staircase_list_communications` and so on; the prefix differs by install. If none are present, stop with the no-connector state in `delivery.md` (in Claude Code add the command: `claude mcp add --transport http staircase-ai https://mcp.staircase.ai/mcp`).
2. **Recipes.** One `staircase_get_recipe` call with `single_account_analysis` and `participant_resolution`; add `portfolio_resolution` for time-off mode, or for loop mode when you may hold a book. Follow them. Where a recipe and this skill disagree, the recipe wins, except the `data-rules.md` overrides it names.
3. **Metadata.** `staircase_report_metadata` once per session. Take field ids, option ids and `current_user_id` from it. Never paste, list or summarize the payload. If the runtime saves it to a file, query the file with a tool (for example `jq`).
4. **You.** One `user` report: `user.id`, `user.full_name`, `user.first_name`, `user.email`, `user.mailbox_connected`, filtered `user.id` In [`current_user_id`]. Your full name finds you in threads; your email finds you as a meeting organizer. If `mailbox_connected` is not true, say so in the line under the headline: your own mail is missing, so owed and recap results will be thin.
5. **Dates.** Your local today, from a tool when one runs. Every window is an explicit two-date array, exactly N days, printed in the answer (`data-rules.md`, Dates).
6. **Company profile.** Exclusions (own org account ids, test accounts, automated senders) and teams for internal asks. The vendor's own account (an account named like your company, holding internal meetings) is left out even when the profile does not list it; name it as likely internal.

## 2. Pick the mode

| The ask | Mode | Default window |
|---|---|---|
| "I just got off a call with X", "recap my meeting with X", "draft my follow-up from the X call", "follow up on today's calls" | Recap (section 4) | The day named, else your local today. Nothing found today: the last 3 days, and say so |
| "who do I owe a reply", "who do I owe a follow-up to", "what follow-ups am I behind on", "did I follow up with X" | Owed (section 5) | Last 30 days. Recaps only for meetings in the last 7 days |
| "keep me posted on accounts I'm copied on", "what's happening at accounts I was brought into", "keep me in the loop" | Loop (section 6) | Accounts: engaged-with, last 30 days. Events: last 7 days |
| "I'm out <dates>, write coverage notes", "cover my accounts while I'm out" | Time off, out (section 7) | The out dates; ask once if missing |
| "I'm back from PTO, who do I owe", "I'm back since <date>" | Time off, back (section 7) | The day you left to today; ask once if missing |
| "check my copied threads" | Owed, received-only accounts (section 5, step 2) | Last 30 days |
| "help me follow up with X" (an account, no meeting named) | Owed, scoped to that account | Last 30 days. Nothing owed: offer a check-in draft from the last thread you took part in (`action-types.md`, quiet account) |

- **Self-only, every mode.** These modes read your own threads and meetings. "Who does <name> owe" or "<name>'s loop" (when <name> is not you; one `user` report settles it, no other calls) gets one line: owed and loop run only on your own scope; a manager can use staircase-manager-team or staircase-csm-today with "for <name>'s book". Recap covers a meeting you attended or have notes for.
- "What did I miss" from someone holding a book belongs to staircase-csm-today's since-date mode when it is installed; otherwise run back mode here and say so.
- "What changed" is not a trigger here (staircase-csm-today and staircase-exec-weekly own it).

## 3. Who you are in a thread (every mode)

| Fact | So |
|---|---|
| An email row's `participants` are its senders. Recipients (To, Cc) appear nowhere in the tools | "You took part in a thread" means your full name is among its participants (type User), so you wrote at least one message. Staircase cannot show you as a recipient |
| Attendees appear only on recorded meetings (`comm_type` Video). A meeting without a transcript has no row in `staircase_list_communications` | "You attended" means your name is on a Video row. A meeting with no transcript shows only in the `meeting` root (subject, start, organizer email, Has Transcript) and in `customer.event.count` with `filter.user` (an invitation there, not proof you attended) |
| Participant type User is our side; Stakeholder is the customer's | Commitment sides and recipients come from these types |
| Names | Match your `user.full_name`, also in "Last, First" form; never the first name alone. Print "name-matched" in the trail's `Seen:` line |
| A customer reply can arrive as its own thread with the same subject | Before calling a thread "you wrote last", check for a split reply (section 5, step 6) |
| Automated senders (the profile's `automated_senders`; names like Concierge, no-reply, notifications) and bulk mail | Never owed, never a loop line. **Automated-only check:** for received-only accounts (you sent 0, met 0), one `staircase_list_communications` call (`per_account_limit` 10, `limit` accounts x 10) to read sender names. Every customer-side sender automated: leave the account out and name it in `Seen:` |
| Transcript speaker labels: [User], [Stakeholder], sometimes [Unknown] | The participant list's type wins over an [Unknown] label |
| Times: `meeting.start_time`, `next_event` and row dates are UTC | Show dates and times in your local time zone (the local clock, with the offset in force on that date; else UTC and say so), and say so once. Once your local evening has passed midnight UTC, extend every list and search window that ends today by the next UTC day (row dates are UTC), and drop meetings that have not started yet. Report metrics such as meeting counts keep the local N-day window |
| `staircase_list_communications` caps rows per account and per call | Set both limits on every call (`data-rules.md` rule 17): accounts x `per_account_limit` stays at or under 300, so batch the accounts (3 a call at 100, 6 at 50, 30 at 10) and run as many calls as the scope needs. An account that comes back at its cap (`truncated`) gets rule 17's earlier-window call before any item on it is judged owed or closed; if that call is not made, the item reads "unconfirmed: older rows not read". Large results may be saved to a file: query it with a tool |

## 4. Recap mode

One recap email draft plus both sides' commitments, for one meeting you attended, built only from its transcript or your notes.

1. **Find the account** (`single_account_analysis` step 1). "Today's calls" with no account: run the engaged-with filter (`scope.md`) with only the `customer.event.count` leaf and column, window today, to list the accounts where you attended a meeting today. Then run steps 2 to 8 for each, at most 5 (more on ask).
2. **Load the day, in one turn:**
   - `staircase_list_communications` with `account_ids` [id], `date_range` from the window's first day to today (row dates are the thread's latest message, so this one call also serves step 7), `per_account_limit` 50, `limit` 50.
   - A `meeting` report with top-level `arguments.dateRange` the same window (rule 1), filter `meeting.customer` In [id]; columns `meeting.id`, `meeting.summary` (the subject), `meeting.start_time`, `meeting.has_recording` (label "Has Transcript"), `meeting.organizer.email`; sort `start_time` Desc, then `meeting.summary` (never an id, rule 16).
   - A `customer` report filtered `customer.id` In [id] with `customer.event.count` (`filter.user` [you], the same `dateRange`: whether you had a meeting there in the window) and `customer.event.next_event` (for the prep offer in step 8).
3. **Pick the meeting.**

   | You see | Do |
   |---|---|
   | A Video row with you among its participants | Transcript path (step 4). Several: the one the user named (subject or time), else the latest; list the others in one line |
   | Your own emails around the start show the customer did not join ("are you able to join", "we missed you") | No meeting to recap; this row wins over the no-transcript row below. Say so, cite the emails, and point to any follow-up already sent (step 7). `customer.event.count` counts invitations, not who showed up |
   | No Video row with you; a meeting row with Has Transcript false; your meeting count 1 or more, or you say you were there | No transcript. Name the meeting (subject, start, organizer) and ask for your notes in one line. Give the Subject line and the To line if you know the attendees; draft no body |
   | Has Transcript true but no Video row yet, or the row reads `summary_status` Pending | Still processing (summaries usually land within hours). Offer: paste notes now, or ask again later |
   | A Video row without you | You were not on it (name-matched). Say who from our side was, and offer to draft from your notes if you were there |
   | Nothing | Say what you checked (account, dates). Ask for the date or your notes |

   **Notes path.** When the user gives notes (in the ask or after), the notes are the only source for the body and the commitments. Never add from other threads, stored fields, scores, or the summary of another meeting. Subject and recipients may come from the meeting row, the thread the user names, or the names in the notes (step 6).
4. **Read the meeting.** `staircase_fetch_evidence` with the Video evidence id, no full transcript: subject, `call_summary`, `issues[]`, `action_items[]`, `transcript_line_count`. Then one more fetch with `transcript_query` set to your first name plus the key nouns of the items going into the draft (owners, dates, deliverables). The excerpt shows each speaker with [User] or [Stakeholder]. Quote only from it.
5. **Commitments, both sides.** One row per action item.
   - Owner from the item text, matched to the participant list: a User name is ours, a Stakeholder name is theirs. "<our company> to ..." is ours with no named owner; "<customer> to ..." is theirs. A trailing "(<name>)" or "(owner: <name>)" names the owner. No owner: unassigned. A name after "with", "to" or "for" ("share the notes with <name>") is a recipient, not the owner.
   - An owner the excerpt shows saying "I'll ..." counts as named, marked "(from the transcript)". An owner inferred from role or context is "(guessed)" and stays out of the customer text.
   - Ours carry names. Theirs read "you mentioned you would ...", never an assigned task. Unassigned items go to internal notes.
   - A commitment heard only in the excerpt (not an action item) may be added, marked "transcript only".
   - Due dates only as said in the item or the excerpt, marked "confirm" in the table. A date or term a colleague said (contract end, pricing, a release) stays in internal notes, never in the draft.
   - An item naming you that the excerpt does not support stays in the table as "not found in the transcript", out of the draft.
6. **Recipients.** Never pull an account's whole contact list (it can hold thousands).
   - Customer side: one `stakeholder` report filtered `stakeholder.customer` Equal <account id> And an Or of `stakeholder.name` Contains <each Stakeholder attendee's name>; columns `stakeholder.name`, `stakeholder.email`, `stakeholder.title`, `stakeholder.last_engagement`. Several records for one name: the one with the latest `last_engagement`, the others named as alternatives. No email found: "<email not found>".
   - Our side (Cc, a suggestion): one `user` report with an Or of `user.full_name` Contains <each of our other attendees>.
   - People who were not on the call go on Cc only when the meeting asked for them (an action item or an excerpt line), marked "(asked on the call)".
   - No attendee names known (no transcript, no names in the notes): skip both reports; To is "<who attended>".
7. **Already followed up?** In the rows from step 2: an outbound or mixed email on the account after the meeting started, from one of our attendees (you included), that thanks them for the meeting, lists its next steps, or delivers items promised on the call (it counts as the follow-up for those items). An email on the same topic that does none of these is not a recap. Fetch it to see what it covered. Found: the headline leads with it (who, when; the evidence id goes to the trail); draft a short add-on covering only what is left (your items first) as the single draft, and offer the full recap in one line. Nothing left open: no draft; say so.
8. **Draft, then the table, then internal notes** (section 8 rules).
   - Subject: "Recap: <meeting subject>", or the topic when the subject is only names. Body: thanks; what we covered (2 to 4 lines, topics from the call summary and issues, no assignments); next steps from us, in the first person and named; next steps from you ("you mentioned ..."), including their own plans and dates as they said them; a one-line close.
   - Internal notes, at most 5 bullets: roadmap, release timing, pricing or terms said on the call (never in the draft), with the transcript line; risks raised; unassigned items; claims to verify.
   - One next action beyond the email, from `action-types.md`: the internal Slack ask when a customer item depends on support, product or the account executive; a prep brief when the next meeting is within 48 hours; or a Timeline note when Gainsight CS is connected.

**Recap answer shape** (`delivery.md`; copy `evals/sample-output.md`)

Layout is `delivery.md`, Chat layout: `###` sections, bullets, verbs in code style, no `#` or `##`.

1. **Headline,** 30 words at most, the first clause in bold, one of: "**Recap ready for <subject> (<account>, <day month>)**, from the transcript: 5 things we owe (2 yours), 3 theirs. Nothing from our side since." / "**<Name> already followed up on <date>;** here's a short add-on for what it left open." / "**No transcript for <subject>;** paste your notes and I'll draft from them." / "**No recap needed:** your emails show the customer didn't join."
2. **The draft:** the label outside the copy block with the recipients and subject ("**Draft 1: email to Morgan and Riya** (cc Jo, suggested) · Subject: Recap: <subject>"), and only the body inside. For "no recap needed" or "already covered, nothing left": no draft and no commitments list; instead the dated lines as bullets (who wrote what, when, by sender, date and channel), then internal notes and the next move.
3. **`### Who owes what`,** one bullet per commitment: ``- **1. <what>** · ours or theirs · <owner, '(from the transcript)' or '(guessed)'> · <due as said, or 'no date said'>``. No table.
4. **`### Internal notes`,** at most 5 bullets.
5. **`### Next move`:** a bullet for the Gmail offer (only when a Gmail connector is present) and the last bullet the one other action, ``- **Ready:** <the action> → `draft 1b` ``.
6. **Proof,** after a rule, two bold-label paragraphs. How I built this: "one meeting, <subject>, <account>, <date>; you were on it (matched by name)", or how attendance was judged without a transcript; what was read ("the call summary and 3 action items, checked against an excerpt"); data as of. What I couldn't see: recipients and who joined, when the transcript doesn't show them. The trail (`why`): `Scope:`, `Window:`, `Seen:` (transcript lines, excerpt checked for N items, action items, attendees from the transcript), `Sources:` with evidence ids.

## 5. Owed mode

Who you owe a reply or follow-up to, across the customers you emailed or met. **Owed means you took part:** you wrote in the thread, or you attended the meeting. Customer mail where you never wrote goes to loop.

A typical run is 15 to 25 Staircase calls, most of them list batches. Over 40 took-part accounts: read the 20 with the most meetings and emails sent first, and say how many were not read. Stop reading closures once each owed item has had one check.

1. **Your engaged accounts.** The engaged-with filter (`scope.md`, as written), window the last 30 days as an explicit array, with the three evidence columns (emails you sent, customer emails you received, meetings with invitations included) and `customer.status`. Sort by the evidence columns, then `customer.name` (a sort on `customer.id` is silently ignored, so paging on it can drop or repeat rows). Page to the end; more than one page: confirm the total with a scalar COUNT. Leave out exclusions and automated-only accounts (section 3); say how many.
2. **Split.** Took part: emails sent 1 or more, or meetings 1 or more. Received only: both 0. Received-only accounts are not read here: list their count in `Seen:` with one line, "N accounts where you only received customer mail (Staircase cannot tell To from Cc); say 'check my copied threads' to read them". On that ask, read them, and move a thread to owed only when the customer's message greets you by name or asks you directly.
3. **Your threads.** `staircase_semantic_search` per `participant_resolution`: `participant_ids` [your user id], `account_ids` every engaged account (a received-only account can hold a thread you wrote before the window), `date_range` the window, `query` "questions, requests, next steps and follow-ups", `limit` 100, `per_account_limit` 25. If 100 come back, split the window in two and run both. Search is ranked and drops some rows even under the limit: print "found by search".
   **Meetings are counted, not searched.** Per account, compare your meeting count (step 1) with your Video hits. Where the count is higher, `staircase_list_communications` on those accounts (3 a call, the window, `per_account_limit` 100, `limit` 300) finds the Video rows with your name that search missed; an account at 100 rows gets the earlier-window call (rule 17). What is still missing is meetings without a transcript.
4. **Read the emails.** Fetch every Email hit, 20 ids a call. For each thread take the last message (sender, date) and your last message's date.

   | Last message | Then |
   |---|---|
   | From a customer-side sender, after your last message | Owed: a reply. Class the ask below |
   | From a customer, greeting a colleague by name | Theirs: one "for <name>" line, not your item |
   | From a colleague, addressed to you (greets you, asks you, or forwards the customer's ask to you) | Owed: a reply, "via <name>", classed by the customer's underlying ask |
   | From a colleague to the customer: a recap or next-steps list that names you as owner of a customer deliverable | Owed: your commitment, "per <name>'s recap". When the meeting's own action item names someone else, show both owners |
   | From a colleague to the customer, a promise the colleague owns that mentions you ("I'll update you after I meet with <you>") | Not your item: one "for <name>; you are named" line, so you can check with them |
   | From a colleague, answering the customer | "Covered by <name>": one line, not an item |
   | From you, with a promise ("I'll come back to you", "by Friday") and no later message from our side delivering it | Owed: a commitment, "from your email", due as you wrote it |
   | From you, anything else | You are waiting on them; check for a split reply (step 6) |

   Class the ask: escalation or frustration; commercial (pricing, terms, renewal, procurement); technical question or bug; scheduling; a file or data request. Thanks, FYI, out-of-office and automated notes drop, unless they also ask something. A customer answering your question with nothing asked is one "answered, no ask" line.
5. **Read the meetings.** Fetch each of your Video rows (no transcript, 20 a call). Your named action items (section 4, step 5) that deliver something to the customer (send, share, schedule, confirm, report back) are commitments you owe. Internal work named to you (build, prioritize, investigate, escalate) is one "internal work named to you" line, no draft. A later email from a colleague that delivers an item closes it, marked "likely closed by <name>"; an item a later decision made moot is "likely superseded; confirm". Judge an item owed only after the account's rows from the item's date to today were read (section 3: capped accounts get the earlier-window call). For meetings in the last 7 days, one `meeting` report over those accounts and days (rule 1) gives subject and organizer. A recap counts as sent when one of our attendees emailed the account after the meeting started, thanking them for it, listing its next steps, or delivering what was promised (section 4, step 7; fetch when unsure). None: "recap not sent". It is your item when your email is the organizer; otherwise it is a "for <organizer>" line in the not-counted block, and your own named items from that meeting stay owed. Meetings without a transcript (your meeting count minus your Video rows, per account; the count includes invitations, so N is an upper bound) get one line: "up to N meetings without a transcript; give me notes to recap one".
6. **Split replies.** For threads where you wrote last, or a colleague did: `staircase_list_communications` on those accounts (6 a call, `per_account_limit` 50, `limit` 300) from the earliest such date; an account that comes back truncated gets the earlier-window call (rule 17). A row of any direction, dated after your last message, whose participants include a customer contact who wrote in your thread or whom you greeted by name may be the reply, landed as its own thread. Fetch every such row (a row's summary can describe an earlier message, so never judge by it), at most 20 fetches a run; if the subject matches or it greets you, treat it as that thread's last message (step 4). Rows beyond the 20 leave their items "unconfirmed".
7. **Rank and tee up.** One row per item; an account can hold two. Show 10, more on ask: the top 5 as items, 6 to 10 as one-line extras. Draft the top 3 in full: a reply in the thread, a recap (section 4), or a short note closing your commitments. The rest are drafted on "draft <n>". When the reply needs an internal answer first, put the Slack ask on top (`action-types.md`); when you are the person who would answer (the ask is in your own field, or names you), skip the internal ask. A draft that needs something only the user knows (a date, times, an answer you cannot see) carries a bracketed placeholder inside the block, and its label says "fill before sending: <what>" outside it.

   Rank rule (verbatim on `why`; How I built this says it in one clause): "Customers waiting on you first, directly or through a colleague (escalation and commercial asks, then technical, then scheduling and requests; oldest wait first within each), then recaps not yet sent for meetings in the last 7 days (most recent first), then your commitments from meetings and your own emails (earliest stated date first, undated last)."

**Owed answer shape** (`delivery.md`, Work a list and Chat layout; copy `evals/sample-output.md`). Three levels only: `###` sections, a bold line per item, bullets; no `#` or `##`.

1. **Headline,** 30 words at most, the count in bold: "**You owe 5 follow-ups at 4 customers.** First: Priya at Account A, waiting since 21 Oct on a quote question. Your reply is ready (`draft 1`)."
2. **The top 5, grouped by when,** each group a `###` heading, the rank rule's order inside each group, numbers in the order shown, an empty group not printed: **Do today** (a customer waiting on you, directly or through a colleague; a recap not yet sent; a commitment already past its stated date), **Due <day>** (a commitment with a stated date in the next 7 days), **This week** (the rest). Each item is a bold line and up to 3 bullets: ``**1. <Account>** · <what you owe, as a verb>``; who asked or what was promised, when, with at most one quote line under its bullet, from fetched text (``> "I'll come back to you by Friday." · *you, 23 Oct email*``; a customer's quote names the speaker and title, your own words are "you"); and the last bullet, ``- **Ready:** <the draft> → `draft 1` `` or the placeholder to fill.
3. **Also owed,** items 6 to 10, one bullet each with the verb (``- **6. <Account>** · what you owe → `draft 6` ``).
4. **Checked, nothing needed from you,** under Also worth a look, a bold label with one bullet per class, account names only: "<name> is handling it" (covered by a colleague), "for <name>" (a colleague's item), answered with no ask, waiting on them, internal work named to you. Detail on ask.
5. **Drafts** after a rule (`---`), under `### Drafts` with one italic line ("*Nothing is sent. Say `put it in Gmail` and I'll save it as a Gmail draft.*"), numbered to match (section 8).
6. **Proof,** after a rule, two bold-label paragraphs. How I built this: "accounts you've emailed or met in the last 30 days (<N>)", the dates, what was read ("22 threads found by search, all read; 9 meetings, 7 with a transcript"), the order in one clause, data as of. What I couldn't see: "Staircase can't tell To from Cc, so <N> accounts where you only received customer mail aren't read (`check my copied threads`)", meetings without a transcript (`give me notes to recap one`), and the mailbox status when it is not connected; each opening phrase in code style.
7. **To act,** the last line, every verb in code style: `draft 4` writes that one · `why 1` for the reasoning · `check my copied threads` for mail you only received. Plain words work too. Owed is rebuilt from the threads each run, so a reply from our side clears an item on its own; don't teach "done" or "snooze" here, since nothing would keep them.

**The trail** (`why`, and in Claude Code `~/.staircase/runs/<date>-staircase-follow-up.md`): `Scope:`, `Window:`, `Seen:` (accounts in scope: took part, received only, left out; threads found by search and read; meetings attended against meetings with a transcript; name-matched; recipients not visible; mailbox status), `Rank rule:`, `Sources:` with each item's evidence ids.

**The board, on ask** (`delivery.md`, rule 3). Build `assets/action-board.html` only when the user asks ("board") or has said yes before. Otherwise, when the list has 5 or more items and 3 or more drafts, end the answer with the one offer line, once per conversation. To build it, copy the file and rewrite only its `board-data` JSON block from this answer (the schema is in the comment above that block). The chat answer stays complete.

## 6. Loop mode

A short read on what is happening at customers you were copied on or brought into: at most 10 lines, from dated events only.

1. **Scope.** The engaged-with filter (`scope.md`), last 30 days, with its three evidence columns plus `customer.status` and `customer.event.next_event`. Run the book fingerprint once (the first-run check in `scope.md`) even though the ask names its scope: if you hold a book, leave your book's accounts out, since loop is for accounts you are not responsible for, and say how many. Exclusions and the automated-only check as in section 3. Tell the user once that "copied on" here means customer mail you received, mail you sent, or meetings on your calendar, since Staircase cannot see Cc.
2. **Events.** One `lifecycle_event` report with top-level `arguments.dateRange` the last 7 days as an explicit array (rule 1), filter `lifecycle_event.customer` In [scope ids]; columns `lifecycle_event.id`, `lifecycle_event.type`, `lifecycle_event.type.label`, `lifecycle_event.date`, `lifecycle_event.customer.name`; sort by date Desc, dedupe by id (rule 16). Event type ids come from metadata.
3. **Read.** `staircase_list_communications` with the `event_ids` of the top 20 by rank, `per_event_limit` 5, `limit` 100. Summarize the linked thread nearest the event date. Summaries are paraphrase: label them "Staircase summary", never anyone's words. An event with no linked thread visible to you keeps its line with "no linked thread visible to you"; a `renewal` event reads "renewal recorded" (it fires after a renewal).
4. **Lines.** A headline first (30 words at most: how many accounts had a dated event, the most serious one, and the one move). Then numbered lines, one per account, at most 10, no table: `<Account> (<status, when not Active>; <your part: you met (N meetings) / you wrote / customer mail to you only>): <the event in plain words (plain-words.md, Events)>, <day month>: <what happened, 20 words at most>. Next meeting <local date>.` Two events on one account: the higher-ranked one, plus "+N more". Then one count line for accounts with no dated event in the 7 days ("no dated events; threads not read"), never "all quiet", and one pointer: "say 'check my copied threads' to read customer mail on those accounts".

   Rank rule (verbatim on `why`; one clause in How I built this): "Accounts with the most serious dated event first (churn notice or churn status, churn risk, extremely negative message, personnel change, commercial discussion, renewal, highly positive message, then other types), then the most recent event, then account name."
5. **One action,** with its verb, then the proof lines and the To act line as in owed mode. Offer a brief on the top account (staircase-account-brief), or, when the top line is a churn signal, an extremely negative message or a personnel change, a Slack draft to the account's owner (`customer.owner`, or the role field `portfolio_resolution` names; `action-types.md`). A summary that reads as already resolved: offer the brief, not the Slack.

Never a "what changed in scores" line: scores have no history. Never a line from a thread you cannot see.

## 7. Time off

**Out: coverage notes.** Needs the out dates (ask once if missing) and the covering colleague (optional; else `<who>`).

1. Scope: your book if you hold one (`portfolio_resolution`, Active), else engaged-with, last 30 days. Say which.
2. One `customer` report on the scope: `customer.name`, `customer.status`, `customer.renewal_date`, plus the three engaged-with evidence columns (the took-part split, section 5 step 2).
3. One `meeting` report with top-level `arguments.dateRange` the out dates (future dates work), filter `meeting.customer` In [scope ids]: every meeting while you are out, with subject, start and organizer email. It shows no attendees.
4. Owed mode steps 3 to 6 over the last 30 days, for what is owed now.
5. Sort the accounts:
   - **Needs cover:** an owed item; a live thread (a customer wrote in the last 7 days in a thread you took part in); a meeting in the window that you organize; a renewal inside the out dates or within 30 days after.
   - **Watch only:** a meeting in the window run by a colleague, at an account where nothing is owed. One line for all of them, with "check whether you are on these invites".

Output: the headline ("7 accounts need cover while you're out 9 to 13 Nov. First: <account>, <why>. Your hand-off note to <cover> is ready (draft 1)."); one three-line item per account that needs cover (heading: the account and what the cover should do; line 1: what is live while you're out, dated; line 2: the contacts and `Ready:`); the watch-only line; one hand-off note to the cover (Slack or email draft) with the table in short form; optional customer heads-up drafts for accounts with a meeting you organize or a waiting customer in the window ("I'm out <dates>; <cover> is your contact"), addressed to the thread's customer contacts (emails as in section 4, step 6). Dates in the drafts come from the threads or the user; never invent a deadline for the cover. Rank rule (on `why`; one clause in How I built this): "Customers waiting on you first, then your open promises, then commitments in your name with a meeting that week, then renewals; watch-only accounts last." Proof lines and the trail as in owed mode.

**Back.** "Out from <date>" means that date is the first day out. Run owed mode over the last 30 days (or since the day you left, when that is longer), so items open before you left still show; tag items that arrived while you were out "while you were out", and include recaps for meetings since the day you left. Then loop over the days you were out (10 lines). If you hold a book and staircase-csm-today is installed, point to its since-date mode for the book view in one line.

## 8. Drafts and write-backs

Every draft (`trust.md`, `action-types.md`):
- Cites only what the recipient said or was present for. A recap uses only that meeting; a reply uses only that thread. Never another contact's thread, a ticket, a stored field, a risk level or a score.
- Ours carry names; theirs read "you mentioned"; guessed owners are flagged and stay out of the customer text.
- No roadmap, release timing, pricing, terms or dates the user did not supply, even when said on the call: they go in internal notes with their source line. A date the user gave on the call for their own commitment may stay, marked "confirm" in the table. The customer's own plans and dates, as they said them, may appear under "you mentioned"; their commercial remarks (budget, renewal intent) stay internal.
- Short, plain text, no `>` bars, no em dashes, contractions on. The label sits outside the copy block (recipient, subject, "in the thread"); only the message goes inside (`delivery.md`, Act). Evidence ids go to the trail, never under or inside a draft. A next step no thread names is labeled "my suggestion" outside the block.

| Connector | Do |
|---|---|
| Gmail present | After the draft, ask once: "Create this as a Gmail draft?" On yes: look for a sent message or a draft with the same subject and recipient in the last 7 days. Sent: stop and say so. A draft exists: update it, never a second one. Otherwise create the draft, in the thread when it is a reply. Never send |
| Gmail absent | The text block is the deliverable |
| Gainsight CS present | Offer a Timeline note as text first (account, activity type from the profile, subject, body: the recap summary and commitments, no internal notes). Create only on yes. A CTA only for a risk the user promotes. When the Gainsight CS plugin is installed, hand logging to it |
| Slack present | Internal asks as drafts to the person or team (`action-types.md`). Never post |

Never say anything was sent, created or logged unless the tool result shows it.

## 9. Proof, trail and scheduled runs

Every answer ends with the two proof lines and, for a list, the To act line (`delivery.md`). The full trail prints on `why`: `Scope:`, `Window:`, `Seen:`, `Rank rule:` (owed, loop, time off), `Sources:`. The scope line for owed and loop follows `scope.md` ("engaged-with, you, emails sent or received and meetings, 4 Oct to 2 Nov, 33 accounts, all statuses (31 Active, 2 Prospect)"); N counts the accounts after exclusions, with the left-out count beside it. Recap uses its own line (section 4). Every `Seen:` mention in this file is a trail line.

Scheduled runs (personal routines on your own session, drafts only, tools limited to read plus draft):
- End of day: recap drafts for today's recorded meetings you attended, delivered to you (a DM to yourself or drafts addressed to you); one line per meeting with no transcript ("send notes to recap <subject>"). A quiet run posts nothing.
- Owed items ride the one morning push (staircase-csm-today's when installed), not a push of their own.
- Loop: weekly, 10 lines. Every run prints "data as of <time>".

## 10. What this skill adds, and the gap each rule covers

| Rule | Server gap it covers |
|---|---|
| Recap only from a transcript or the user's notes | About half of meetings have no transcript, and those have no attendees or content in any tool |
| "You" found by name among senders and Video attendees | Participants carry name and type only: no email, no To or Cc role; no participant filter on `staircase_list_communications` |
| Owed means you wrote or attended; received-only mail goes to loop | Recipients are not exposed, so "addressed to you" cannot be told from "copied" |
| Last sender read from `staircase_fetch_evidence` | List rows give one direction per thread (`mixed`), not the last sender |
| Split-reply check | A reply can land as its own thread, with no link to the first |
| Owner and side parsed from action-item text, guesses flagged | `action_items[]` are plain strings: no owner, side or due date |
| Meeting row joined to the Video row by account and day | The two share no id, and the `meeting` root has no attendee link |
| A person's threads listed by participant search, printed as found by search; meetings counted, then Video rows listed where search missed them | No exhaustive list of one person's threads; search drops rows below its relevance cutoff even under the limit |
| List calls batched so accounts x `per_account_limit` stays at or under 300; a capped account is read further back before any item on it is judged | `staircase_list_communications` caps rows per account and per call (100 by default, 300 at most) with no cursor |
| Paged account pulls sorted last on `customer.name`, totals checked with a COUNT | A sort on `customer.id` is silently ignored |
| Loop from dated events only | No score or field history |
| Self-only modes | Owed and loop read a person's own threads; nothing server-side scopes them to a viewer |
| The engaged-with filter from `scope.md`, never `customer.total_activity` | Chat counts leak across users under `filter.user` |
| Owed is rebuilt from the threads each run: a later message from our side closes an item | No server record of what was surfaced or handled |
