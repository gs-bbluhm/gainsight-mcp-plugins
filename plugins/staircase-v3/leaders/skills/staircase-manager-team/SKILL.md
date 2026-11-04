---
name: staircase-manager-team
description: "A team manager's weekly view of the team's customer accounts from Staircase AI: load and exposure facts per team member (alphabetical, never ranked), a separate lane for likely pooled or placeholder books, up to 10 accounts to lean in on with the rank rule printed and a mark when an account is already on that CSM's own list, and a Slack note to the CSM with one ask. Use for 'how's my team', 'what's at risk across my team', 'who on my team needs help', 'team renewals', 'what's renewing on my team', '<name> is leaving, who takes their accounts', 'rebalance my team's books', or 'write my update to my VP'. Works for '<name>'s team' too. Not for a 1:1 with one report (staircase-manager-1on1-prep), one account in depth (staircase-account-brief), or your own book (staircase-csm-today). Drafts only: nothing is sent, and reassignment drafts stay with you until you release them. Needs the Staircase AI connector."
license: MIT
compatibility: "Needs the Staircase AI MCP connector. Works in Claude Code, Claude Desktop, Cowork and claude.ai. No script runtime needed; Slack, mail and Gainsight CS connectors are optional."
metadata:
  version: "3.0.0-alpha.1"
  layer: "persona"
  pack: "staircase-leaders"
---

# Staircase Manager Team

A first-line manager's Monday view of the team's book: where load and exposure sit, which accounts deserve the manager's own move this week, and the note to send the CSM. Four modes: the **weekly view** (default), **team renewals**, **reassign** ("<name> is leaving") and **my update to my VP**.

The server owns the mechanism. `portfolio_resolution` (TEAM path) settles who is on the team and which role field links each member to accounts. This skill adds the manager's judgment: how to show people without ranking them, how to keep a pooled book from hiding inside the team, which accounts a manager's move can change, and the draft that hands the account back to its holder.

The shared references sit in this skill's `references/` folder. Read each at the moment named.

| File | Read it |
|---|---|
| `references/scope.md` | Before the first call (statuses, the scope line, pooled lanes, engaged-with team form) |
| `references/data-rules.md` | Before the first report (Dates first) |
| `references/evidence.md`, `references/delivery.md`, `references/plain-words.md` | Before the first answer (surface, layers, verbs, states, the user's words) |
| `references/trust.md` | Before any draft |
| `references/company-profile.md` | Once per session (pooled users, exclusions, Slack teams) |
| `references/action-priority.md`, `references/action-types.md` | Before the lean-in list (stage 2, suppression, draft evidence) |
| `references/staircase-account-brief.md` | Only when the manager asks for a handoff or takeover brief (if the file is absent, follow the `single_account_analysis` recipe) |

## 1. The people rule (every mode, every answer)

People are never ranked. Accounts may be ranked, with the rule printed.

- Rows of people sort alphabetically by name. No order by load or exposure, no color, status, score, percentile, "top", "bottom", "stretched", "behind" or "needs help" label on a person.
- No per-person activity numbers: emails sent, meetings held, response time, sentiment received, effort hours. They read as surveillance, and effort spans all of a person's accounts and cannot be filtered.
- A person's numbers are load facts about their accounts (how many, renewing, risk, untouched), side by side with everyone else's in one alphabetical list. The manager judges.
- Flag a person's row only against a line the manager states ("anyone with more than 6 renewals in 90 days"), as "over your line", and say which line.
- "Who on my team needs help": answer with the load lines and the lean-in accounts, then one line: "I don't rank people. Give me a line (for example, renewals in 90 days above N) and I'll mark the rows over it."
- Owed replies and loop digests are self-only (`trust.md`). "Who does <name> owe a reply" gets: "That list is <name>'s own to run; I can show the accounts on their book where a customer is waiting, without reading their inbox for them." Then run one count-only pull on that member's book (their picked field, Active): `customer.name` and `customer.email.customer_open_threads` with `dateRange` the last 30 days, filtered GreaterOrEqual 1, sorted by name. List those accounts as "a customer thread is open (likely waiting on us; direction not confirmed)", with no thread content and no read of their mail.
- Never quote a team member's own emails back to the manager. Cite customer evidence, stored fields and dated events.
- Thread access is per user. The manager may see fewer threads than the account holder: zero threads means "not visible to you", never "nothing happened".

## 2. Before the first call

1. **Connector.** Staircase tool names end in `staircase_run_report`, `staircase_get_recipe` and so on. If none are present, stop with the no-connector state in `delivery.md` (the CLI command only in Claude Code).
2. **Recipes.** One `staircase_get_recipe` call with `["portfolio_resolution", "churn_signal_resolution"]`. Follow them. Where this skill and a recipe disagree, the recipe wins, except the date rules in `data-rules.md` (rules 1 to 3) and the status reading in `scope.md`.
3. **Metadata.** `staircase_report_metadata` once per session. Never paste or summarize it. If the runtime saves it to a file, query the file with a tool (for example `jq`) for: every `customer` field of type Reference with `referencedEntity` `user` (the role fields, with their labels), the `customer.status` option ids, `eventType` options, and `current_user_id`.
4. **Company profile.** `exclusions.pooled_user_ids` marks pooled users outright; `exclusions.own_org_account_ids` and `test_accounts` are left out and counted; `teams` names the Slack channels for asks.
5. **Dates.** Take the user's local today (T) and compute every bound once, per `data-rules.md` Dates, with a tool when one runs: next 90 days `[T, T+89]`, next 60 days `[T, T+59]`, last 30 days `[T-29, T]`, last 14 days `[T-13, T]`, last 7 days `[T-6, T]`; no touch in 30 days means `customer.last_touch` LessThan `<T-29>T00:00:00Z` or NotDefined; no touch in 21 days, LessThan `<T-20>T00:00:00Z` or NotDefined. Print the dates in the load lines and in the trail.

6. **Sort keys.** Every `customer` pull ends its `sortBy` with `customer.name` (sorting on `customer.id` is silently ignored, so paging on it can drop or repeat rows). Dedupe joined rows by `customer.id`.

Statuses: every mode here is about current customers, so add `customer.status` In [the Active option id] and print "Active only" (`scope.md`, statuses).

## 3. Scope: the team

Follow the recipe's TEAM path. What it leaves to this skill:

1. **Which manager.** "My team": `current_user_id`. "<name>'s team": a `user` report with `user.full_name` Contains the name; several matches, ask. "My org", "skip levels", "everyone under me": the recipe's `manager`-entity step. Otherwise direct reports only.
2. **Fingerprint the team once** (recipe TEAM step 2): columns `user.id`, `user.full_name`, `user.title`, `user.has_access`, `user.is_auto`, plus one unconditioned COUNT per role field. Nine role-field COUNTs ran in one call on a 16-person team. If it returns no rows, the tenant may not fill `user.manager`: ask the manager to name the team, then use the recipe's SEVERAL NAMED USERS path.
3. **Sort each member into one lane:**

| Lane | Test | Shown as |
|---|---|---|
| Likely pooled | The likely-pooled test in `references/scope.md` (Book), on the fingerprint counts | Its own row, labeled "likely pooled", never folded into a person or a team average; never offered as a receiver in reassign mode |
| Holds a book | Any role-field count above 0 | A line in the load list, on the field the recipe's PICKING FIELDS gives (ties: both fields, one line each) |
| No Staircase access, holds a book | `has_access` not true, any role-field count above 0, and not likely pooled | A row, marked "no Staircase access". Add one line: "If <name> has left, these accounts may need a new holder" and offer reassign mode |
| Holds nothing | Every role-field count 0 | One line under the load list: "Hold no accounts: <names>" (the recipe asks to report them, not omit them) |

4. **Fields per member, never one field for the whole team.** Group members by their picked field. The team filter is an `Or` of one condition per field: `customer.<field>` In [named members on that field]. The pooled lane gets its own filter: `customer.<field>` In [pooled ids on that field].
5. **Totals come from scalar COUNTs, never from summing members.** An account held by two members on different fields counts once in the team and once in each member's row.

The scope line (`scope.md`; it prints in the trail, and How I built this says it in words), for example: `Scope: team, <manager>'s 12 direct reports (9 hold a book, 1 likely pooled, 2 hold none), CSM field for 8 and a renewal-owner field for 1, 240 Active accounts held by named members, plus a pooled lane of 600, Active only.`

## 4. Weekly view (default)

Answers "how's my team", "what's at risk across my team", "who on my team needs help".

### 4.1 Load facts (one call per role field in use)

A `user`-rooted rollup, filtered `user.id` In [members on that field, named and pooled], sorted by `user.full_name`, then `user.id`. Four conditioned COUNTs per call, every condition starting with Active:

| Column label (dates printed) | Child condition, added to `customer.status` In [Active] |
|---|---|
| Active accounts | none |
| Renewing `<T>` to `<T+89>` | `customer.renewal_date` InRange `[T, T+89]` |
| Risk 4 or 5 | `customer.risk.risk_level` GreaterOrEqual 4 |
| No touch from us since `<T-29>` | `Or`: `customer.last_touch` LessThan `<T-29>T00:00:00Z`, `customer.last_touch` NotDefined |

Each column: `{"field": {"rootEntityPath": "user", "childEntity": "customer", "referenceField": "customer.<field>", "aggregation": "COUNT", "condition": {"operator": "And", "conditions": [<Active>, <the row's condition>]}}, "key": "<k>", "label": "<label with dates>"}`.

Four counts per call is the tested shape; six ran clean once, nine with an effort column timed out. On `timeout`, split the columns in half once and say so. A member on a minority field (one or two people) gets a small call of their own.

### 4.2 Team totals (scalar COUNTs)

1. Distinct Active accounts held by named members (team filter, Active).
2. The same with `customer.risk.risk_level` Defined: the risk coverage ("risk level on N of M").
3. Distinct Active accounts in the pooled lane (the pooled filter, every pooled user on their own field in one `Or`), and the same with `customer.renewal_date` InRange `[T, T+89]`. Two pooled users can share accounts, so never add their rollup rows.
4. Distinct Active accounts across the whole team, named and pooled filters joined in one `Or`. Then `overlap = named + pooled - whole team`: pooled accounts that also have a named member in another role. Print it when above 0.

Reconcile: "Members' Active counts sum to S; distinct Active accounts held by named members: N" (the difference is accounts two members share).

### 4.3 Lean-in candidates (stage 1, named members)

Two `customer`-rooted pulls on the same filter, joined on `customer.id`: P1 sorted `customer.renewal_date` Asc then `customer.name` Asc, P2 sorted by `customer.name` Asc; pages of 100 (page on `has_more`; confirm the row total with a scalar COUNT on the same filter, and dedupe by id). Never sort or page on `customer.id`: that sort is silently ignored, so pages can drop or repeat rows.

Filter: the team filter, Active, and an `Or` of
- `customer.renewal_date` InRange `[T-29, T+59]` (a date passed in the last 30 days, or due in the next 60);
- an `And` of `customer.renewal_date` LessThan `<T-29>` and `customer.risk.risk_level` GreaterOrEqual 4 (an older passed date on a risky account);
- `customer.last_lifecycle_event_date` with `eventType` each of `churn_risk`, `churn`, `exceptional_negative`, `farewell`, GreaterOrEqual `<T-13>` (a Date: `YYYY-MM-DD`); use only event ids metadata offers;
- an `And` of `customer.risk.risk_level` GreaterOrEqual 4 and the no-touch-in-21-days `Or`.

| Pull | Columns besides `customer.id` |
|---|---|
| P1, state | `customer.name`, `customer.<field>.full_name` for each field in use, `customer.renewal_date`, `customer.risk.risk_level`, `customer.revenue_converted` (tie-break only, never printed), `customer.last_touch`, `customer.event.next_event` |
| P2, signals | `customer.name` (the sort key), `customer.last_lifecycle_event_date` for `churn_risk`, `churn`, `exceptional_negative`, `farewell` and `renewal_discussion` (one column each, labels from `eventType` options), `customer.event.last_event`, `customer.email.organization_last_sent`, `customer.url` (the account's page: each item's `account_url`, `references/data-rules.md` rule 29) |

P1 ran at 10 columns on a team using four role fields. If either pull times out, split it once.

### 4.4 The rank rule (on `why` and in the run log, as written, dates filled in; How I built this carries it in one clause)

> Lean-in accounts are ranked by where a manager's move can change the outcome. Group 1, a renewal decision: the renewal date passed since `<T-29>` with the account still Active, or falls by `<T+59>`, and the account is risk 4 or 5 or has no meeting booked; or an older passed date on a risk 4 or 5 account. Group 2, a fresh signal since `<T-13>`, ordered by signal (a churn notice, then a very negative message, then churn risk, then a personnel change at the customer), then by how many fresh signals the account has, then by the renewal date closest to today. Group 3, exposed and quiet: risk 4 or 5 with no touch from us since `<T-20>`. Within Groups 1 and 3: the renewal date closest to today first (just passed or coming up), then higher risk, then higher revenue within the team (not shown). The read covers up to 6, 4 and 2 accounts from the three groups, and always every account with a churn notice since `<T-13>`. After the read, accounts the threads show are settled are dropped, and accounts in hand (a two-way thread in the last 7 days and a meeting booked) move to the end of the whole list, below Group 3, before the cap of 10. People are not ranked.

- "No meeting booked": `customer.event.next_event` blank or before T.
- An account in several groups takes its highest group, once.
- **Record check, not lean-in:** an Active account whose renewal date passed before `<T-29>` and is not risk 4 or 5 is CRM hygiene, not a manager's move. One scalar COUNT (team filter, Active, renewal LessThan `<T-29>`, and risk below 4 or NotDefined) plus an 8-row pull sorted by renewal date Desc gives one line: "N Active accounts show a renewal date more than 30 days past (<up to 8 names>): ask each holder whether it closed and the date moved."
- **Base-rate guard** (`evidence.md`): a test true on more than 80 percent of the candidates (for example "no meeting booked") does not separate accounts. Drop it from the groups and name it.
- No script runtime: this rule is already the reduced mode (`action-priority.md`, scoring with no script): sort by group, then nearness of the renewal date to today, then risk. Do not multiply scores by hand. With a script runtime, the same rule may run in a script; never a different rule.
- Tally the groups by listing each group's account ids, then counting the lists; never estimate a count by eye.

### 4.5 Stage 2: read the shortlist (required)

Stage 1 is a shortlist, never the answer (`action-priority.md`). Take the top 6 of Group 1, the top 4 of Group 2 and the top 2 of Group 3; a group with fewer rows passes its spare places to the other groups, Group 1 first (12 in all). Then add every candidate with a churn notice since `<T-13>` that is not already on it, whatever its group or rank: a fresh churn notice is always read, even when that takes the shortlist past 12. Then:

1. `staircase_list_communications` with those `account_ids`, `date_range` `["<T-13>", "<T>"]`, `per_account_limit` 5.
2. For every shortlisted row with a fresh signal (any group): a `lifecycle_event` report with top-level `arguments.dateRange` `["<T-13>", "<T>"]`, filtered `lifecycle_event.customer` In [those ids] and `lifecycle_event.type` In [the four event ids]; columns `lifecycle_event.id`, `.type`, `.date`, `lifecycle_event.customer.name`; sort by date, dedupe by id. Then `staircase_list_communications` with those `event_ids`.
3. For a churn notice or churn risk row, read it the `churn_signal_resolution` way: a notice is something said, not an outcome. Check `customer.status` and what the thread says.
4. `staircase_fetch_evidence` only for the quote a draft needs (customer-side sender only, `evidence.md`), or with a `transcript_query` when a summary cannot say which side a personnel change is on.

For each row decide: **keep** (write its line from what the threads show; the evidence id goes to the trail), **settled, drop** (only when a thread shows the outcome in writing: signed, closed, or a departure confirmed as a false alarm; an approval still waiting on a signature is not settled; say so in the Checked line), or **in hand** (a two-way thread in the last 7 days and a meeting booked: keep it, and the move becomes "ask if they want you on the <date> call"; when the threads show a customer deadline before that meeting, the move is "ask what's needed before <deadline>"). A personnel change on our side (a colleague leaving or joining) is not a customer signal: drop it from Group 2 unless it leaves the account with no holder. Order the kept rows by the rule (in-hand rows last), keep at most 10, and name any read row the cap cut. A read row with a fresh churn notice is never cut silently: if the cap cuts it, name it with its date in the line under the list.

### 4.6 "On their list"

A row is on the holder's own today list when any of these hold: a renewal date passed since `<T-29>` or due by `<T+29>`; a churn notice, churn risk or very negative message since `<T-13>`; a meeting today or tomorrow (`customer.event.next_event` on T or T+1); a meeting in the last 72 hours with no email from us since (`customer.email.organization_last_sent` before `customer.event.last_event`). Most Group 1 and 2 rows meet this by construction, so mark only the exceptions: add to the first line of a row that meets none of them "Not on <first name>'s list from today's signals." Under the list print one count line: "N of the M rows are already on their holders' own lists from today's signals; the rest are marked." The mark rule goes to the trail (section 9). This is a proxy built from the same signals: no server record of anyone's list exists yet.

### 4.7 The pooled lane

From the load rollup: the pooled row's four facts, its share of the team ("the pooled lane holds 600 of the team's 820 Active accounts, and 110 renewals by `<T+89>`"), and the overlap from 4.2. Then up to 5 pooled accounts that most need a named holder: a P1-shaped pull on the pooled filter, Active, renewal InRange `[T-29, T+59]`, and risk 4 or 5 or no touch since `<T-29>`; sorted by renewal date, `pagination {from: 0, to: 5}`. Older passed dates in the pool go in one record-check count, like section 4.4. Show any named co-holder ("CE CSM: <name>"). The move for each: assign a named holder, or a scaled play.

Optional, one scalar COUNT: pooled Active accounts the team engaged with in the last 30 days, using the engaged-with team form in `scope.md` (`user.manager` In [manager id] in both `filter.user` slots). Print it as a coverage fact, never per person.

### 4.8 Weekly view output

Follow `delivery.md` (Work a list: the four layers and their budgets, verbs, states; Chat layout: where the eye goes) and `plain-words.md` above the proof lines; the people rule (section 1) holds in every line. Three levels only: `###` sections, a bold line per item, bullets; no `#` or `##`. In order:

1. **Headline,** 30 words at most, the count in bold: how many accounts on the team need the manager's move this week, the first one (item 1) with its holder, its deadline, and what is ready, the verb in code style: "**4 accounts on your team need your move this week.** First: Northwind (Member C), renews 14 Nov at high risk, no meeting booked. Your Slack is ready (`draft 1`)."
2. **Lean in this week,** the top 5 kept rows as items, each group a `###` heading. Inside a group the section 4.4 order holds; numbers run in the order shown; an empty group does not print.

| Group | Goes there |
|---|---|
| Do today | A deadline today or tomorrow (a renewal date, a customer deadline the threads show, a meeting), or a churn notice in the last 2 days |
| Before <day> | An in-hand row whose meeting falls later this week (the move: offer to join), one group per day |
| This week | The rest of the top 5 |

   Each item is a bold line and up to 3 bullets: ``**1. <Account>** (<holder>, <role>) · <the manager's move>, <deadline>``. The bullets say what we see, dated, from the threads or Staircase, one fact a bullet, with at most one customer quote line under its bullet (`> "exact words" · *Name, Title, when*`, fetched text only), plus the section 4.6 mark as an italic bullet ("*Not on <first name>'s list from today's signals.*") when it applies. The last bullet is the move: ``- **Ready:** a Slack to Member C offering to join → `draft 1` ``.
3. **`### Also worth a look`,** rows 6 to 10 of the lean-in list, one bullet each with the holder and the move ("- **6. Contoso** (Member B) · renewal date passed 28 Oct, still active; in hand, meeting 5 Nov. Ask if they want you on the call → `draft 6`"). Then, each only when it has rows, a bold label with bullets: **CRM may be out of date** (the section 4.4 record-check line), **Checked, nothing needed now** (settled rows dropped, our-side contact changes), and "<N> more candidates matched no group (`more`)". A read row with a fresh churn notice that the cap cut is named here with its date.
4. **`### Your team's load`,** alphabetical by name, never ranked, one bullet per person with the name in bold, then the likely pooled row, then the distinct count: "- **Member A** (CSM): 31 accounts · 5 renew by 30 Jan · 4 high risk · 1 with nothing from us since 4 Oct". Under it, one italic note each when they apply: "Members' counts add to S because N accounts sit with two people"; "Hold no accounts: <names>"; "<name> has no Staircase access (`<name> is leaving` plans a handoff)".
5. **Shared queue (likely pooled),** a bold label with one or two bullets at the end of the load section: its share of the team's accounts, renewals by `<T+89>`, the overlap, and up to 5 accounts that need a named holder.
6. **Drafts,** after a rule (`---`), under `### Drafts` with one italic line: one Slack note for each of the top 3 (section 8), numbered to match, each a bold label line and then the code block with only the message; the rest on `draft <n>`.
7. **Proof,** after a rule, two bold-label paragraphs. **How I built this:** whose team in words ("your 9 direct reports: 7 hold accounts, 1 is a shared queue, 1 holds none"), the dates read, how many accounts were read closely, "ordered by where your move can change the outcome: renewal decisions, then fresh warnings, then high-risk accounts gone quiet; people are listed alphabetically, never ranked", "data as of <time>". **What I couldn't see:** threads your team can see and you can't; the coverage gap that changes a decision ("risk is scored on only 38 of 180 accounts, so the high-risk counts are floors"); roles not included, with the phrase that adds them in code style (`include other roles`).
8. **To act,** the last line, with the verbs this view supports, in code style: "**To act:** `draft 4` writes the Slack for that row · `brief Northwind` for the full account · `why 2` for the reasoning. Plain words work too."

**The trail** prints on `why` (in Claude Code also `~/.staircase/runs/<date>-staircase-manager-team.md`): section 9's lines. `why <n>`: that row's group, the signals behind it with dates, its evidence ids and stored fields.

**The board, on ask** (`delivery.md`, rule 3). Build `assets/action-board.html` only when the user asks ("board") or has said yes before. Otherwise, when the lean-in list has 5 or more rows and 3 or more drafts, end the answer with the one offer line, once per conversation. To build it, copy the file and rewrite only its `board-data` JSON block from this answer (the schema is in the comment above that block). The chat answer stays complete; people stay alphabetical and unranked there too.

## 5. Team renewals mode

Answers "team renewals", "what's renewing on my team", "renewals across my team in the next 120 days". Default window: the next 90 days (a number the manager says wins).

1. Scope (section 3) and the section 4.2 scalar COUNTs for the scope line (named distinct, pooled, whole team). No load rollup.
2. **R1:** team filter, Active, `customer.renewal_date` InRange `[T, T+N-1]`; columns `customer.id`, `customer.name`, holder `full_name` per field, `customer.renewal_date`, `customer.risk.risk_level`, `customer.event.next_event`, `customer.last_touch`. Sort renewal date, then `customer.name`; page to the end; confirm with a scalar COUNT. Run R1 and R2 with the window widened to start at `<T-29>`: rows with a date passed since then sit at the top of the list, flagged "date passed <date>" (still-open decisions).
3. **R2:** the same filter; `customer.id`, `customer.last_lifecycle_event_date` (`renewal_discussion`), `customer.relationship_score.stakeholders_count`, `customer.last_dm_touch`, `customer.last_lifecycle_event_date` (`farewell`), `customer.url` (each row's `account_url`).
4. **Flags per row:** risk 4 or 5; no meeting booked; no commercial discussion since `<T-89>` (the `renewal_discussion` event; use its label from metadata); one contact or fewer; a personnel change since `<T-29>`. Run the base-rate guard on each flag before showing it.
5. **Older passed dates:** the section 4.4 record check (renewal before `<T-29>`): one scalar COUNT and an 8-row pull, one line.
6. **Read the 5 soonest flagged renewals** (one `staircase_list_communications` call, `date_range` `["<T-29>", "<T>"]`, `per_account_limit` 5): where each renewal stands, its evidence ids in the trail. A thread contradicting a flag wins over the flag; show both with dates.
7. **Pooled lane:** the pooled renewal count in the window, and its 10 soonest renewals (same columns as R1, `pagination` 0 to 10).

Output (`delivery.md`, Work a list): the headline, 30 words at most (renewals in the window for named members and for the shared queue, how many carry a flag, and the one that needs the manager first: the first row of "Where the top 5 stand" whose read shows an open decision, with its draft). Then **Where the top 5 stand,** the 5 soonest flagged renewals as three-line items (heading: account, holder, the move, the renewal date; what the threads show, dated; `Ready:` the Slack to the holder and its verb). Then **All renewals,** soonest first, at most 25 lines (say how many more), grouped under one heading per month, one line each: "<d Mon> · <account> (<holder>) · <flags in words: high risk, no meeting booked, no renewal conversation since <date>, one contact, a contact change since <date>>"; a date passed since `<T-29>` heads the list as "date passed <date>". Then the shared queue in one or two lines, the CRM line (step 5), the drafts, the proof lines and the To act line, as in section 4.8. Rank rule (trail): "Sorted by renewal date, soonest first; flags shown, not weighted. The read covers the 5 soonest flagged renewals."

## 6. Reassign mode

Answers "<name> is leaving, who takes their accounts", "rebalance my team's books", "assign the pooled renewals". The departure may not be announced yet: everything stays with the manager.

1. **Resolve the person** with the recipe's SINGLE USER step 1. Check they report to this manager; if not, say so and continue only on the manager's yes. If they already have no Staircase access, say so.
2. **Their book:** the recipe's field pick. One small `user`-rooted rollup for that person with an Active COUNT per other non-zero role field gives one line: "Also holds Active accounts as <role> (N), <role> (N): moving those is a separate call; say 'include them' to add them."
3. **Transfer list:** P1 columns plus `customer.last_lifecycle_event_date` (`farewell`, `churn_risk`) on that person's field, Active. Show an event date only when it falls since `<T-89>`; older dates are blank. Urgency order, printed: "a renewal date passed since `<T-29>` or due by `<T+89>` first (closest to today first), then risk 4 or 5, then no touch from us since `<T-29>`, then the rest by renewal date." One line of state per account. Before writing the state lines, read the 3 most urgent rows (one `staircase_list_communications` call, `date_range` `["<T-13>", "<T>"]`, `per_account_limit` 5) and write their lines from the threads (evidence ids in the trail); every other row's events print as "logged, unread".
4. **Receiving view:** the load facts (section 4.1) on the departing person's role field, for every other named member with a count above 0 on that field, alphabetical. One line names the members who hold books only on other fields. Pooled users are never receivers. Never pick the person, and never suggest one.
5. **A split:** when the manager states one ("<member A> takes the Enterprise ones, <member B> the rest") or a rule ("even out renewals in the next 180 days", "keep parent and child accounts together"), show each receiving member's load facts before and after, alphabetical, one line per person with the arithmetic in words ("Member A: 27 + 9 = 36 accounts · 4 + 2 = 6 renew by 30 Jan"). With no split stated, end the section with: "Tell me who takes which, or a rule to split by, and I'll show everyone's load after the move and draft the notes."
6. **Handoff briefs:** one line each in the transfer list. Full takeover briefs on ask, for up to 10 accounts in batches of 5 (`references/staircase-account-brief.md`, takeover lens; otherwise the `single_account_analysis` recipe).
7. **Drafts, held** (`trust.md`): before a split, one held reassignment request to CS ops with every transfer-list account and a blank "to" column, so the manager fills names and releases it. After a split exists, a Slack note to each receiving member (their accounts, the most urgent one first); an intro email from the new holder to each account's main contact; a reassignment request to CS ops (account, role field, from, to). Label every draft, outside its copy block, "Held: release when the change is announced." Never draft to a channel the departing person can see, and never a message to the departing person. Role fields change in the CRM, not in Staircase.
8. **Shape:** the headline (who is leaving, how many accounts, the most urgent one), the transfer list one line per account, the receiving view, the held drafts, then the proof lines and the trail as in section 4.8. No table wider than 3 columns.

## 7. "My update to my VP" mode

Answers "write my update to my VP", "my weekly update for <VP>", "team summary for my boss". A short draft the manager edits and sends.

1. Run the weekly view's data (sections 4.1 to 4.7) if it has not run this session, plus three scalar COUNTs on the whole team filter (Active): renewing by `<T+89>`, risk 4 or 5, and risk level Defined (the coverage). The headline uses these distinct counts, never member sums.
2. **This week:** one `lifecycle_event_type`-rooted rollup, columns `lifecycle_event_type.id`, `lifecycle_event_type.label`, and two child COUNTs of `lifecycle_event` (named members, pooled lane), each conditioned on `lifecycle_event.date` InRange `[T-6, T]`, `lifecycle_event.customer.status` In [Active], and the team or pooled `Or` written as `lifecycle_event.customer.<field>` In [ids]. These count events, not accounts: say "events".
3. **Wins:** up to 2. Candidates: `renewal` events this week (a renewal that closed) and `exceptional_positive` events. Read each with `staircase_list_communications` (`event_ids`) and quote only from `staircase_fetch_evidence`, a customer-side sender only. A renewal event with no linked communication is counted as "renewal events logged", never called a win. Courtesy thanks and praise for fixing our own problem are not wins. None found: say "no verified win this week".
   In "this week", label `farewell` events "personnel-change events (either side, unread)": the type also fires on our own staff changes. Leave `organization_personnel_change` out.
4. **The draft** (a copy block with its label outside, per `delivery.md`, Act; Slack or mail draft only if that connector is present and the manager asks). The answer: a headline of 30 words at most, the draft, the proof lines:
   - Headline: Active accounts (named and pooled), renewing by `<T+89>`, risk 4 or 5 with coverage.
   - This week: the event counts that moved (renewal events logged, churn notices, churn risk, personnel-change events), each labeled as events.
   - Three accounts and my move: the top 3 lean-in rows, account names and the manager's own move only.
   - Wins, with the dated quote.
   - Asks of you: only where a lean-in move is an executive sponsor touch, and only after the Slack to the account holder (`action-types.md`, executive order).
   - Coverage: the pooled lane's share, as a fact.
   Rules: no team member names and no per-person numbers in the VP draft; no revenue unless the manager asks; no roadmap, price or date promises; a churn notice is "said", not "lost".

## 8. Drafts

The Slack note to a CSM: one account, one ask, written as a question or an offer, never a correction.

**Draft 1: Slack to <first name>**
```
Hi <first name>, <one ask, as a question: "want me on the <date> call for <account>?" / "who's the second contact we could bring in at <account> before the renewal?" / "anything I can unblock with <account>'s exec?"> It renews <date>, and <what we see, one fact with its date>. Happy to help either way.
```

- Never "why haven't you", never a count of their untouched accounts, never their own emails quoted.
- With a Slack connector: a draft only, to the person; never a send, never a channel post.
- A pooled account's draft goes to whoever assigns pooled accounts: the manager, or `teams.admin` in `company-profile.md` when set (otherwise write `<who>` and say so). The same recipient takes the reassign mode's CS ops request: "Can we put a named holder on <account> before its <date> renewal?"
- An executive sponsor ask waits for the Slack to the holder (`action-types.md`).
- When the signed-in user is not the manager ("<name>'s team"), write the drafts for the manager to send and say so in one line.
- The evidence a draft rests on goes to the trail (`why <n>`), never under or inside the draft. Label outside the block, only the message inside, contractions on (`delivery.md`, Act).

## 9. The trail (every answer, on `why`)

The answer carries only the two proof lines (section 4.8). These lines print on `why` and, in Claude Code, go to `~/.staircase/runs/<date>-staircase-manager-team.md`:

- `Scope:` the scope line (section 3).
- `Window:` every date that ran: "renewals 2 Nov to 30 Jan; no touch since 4 Oct; signals 20 Oct to 2 Nov; threads 20 Oct to 2 Nov, both included".
- `Seen:` threads read out of `total_count` for the shortlist (visible to you; holders may see more); risk level on N of M; members with no Staircase access; members whose second role field holds more than half their picked field's count (fingerprint counts); flags dropped by the base-rate guard; anything that timed out and was split; the section 4.2 reconciliation line.
- `Rank rule:` the section 4.4 sentence (weekly), or the renewals or urgency sentence. Then `Mark rule:` the section 4.6 sentence, in the weekly view and VP mode only.
- `People:` "Team members are listed alphabetically and never ranked."
- `Sources:` fields by name, the reports run, evidence ids per row.

The saved specs (the load rollup and the candidate pulls) are offered on `why` in one line (`delivery.md`, report mode).

## 10. When things go sideways

| Situation | Do |
|---|---|
| `user.manager` returns no rows | Ask for the team's names; use SEVERAL NAMED USERS. Say the tenant's manager field looks empty |
| The manager also holds a book | Leave it out unless asked ("include my own accounts"); say so in How I built this |
| More than 300 candidate rows | Tighten the candidate filter to renewal by `<T+29>` or a fresh signal, say so, and offer the wider list |
| A pull times out | Split it in half once (`data-rules.md` rule 5); never resend the same config |
| Every lean-in candidate is settled | Say so; show the load facts and the record-check line; that is a good week |
| Every direct report holds nothing | Say so, list them, and offer "my org" (skip levels) or a named roster. Leave out the rank and mark lines, since no list ran |
| The manager asks for revenue | Add a SUM of `customer.revenue_converted` per member as its own rollup call; label the currency; never in the lean-in ranking columns |
| "Compare <name> and <name>" or "who's my weakest" | Decline in one line (section 1) and show the alphabetical load lines |

## 11. What this skill adds, and the gap each rule covers

| Rule | Server gap it covers |
|---|---|
| Alphabetical people, no activity numbers, flags only against a stated line | No recipe covers manager output; v2 ranked people by effort and risk |
| Likely pooled lane by outlier share plus a sign | No `is_pooled` flag (T11); the recipe lists signs but no test |
| One load call per role field, four counts each | Mixed-role teams; nine child counts timed out (F39); no team rollup recipe |
| Team totals by scalar COUNT and the overlap line | Members can share accounts across fields; the recipe forbids summing |
| Manager rank rule with a required thread read | No `action_priority` recipe; stage 1 alone was wrong on 3 of 12 rows (F45) |
| "On their list" proxy | No server record of a user's list or dismissals (CATALOG ask 7) |
| Record-check line for passed renewal dates | CRM renewal dates lag closed renewals; no renewal outcome record (CATALOG ask 12) |
| Held reassignment drafts; role fields change in the CRM | Role fields are not writable through the MCP |
