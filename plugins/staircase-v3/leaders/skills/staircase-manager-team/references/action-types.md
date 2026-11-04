# Action types: which action fits, what to prepare, how to tee it up

Every item on a list arrives ready to act. Pick one action per item from the situation, prepare it with the evidence named here, and tee it up in the user's own tools. Drafts are free; sending, posting, inviting or creating a record waits for the user's yes, each time (`trust.md`). Detection and ranking: `action-priority.md`.

## Situation to action

| Situation | First action | Also offer | Evidence the draft needs |
|---|---|---|---|
| Customer waiting: technical question or bug | Slack ask to support, or the product expert, with the question and the impact | A quick "working on it" reply to the customer; a full reply when the answer is already in the threads | Thread evidence id, the ask fetched verbatim, waiting since (date), any ticket in the threads, renewal date and risk level for the impact line |
| Customer waiting: billing, quote, pricing, renewal terms | Slack ask to the account executive or renewal owner | A reply confirming who owns it (no price, terms or dates the user did not give) | The ask verbatim, renewal date, open commercial threads, the owner's name from the account's role field |
| Customer waiting: scheduling, data request, how-to | Customer reply draft | A resource or value share when a known answer exists | The ask verbatim; the resource the user or the company profile names |
| Customer waiting: escalation or frustration | Escalation: internal Slack to the user's manager or the account team | A reply whose tone the user picks; a meeting proposal to talk it through | Dated quote, what was already tried (from threads), risk level, renewal date |
| Meeting held, no follow-up sent | Customer recap email | A CS record hand-off (Timeline note) when Gainsight CS is connected | Meeting `call_summary`, `issues[]`, `action_items[]` and evidence id; a transcript exists, or the user's notes |
| Meeting in the next 48 hours, or this week in week mode, that the read raised (a business review, a renewal or pricing talk, an executive or a new contact, an open ask or a blocker) | 3 to 5 agenda lines from what the read found | The full prep brief (single-account read); a quiet spell or an expansion signal on the account as one more line ("raise it in the meeting") | Stored fields, the last 3 threads and the invite, open asks, who attends and their titles |
| Quiet account | A value share or check-in email to the most engaged contact | A meeting proposal (short check-in) | Last two-way date, last thread topic, something useful to say (a release that fits their last ask, a tip, their own open question) |
| One-sided chase (we write, they don't answer) | Change the path: Slack to the account executive or the exec sponsor holder, or an email to a second contact | A hold for the next scheduled meeting | Our unanswered threads with dates and senders, the other contacts on the account |
| Fresh risk | Escalation: an internal huddle post with the play. Save while the customer has not decided (risk words, no notice); manage closure once a written notice or a named replacement exists; ask the account owner when the threads leave it open | A customer email, only after the user picks the play | Event type and date, dated quote, whole account or one product, the churn reading |
| A non-renewal notice that asks us to confirm receipt | A short reply confirming receipt and asking which subscriptions it covers (no terms) | A Slack to the CSM and the account owner | The notice verbatim, its date, the products the stored fields show |
| Renewal decision due or passed | Email to the buyer, or a note to the renewal owner | A CRM fix note when the date looks wrong | Renewal date, last renewal discussion, open commercial threads |
| Renewal checkpoint (120, 90, 60 days) | Kickoff email to the buyer, copying the sales owner | A meeting proposal with the decision maker | Renewal date, last renewal discussion, last decision-maker touch |
| Value review (renewal 121 to 180 days out, no renewal conversation yet) | A value-review proposal to the main contact: what they set out to do and what we can show on it | A Slack to the renewal owner that the review is coming, so the renewal conversation opens on it | Renewal date, their goals or asks from the threads, the last review or business meeting, usage the user can bring (never invented) |
| Settled loss: a notice that holds, a closure being managed, offboarding done on an Active account | The Closing line, not an item: what closes, when, who has the commercial steps | An item only for a dated step the user owns (a customer waiting, a meeting with them, an export task), and the item is that step; a product that stays is named on the line; a CRM fix when the account still reads Active | The notice or the stored churn analysis (named), its date, the products it covers, the renewal owner |
| Do not contact (the customer asked us to stop) | Internal only: a Slack to the renewal owner or the team, a close-out step, a CRM fix | A reply only to a thread the customer started | The user's own words or the customer's request and its date |
| Stakeholder left | Slack to the account team, plus an intro ask to a remaining contact | A CS record hand-off (contact change) | Event date, dated quote, the contact's role |
| New stakeholder joined | Welcome email | A meeting proposal (intro) | Event date, quote, role |
| Expansion ready | Slack to the account executive with the evidence | A discovery email, held until the account executive agrees | Opportunity summary line, readiness level, decision-maker field, the customer's own words |
| Open situation (risk 4+, no fresh event) | The next step in the save plan, or closure | A CS record hand-off (CTA or success-plan step) when connected | Stored risk analysis (named), top issue, last movement |
| The same ask at several accounts (bug, feature) | Slack with the accounts and quotes, routed by ask type: a configuration or how-to ask (the quotes show set-up or services work, not a missing feature) goes to enablement or services (`teams.enablement`); a mixed ask goes to product with enablement copied; a product ask (a missing or broken capability) goes to product. Use the same per-thread test `staircase-voice` uses so every skill routes the same way | A ticket draft (Linear or Jira when connected) | One dated quote per account; "at least N" when the count comes from search |
| Praise or an outcome in the customer's words | Safe-to-ask check (`safe-to-ask.md`), then a Slack to the CSM | The reference or case-study ask, held for the CSM's go | The check result, the quote, the speaker's side |
| A stored field looks wrong | A note to the admin or CS ops | none | The field, its value, its source and date, what the threads show |

## How each action is teed up

| Action | With a connector | Without one | Who it goes to |
|---|---|---|---|
| Customer email | A draft in the user's mail connector, in the thread when it is a reply | A copy block holding only the body; To and Subject in its label (`delivery.md`, Act) | Contacts who wrote or attended (participant type Stakeholder). Addresses come from a `stakeholder` report (fetched messages carry `sender_name` only); none there: the name plus "(address not in Staircase)". The draft cites only what that recipient said or was present for |
| Slack ask to the user's own team | A Slack draft to the person, or to the team channel in `company-profile.md`; never a send | A copy block, the recipient in its label | Support, product, the account executive, the renewal owner, the exec sponsor holder or the user's manager: the person from the account's role fields (`customer.<role_field>.full_name`) or `user.manager`, the team from the company profile. Unknown: write `<who>` and say so |
| Meeting or hold | A proposed hold on the user's calendar, or 2 to 3 proposed times inside the email draft; never an invite without a yes | Proposed times in the text | Attendees of the last meeting, or the thread's contacts |
| Escalation | A Slack draft to the manager or the account team channel | A text block | Internal only. Quote the customer; never forward the thread |
| Hand-off to a CS record | Gainsight CS: a drafted Timeline note, CTA or success-plan step, created only on yes | A text block to paste | The account's CS record; CTA reason and Timeline type from the company profile |
| Resource or value share | Inside the customer email draft | Same | A link the user gives or the company profile lists. Never invent a URL |
| CRM fix | A Slack or email draft to the admin | A copy block | The admin from the company profile |

## Rules

- One action per item. The "also offer" draft is offered in one line with its verb ("say 'draft 2b'"), not stacked under the first.
- **Several situations on one account.** A ranked list takes the item with the highest priority (`action-priority.md`). A one-account answer with no score takes the first that applies: (1) a customer waiting on the user with an escalation, commercial or renewal ask; (2) a fresh risk, or fix first before a renewal or a pitch; (3) a commitment of ours due before the next meeting or within 7 days; (4) a customer waiting with a technical, data or how-to ask; (5) the job's own move (agenda, invite, intro email, escalation note); (6) a proactive move (quiet account, value share). An ask addressed to a colleague, or already handled by one, becomes a one-line nudge to that colleague.
- When the customer reply depends on an internal answer, draft both and put the Slack ask on top. When the user is the person who would answer (the ask is in their own field, or names them), skip the internal ask and draft the reply, with bracketed placeholders for what only they know.
- In a CSM lens on a renewal someone else owns, renewal actions go to the renewal owner (a Slack with your read and the step), not to the customer.
- An email from an executive to a customer sponsor waits for a Slack to the account owner first.
- Customer drafts carry no roadmap promises, prices, terms or dates the user did not supply (`trust.md`, no promises). The customer's own plans and dates, as they said them, may be restated under "you mentioned".
- Our commitments carry names; theirs read "you mentioned"; a guessed owner is flagged as a guess.
- No meeting recap without a transcript or the user's notes; say which one the recap rests on.
- The evidence ids a draft rests on go to the trail (`why <n>`), never under or inside the draft; the item names its sources as sender, date and channel (`delivery.md`).
- A next step no thread names is labeled "my suggestion", outside the copy block.
