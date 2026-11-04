# Scope: whose accounts

Every answer runs on one scope and says which. There are three modes. Org context (tiers, regions, product lines, role names) resolves in this order: org context served by the Staircase server when it offers one, then `company-profile.md`, then live discovery with the default named in the answer.

## Pick the mode

| Mode | Use when | Resolve with | Statuses |
|---|---|---|---|
| Book | "my accounts", "my book", "<name>'s accounts", "my team"; and any unscoped ask from someone who holds a book | The `portfolio_resolution` recipe (single user, several named users, or team). Never `customer.owner` by default | From the user's words (below) |
| Slice | Org views: a tier, a region, a product line, the whole org. The default for people with no book (support, product, admin, most executives) | Tier: `customer.tier`, a Reference to the `tier` entity (below). Region and product line: only a field named in `company-profile.md` or found in discovery; if none, say so and offer tier or the whole org | Active by default, stated |
| Engaged-with | "accounts I've engaged with", "worked with", "been in touch with", "copied on", "keep me posted"; follow-up and stay-in-the-loop jobs for anyone | The filter below | All, with a status column and the split |

- Book holders (CSM, AM, manager): the whole org only on request.
- Every skill accepts an override: "for <name>'s book", "for the <tier> tier", "for the whole org". Two exceptions stay self-only: owed replies and loop digests (`trust.md`).
- **Under a "for <name>" override:** "you" and "your leader" mean the named person and that person's manager; drafts are written for them to send; a customer waiting is "waiting on our side", with no per-person reply time; never save the scope file; read and write only ledger entries scoped to that book (`action-priority.md`, Ledger); and say threads are what the signed-in user can see, so the book holder may see more.
- Leave out the accounts listed in `company-profile.md` under `exclusions` (the vendor's own org account, test accounts), and say how many were left out. If the vendor's own account shows up and the profile does not list it, name it as likely internal.

## First-run scope check

Run it on the first scoped ask of a session (one call: fingerprint the user once).

1. **The ask names a scope.** Use it: "my book", "<name>'s accounts", "my team", "the Enterprise tier", "the whole org", "accounts I've engaged with". A named slice (a tier, the whole org) needs no fingerprint and no scope file.
2. **The ask names none** ("how many accounts renew next quarter"). Fingerprint the user once, per `portfolio_resolution` single-user step 1 with `current_user_id`.
   - Any role-field count above 0: default to their book (recipe steps 2 and 3), say so, and offer the whole org in one line.
   - Every count 0: no book. Use slice mode: answer on the whole org, and offer the change once in one line ("Want one tier, region or product line instead?"). Do not wait for a reply before answering. Keep the choice for the session.
3. **Statuses** from the user's words (next section).
4. **Keep it.** In Claude Code with file access, save `~/.staircase/me.md` (mode, user id, role field id and label or "none", slice, date) and reuse it unless the user changes scope or metadata no longer has the field. Elsewhere, the scope line in each answer is the record.

## Statuses from the user's words

The recipes add a status only when the user asks for one. Read renewals, risk, touch, health, "customers", "what needs attention" and "at risk" as asking for current customers: add `customer.status` In [the Active option id from metadata] and print "Active only". A slice defaults to Active. A plain list of "my accounts" with none of those words: no status filter, a status column, and the split in the scope line.

Gap covered: `staircase_run_report` adds status only when the user asks, and users rarely say "active" when they mean it.

## Book: what the recipe leaves to you

- **Likely pooled** (team scope): a member is likely pooled when any one of these holds: listed in `exclusions.pooled_user_ids`; a team-like name (no surname, or words like team, pool, scaled, digital, queue, success) together with no Staircase access, no title or `user.is_auto`; or at least twice the largest other member's count on the same field, together with one of those signs. Give that lane its own row; never fold it into a person's numbers or offer it as a receiver of accounts. No pooled-user flag exists yet, and an outlier share alone missed a queue by one account.
- **Several role fields.** Follow the recipe's picking rule. When it picks one dominant field, name the person's other non-zero fields with their counts in `Seen:` and, in What I couldn't see, offer "include my other roles" (their union); never union or drop them silently. When two role fields carry similar counts, show which field each account came from (a `customer.<role_field>.full_name` column per field), so the user can correct the pick.
- **Book pulls** page per `data-rules.md` rule 16: one unsorted page of up to 1,000 rows, or `customer.name` as the last sort key, never `customer.id`; the total checked with a scalar COUNT.

## Slice: tiers and other segments

- `customer.tier` is a Reference: metadata lists no tier options. Get tier ids and names from a report rooted on `tier` (`tier.id`, `tier.name`). Filter `customer.tier` In [those ids], or `customer.tier.name` Contains a name the user gives.
- Leave out tiers with no active accounts, and name them.
- **"Segment" means tier.** "The Enterprise segment", "by segment", "which segment" all read `customer.tier`, unless `company-profile.md` names a `segment_field`. Many orgs also sync CRM fields with Segment in the label (a sales, product or company segment); never switch to one on your own. When metadata shows one, say so in one line: "Segment read as tier; <field label> is also available." Same for "cohort" when it names a tier.

## Engaged-with: the filter

An account is in scope when, in the window, the person sent an email to it, received or was copied on an email the customer wrote, or had a meeting with it (an invitation can count). Default window: the last 30 days as an explicit array, `["<today - 29>", "<today>"]` on the user's local date (`data-rules.md`, Dates).

```json
{"operator": "Or", "conditions": [
  {"field": {"id": "customer.email.sent_count", "arguments": {"dateRange": ["<start>", "<today>"],
    "filter.user": {"operator": "And", "conditions": [
      {"field": {"id": "user.id"}, "operator": "In", "values": [<user_id>]}]}}},
   "operator": "GreaterOrEqual", "value": 1},
  {"field": {"id": "customer.event.count", "arguments": {"dateRange": ["<start>", "<today>"],
    "filter.user": {"operator": "And", "conditions": [
      {"field": {"id": "user.id"}, "operator": "In", "values": [<user_id>]}]}}},
   "operator": "GreaterOrEqual", "value": 1}]}
```

- Nest this group inside the report's top-level `And` filter. Where no date can be computed, `"[PastMonth]"` is the fallback (it rolls on the server's UTC date; say so).
- Evidence columns, each with the same `dateRange` and `filter.user`: `customer.email.organization_sent_count` (emails the person sent), `customer.email.customer_sent_count` (customer-written emails they received or were copied on; its label "Account sent emails" misleads), `customer.event.count` (meetings, invitations included). `customer.email.sent_count` is both directions despite its id.
- `<user_id>`: `current_user_id` from metadata for "me"; for a named person, the `user.id` from the recipe's single-user step 1.
- Team form: put `user.manager` In [<manager_id>] in both `filter.user` slots (direct reports; tested). Several ids in one `In` use the same path but are untested.
- What counts: emails the person sent; customer-written emails where they are on To or Cc; meetings on their calendar with the account. `customer.event.count` under `filter.user` can count invitations (declined ones, and later-today meetings inside the window), so it is not proof of attendance: one live check read 3 for a day with 1 attended meeting. Say "meetings", not "meetings attended", unless a recorded meeting shows the person on the call.
- What does not: chat; bcc; an email a colleague wrote with the person only on Cc (left out on purpose, since it would inflate a person's outbound engagement); threads no connected mailbox ingested; phone calls.
- Never use `customer.total_activity` for a person: under `filter.user` it adds every customer chat message on the account, so every user gets the same chat-heavy accounts. Never pass `commType` to split channels (customer fields ignore it silently); use the per-channel fields. Never set `aggregateParentChild` with `filter.user` (rejected).
- A threshold of 1 is permissive: sort by the evidence columns (meetings, then emails sent, then emails received), then `customer.name` (never `customer.id`), and say so. A paged list is confirmed with a scalar COUNT.
- Zero is a valid answer: "no engaged accounts in the last 30 days". Never fall back to another scope without saying so.
- Before reporting zero or a surprisingly small count, check the person's `user.mailbox_connected` (null means not connected: test NotEqual true). Not connected means their own mail is missing; say so in the `Seen:` line.
- Status split: when the list fits in one or two pages, page to the end; otherwise one scalar COUNT per status.

## The scope line (every answer)

`Scope: <mode>, <who or which slice>, <role field label or filter in words>, <N> accounts, <statuses>.`

It prints in the trail (`why`) and in report mode's footer; elsewhere How I built this says it in plain words ("your 28 active accounts where you're the CSM", `plain-words.md`). N is the number of accounts the answer covers. For a slice, the slice's own size goes in the `Seen:` line ("of 1,200 Active accounts in the org").

Example: `Scope: engaged-with, you, emails sent or received and meetings, 4 Oct to 2 Nov, 12 accounts, all statuses (11 Active, 1 Prospect).`
