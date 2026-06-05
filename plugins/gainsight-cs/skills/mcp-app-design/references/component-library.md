# Cowork Component Library

**Audience:** Every skill in this plugin that produces user-facing Cowork output.

**Purpose:** Concrete copy-paste HTML/markup for each visual primitive defined in `cowork-output-patterns.md`. The patterns doc covers WHAT to render and WHY; this doc covers HOW (the actual markup the skill should produce).

**How to use this doc:**
1. Read `cowork-output-patterns.md` first — it tells you which patterns apply per skill.
2. For each pattern you need, find its section here and copy the markup template.
3. Substitute the placeholder values with the actual content from your skill's output.
4. Wherever a `class="..."` attribute appears, use that exact class name — Cowork's renderer maps these to native primitives.

---

## ⚡ Component index

| # | Component | Pattern reference | When to use |
|---|---|---|---|
| 1 | App header (colored brand strip) | patterns §1 | Top of EVERY multi-tab skill output |
| 2 | Metric card grid | patterns §2 | Header card area; 3+3 or 2+2+2 layout |
| 3 | Section callout | patterns §1, §2, §12 | Inline warnings/info/success/error notes |
| 4 | Tab navigation with counts | patterns §3 | Multi-section outputs |
| 5 | Ranked table with chevrons + signal pills | patterns §7 | Prioritized account lists |
| 6 | Drill-down card | patterns §7 | Per-account expanded state + next moves |
| 7 | Working mode picker (full + collapsed) | patterns §6 | Top of multi-action flows |
| 8 | Inline choice card | patterns §5 | Preference questions with branching outcomes |
| 9 | Action proposal card | patterns §4 | One-at-a-time action surfacing with approve/edit/skip |
| 10 | Sticky pending-action footer | patterns §9 | Queued actions across session |
| 11 | Done-state badge | patterns §12 anti-patterns | Replace action button when item is complete |
| 12 | Empty state | universal | When a tab/section has no content |

---

## Brand color palette

One canonical brand color per plugin. Used for the app header strip, primary CTAs, focused/active states.

| Plugin | Brand color | Hex | Use |
|---|---|---|---|
| `gainsight-cs` | Gainsight CS blue | `#1976D2` | App header, primary CTAs |
| (future) `staircase-only` | Staircase navy | `#1A2C5C` | App header, primary CTAs |
| (future) `cs-neutral` | Plugin teal | `#0F8E8E` | App header, primary CTAs |

Signal colors (universal across plugins, per patterns §10):

| Signal | Hex tint | Hex border | Use |
|---|---|---|---|
| 🔴 Risk | `#FEE2E2` bg / `#DC2626` border | Risk metric cards, risk pills, risk badges |
| 🟡 Watch | `#FEF3C7` bg / `#D97706` border | Watch metric cards, EBR pills, amber callouts |
| 🟢 Healthy | `#D1FAE5` bg / `#059669` border | Healthy state badges, success notes |
| 🔵 Expansion | `#DBEAFE` bg / `#2563EB` border | Expansion-ready, opportunity pills |
| ⚪ Inactive | `#F3F4F6` bg / `#6B7280` border | Closed/inactive items, gray badges |
| 🟣 Advocacy (optional) | `#EDE9FE` bg / `#7C3AED` border | Hero accounts, advocacy moments |

---

## 1. App header (colored brand strip)

**Purpose:** Identity strip at the top of every multi-tab skill output.

**Visual sketch:**

```
┌──────────────────────────────────────────────────────────────────┐
│ █ 📊  Book Pulse  ·  Hannah Lee  ·  Week of May 26, 2026   ⟳ ?   │
└──────────────────────────────────────────────────────────────────┘
```

The left edge `█` is a 4px branded color strip. The whole row sits on a slightly tinted background of the same color (alpha ~0.05).

**Cowork markup:**

```html
<div class="app-header" data-brand="gainsight">
  <span class="app-header__brand-strip"></span>
  <span class="app-header__icon">📊</span>
  <span class="app-header__title">Book Pulse</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__persona">Hannah Lee</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__date">Week of May 26, 2026</span>
  <div class="app-header__actions">
    <button class="app-header__action" title="Refresh data">⟳</button>
    <button class="app-header__action" title="Help / how this works">?</button>
  </div>
</div>
```

**Substitutions per skill:**

| Placeholder | Source |
|---|---|
| `data-brand` | Plugin brand (`gainsight` / `staircase` / `cs-neutral`) |
| `app-header__icon` content | Per-skill icon from patterns §11 mapping |
| `app-header__title` | Short skill name ("Book Pulse" / "Meeting Recap" / "Renewal Radar") |
| `app-header__persona` | Filter value or "Portfolio" for exec skills |
| `app-header__date` | "Week of <date>" / "<date>" / "<date> - <date>" |

**Cowork fallback (no `data-brand` styling):**

A simple bordered `div` with the brand color on left border still renders the visual intent. Cowork's parser will at least surface the icon + title + persona + date in order.

**Code fallback:**

```markdown
# 📊 Book Pulse — Hannah Lee · Week of May 26, 2026
```

---

## 2. Metric card grid

**Purpose:** 4-6 metric tiles in a balanced grid. Signal-color-striped where appropriate.

**Visual sketch (3+3 grid):**

```
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Book size  │ │ Total ARR  │ │ Risk⚠      │
│   31       │ │  $830K     │ │   4        │
│ all SMB    │ │ avg $26.8K │ │ Risk 4-5   │
└────────────┘ └────────────┘ └────────────┘
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Overdue CTA│ │ EBRs       │ │ Expansion🟢│
│   1        │ │   5        │ │   7        │
│ 5 tasks    │ │ 60-120d    │ │ ER 3+      │
└────────────┘ └────────────┘ └────────────┘
```

The Risk and Expansion cards get color-stripe accents (left border or top border tinted to the signal color).

**Cowork markup:**

```html
<div class="metric-grid metric-grid--3x2">
  <div class="metric-card">
    <span class="metric-card__label">Book size</span>
    <span class="metric-card__value">31</span>
    <span class="metric-card__sub">all SMB tier</span>
  </div>
  <div class="metric-card">
    <span class="metric-card__label">Total ARR</span>
    <span class="metric-card__value">$830K</span>
    <span class="metric-card__sub">avg $26.8K</span>
  </div>
  <div class="metric-card metric-card--risk">
    <span class="metric-card__label">High-risk signals</span>
    <span class="metric-card__value">4</span>
    <span class="metric-card__sub">Risk 4-5 in Staircase</span>
  </div>
  <div class="metric-card">
    <span class="metric-card__label">Overdue CTAs</span>
    <span class="metric-card__value">1</span>
    <span class="metric-card__sub">5 tasks, 20d overdue</span>
  </div>
  <div class="metric-card metric-card--watch">
    <span class="metric-card__label">EBRs in window</span>
    <span class="metric-card__value">5</span>
    <span class="metric-card__sub">renewal 60-120d out</span>
  </div>
  <div class="metric-card metric-card--expansion">
    <span class="metric-card__label">Expansion-ready</span>
    <span class="metric-card__value">7</span>
    <span class="metric-card__sub">ER 3+ in Staircase</span>
  </div>
</div>
```

**Grid layout modifiers:**
- `metric-grid--3x2` — 3 columns × 2 rows (6 cards) — recommended for book/scope skills
- `metric-grid--2x3` — 2 columns × 3 rows
- `metric-grid--2x2` — 2 columns × 2 rows (4 cards)

**Signal modifiers:**
- `metric-card--risk` — red stripe (use for risk-related metrics)
- `metric-card--watch` — amber stripe (EBR-due, past-renewal, stale engagement)
- `metric-card--healthy` — green stripe (healthy stats, completed work)
- `metric-card--expansion` — blue stripe (expansion-ready, opportunity stats)
- `metric-card--neutral` — no stripe (book size, totals, counts without signal)

**Rules:**
- Every card carries a visible border and a subtle surface fill so even neutral (no-stripe) cards read as real data tiles, not muted text. Signal cards layer their color stripe on top of that border. (Refinement 2026-06-05 from Cowork render feedback: borderless neutral cards looked too flat.)
- NEVER use 4+2 (4 cards row + 2 cards row with empty space). Looks broken.
- If you only have 4 metrics, use `metric-grid--2x2` (2×2) — don't try to fill 6 slots with weak metrics.
- The first 2 metrics are usually neutral (book size, ARR). Subsequent metrics carry signal stripes where appropriate.
- Sub-text is 3-5 words max ("avg $26.8K" / "Risk 4-5 in Staircase" / "60-120d out").

---

## 3. Section callout

**Purpose:** Inline alert/info/success/error notes — usually surfacing observations the user needs to see but that aren't part of the main grid.

**Visual sketch:**

```
┌─⚠────────────────────────────────────────────────────────────────┐
│  5 accounts past renewal — needs reconciliation today             │
│  Soto Marketplace, Venice Data, Puma Raven, Roberts Ecommerce,    │
│  Moose Analytics. Check with deal desk.                           │
└──────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="callout callout--warning">
  <span class="callout__icon">⚠</span>
  <div class="callout__body">
    <div class="callout__title">5 accounts past renewal — needs reconciliation today</div>
    <div class="callout__detail">
      Soto Marketplace, Venice Data, Puma Raven, Roberts Ecommerce, Moose Analytics.
      Renewal dates lapsed 25-72 days ago. Check with deal desk.
    </div>
  </div>
  <button class="callout__action">Draft deal desk ask</button>
</div>
```

**Severity modifiers:**
- `callout--warning` — amber. Past-due items, stale flags, risk observations.
- `callout--info` — blue. Briefing notes, contextual observations.
- `callout--success` — green. Wins, completed work, advocacy moments.
- `callout--error` — red. Failed writes, contradictions, blockers.

**Rules:**
- ALWAYS include an icon. Icon matches the severity (⚠ warning · ℹ info · ✓ success · ✗ error).
- Title is single line, scannable.
- Detail is optional — short paragraph if context needed.
- Action button is optional but recommended — every observation that could lead to action gets a button (per patterns §12).

---

## 4. Tab navigation with counts

**Purpose:** Tab bar at the top of multi-section skill output. Counts on each tab give a glance signal of where attention concentrates.

**Visual sketch:**

```
┌────────────┐ ┌─────────────┐ ┌─────────────────┐ ┌──────────────────┐
│ At a glance│ │ Priorities  │ │  Active work    │ │ Watch / briefing │
│            │ │     (8)     │ │      (4)        │ │       (7)        │
└────────────┘ └─────────────┘ └─────────────────┘ └──────────────────┘
   active        not active       not active            not active
```

**Cowork markup:**

```html
<div class="tab-nav">
  <button class="tab-nav__item tab-nav__item--active">
    At a glance
  </button>
  <button class="tab-nav__item">
    Priorities <span class="tab-nav__count">8</span>
  </button>
  <button class="tab-nav__item">
    Active work <span class="tab-nav__count">4</span>
  </button>
  <button class="tab-nav__item">
    Watch / briefing <span class="tab-nav__count">7</span>
  </button>
</div>
```

**Rules:**
- 3-5 tabs max. More = scan failure.
- Counts only on tabs with countable items (Priorities, Active Work, Watch). Skip on overview/at-a-glance tabs.
- The count renders as a small inline pill/badge tight against the label, NOT trailing text with a gap. The `tab-nav__count` span follows the label with no whitespace between them. (Refinement 2026-06-05 from Cowork render feedback: gapped counts read as loose text, not an app badge.)
- Active tab gets the brand color underline or bottom border.
- Tab labels are short noun phrases. "Priorities" not "Things to focus on this week."

---

## 5. Ranked table with chevrons + signal pills

**Purpose:** Prioritized account list. Sortable. Signal column tied to row color-dot.

**Visual sketch:**

```
┌──┬───────────────────────┬──────┬─────────┬──────┬────────┬──────────────┐
│  │ ACCOUNT          ▼    │ ARR  │ RENEWAL │ RISK │ HEALTH │ SIGNAL       │
├──┼───────────────────────┼──────┼─────────┼──────┼────────┼──────────────┤
│🔴│ 1 · Navy Bayview      │ $45K │ 46d     │  5   │   34   │ Active exit  │
│🔴│ 2 · Hillview          │ $15K │ 75d     │  5   │   43   │ Decision final│
│🟡│ 3 · Rosales Tech      │ $30K │  2d     │  -   │   91   │ CTA false-pos│
│🔴│ 4 · Soto Marketplace  │ $30K │ -72d    │  -   │   21   │ Past renewal │
│🔵│ 6 · Ito Fulfillment   │ $15K │ 39d     │  -   │   66   │ Expansion play│
└──┴───────────────────────┴──────┴─────────┴──────┴────────┴──────────────┘
                    [ Show watch list (9-15) ]
```

**Cowork markup:**

```html
<table class="ranked-table">
  <thead>
    <tr>
      <th class="ranked-table__signal-col"></th>
      <th class="ranked-table__sortable ranked-table__sortable--active-desc">
        Account <span class="ranked-table__chevron">▼</span>
      </th>
      <th class="ranked-table__sortable">ARR <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Renewal <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Risk <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Health <span class="ranked-table__chevron">⇅</span></th>
      <th>Signal</th>
    </tr>
  </thead>
  <tbody>
    <tr class="ranked-table__row" data-signal="risk">
      <td><span class="signal-dot signal-dot--risk"></span></td>
      <td>1 · Navy Bayview Supply</td>
      <td>$45K</td>
      <td>46d</td>
      <td>5</td>
      <td>34</td>
      <td><span class="signal-pill signal-pill--risk">Active exit</span></td>
    </tr>
    <tr class="ranked-table__row" data-signal="watch">
      <td><span class="signal-dot signal-dot--watch"></span></td>
      <td>3 · Rosales Technologies</td>
      <td>$30K</td>
      <td>2d</td>
      <td>—</td>
      <td>91</td>
      <td><span class="signal-pill signal-pill--watch">CTA false-pos</span></td>
    </tr>
    <tr class="ranked-table__row" data-signal="expansion">
      <td><span class="signal-dot signal-dot--expansion"></span></td>
      <td>6 · Ito Fulfillment</td>
      <td>$15K</td>
      <td>39d</td>
      <td>—</td>
      <td>66</td>
      <td><span class="signal-pill signal-pill--expansion">Expansion play</span></td>
    </tr>
    <!-- ... more rows ... -->
  </tbody>
</table>
<button class="ranked-table__expand">Show watch list (9-15)</button>
```

**Key components:**
- `signal-dot--{risk|watch|healthy|expansion|inactive}` — colored dot in the leftmost column
- `signal-pill--{risk|watch|healthy|expansion|inactive}` — pill in the Signal column with MATCHING color tint
- `ranked-table__sortable` — sortable column header with chevron
- `ranked-table__sortable--active-desc` / `--active-asc` — currently-sorted column with directional chevron

**Color tie-back is mandatory.** Row signal-dot color === signal-pill background tint. Anti-pattern: red dot but blue pill (visual disconnect).

**Rules:**
- Default sort = priority/composite score descending (no header sort active).
- "Why here" / Signal column is mandatory — every row needs a signal label.
- Top 8-10 rows by default. Watch list 11+ collapsed below `[Show watch list]` button.
- Row click triggers drill-down (component #6 below).

---

## 6. Drill-down card

**Purpose:** Per-row expanded state with customer state, stakeholders, recommended next moves.

**Visual sketch:**

```
┌─ Navy Bayview Supply   $45K ARR · renewal 2026-07-11 (46d) · Risk 5 · Health 34 ─┐
│                                                                                   │
│  STATE                                                                            │
│  • John Jennings + Timothy Mitchell have committed to a competitor.               │
│  • They asked for free-tier downgrade + data export.                              │
│  • Our last outreach pitched expansion — comms mismatch is the immediate problem. │
│                                                                                   │
│  STAKEHOLDERS                                                                     │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────────────────────┐   │
│  │ John Jennings    │ │ Timothy Mitchell │ │ David Johnson                   │   │
│  │ Primary · Detr.  │ │ Decision-maker · │ │ Comms-risk · Unclear role       │   │
│  │                  │ │ Detractor        │ │                                 │   │
│  └──────────────────┘ └──────────────────┘ └─────────────────────────────────┘   │
│                                                                                   │
│  NEXT MOVES                                                                       │
│  [ Draft offboarding-first outreach to John Jennings ]                            │
│  [ Update CTA → Save: Offboarding control ]                                       │
│  [ Brief Timothy in parallel ]                                                    │
│                                                                                   │
│                                                          [ Skip ] [ More context ]│
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="drilldown-card">
  <div class="drilldown-card__header">
    <span class="drilldown-card__title">Navy Bayview Supply</span>
    <span class="drilldown-card__meta">$45K ARR · renewal 2026-07-11 (46d) · Risk 5 · Health 34</span>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">STATE</div>
    <ul class="drilldown-card__state-list">
      <li>John Jennings + Timothy Mitchell have committed to a competitor.</li>
      <li>They asked for free-tier downgrade + data export.</li>
      <li>Our last outreach pitched expansion — comms mismatch is the immediate problem.</li>
    </ul>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">STAKEHOLDERS</div>
    <div class="stakeholder-chips">
      <div class="stakeholder-chip">
        <span class="stakeholder-chip__name">John Jennings</span>
        <span class="stakeholder-chip__role">Primary contact · Detractor</span>
      </div>
      <div class="stakeholder-chip">
        <span class="stakeholder-chip__name">Timothy Mitchell</span>
        <span class="stakeholder-chip__role">Decision-maker · Detractor</span>
      </div>
      <div class="stakeholder-chip">
        <span class="stakeholder-chip__name">David Johnson</span>
        <span class="stakeholder-chip__role">Comms-risk signal · Unclear role</span>
      </div>
    </div>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">NEXT MOVES</div>
    <div class="next-moves">
      <button class="next-move next-move--primary">Draft offboarding-first outreach to John Jennings</button>
      <button class="next-move">Update CTA → Save: Offboarding control</button>
      <button class="next-move">Brief Timothy in parallel</button>
    </div>
  </div>

  <div class="drilldown-card__footer">
    <button class="drilldown-card__skip">Skip this account</button>
    <button class="drilldown-card__more">More context</button>
  </div>
</div>
```

**Rules:**
- 2-4 Next Moves buttons per drill-down. ALWAYS show at least 1 — never empty.
- First Next Move is `next-move--primary` (the recommended action).
- Stakeholders rendered as chips (1-4 per card). Click should reveal stakeholder details (engagement history, last touch, sentiment trend) — future enhancement.
- State bullets are concrete (named stakeholders, specific actions, evidence). Not abstractions.
- "More context" reveals a Timeline-style activity history if available.

---

## 7. Working mode picker (full + collapsed)

**Purpose:** Let user pick session mode (one-at-a-time / batch / focused). Full state shown on first visit; compresses to single line after selection.

### Full state (first visit)

**Visual sketch:**

```
┌─ Working mode ────────────────────────────────────────────────────────────┐
│  How do you want to work through this?                                    │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────┐   │
│  │ One at a time    │  │ All actions      │  │ Must-do only          │   │
│  │ (Recommended)    │  │  at once         │  │                       │   │
│  │ I walk you       │  │ Show every       │  │ Top 3, skip watch     │   │
│  │ through #1, you  │  │ proposed move in │  │ list.                 │   │
│  │ decide, then #2. │  │ a stacked queue. │  │                       │   │
│  └──────────────────┘  └──────────────────┘  └───────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="mode-picker">
  <div class="mode-picker__title">Working mode</div>
  <div class="mode-picker__question">How do you want to work through this?</div>
  <div class="mode-picker__options">
    <button class="mode-picker__option mode-picker__option--recommended">
      <span class="mode-picker__badge">Recommended</span>
      <span class="mode-picker__option-title">One at a time</span>
      <span class="mode-picker__option-desc">I walk you through #1, you decide, then #2.</span>
    </button>
    <button class="mode-picker__option">
      <span class="mode-picker__option-title">All actions at once</span>
      <span class="mode-picker__option-desc">Show every proposed move in a stacked queue.</span>
    </button>
    <button class="mode-picker__option">
      <span class="mode-picker__option-title">Must-do only</span>
      <span class="mode-picker__option-desc">Top 3, skip watch list.</span>
    </button>
  </div>
</div>
```

### Collapsed state (after selection)

**Visual sketch:**

```
┌─ Mode: One at a time · [ change ] ──────────────────────────────────────┐
└─────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="mode-picker mode-picker--collapsed">
  <span class="mode-picker__current-label">Mode:</span>
  <span class="mode-picker__current-value">One at a time</span>
  <button class="mode-picker__change">change</button>
</div>
```

**Rules:**
- Default selection = "One at a time" (Recommended badge).
- After click → compress to collapsed state with `[change]` affordance.
- "change" link re-expands to full state.
- Selected mode persists across tab switches within the session.

---

## 8. Inline choice card (preference question)

**Purpose:** When skill needs user to pick between approaches with branching outcomes.

**Visual sketch:**

```
┌─ How should we approach Navy Bayview? ──────────────────────────────────┐
│                                                                         │
│  ⚪ Offboarding-first  [Recommended]                                    │
│     Course-correct apology, free-tier path, export checklist.           │
│     Accept the migration but contain the damage.                        │
│                                                                         │
│  ⚪ Save-with-incentive                                                 │
│     Offer free-tier-plus-services to retain.                            │
│     Higher risk; bigger upside if it lands.                             │
│                                                                         │
│  ⚪ Multi-thread before responding                                      │
│     Identify a third stakeholder above John + Timothy.                  │
│     Delays response 1-2 days.                                           │
│                                                                         │
│                                                          [ Pick approach ]│
└─────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="choice-card">
  <div class="choice-card__question">How should we approach Navy Bayview?</div>
  <div class="choice-card__options">
    <label class="choice-card__option choice-card__option--recommended">
      <input type="radio" name="approach" value="offboarding-first" checked>
      <span class="choice-card__badge">Recommended</span>
      <span class="choice-card__option-title">Offboarding-first</span>
      <span class="choice-card__option-desc">
        Course-correct apology, free-tier path, export checklist.
        Accept the migration but contain the damage.
      </span>
    </label>
    <label class="choice-card__option">
      <input type="radio" name="approach" value="save-with-incentive">
      <span class="choice-card__option-title">Save-with-incentive</span>
      <span class="choice-card__option-desc">
        Offer free-tier-plus-services to retain.
        Higher risk; bigger upside if it lands.
      </span>
    </label>
    <label class="choice-card__option">
      <input type="radio" name="approach" value="multi-thread">
      <span class="choice-card__option-title">Multi-thread before responding</span>
      <span class="choice-card__option-desc">
        Identify a third stakeholder above John + Timothy.
        Delays response 1-2 days.
      </span>
    </label>
  </div>
  <button class="choice-card__submit">Pick approach</button>
</div>
```

**Rules:**
- 2-4 options. More = too many branches.
- One option flagged `--recommended` (the AI's pick based on the merge classification + signals).
- Each option has 1-2 sentence description explaining the trade-off.
- Submit button at bottom; never auto-submit on selection.

---

## 9. Action proposal card

**Purpose:** When user picks a Next Move from a drill-down, surface ONE deliverable as an approval-gated card.

**Visual sketch:**

```
┌─ Draft offboarding-first outreach to John Jennings ─────────────────────┐
│                                                                         │
│  To:  jjennings@navybayview.example                                     │
│  CC:  tmitchell@navybayview.example                                     │
│  Subject: Re-aligning on your next steps                                │
│                                                                         │
│  John —                                                                 │
│                                                                         │
│  Wanted to follow up directly on our last few exchanges. Hearing you    │
│  loud and clear that the team has committed to a different path — and  │
│  apologize for the expansion-oriented tone of the last note...         │
│                                                                         │
│  [body continues, ~150 words]                                           │
│                                                                         │
│  ────────────────────────────────────────────────                       │
│                                                                         │
│  ⚠ VERIFY BEFORE SENDING:                                               │
│  • Free-tier downgrade path is real (confirmed with ops?)               │
│  • Data export checklist + timeline matches what we can deliver         │
│  • Named owner for the offboarding has internal sign-off                │
│                                                                         │
│              [ Approve & send to drafts ]  [ Edit ]  [ Skip ]           │
└─────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="action-card">
  <div class="action-card__title">Draft offboarding-first outreach to John Jennings</div>

  <div class="action-card__preview">
    <div class="action-card__field">
      <span class="action-card__field-label">To:</span>
      <span class="action-card__field-value">jjennings@navybayview.example</span>
    </div>
    <div class="action-card__field">
      <span class="action-card__field-label">CC:</span>
      <span class="action-card__field-value">tmitchell@navybayview.example</span>
    </div>
    <div class="action-card__field">
      <span class="action-card__field-label">Subject:</span>
      <span class="action-card__field-value">Re-aligning on your next steps</span>
    </div>
    <div class="action-card__body">
      <p>John —</p>
      <p>Wanted to follow up directly on our last few exchanges...</p>
      <!-- body continues -->
    </div>
  </div>

  <div class="action-card__verify">
    <div class="action-card__verify-title">⚠ Verify before sending:</div>
    <ul>
      <li>Free-tier downgrade path is real (confirmed with ops?)</li>
      <li>Data export checklist + timeline matches what we can deliver</li>
      <li>Named owner for the offboarding has internal sign-off</li>
    </ul>
  </div>

  <div class="action-card__actions">
    <button class="action-card__approve">Approve & send to drafts</button>
    <button class="action-card__edit">Edit</button>
    <button class="action-card__skip">Skip</button>
  </div>
</div>
```

**Rules:**
- Card variants per action type:
  - `action-card--email` (rendering above) — for outreach drafts
  - `action-card--cta` — for CTA creates/updates (show CTA fields, not email)
  - `action-card--sp` — for SP creates/updates
  - `action-card--timeline` — for Timeline activity creates
  - `action-card--slack` — for Slack messages
- ALWAYS include `action-card__verify` block when sending external comms (emails, Slack to customer, etc.). NEVER skip for internal-only writes (CTA tasks, Timeline activities).
- "Approve" wording matches the destination but stays SHORT enough to fit the button: "Approve → drafts" (Gmail), "Approve → post" (Gainsight write), "Approve → schedule" (calendar). Avoid long labels like "Approve & send to drafts" that overflow. (Refinement 2026-06-05 from Cowork render feedback.)
- **Reply-approval cards lead with an incoming-context block** so the user can validate the draft against what they are responding to. Above the draft preview, render an `action-card__incoming` section: sender + who is on the thread, a 1-2 line thread TLDR, the actual quote of the ask (`action-card__quote`), and a deep-link to the source (`action-card__threadlink`, e.g. "View full email in Gmail"). Then an `action-card__divider` labeled YOUR DRAFT, then the preview. Never ask the user to approve a reply they cannot see the trigger for. (Added 2026-06-05.)

---

## 10. Sticky pending-action footer

**Purpose:** As actions accumulate across the session, show the queue + final review affordance.

**Visual sketch:**

```
┌──────────────────────────────────────────────────────────────────────────┐
│  3 actions queued · 1 CTA · 1 outreach · 1 SP update                     │
│                                                       [ Review all (3) ] │
└──────────────────────────────────────────────────────────────────────────┘
```

Sticky to viewport bottom. Updates live as user approves/skips moves.

**Cowork markup:**

```html
<div class="pending-footer">
  <div class="pending-footer__summary">
    <span class="pending-footer__count">3 actions queued</span>
    <span class="pending-footer__sep">·</span>
    <span class="pending-footer__breakdown">1 CTA · 1 outreach · 1 SP update</span>
  </div>
  <button class="pending-footer__review">Review all (3)</button>
</div>
```

**Behavior:**
- Hidden when queue empty.
- Appears on first action approval; updates live.
- "Review all" opens the consolidated pre-write validation card (per patterns §8).
- After consolidated approval fires + writes execute → footer empties + re-hides.

**Conditional rendering:**
- Show in conversational mode (one-at-a-time).
- HIDE in batch mode — the approval queue already shows the items, footer is redundant.

---

## 11. Done-state badge

**Purpose:** Replace action button when an item is genuinely complete (no action needed).

**Visual sketch:**

```
[ Bennett Birch Supply · Renewal SP · 100% complete · all 4 CTAs closed ]    ✓ Done
```

vs the anti-pattern:

```
[ Bennett Birch Supply · Renewal SP · 100% complete · all 4 CTAs closed ]    [ Light-touch follow ]
```

The "Light-touch follow" button implies action — but reality is "you're done, just confirm renewal proceeds." The done-state badge signals completion, not a pending task.

**Cowork markup (done-state):**

```html
<div class="list-item list-item--done">
  <div class="list-item__title">Bennett Birch Supply</div>
  <div class="list-item__meta">Renewal SP · 100% complete · all 4 CTAs closed</div>
  <span class="list-item__done-badge">✓ Done</span>
</div>
```

**Rules:**
- Use when the item state is genuinely complete + no action needed.
- If the user might want to do something (confirm, archive, etc.), use a muted/secondary button instead: `<button class="list-item__action list-item__action--muted">Confirm renewal proceeds</button>`.
- Never use a primary-styled action button on a done-state item.

---

## 12. Empty state

**Purpose:** When a tab/section has no content, render an empty state — not a blank space, not a "no data" prose line.

**Visual sketch:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                              🎉                                          │
│                                                                         │
│                  No overdue CTAs in your book                            │
│                                                                         │
│         You're caught up on all CTAs assigned to you.                    │
│         Want to review accounts that don't have CTAs yet?                │
│                                                                         │
│                       [ Scan for CTA-worthy accounts ]                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Cowork markup:**

```html
<div class="empty-state">
  <div class="empty-state__icon">🎉</div>
  <div class="empty-state__title">No overdue CTAs in your book</div>
  <div class="empty-state__detail">You're caught up on all CTAs assigned to you. Want to review accounts that don't have CTAs yet?</div>
  <button class="empty-state__action">Scan for CTA-worthy accounts</button>
</div>
```

**Icon library per state:**
- 🎉 — positive empty state (all caught up, all renewed, nothing overdue)
- 📭 — neutral empty (no items in this category yet)
- 🔍 — search empty (filter didn't match)
- ⚠ — concerning empty (this should have items but doesn't — investigate)

**Rules:**
- Empty state is more important than a populated state — it's where users learn what the section IS.
- ALWAYS include an action button — "what would the user want to do from here?" — even if it's a "Scan again" / "Widen lookback" / "Compare to last week."
- Concerning empty states (⚠) prompt investigation, not celebration.

---

## Class naming convention

All component classes follow BEM-like structure:

- `component-name` (block)
- `component-name__element` (element within block)
- `component-name--modifier` (modifier of block)
- `component-name__element--modifier` (modifier of element)

If Cowork's renderer doesn't support these specific classes, the markup still renders the content in order — the structure degrades gracefully to a div-wrapped list.

---

## Cross-references

- **Pattern intent + when-to-use:** `cowork-output-patterns.md` — the canonical patterns reference
- **Output content discipline (writes):** `gainsight-output-best-practices.md` — what to write
- **MCP query composition:** `staircase-mcp-expert/references/query-patterns.md` — how to query Staircase

---

## Versioning

**v1.0 — 2026-05-26.** Initial component library extracted from Layer 2 Cowork testing of Demo 1 (CSM Book Pulse on Hannah Lee). Brady's per-tab UX feedback drove the spec: colored header, metric color stripes, sortable chevrons, signal pill tie-back, drill-down placement, working mode picker collapse, action affordance everywhere, sticky pending-action footer, done-state badge, empty state.

Subsequent iterations: as Cowork ships new primitives, add components. When a component proves not to render well in actual Cowork, mark deprecated rather than deleting.
