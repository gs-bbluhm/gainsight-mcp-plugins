<!-- synthetic-data: every account name, figure, date, and evidence id in this file is invented for illustration. -->
# Staircase Component Library

**Audience:** Every Staircase skill that produces user-facing Cowork output.

**Purpose:** Copy-paste HTML markup for each read/synthesis component. `patterns.md` covers what to render and why; this doc covers how (the actual markup). Staircase is read-only, so this library carries only components that surface or explain. There are no action-proposal cards, no approval gates, no pending-write footers, no done-state write badges: this plugin never writes.

**How to use:**
1. Read `patterns.md` first: it tells you which components apply per skill and how to detect the surface.
2. For each component you need, copy its markup below and substitute the placeholder values with your skill's content.
3. Keep the `class="..."` names exactly: the renderer maps them to native primitives. If a class is unsupported, the markup still degrades to a div-wrapped list in order.

---

## Component index

| # | Component | When to use |
|---|---|---|
| 1 | App header (brand strip) | Top of every multi-section skill output |
| 2 | Metric card grid | Header area; 3+3 or 2+2+2 layout |
| 3 | Section callout | Inline info/warning/success notes |
| 4 | Tab navigation with counts | Multi-section outputs |
| 5 | Ranked table with signal pills | Prioritized account lists |
| 6 | Drill-down card (read-only) | Per-account expanded synthesis + evidence |
| 7 | Empty state | When a tab/section has no content |

For multi-dimensional data that a table flattens, do not force it into component #5. Consider an **interactive experience** instead (see `interactive-experiences.md`).

---

## Brand and signal colors

**Brand:** Staircase indigo `#4B53D4`. App header strip, brand mark, active states, primary accents.

**Signal colors** (semantic, independent of brand). Yellow = neutral/average, never "concern".

| Signal | Meaning | Background tint | Border / dot |
|---|---|---|---|
| Green | healthy / rising | `#E7F6EE` | `#16A46B` |
| Yellow | neutral / average | `#FFF6E6` | `#F4A72E` |
| Red | at-risk / declining | `#FDECEC` | `#E5484D` |
| Blue | informational | `#E9EFFC` | `#3B7DD8` |
| Gray | inactive / no-signal | `#F3F4F6` | `#6B7280` |

Row signal-dot color must match its signal-pill background tint. A red dot with a blue pill is a visual disconnect.

---

## 1. App header (brand strip)

Identity strip at the top of every multi-section skill output. The single biggest "this is an app, not a chat" cue. The left edge is a 4px indigo strip; the row sits on a faint indigo tint.

```html
<div class="app-header" data-brand="staircase">
  <span class="app-header__brand-strip"></span>
  <svg class="app-header__logo" viewBox="0 0 26 26" width="22" height="22" aria-hidden="true">
    <circle cx="13" cy="13" r="13" fill="#4B53D4"></circle>
    <rect x="6"  y="15" width="4" height="5"  rx="1" fill="#fff"></rect>
    <rect x="11" y="12" width="4" height="8"  rx="1" fill="#fff"></rect>
    <rect x="16" y="8"  width="4" height="12" rx="1" fill="#fff"></rect>
  </svg>
  <span class="app-header__title">Risk Radar</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__scope">My accounts</span>
  <span class="app-header__sep">·</span>
  <span class="app-header__date">As of Aug 6, 2026</span>
</div>
```

**Substitutions:** `app-header__title` = short skill name; `app-header__scope` = the Owner scope or "Portfolio"; `app-header__date` = the as-of date.

**Code fallback:** a markdown H1, e.g. `# Risk Radar · My accounts · As of Aug 6, 2026`.

---

## 2. Metric card grid

Four to six metric tiles in a balanced grid. Signal-striped where a tile carries a signal.

```html
<div class="metric-grid metric-grid--3x2">
  <div class="metric-card">
    <span class="metric-card__label">Accounts scanned</span>
    <span class="metric-card__value">32</span>
    <span class="metric-card__sub">my book</span>
  </div>
  <div class="metric-card">
    <span class="metric-card__label">Revenue at risk</span>
    <span class="metric-card__value">$2.4M</span>
    <span class="metric-card__sub">risk 4-5</span>
  </div>
  <div class="metric-card metric-card--risk">
    <span class="metric-card__label">Acute band</span>
    <span class="metric-card__value">5</span>
    <span class="metric-card__sub">nearest a decision</span>
  </div>
  <div class="metric-card metric-card--watch">
    <span class="metric-card__label">Renewals &lt; 90d</span>
    <span class="metric-card__value">7</span>
    <span class="metric-card__sub">the clock</span>
  </div>
  <div class="metric-card metric-card--info">
    <span class="metric-card__label">Silent risk</span>
    <span class="metric-card__value">3</span>
    <span class="metric-card__sub">sliding, not flagged</span>
  </div>
  <div class="metric-card metric-card--healthy">
    <span class="metric-card__label">Stabilizing</span>
    <span class="metric-card__value">4</span>
    <span class="metric-card__sub">signals recovering</span>
  </div>
</div>
```

**Layout modifiers:** `metric-grid--3x2`, `metric-grid--2x3`, `metric-grid--2x2`.
**Signal modifiers:** `metric-card--risk` (red), `metric-card--watch` (yellow), `metric-card--healthy` (green), `metric-card--info` (blue), `metric-card--neutral` (no stripe).

**Rules:**
- Every card has a visible border and a subtle fill, so even neutral cards read as data tiles.
- Never a 4+2 grid with an empty slot. Use 3+3 or 2+2+2. With four metrics use 2x2.
- The first one or two cards are usually neutral (counts, revenue). Later cards carry signal stripes.
- Sub-text is three to five words.

---

## 3. Section callout

Inline info/warning/success note surfacing an observation. Read-only: no action button (this plugin does not act), but it may end on a plain-text next step.

```html
<div class="callout callout--warning">
  <span class="callout__icon">!</span>
  <div class="callout__body">
    <div class="callout__title">11 of 14 near-term at-risk renewals have no working session booked</div>
    <div class="callout__detail">
      This is a portfolio-level pattern, not 11 individual nudges. Consider standing up the save-session
      motion once. Evidence IDs listed per account in the table.
    </div>
  </div>
</div>
```

**Severity modifiers:** `callout--warning` (yellow), `callout--info` (blue), `callout--success` (green), `callout--error` (red, for contradictions or data gaps). Always include an icon matched to severity. Title is one scannable line; detail is optional.

---

## 4. Tab navigation with counts

Tab bar for multi-section output. Counts give a glance signal of where attention concentrates.

```html
<div class="tab-nav">
  <button class="tab-nav__item tab-nav__item--active">Overview</button>
  <button class="tab-nav__item">Priorities <span class="tab-nav__count">8</span></button>
  <button class="tab-nav__item">Silent risk <span class="tab-nav__count">3</span></button>
  <button class="tab-nav__item">Trend</button>
</div>
```

**Rules:** three to five tabs. Counts only on tabs with countable items; the count pill sits tight against the label with no whitespace between them. Active tab gets the indigo underline. Labels are short noun phrases.

---

## 5. Ranked table with signal pills

Prioritized account list. Sortable. The signal column ties to the row's color-dot.

```html
<table class="ranked-table">
  <thead>
    <tr>
      <th class="ranked-table__signal-col"></th>
      <th class="ranked-table__sortable ranked-table__sortable--active-desc">
        Account <span class="ranked-table__chevron">▼</span>
      </th>
      <th class="ranked-table__sortable">Revenue <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Renewal <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Severity <span class="ranked-table__chevron">⇅</span></th>
      <th class="ranked-table__sortable">Health <span class="ranked-table__chevron">⇅</span></th>
      <th>Why here</th>
    </tr>
  </thead>
  <tbody>
    <tr class="ranked-table__row" data-signal="risk">
      <td><span class="signal-dot signal-dot--risk"></span></td>
      <td>1 · Acme Corp</td>
      <td>$48K</td>
      <td>38d</td>
      <td>0.81</td>
      <td>12</td>
      <td><span class="signal-pill signal-pill--risk">Renewal + low engagement</span></td>
    </tr>
    <tr class="ranked-table__row" data-signal="watch">
      <td><span class="signal-dot signal-dot--watch"></span></td>
      <td>2 · Globex</td>
      <td>$120K</td>
      <td>132d</td>
      <td>0.55</td>
      <td>47</td>
      <td><span class="signal-pill signal-pill--watch">Value question</span></td>
    </tr>
    <tr class="ranked-table__row" data-signal="info">
      <td><span class="signal-dot signal-dot--info"></span></td>
      <td>3 · Initech</td>
      <td>$64K</td>
      <td>410d</td>
      <td>0.31</td>
      <td>88</td>
      <td><span class="signal-pill signal-pill--info">Silent risk: sentiment slide</span></td>
    </tr>
  </tbody>
</table>
<button class="ranked-table__expand">Show full list</button>
```

**Rules:**
- Default sort = composite priority descending (no header sort active).
- The "Why here" / signal column is mandatory: every row gets one short signal label.
- Row signal-dot color equals signal-pill background tint (mandatory tie-back).
- Top eight to ten rows by default; the rest collapse under the expand button.
- Row click opens the drill-down (component #6). Yellow pills read as neutral, never "concern".

---

## 6. Drill-down card (read-only synthesis)

Per-row expanded state: account state, stakeholders, recommended next moves as copy-ready text, and evidence IDs. This is synthesis the user reads and acts on in their own tools. There are no write buttons.

```html
<div class="drilldown-card">
  <div class="drilldown-card__header">
    <span class="drilldown-card__title">Acme Corp</span>
    <span class="drilldown-card__meta">$48K revenue · renewal 2026-09-13 (38d) · risk 4 · health 12</span>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">STATE</div>
    <ul class="drilldown-card__state-list">
      <li>Engagement has gone quiet: last customer-initiated activity was weeks ago.</li>
      <li>Coverage is thin (2 stakeholders), and the renewal is inside 60 days.</li>
      <li>Renewal is the clock; the underlying lens is engagement/value, not competitive.</li>
    </ul>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">STAKEHOLDERS</div>
    <div class="stakeholder-chips">
      <div class="stakeholder-chip">
        <span class="stakeholder-chip__name">Primary contact</span>
        <span class="stakeholder-chip__role">2 known · single-threaded risk</span>
      </div>
    </div>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">RECOMMENDED NEXT MOVES</div>
    <ol class="drilldown-card__moves">
      <li>Book a working session before the renewal date; do not let it ride on email.</li>
      <li>Re-establish the value story and confirm the outcomes the buyer expects.</li>
      <li>Widen coverage: identify a second stakeholder beyond the primary contact.</li>
    </ol>
  </div>

  <div class="drilldown-card__section">
    <div class="drilldown-card__section-label">EVIDENCE</div>
    <div class="drilldown-card__evidence">ev_4821 · ev_4830 · ev_4844 (fetch to read the source communications)</div>
  </div>
</div>
```

**Rules:**
- The RECOMMENDED NEXT MOVES list is read-only text, never buttons. The user executes in their own tools.
- State bullets are concrete (specific signals, named lenses, real activity), not abstractions.
- Always include an EVIDENCE line so the read is verifiable. Ground every shared claim in a fetched evidence ID.
- One to four stakeholder chips. Keep the whole card under about 150 words; move depth to the source evidence.

---

## 7. Empty state

When a tab/section has no content, render an empty state, not a blank space or a "no data" line. Because this plugin does not act, the affordance is a re-scan or widen-scope suggestion phrased as plain guidance.

```html
<div class="empty-state">
  <div class="empty-state__icon">✓</div>
  <div class="empty-state__title">No acute-band accounts in scope</div>
  <div class="empty-state__detail">
    Nothing is inside a near-term decision with high severity right now. Widen the renewal window or
    re-run against the full book to pressure-test.
  </div>
</div>
```

**Icon library:** ✓ positive empty (all clear); an inbox glyph for neutral empty; a magnifier for a filter that matched nothing; ! for a concerning empty (this should have items, investigate). Empty states teach the user what the section is; write them with care.

---

## Class naming convention

BEM-like: `block`, `block__element`, `block--modifier`, `block__element--modifier`. If the renderer does not support a class, the markup degrades to a div-wrapped list in order.

## Cross-references

- **Pattern intent and surface detection:** `patterns.md`
- **Interactive experiences:** `interactive-experiences.md`
- **Content discipline:** `../../../_shared/staircase-output-best-practices.md`

## Versioning

**v1.0 (2026-08-06).** Ported from the gainsight-cs `mcp-app-design` component library and rebranded to Staircase (indigo `#4B53D4`, stair-bars mark, yellow = neutral). All write-oriented components removed (action proposal card, working mode picker, inline choice card, sticky pending-action footer, done-state write badge): this plugin is read-only synthesis. Drill-down reworked to read-only recommendations plus evidence. Seven read/synthesis components retained.
