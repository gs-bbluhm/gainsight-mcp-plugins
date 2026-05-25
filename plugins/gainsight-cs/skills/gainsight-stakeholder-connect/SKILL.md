---
name: gainsight-stakeholder-connect
description: Analyze stakeholder alignment for an account or CSM book, then draft personalized outreach emails to reconnect with key contacts. Uses Staircase Personnel Changes + Risk Analysis stakeholder section.
user_type: ic
---

# Stakeholder Connect

## Discovery

**Auto-trigger phrases:**
- "stakeholder check-in"
- "draft outreach for [account]"
- "reconnect with my stakeholders"
- "who do I need to reach out to"
- "stakeholder alignment for [account]"
- "champion check-ins"

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas (15-cap, OR not supported, determinism)
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Risk stakeholder section)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)
- `../gainsight-cs-mcp-expert/references/write-path-patterns.md` — canonical CTA + Task (Email type) + Timeline recipes with HTML templates
- `../gainsight-cs-mcp-expert/references/anti-patterns.md` — gotchas, custom field requirements, HTML formatting

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

For the CSM moment: "I haven't touched my stakeholders in a while — who should I reconnect with, and what should I say?" The skill analyzes stakeholder alignment from Staircase signals and drafts personalized outreach per named stakeholder.

The Personnel Changes flag returns accounts with named champion-departure narratives plus supporting evidence IDs. The per-account Risk Analysis stakeholder section returns named stakeholders with sentiment + recommended engagement approach.

---

## Team-member field discovery (CRITICAL)

Staircase has a standard `Owner` field that's consistent across orgs. Most orgs also have custom team-member fields (e.g., `CSM`, `Account Manager`, `Renewal Owner`, or an org-bespoke variant) — these must be discovered via the Gainsight `get_object_metadata("company")` call. The `gainsight-mcp-setup` skill walks the user through this discovery once and caches the field name in the user profile.

In any query in this skill that filters by a CSM, substitute `<team-member-field>` with the field discovered during setup.

---

## Step 0: Scope

User specifies either:
- **Account-scoped:** "draft outreach for the <account> team" / "stakeholder check-in on <account>" — single account, all relevant stakeholders
- **Book-scoped:** "who in my book needs outreach" / "stakeholder pulse across my accounts" — full CSM book, surface the highest-need stakeholders across N accounts

Default to book-scoped if ambiguous (catches more value).

---

## Step 1A (Account-scoped path)

```
A. staircase_account_lookup(name=<account>) → account_id
B. gainsight resolve_customer(search_name=<account>) → company GSID
C. staircase_analyze_account(account_id, query="
   Pull the full stakeholder analysis for <Account>. For each named
   stakeholder, return:
   - Name, title, role
   - Sentiment (Champion / Neutral / Detractor)
   - Last engagement date if knowable
   - Recommended engagement approach for them given the current
     account context (their concerns, their priorities, their style)
   - Any recent changes (new role, recent communication, departures)
   - Supporting evidence IDs")
```

Returns the rich Risk-Analysis-style stakeholder block — typically 4-5 sentiment-classified stakeholders with engagement approach per stakeholder.

---

## Step 1B (Book-scoped path)

Run in parallel:

```
A. staircase_ask("Which of my accounts are flagged as No Reach Out?
   For each, include the last reach-out date if known.")

B. staircase_ask("Which of my accounts have had recent account personnel
   changes or stakeholder shifts in the last 60 days? Include a one-line
   description of the change.")

C. staircase_ask("List the accounts where the <team-member-field> is <CSM Name>.
   For each, include name, last reach-out date, last engagement date,
   health score, ARR.")
   → CSM book to intersect against
```

Client-side intersect: book ∩ (No Reach Out ∪ Personnel Changes) = priority accounts for outreach.

For top 5 priority accounts, run the Step 1A account drill-down to get per-stakeholder detail.

---

## Step 2: Draft per-stakeholder outreach

For each stakeholder to engage, generate a personalized email using the established email-format conventions (carries forward from `gainsight-meeting-processor/references/email-format.md`):

### Email structure per stakeholder

```
Subject: <personalized — references something specific to them or their account>

Greeting: Good <morning/afternoon>, <FirstName>,

Opening (1-2 sentences):
  - For champion check-in: "Wanted to reconnect — wanted to share some
    progress on <specific thing they care about> and hear how things are
    going on your side."
  - For new-stakeholder (after personnel change): "<FirstName from
    departing CSM> mentioned you've taken over <area>. I'd love to set up
    a brief intro to get aligned on what matters most to you."
  - For detractor reconnect: "<FirstName>, I know our last few conversations
    have surfaced real friction — wanted to come back with a clear path
    forward on <specific friction>."

Specific context (1-2 sentences):
  - Reference recent activity: "I saw the team made progress on <X>",
    "I know <topic> is on your roadmap for this quarter"
  - From their named priorities (Risk Analysis stakeholder section)

Ask (1-2 sentences):
  - Concrete call to action: 30-min check-in, share progress, get input
    on a decision, etc.

Closing line:
  Brief warm sentence.

(No sign-off — Gmail signature handles it)
```

### Tone notes
- No em dashes, no emojis, no filler openers
- Action-oriented ("share progress", "get aligned") not info-oriented ("just checking in")
- Specific > generic — reference something the Risk Analysis surfaced as their concern
- Length scales with relationship: champion = warmer/longer, detractor = direct/shorter

---

## Step 3: Present the packet

### Account-scoped output

```markdown
# Stakeholder Connect — <Account>

## Stakeholder alignment summary
- <count> stakeholders identified
- <count> champions · <count> neutrals · <count> detractors
- <count> recent stakeholder shifts (new contacts or departures)
- Engagement gap: <highest-priority stakeholder hasn't been touched in X days>

## Per-stakeholder outreach drafts

### <Name> — <Title> · <Sentiment>
**Last engagement:** <date>
**Why this matters:** <one-sentence — recent change, expansion conversation, friction, etc.>

**Drafted email:**
```
Subject: ...
[Full email body, ready to copy]
```

**Approve & post:**
- [ ] Create Gmail draft
- [ ] Edit before posting
- [ ] Skip this one

### <Name> — <Title> · <Sentiment>
...
```

### Book-scoped output

```markdown
# Stakeholder Outreach Pulse — <CSM> · Week of <date>

## Outreach priority list
| # | Account | Stakeholder | Why now | Sentiment |
|---|---------|-------------|---------|-----------|
| 1 | <account> | <stakeholder> | Champion departed — reconnect needed | Champion (departing) |
| 2 | <account> | <stakeholder> | Last touch 12d, active project | Champion |
| 3 | ... | ... | ... | ... |

## Drafts (top 5)

[Per-stakeholder draft as above]
```

### Format adaptation

- **Cowork:** per-stakeholder card with the drafted email body + edit/copy buttons; sentiment badge color-coded.
- **Code:** full markdown to stdout.

---

## Step 4: Optional close-out (approval-gated)

- Create Gmail drafts via `create_draft` for approved emails
- Log Timeline activity in Gainsight noting "Stakeholder outreach sent — <list of named recipients>"
- Create CTAs in Gainsight to follow up if no response in 7 days

---

## Edge cases

| Situation | What to do |
|---|---|
| Stakeholder name unclear or no email known | Generate email with [INSERT EMAIL] placeholder; flag in summary |
| Champion departure flagged but no replacement identified yet | Draft a "transition-aware" email to the team rather than a single person |
| Detractor present | Draft is more direct, shorter, acknowledges friction explicitly |
| Last engagement date unknown | Default to "We haven't connected in a while" rather than a specific timeframe |
| Account has 10+ stakeholders | Pick top 3-5 by sentiment importance (champions + detractors) |
| Stakeholder is internal (Gainsight side, not customer) | Skip — outreach is customer-facing |

---

## Why this matters

Champion attrition is the silent killer of CSM relationships. When the Personnel Changes flag surfaces accounts with named departures, the plugin drafts a transition-aware outreach to the team. The CSM reviews five drafts in two minutes instead of writing five emails in an hour.

---

## Sources

- `gainsight-meeting-processor/references/email-format.md` — tone + structure
- `staircase-analyst-data-models.md` — stakeholder section query template

## Output Best Practices (Gainsight writes)

**Before writing customer-facing content to Gainsight**, follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Core rules:

1. **User approval gate** before customer-facing writes.
2. **Commitment discipline.** PROPOSAL language. Email Tasks carry "Verify Before Sending."
3. **HTML formatting** in rich-text. `<p>`, `<ul>`, `<ol>`, `<strong>`, `<br>`.
4. **Teammate-facing, customer-focused.** No internal classification labels in customer surfaces.
5. **Evidence as readable references.** `Email (Person, date)` / `Meeting (date)`.
6. **Reuse-vs-create.** Fetch existing first.
7. **Cleanup discipline** for stagnant artifacts.
8. **Org-specific discovery** of CTA Types / SP Types / Timeline custom fields.

### Skill-specific emphasis

**Outreach drafts go into Email-type Task descriptions** (with full Verify Before Sending checklist for each external commitment), NOT into CTA Comments. The CTA Comments stay light: TLDR + stakeholder map + Tasks reference. Deeper stakeholder context (named-stakeholder analysis, relationship history, sentiment trajectories) goes into the CTA's linked Timeline activity. Principle: Comments = scannable TLDR. Tasks = action playbook with accelerator content. Timeline = deep team context.

---

## Learnings

See `.learnings.md`.
