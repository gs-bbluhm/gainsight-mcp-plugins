# Cowork Output Patterns

**Audience:** Every skill in this plugin that produces user-facing output. Most of these skills run in BOTH Claude Code (CLI) and Claude Cowork (visual chat). Cowork is the primary optimization target.

**Purpose:** Make the plugin's output feel like an app, not a markdown dump. Cowork has interactive primitives (cards, tabs, buttons, inline choices, approval gates) — when a skill defaults to a long markdown response, those primitives go unused and the experience reads as a document, not a tool.

---

## ⚡ READ THIS FIRST — Cowork rendering checklist (run before producing any user-facing output)

**Detect the rendering mode FIRST.** If Cowork → render as app. If Code → render as scannable markdown.

### Cowork rendering (app-feel)

- [ ] **Header card up top** with 4-6 metrics. 30-second readable. NEVER lead with prose.
- [ ] **Tabs (or equivalent visual grouping) for multi-section outputs.** 3-5 tabs max. No 7-section walls.
- [ ] **Sortable ranked tables** for prioritized lists. Badges for flag decoration (red/yellow/green/blue).
- [ ] **Action tee-up = ONE at a time.** When user picks an action, produce that ONE deliverable as a card. Don't dump 6 proposed actions in a bullet list.
- [ ] **Approval gates = visual confirm cards** with approve/edit/skip buttons. NEVER "type approve to continue."
- [ ] **Preference questions = inline choice cards** (radio buttons / chips). NEVER prose questions buried in markdown.
- [ ] **Working mode picker** at the top of any multi-action flow: "walk me through one at a time / show me all / focused only."
- [ ] **Per-card content stays short.** If a card needs >150 words, split it or move detail to an expandable section.
- [ ] **Color/badge semantics:** red = risk · yellow = watch · green = healthy · blue = expansion-signal · gray = inactive/closed.

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

## 1. Header card pattern (universal — every skill)

**Purpose:** 30-second read that orients the user. Always first.

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

## 2. Tab structure pattern (multi-section outputs)

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

## 3. Action tee-up sequence (the key behavioral pattern)

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

## 4. Preference question card pattern

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

## 5. Working mode picker pattern

**When to use:** At the start of any multi-action workflow (book pulse, account workspace, renewal planner).

**Purpose:** Let the user pick how to consume the output. Conversational walkthrough = the Cowork default. Batch = power-user mode. Focused = "just the must-do, skip noise."

**Cowork rendering:** Inline choice card at top of Tab 2 (Priorities), pre-selected to "conversational" by default. User can change anytime.

**Code rendering:** A one-line header at top of the priority list: `**Mode:** Conversational (default) · Reply "batch" to see all actions at once · Reply "focused" to skip watch list.`

---

## 6. Sortable ranked table pattern

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

---

## 7. Approval card pattern (per-write gate)

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

## 8. Color / badge semantics (universal)

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

## 9. Per-skill mapping

| Skill | Header card | Tabs | Action pattern | Preference questions | Mode picker |
|---|---|---|---|---|---|
| `gainsight-csm-book-pulse` | Book stats | 4: Overview / Priorities / Active Work / Watch | One-at-a-time + batch toggle | Per-account approach choice | Top of Priorities tab |
| `gainsight-account-workspace` | Account stats | 4: State / Recommended Actions / Existing Work / Briefing | One-at-a-time | Per-action approach choice | N/A (single account) |
| `gainsight-meeting-processor` | Call recap stats | 5: Email / Timeline / CTA / Tasks / Wins | Sequential approval per artifact | Per-artifact "approve/edit/skip" | N/A (review packet flow) |
| `gainsight-exec-renewal-radar` | Portfolio stats | 4: Per-Tier (Ent/MM/SMB) + Themes | Briefing-grade; optional handoff CTAs | "Drill into a tier?" choice | N/A (briefing) |
| `gainsight-renewal-priority-planner` | Renewal flight stats | 3: Priorities / Per-Account Plans / Open Items | One-at-a-time per account | Save vs save-then-expand vs skeptical | Top of Priorities |
| `gainsight-stakeholder-connect` | Stakeholder map stats | 3: Map / Outreach Drafts / Notes | Per-stakeholder outreach card | Tone choice (warm/firm/exploratory) | N/A |
| `gainsight-no-qbr-ebr-scheduler` | EBR pipeline stats | 2: Accounts Needing EBR / Scheduled | Per-account scheduling card | EBR scope choice | N/A |
| `gainsight-account-handoff-onboarding` | Onboarding stats | 5: Discovery / Validation / 90-Day Plan / Risks / Open Items | Sequential SP build | Validation question per section | N/A (sequential) |
| `gainsight-exec-pattern-hunter` | Portfolio stats | 3: Themes / Evidence / Recommendations | Briefing-grade | "Drill into theme?" choice | N/A (briefing) |
| `gainsight-exec-churn-retrospective` | Churn cohort stats | 4: Cohort / Patterns / Gaps / Recommendations | Briefing-grade | "Drill into pattern?" choice | N/A (briefing) |
| `gainsight-mcp-setup` | (skip header) | 1: Linear onboarding flow | Sequential setup | Role + filter field + practice round | N/A |

---

## 10. Anti-patterns (the failure modes)

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

---

## 11. Cross-references

- **Output content discipline:** `_shared/gainsight-output-best-practices.md` — what to write (CTA structure, Task content, Timeline format)
- **MCP query composition:** `staircase-mcp-expert/references/query-patterns.md` — how to query Staircase
- **Cross-walk between MCPs:** `_shared/mcp-cross-walk.md` — field-level Staircase ↔ Gainsight mapping

This doc (`cowork-output-patterns.md`) covers HOW to render. The output best-practices doc covers WHAT to write. Both apply on every Cowork-surfaced output.

---

## 12. Versioning + iteration

**v1.0 — 2026-05-26.** Initial codification from Layer 2 Cowork testing of Demo 1 (CSM Book Pulse on Hannah Lee). The wall-of-text failure mode triggered this doc.

Subsequent iterations as more demos validate the patterns. When a new pattern emerges that isn't covered here, add it. When a pattern proves not to work in Cowork's actual rendering, mark it deprecated rather than deleting (so historical reasoning survives).
