# Delivery: surface, answer shape, verbs, and where drafts go

## Surfaces: pick by the user's next move

| Next move | Sounds like | Chat (always complete) | Add only when it fits |
|---|---|---|---|
| Know | "when does X renew", "how many renew this quarter", "which renewal do I lean into" | The answer in 1 to 3 lines; a table of up to 8 rows when there are rows; one proof line | A Sheet or CSV, on ask, past 25 rows |
| Work a list | today, this week, follow-ups, renewals, my team | Headline with the first move; up to 5 items of 3 lines, grouped by when; one-line extras; drafts; proof | The action board (`assets/action-board.html`), on ask; offered in one line when the list has 5 or more items and 3 or more drafts (rule 3) |
| Walk into a moment | "prep me for X", "catch me up on X" | One screen: status line, 3 things to know, 3 to say or ask, the next move and its draft | A doc, on ask ("as a doc", "print it", "send it to") |
| Hand it to someone | exec weekly, QBR outline, retention review | Headline, 3 numbers, where the doc is | The doc: Claude's own document in Claude apps, else a markdown file; Google Docs or Notion only when the user asks |

1. **Chat is the complete answer.** A board or a doc is a second copy, never the only one. A scheduled push is the same answer cut to 12 lines, with verbs.
2. **Layers in order, never mixed.** Glance, scan, act, proof (below). Nothing from a lower layer moves up.
3. **Chat first; anything else earns its place.** The chat answer already gives every draft a copy button and every item a one-reply verb. A board or a doc repeats it and costs a full page of output (the board is about 60 KB), so: a doc unasked only when the move is handing it to someone; the board only when the user asks ("board", "make it clickable") or has said yes before, else offered once per conversation as the answer's last line when the list has 5 or more items and 3 or more drafts: "Want a board you can click through? Say 'board'." Never ask which surface before answering. No doc for a list (a list needs done and snooze), no board for one fact, a brief, a count or a voice readout.
4. **The user's words.** Labels from `plain-words.md`. No field ids, enum values, scores or evidence ids above the proof lines.
5. **One reply to act.** Every actionable line ends in one move and its verb (`draft 2`); plain words always work too.

## Answer shape: four layers, with budgets

| Layer | Budget | What goes in it |
|---|---|---|
| **Glance** | The headline, 30 words at most | The count in bold, then the first move, its deadline, what is ready: "**5 things need you this week.** First: Acme, waiting since 27 Oct on a sandbox question, meets with us at 14:30 today. Your Slack to Dana is ready (`draft 1`)." The first move is the earliest deadline where the user's action changes an outcome |
| **Scan** | About 80 words an item; whole scan through item 5 under 500 words | Each item is a bold heading line (the account, the move as a verb, the deadline) and up to 3 bullets: what happened, who, when, with at most one quote line under it; then `Ready:` the kind of draft and the recipient, the also-offer, and the verb. Lists group by when ("Do today", "Prep for Wed", "This week") and keep the engine's order inside each group. Layout: Chat layout, below. No table wider than 3 columns in a list answer; extra rows are one-line bullets |
| **Act** | Drafts after the list, numbered to match | The label sits outside the copy block ("**Draft 1: Slack to Dana**"); only the message goes inside, nothing the user would delete before sending except fill-ins they must complete ("[attach the screenshot]"). Contractions on. A Slack ask opens with the question, then the context, about 80 words. A customer reply stays at 2 or 3 sentences. "Nothing is sent" is said once, beside the drafts |
| **Proof** | Two lines, about 120 words | **How I built this:** which accounts, which dates, how much was read, the order in one clause, "data as of <time>". **What I couldn't see:** what is not visible, the one coverage gap that changes a decision ("risk is scored on only 5 of your 28 accounts, so a quiet account isn't a safe one"), and what was not opened, each with the phrase that opens it ("say 'check departures'") |

The full trail (scope, window, threads read out of `total_count` per `data-rules.md` rule 17, rank rule, sources, evidence ids) prints on `why` or `why <n>`, and in Claude Code also goes to `~/.staircase/runs/<date>-<skill>.md`. Report mode (below) keeps its full footer in the answer: that reader is checking numbers.

**Sources in the user's view** are a sender, a date and a channel: "Dana's email, 3 Nov 08:36", "the 28 Oct call notes". Quote only fetched text; a claim from a summary says "per the call notes". Evidence ids never appear above the proof lines; a doc keeps them in its appendix.

Always: names, numbers, dates. No em dashes. Account names (`customer.name`), never an id alone. Times in the user's local zone (`data-rules.md`, Dates). No revenue in ranked lists unless the user asks; a one-account answer may name stored revenue (CRM) on its status line when the job turns on money (renewal, risk, commercial, takeover, exec, escalation), never in a customer draft. "Your accounts" only for a book or engaged-with scope; a slice is "the Enterprise accounts". When you hold more rows than you show, say how many more and offer them; never drop them silently.

**One-account answers** (a brief): the status line opens the answer; the rest follows the same four layers.

## Chat layout: where the eye goes

Chat renders markdown, so structure carries the flow: the reader should see where one item ends and the next begins, which line is the customer's voice, and which line is the move, without reading every word. `_dev/scripts/check_output.py` checks the rules marked (checked).

1. **Three levels, never more.** `###` for sections (the when-groups, Also worth a look, Meetings, Drafts; in a brief: What to know, What to say or ask, Next move). A bold line for each item: `**1. Copperline** · get Priya a licensing answer before the 15:00 call`. Bullets under it. No `#` or `##` (they fill a phone screen) and no fourth level.
2. **Bullets carry the facts.** One fact a bullet, about 30 words at most, up to 3 bullets an item counting Ready. A blank line between items; nothing runs together.
3. **Customer voice is a quote line,** nested under the bullet it backs: `> "Can you confirm before we add the next team?" · *Priya Shah, Operations Manager, 08:12 today*`. At most one an item, fetched text only. The name and title come from the stakeholder record: the name alone when there is no title, never a guessed role. Our side is "you" or the colleague's first name and role ("Lee, renewal owner").
4. **The move is the last bullet** (checked): `- **Ready:** a Slack to Lee Moreno (renewal owner), plus a reply to Priya → draft 1`, with the verb in code style. The also-offer follows on the same bullet: "Also: the full brief → `brief Harbor Analytics`".
5. **Every verb is in code style** (checked): `draft 2`, `done 4`, `snooze 5 until Friday`, `brief Acme`, so it reads as "type this", in items, rows, notes and the To act line.
6. **Tags only when they change the move,** as the item's first bullet, in italics: `- *Don't miss: renews 14 Nov at high risk.*` Risk words stay in words ("high risk"); no emoji or colour codes.
7. **Rules (`---`) only before Drafts and before the proof lines.** Tips and notes in italics ("*Tip: reply with a number and a word, like `draft 1` or `done 3`.*"). The proof is two bold-label paragraphs.
8. **Drafts:** a bold label line (`**Draft 1: Slack to Lee Moreno**`), then the code block with only the message in it, so the copy button takes exactly what gets sent.
9. **Extra rows are one line each:** `- **6. Lumen Freight** · their main contact leaves the team 9 Nov; renews 16 Dec. Intro to a second contact → \`draft 6\``. Secondary strips (CRM may be out of date, Checked, nothing needed now) are a bold label and bullets under Also worth a look.
10. **A Slack push** uses bold in place of `###` and keeps quote lines and bullets (Slack renders both).

## Verbs

One grammar, `<verb> <number>`, with a letter for the also-offer (`draft 2b`). Teach these: `draft`, `done`, `snooze`, `not mine`, `why`, plus `draft all` and `brief <account>`. Each actionable line shows its verb once, at the end of its `Ready:` line. The last line of a list, verbs in code style: "**To act:** `draft 1` saves it to your Slack or Gmail drafts · `done 4` or `snooze 5 until Friday` clears one · `not mine 3` · `why 2` shows the reasoning. Plain words work too." When the board earns an offer (rule 3), that one line follows it. On a first run (no cleared items yet), one tip line sits under the headline; it stops once the user has used any verb. "Wrong" is accepted, never taught: treat it as `not mine` and offer the CRM-fix note when the item rests on a stored field. Clearing mechanics: `action-priority.md`, Ledger.

## States

- **First run:** "I found 28 accounts where you're the CSM. Is that your book? (yes, or tell me your role)", then the list with the verb tip.
- **No Staircase connector:** in Claude apps, "Staircase isn't connected yet. Add it from your connector settings, then ask again." The CLI command only in Claude Code.
- **Empty day:** "Nothing needs you today. Next up: <nearest meeting or renewal>. I checked 28 accounts." A scheduled push still posts nothing on a quiet day.
- **Blind spots** always end in the phrase that opens them.

## Report mode

Runs for ask-style reports (`staircase-ask`): the user says "report", or the answer is a group-by or a list of rows. A count answer (one to three numbers, no rows) is a quick count: steps 2 and 5 plus the coverage check only, then offer the saved spec in one line. Persona skills (a today list, a brief, voice, a team view) do not run report mode: they offer the saved spec of their main calls on `why`.

1. **Definition card,** in words, above the table: what one row is (an account, an event, a contact), the scope, the statuses, the window (with dates), each filter, each column, and the rank rule if sorted. When a term has two readings, pick the one the fields support, name it, and name the alternative in one line ("no touch from us: no email, meeting or reply from our side logged since 4 Oct; a stricter reading, no two-way exchange, is available"). "Us" and "we" mean our whole side (any colleague) unless the user says "me"; say which. Ask first only when no default makes sense.
2. **Build** with ids, operators and options copied from metadata, per `data-rules.md`. Start lean: `customer.id`, `customer.name`, and only the columns the definition needs (a base-rate column such as total accounts per group is allowed). Thresholds and windows go in the filter as explicit dates (`data-rules.md`, Dates), never in your arithmetic.
3. **Group.** "By tier", "by owner" is a report rooted on the group entity with child aggregations (there is no `groupBy`). Give each aggregation column a distinct label, and sort by the headline column, then by name.
4. **Reconcile.** Run a scalar COUNT with the same filter for each differently filtered total. Print "Reconciles: <groups> sum to N; COUNT is N" for a rollup, or "rows returned: N; COUNT is N" for a list. If they differ, show the remainder as its own row ("no tier: N") or name the filter that dropped rows. A table that does not reconcile is not delivered as final.
5. **Check it narrowed.** Zero rows, or every row, is a question before it is an answer: check the option id, the operator and the window.
6. **Saved spec.** End with the ReportConfig of each call that produced a number in the answer, in a code block titled "Report setup (run it again)". In Claude Code, offer to save it to `~/.staircase/reports/<name>.json`. Export to a Sheet or CSV only on the user's yes.

Report footer, one line each: `Scope:`, `Window:` (the dates that ran, from the user's local date; a named fallback window prints by name, with "bounds set by the server"), `Seen:` (threads read out of `total_count`, blank fields, coverage of sparse fields, data freshness), `Rank rule:` on every ranked list, `Sources:` (fields by name, the report). Also say what the report cannot show: history and trends (scores are current values only), product usage, CRM pipeline, anything outside connected mailboxes.

## Drafts and write-backs

| Target | Prepared as | Needs the user's yes for |
|---|---|---|
| Email | A draft in the user's mail connector, or a copy block | Sending |
| Slack | A draft, or a copy block | Sending or posting |
| Calendar | A proposed hold or proposed times | Creating an invite |
| Gainsight CS (Timeline, CTA, success plan) | Drafted fields, or a copy block | Creating or updating the record |
| Ticket (Linear, Jira) | A draft | Creating it |
| Doc | Claude's own document in Claude apps, else a markdown file | Writing to Google Docs or Notion, which happens only when the user asks |
| Sheet or CSV | The table | Writing the Sheet or the file |

Optional connectors: detect them, use them when present, fall back to a copy block when absent. Never require one. Name the connector you used.

## Memory on the user's side

| What | Claude Code | Elsewhere |
|---|---|---|
| Scope | `~/.staircase/me.md` | The scope line in "How I built this" |
| Cleared items (account-level, scoped to the book) | `~/.staircase/ledger.jsonl` | A pasted state line (`action-priority.md`); to the user: "Paste this line next time so I remember what you cleared" |
| Saved reports | `~/.staircase/reports/<name>.json` | The "Report setup" block |
| Board yes or no | `~/.staircase/me.md` (`board: yes`) | Offered again, once, in each new conversation |

## Scheduled runs

- One morning push per person; a quiet run posts nothing.
- Personal routines run on the user's own session.
- Org routines on a system token stay aggregate (no account names) or go to admins only, until the server scopes output to each recipient.
- Every scheduled output says "data as of <time>".
