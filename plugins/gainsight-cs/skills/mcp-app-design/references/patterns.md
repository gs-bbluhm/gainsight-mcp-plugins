# Cowork Output Patterns

**Audience:** Every skill in this plugin that produces user-facing output. Most of these skills run in BOTH Claude Code (CLI) and Claude Cowork (visual chat). Cowork is the primary optimization target.

**Purpose:** Make the plugin's output feel like an app, not a markdown dump. Cowork has interactive primitives (cards, tabs, buttons, inline choices, approval gates) — when a skill defaults to a long markdown response, those primitives go unused and the experience reads as a document, not a tool.

---

## ⚡ READ THIS FIRST — Cowork rendering checklist (run before producing any user-facing output)

**Detect the rendering mode FIRST.** If Cowork → render as app. If Code → render as scannable markdown.

### Cowork rendering (app-feel)

- [ ] **Colored app header** up top (branded color, persona/scope/date). The "you're in an app, not a chat" cue. See §1.
- [ ] **Header card with metrics grid** (3+3 or 2+2+2 — never 4+2 with empty space). Color-stripe each card by signal type. See §2.
- [ ] **Tab navigation with counts in labels** (`Priorities (8)`, `Active Work (3)`, `Watch (7)`). See §3.
- [ ] **Sortable ranked tables** with chevrons on sortable columns. Signal pill color matches the row's signal-dot color. See §7.
- [ ] **Action tee-up = ONE at a time.** When user picks an action, produce that ONE deliverable as a card. Don't dump 6 proposed actions in a bullet list. See §4.
- [ ] **Approval gates = visual confirm cards** with approve/edit/skip buttons. NEVER "type approve to continue." See §8.
- [ ] **Preference questions = inline choice cards** (radio buttons / chips). NEVER prose questions buried in markdown. See §5.
- [ ] **Working mode picker collapses to single line after selection.** Don't keep the 3-card picker visible all session. See §6.
- [ ] **Action affordance everywhere** — every observation that could lead to action gets an inline button. Cleanup recommendations, past-renewal accounts, briefing observations. See §12 anti-patterns.
- [ ] **Sticky pending-action footer** as actions accumulate through the session. See §9.
- [ ] **Per-card content stays short.** If a card needs >150 words, split it or move detail to an expandable section.
- [ ] **Color/badge semantics:** red = risk · yellow = watch · green = healthy · blue = expansion-signal · gray = inactive/closed. Applied to ALL visual elements with signal value (card stripes, pill backgrounds, badge accents). See §10.
- [ ] **No prose escape hatches.** If you're tempted to write a paragraph explaining what the user should do, convert to a tooltip, help icon, or inline button. See §12 anti-patterns.

**For concrete HTML markup of each component**, see `component-library.md` in this same `references/` folder (copy-paste-ready templates).

**For per-skill chrome decisions** (which tabs / components / patterns each skill uses), see `per-skill-mappings.md` — the bridge doc that tells you what to render for any given skill.

### Code rendering (CLI-friendly markdown)

- [ ] **Structured headers** (`## At a Glance` → `## Priorities` → `## Active Work` → `## Watch List`).
- [ ] **Markdown tables** for prioritized lists. Use emoji as badge surrogate (🔴 🟡 🟢 🔵).
- [ ] **Action queue in a single table** with approval syntax (`approve 1,3`, `edit 2`, etc.). Code users batch decisions.
- [ ] **Inline reasoning is fine in Code.** Code users want the analysis exposed.
- [ ] **Save the full packet to disk** (e.g., `inbox/workshop/<skill>-<account>-<date>.md`) so the user can grab it.

### Mode detection (how to know which rendering to use)

The agent doesn't have a reliable "what surface am I in" signal yet. Default heuristics:
- If `show_widget` / interactive card tools are available → Cowork.
- If working from a Claude Code CLI with TodoWrite + Bash + Read tools → Code.
- If unsure → produce Cowork-style structure (cards + short prose); markdown still renders cleanly. Cowork-as-default falls back gracefully to Code; Code-as-default does NOT fall up to Cowork (markdown walls in Cowork = app-feel failure).

---

## 1. Colored app header (universal — sets the "this is an app" cue)

**Purpose:** Identity strip at the top of every multi-tab skill output. The single biggest "looks like an app vs looks like a chat dump" signal.

**Anatomy:**
- Branded color strip (Gainsight CS blue `#1976D2` / Staircase navy `#1A2C5C` / neutral plugin teal `#0F8E8E` — one canonical brand color per plugin)
- Icon (📊 / 📞 / 🎯 / 🔄 — semantic to the skill)
- Skill name · persona · scope · date (compact, single line)
- Optional right-side affordances: refresh, help (`⟳` / `?`)

**Cowork rendering:**

```html
<div class="app-header app-header--brand">
  <span class="app-header__icon">📊</span>
  <span class="app-header__title">Book Pulse</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__persona">Hannah Lee</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__date">Week of May 26, 2026</span>
  <div class="app-header__actions">
    <button title="Refresh">⟳</button>
    <button title="Help">?</button>
  </div>
</div>
```

Concrete markup in `cowork-component-library.md` §1.

**Rules:**
- Always-on at the top of every multi-tab skill. Tabs sit below the header.
- Skill icon is the visual anchor — picked per skill (see component library mapping).
- Brand color is consistent within a plugin (don't change between skills).
- Persona + scope + date renders inline; no line breaks.
- For Code rendering: replace with a markdown H1 (`# 📊 Book Pulse — Hannah Lee · Week of May 26, 2026`).

---

## 2. Header card pattern (universal — every skill)

**Purpose:** 30-second read that orients the user. Sits directly under the colored app header.

**Cowork rendering:**
```
┌─ <Skill name> — <scope/persona> — <date>
│
│  N accounts · $X.XM ARR · Y new signals this week
│  N CTAs overdue · M EBRs due · K expansion-ready
│
└─ [ Show priorities ] [ Show watch list ] [ Show briefing ]
```

**Code rendering:**
```markdown
## <Skill name> — <scope/persona> — <date>

- **N accounts · $X.XM ARR** · Y new signals this week
- **N CTAs overdue** · M EBRs due · K expansion-ready
- **Top action:** <one-line summary of #1 priority>
```

**Rules:**
- 4-6 metrics max. More = scan failure.
- Specifics, never abstractions. "$830K ARR" not "significant ARR."
- Single primary CTA button in Cowork (the user's most likely next move).
- Color/badge decoration on the metrics where it adds signal.

---

## 3. Tab structure pattern (multi-section outputs)

**When to use:** Any skill output with 3+ distinct sections (book pulse, account workspace, exec radar, etc.).

**Cowork pattern (3-5 tabs, never more):**

| Tab pattern | Example use |
|---|---|
| **Overview / Priorities / Active Work / Watch / Briefing** | book pulse, daily cockpit |
| **Account State / Recommended Actions / Existing Work / Briefing** | account workspace |
| **Per-Tier Tabs (Enterprise / Mid-Market / SMB) + Themes + Resource Allocation** | exec renewal radar |
| **Review Packet (Email / Timeline / CTA / Tasks / Wins)** | meeting processor |
| **Discovery / Validation / 90-Day Plan / Risks / Open Items** | account handoff onboarding |

**Code fallback:**
Each tab becomes a `## Section header`. Use `---` between sections so the structure stays scannable.

**Rules:**
- Tab names are short noun phrases. "Priorities" not "Things to focus on this week."
- The user lands on the most-likely-useful tab by default (usually Tab 1: Overview or Priorities).
- Tabs link to one another via primary CTA buttons in the header card.
- Don't put workflow steps in tabs (workflow = sequence, tabs = parallel views).

---

## 4. Action tee-up sequence (the key behavioral pattern)

**The wall-of-actions failure mode:** dumping 6 proposed actions in a markdown table where each cell has 2-3 lines. The user has to scan, choose, then ask Claude to draft a specific one. That's TWO interaction steps where ONE would do.

**The correct pattern (Cowork):**

1. **Surface the ranked priority list** (Tab 2: Priorities). Each row is an account, expandable.
2. **User taps a row** → drill-down card opens with state + 2-3 proposed next moves for that account.
3. **User picks ONE move** ("Draft outreach" / "Update CTA" / "Schedule EBR prep") → that move's button in the drill-down card.
4. **Claude produces ONLY that ONE deliverable** as a new card with:
   - Preview (email body, CTA fields, EBR outline, etc.)
   - **[ Approve & post ] [ Edit ] [ Skip ]** buttons
5. **On approve** → write executes → confirmation card → returns to Priorities tab with the next account surfaced (or the same account if more moves remain).

**Batch mode (for power users):**

At the top of Tab 2, surface the working-mode picker:
- ⚪ Walk me through one at a time (conversational — default)
- ⚪ Show me all proposed actions at once (batch mode)
- ⚪ Just the must-do this week, skip watch list (focused mode)

If the user picks batch mode, surface all proposed actions in a single approval card with checkboxes ("Approve selected / Approve all / Cancel"). The output discipline still holds — each row is short, action-specific, with a clear approve toggle.

**Code fallback:**
Render the full action queue as a numbered table with approval syntax:
```
| # | Action | Target | Type | Notes |
| A | Draft outreach to John Jennings | Navy Bayview | Gmail draft | Offboarding-first tone |
| B | Update CTA → Save: Offboarding | Navy Bayview | NEW CTA | High priority |
| ... |

Reply with `approve A,C` (selective) or `approve all` to post.
```

Code users handle batch better in markdown — they're already in CLI mindset.

---

## 5. Preference question card pattern

**When to use:** Any time Claude needs the user to pick between substantively different approaches (e.g., save-with-incentive vs offboarding-first, expansion-leaning vs renewal-leaning lens, multi-thread now vs wait for champion stability).

**Failure mode today:** prose question buried in markdown ("Want me to drill into Stanley Waterfront's last 90 days?"). User has to scroll up to find context, then type a yes/no response.

**Correct Cowork pattern:**

Inline choice card. Title + 2-4 mutually exclusive options. Each option has a short description.

```
┌─ How should we approach Navy Bayview?
│
│  ⚪ Offboarding-first
│     Course-correct apology, free-tier path, export checklist.
│     Accept the migration but contain the damage. (Recommended)
│
│  ⚪ Save-with-incentive
│     Offer a free-tier-plus-services concession to retain.
│     Higher risk but bigger upside if it lands.
│
│  ⚪ Multi-thread before responding
│     Identify a third stakeholder above John + Timothy before
│     committing to a path. Delays response 1-2 days.
│
└─                                              [ Pick approach ]
```

This is the visual equivalent of `AskUserQuestion`. Use it whenever there's a meaningful branch.

**Code fallback:**
Same content as a numbered list with explicit prompt for user input:
```
**How should we approach Navy Bayview?**

1. **Offboarding-first (Recommended)** — Course-correct apology, free-tier path, export checklist.
2. **Save-with-incentive** — Offer concession to retain. Higher risk/upside.
3. **Multi-thread first** — Identify a third stakeholder before responding.

Reply with 1, 2, or 3.
```

---

## 6. Working mode picker pattern

**When to use:** At the start of any multi-action workflow (book pulse, account workspace, renewal planner).

**Purpose:** Let the user pick how to consume the output. Conversational walkthrough = the Cowork default. Batch = power-user mode. Focused = "just the must-do, skip noise."

**Cowork rendering:** Inline choice card at top of Tab 2 (Priorities), pre-selected to "conversational" by default. User can change anytime.

**Code rendering:** A one-line header at top of the priority list: `**Mode:** Conversational (default) · Reply "batch" to see all actions at once · Reply "focused" to skip watch list.`

---

## 7. Sortable ranked table pattern

**The structure:**

| # | Account | ARR | Renewal | Risk | Health | Flags | Why here |

**Cowork rendering:**
- Sortable by any column header.
- Badge decoration in the Flags column (🔴 risk · 🟡 watch · 🔵 expansion · 🟢 healthy).
- Row click expands to drill-down card.
- Optional: pagination if >25 rows.

**Code rendering:**
- Pure markdown table.
- Emoji badges in Flags column.
- Rows in priority order; user scrolls.

**Rules:**
- Show top 8-10 rows by default. "Watch list" 11-25 goes in a collapsed section or separate tab.
- "Why here" column is mandatory — single short phrase per row explaining the priority. Specificity beats generality ("Active exit in motion · biggest ARR" beats "Save play").
- ARR formatted compact ($45K not $45,000).
- Renewal as days-from-today (46d, -72d for past, 2d for imminent).

### Sortable column affordances

- **Chevron icons on sortable columns** (▲ ▼) — hover state shows the available sort direction. Active sort column shows the chevron filled.
- **Default sort:** by priority/composite score descending — never alphabetical, never insertion order.
- **Sort persistence:** keep the user's sort choice across tab switches within the same session.

### Signal pill color tie-back

The Signal column's pill background color MUST match the row's signal-dot color. Disconnect breaks the visual chain:
- 🔴 dot + "Active exit" pill → red-tinted pill background
- 🟡 dot + "EBR window" pill → amber-tinted pill background
- 🔵 dot + "Expansion play" pill → blue-tinted pill background
- 🟢 dot + healthy state → green-tinted pill background

Without tie-back, the user has to look up which color means what twice (once in the dot, once in the pill). With tie-back, the meaning is reinforced at every glance.

### Inline row expansion (preferred) vs bottom drill-down

**Preferred Cowork pattern (if supported):** clicking a row expands the drill-down INLINE below that row, pushing subsequent rows down. Visual continuity preserved.

**Fallback pattern (if inline expand not supported):** pinned right panel or bottom drill-down card. Pinned-right is preferred over bottom (less scrolling for the user). Bottom-pinned is acceptable but should be sticky (stays in viewport when user scrolls table).

**Anti-pattern:** drill-down at the actual bottom of the page (no sticky), forcing user to scroll past the table to see it.

---

## 8. Approval card pattern (per-write gate)

**Every Gainsight write triggers an approval card.** Never write silently.

**Cowork rendering:**

```
┌─ Ready to write to Gainsight
│
│  ✅ 1 CTA · "[DEMO] Save: Offboarding control" — Navy Bayview
│     Owner: Hannah · Priority: High · Due: 5/27
│
│  ✅ 1 Email draft → Gmail
│     To: John Jennings · Subject: Re-aligning on your next steps
│
│  ✅ 1 Timeline activity → Bennett Birch
│     Context anchor: 23% click-through lift
│
│  Discipline: ✓ HTML formatting · ✓ TLDR descriptions · ✓ Reuse-vs-create checked
│
└─       [ Approve all ] [ Approve selected ] [ Cancel ]
```

**Code rendering:**
Show the validation summary as a markdown block + ask for approval text:
```
**Pre-write validation — Navy Bayview**

- 1 CTA · "[DEMO] Save: Offboarding control" · High · Due 5/27
- 1 Email draft → John Jennings · Subject: Re-aligning on your next steps
- 1 Timeline activity → context anchor: 23% click-through lift
- Discipline ✓ HTML · ✓ TLDR · ✓ Reuse-vs-create

Reply `approve all`, `approve 1,3`, or `cancel`.
```

This pattern is mandatory per `gainsight-output-best-practices.md` — the validation summary surfaces every time before a write.

---

## 9. Sticky pending-action footer

**Purpose:** As the user approves moves through a session, accumulate the pending Gainsight writes in a sticky bottom bar so they have a constant sense of what's queued. Final "Approve all" review happens before any writes hit the API.

**Cowork rendering:**

```
┌──────────────────────────────────────────────────────────────────┐
│  3 actions queued · 1 CTA · 1 outreach draft · 1 SP update       │
│                                          [ Review all (3) ]      │
└──────────────────────────────────────────────────────────────────┘
```

Concrete markup in `cowork-component-library.md` §10.

**Behavior:**
- Starts hidden. First action approval makes it appear.
- Updates count + breakdown live as user approves/skips moves.
- Sticky to viewport bottom — stays visible across tab switches.
- "Review all" button opens the consolidated pre-write validation card (per §8 approval card pattern). User has one final approve-all/cancel gate before any actual API call.
- Clears after the consolidated approval fires (write executes, log records, footer empties + re-hides).

**Why this matters:** in conversational mode (one action at a time), the user can lose track of how many moves they've queued. The sticky footer fixes that. In batch mode, the footer is redundant (the approval card already shows the queue) — hide it.

**Code rendering:**

No sticky UI in CLI. Replace with a periodic summary line: `Pending writes queued: 3 (1 CTA · 1 outreach · 1 SP update). Reply 'review' to see all before posting.`

---

## 10. Color / badge semantics (universal)

Consistent across all skills:

| Color | Meaning | Use case |
|---|---|---|
| 🔴 Red | Risk / critical / overdue | Risk 4-5, past-renewal, overdue CTAs, critical signals |
| 🟡 Yellow | Watch / attention needed | Risk 3, renewal 30-90d, stale engagement, EBR-due |
| 🟢 Green | Healthy / on-track | Renewed cleanly, healthy adoption, sentiment positive |
| 🔵 Blue | Expansion signal / opportunity | Readiness ≥4, expansion conversation in flight |
| ⚪ Gray | Inactive / closed / past | Closed CTAs, churned accounts, parked items |
| 🟣 Purple (optional) | Advocacy / hero account | Verified Outcome captured, advocacy-grade quote in 90d |

**Rules:**
- Never use color alone to convey meaning (accessibility). Always pair with a label or icon.
- Don't invent custom colors per skill — these 6 cover every signal type the plugin produces.

---

## 11. Per-skill mapping

| Skill | Colored header icon | Header card | Tabs | Action pattern | Preference questions | Mode picker |
|---|---|---|---|---|---|---|
| `gainsight-csm-book-pulse` | 📊 | Book stats | 4: Overview / Priorities / Active Work / Watch | One-at-a-time + batch toggle | Per-account approach choice | Top of Priorities tab |
| `gainsight-account-workspace` | 🧭 | Account stats | 4: State / Recommended Actions / Existing Work / Briefing | One-at-a-time | Per-action approach choice | N/A (single account) |
| `gainsight-meeting-processor` | 📞 | Call recap stats | 5: Email / Timeline / CTA / Tasks / Wins | Sequential approval per artifact | Per-artifact "approve/edit/skip" | N/A (review packet flow) |
| `gainsight-exec-renewal-radar` | 🎯 | Portfolio stats | 4: Per-Tier (Ent/MM/SMB) + Themes | Briefing-grade; optional handoff CTAs | "Drill into a tier?" choice | N/A (briefing) |
| `gainsight-renewal-priority-planner` | 🗓 | Renewal flight stats | 3: Priorities / Per-Account Plans / Open Items | One-at-a-time per account | Save vs save-then-expand vs skeptical | Top of Priorities |
| `gainsight-stakeholder-connect` | 🤝 | Stakeholder map stats | 3: Map / Outreach Drafts / Notes | Per-stakeholder outreach card | Tone choice (warm/firm/exploratory) | N/A |
| `gainsight-no-qbr-ebr-scheduler` | 📆 | EBR pipeline stats | 2: Accounts Needing EBR / Scheduled | Per-account scheduling card | EBR scope choice | N/A |
| `gainsight-account-handoff-onboarding` | 🚀 | Onboarding stats | 5: Discovery / Validation / 90-Day Plan / Risks / Open Items | Sequential SP build | Validation question per section | N/A (sequential) |
| `gainsight-exec-pattern-hunter` | 🔍 | Portfolio stats | 3: Themes / Evidence / Recommendations | Briefing-grade | "Drill into theme?" choice | N/A (briefing) |
| `gainsight-exec-churn-retrospective` | 🔁 | Churn cohort stats | 4: Cohort / Patterns / Gaps / Recommendations | Briefing-grade | "Drill into pattern?" choice | N/A (briefing) |
| `gainsight-mcp-setup` | (skip header — linear flow) | (skip header) | 1: Linear onboarding flow | Sequential setup | Role + filter field + practice round | N/A |

---

## 12. Anti-patterns (the failure modes)

| Anti-pattern | Why it fails | Use instead |
|---|---|---|
| **Wall of markdown with 6+ section headers** | Cowork user has to scroll-and-read; can't act fast | Tabs (3-5 max) + per-section cards |
| **Dumping all proposed actions in a table** | User has to scan + ask Claude to draft a specific one — 2 steps for what should be 1 | Sequential action cards: one at a time, approve/edit/skip |
| **Prose questions buried in markdown** | User has to scroll for context, then type answer | Inline choice card (preference question pattern) |
| **Markdown tables in Cowork without badges/sorting** | Defaults to alphabetical or insertion order; loses the priority signal | Sortable table with badge decoration |
| **Multi-line cells in approval gates** | Card becomes unscannable | Compact summary; details in expandable section |
| **"Type approve to continue" prompts** | User has to context-switch to keyboard | Visual approve/edit/skip buttons |
| **Generic CTA on header card** ("Continue" / "Next") | Doesn't tell user what's next | Specific primary action ("Show top priorities" / "Drill into Navy Bayview") |
| **Using emoji badges in Cowork when real badges are available** | Looks like CLI output in a visual surface | Use Cowork's badge primitives if available; emoji as Code fallback only |
| **Asking "want me to do X?" prose questions** | Forces user to type back yes/no | Just do X with an approval gate, OR offer the choice as a card |
| **Prose escape hatches** (paragraph explanations where a tooltip / inline help / button would do) | Reads as "the system gave up on rendering this properly" — breaks app-feel | Convert to: tooltip on hover, ? icon, muted footer note, or expandable section. If the explanation is needed, it's not finished rendering. |
| **Count-vs-list mismatch** ("5 accounts past renewal" header above a list of 7) | Erodes trust — user wonders what else is misreported | Sub-group with sub-headings: "5 past renewal · 2 borderline (Cooper Osprey, Yang Clinics) — different timing pattern" |
| **Observation without action affordance** (cleanup recommendations, briefing notes, past-renewal accounts as plain text) | The most actionable items become the least clickable items | Every signal that could lead to action gets an inline button. Even briefing notes deserve `[ Investigate ]` |
| **Action button on a done-state item** (e.g., "Light-touch follow" on a 100%-complete closed SP) | Implies action needed when reality is "you're done" | Replace with check-mark badge + muted text ("✓ Done — confirm renewal proceeds") |
| **Working mode picker visible after selection** | Eats viewport real estate; user already chose | Compress to single-line chip: `Mode: One at a time · [change]` |
| **Uneven metric card grid** (4+2 with empty space on right) | Breaks visual rhythm; cards become "less important than the others" without intent | Use 3+3 or 2+2+2 grids. Or fill the empty cell with a sparkline / mini-chart / brand mark. |

---

## 13. Cross-references

- **Output content discipline:** `_shared/gainsight-output-best-practices.md` — what to write (CTA structure, Task content, Timeline format)
- **MCP query composition:** `staircase-mcp-expert/references/query-patterns.md` — how to query Staircase
- **Cross-walk between MCPs:** `_shared/mcp-cross-walk.md` — field-level Staircase ↔ Gainsight mapping

This doc (`cowork-output-patterns.md`) covers HOW to render. The output best-practices doc covers WHAT to write. Both apply on every Cowork-surfaced output.

---

## 14. Versioning + iteration

**v1.0 — 2026-05-26.** Initial codification from Layer 2 Cowork testing of Demo 1 (CSM Book Pulse on Hannah Lee). The wall-of-text failure mode triggered this doc.

Subsequent iterations as more demos validate the patterns. When a new pattern emerges that isn't covered here, add it. When a pattern proves not to work in Cowork's actual rendering, mark it deprecated rather than deleting (so historical reasoning survives).
