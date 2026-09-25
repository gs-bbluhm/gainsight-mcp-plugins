# Staircase Rendering Patterns

**Audience:** Every Staircase skill that produces user-facing output. Most run in both Cowork (visual chat) and Code (CLI). Cowork is the primary optimization target.

**Purpose:** Make the plugin's output feel like an app, not a markdown dump. Cowork has interactive primitives (cards, tabs, tables, and self-contained interactive experiences); when a skill defaults to a long markdown response, those primitives go unused and the read feels like a document, not a tool. This doc is the "what to render and why". `component-library.md` is the "how". `interactive-experiences.md` covers the rich interactive path.

---

## Pre-render checklist (run before producing any user-facing output)

**Detect the surface first.** Cowork means render as an app; Code means render as scannable markdown.

### Cowork rendering (app-feel)

- [ ] **Static vs interactive decided per section.** For each section, named the user's intent and picked a component from the library, or an interactive experience where the data has structure a table hides (see `interactive-experiences.md`). No defaulting to prose out of habit.
- [ ] **Colored app header** up top (indigo strip, stair-bars mark, scope, as-of date). See component #1.
- [ ] **Header metric grid** (3+3 or 2+2+2, never 4+2 with an empty slot). Signal-stripe each card by type. See component #2.
- [ ] **Tab navigation with counts** in the labels. See component #4.
- [ ] **Sortable ranked table** with chevrons and signal pills; pill color matches the row's signal-dot. See component #5.
- [ ] **Drill-down = read-only synthesis** (state, stakeholders, recommended next moves as text, evidence IDs). No write buttons; this plugin does not act. See component #6.
- [ ] **Empty sections get an empty state**, never a blank space. See component #7.
- [ ] **Signal semantics:** green healthy/rising, yellow neutral (never "concern"), red at-risk/declining, blue informational, gray inactive. Applied to every element with signal value. Never color alone; pair with a label.
- [ ] **No prose escape hatches.** If tempted to write a paragraph explaining what the user should do, it belongs in a callout, a drill-down bullet, or a tooltip.

### Code rendering (CLI-friendly markdown)

- [ ] **Structured headers** (`## Overview`, `## Priorities`, `## Silent risk`, `## Trend`).
- [ ] **Markdown tables** for prioritized lists. Emoji as signal surrogate (red, yellow, green, blue circles).
- [ ] **Inline reasoning is fine in Code.** CLI users want the analysis exposed.
- [ ] **Offer a saved artifact** the user can grab (a markdown file), since Code has no interactive surface.

### Surface detection (how to know which rendering to use)

Default heuristics:
- If interactive card / widget rendering is available, treat it as Cowork.
- If working from a Claude Code CLI with Bash + Read + file tools, treat it as Code.
- If unsure, produce Cowork-style structure (cards plus short prose). Cowork structure degrades gracefully to Code; a Code-style markdown wall does not fall up to Cowork (a wall in Cowork is the app-feel failure).

---

## 1. Colored app header (universal)

Identity strip at the top of every multi-section output: indigo brand strip, stair-bars mark, skill name, scope, as-of date. Consistent brand within the plugin. For Code, replace with a markdown H1. Concrete markup in `component-library.md` #1.

## 2. Header card (universal)

A 30-second orient. Four to six metrics, specifics not abstractions ("$X.XM revenue at risk", a real figure, not "significant revenue"). Signal-decorate the metrics that carry a signal. Concrete markup in `component-library.md` #2.

## 3. Tab structure (multi-section outputs)

Any output with three or more distinct sections uses tabs (three to five, never more). Common Staircase patterns:

| Tab pattern | Example use |
|---|---|
| Overview / Priorities / Silent risk / Trend | risk radar |
| Themes / Evidence / Accounts | voice of customer |
| Snapshot / Signals / Stakeholders / Evidence | single-account deep dive |

Tab names are short noun phrases. The user lands on the most useful tab by default. In Code, each tab becomes a `## Section` with `---` between sections.

## 4. Prioritized list (the ranked table)

Rank by a composite priority (winnable x high-stakes x urgent), not raw severity, so already-lost and not-yet-urgent accounts do not float to the top. Show the top eight to ten; collapse the rest. The "Why here" column is mandatory: one short signal phrase per row. Renewal as days-from-today; revenue compact (K and M suffixes, never the full digit string). Row click opens the read-only drill-down. Concrete markup in `component-library.md` #5 and #6.

## 5. Interactive experience (when the data earns it)

When a section's data is multi-dimensional in a way a table flattens (severity and urgency and revenue and lens at once), render an interactive experience instead of forcing it into a table. The Risk Radar is the first. Full rules and the when-to-use heuristic are in `interactive-experiences.md`. Do not reach for this when a sorted table answers the question; the visual has to add a dimension to be worth it.

## 6. Signal semantics (universal)

| Color | Meaning | Use |
|---|---|---|
| Green | healthy / rising | recovering signals, positive sentiment, stabilizing |
| Yellow | neutral / average | mid-band health, steady mix. Never "concern" |
| Red | at-risk / declining | high severity, negative sentiment, near-term decision |
| Blue | informational | silent/emerging risk, context notes |
| Gray | inactive / no-signal | out of scope, no fired signal |

Never use color alone. Always pair with a label or icon (accessibility).

---

## Anti-patterns

| Anti-pattern | Why it fails | Use instead |
|---|---|---|
| Wall of markdown with six-plus headers in Cowork | The user has to scroll and read; cannot act fast | Tabs (three to five) plus per-section components |
| Markdown tables in Cowork without pills/sorting | Loses the priority signal | Sortable table with signal pills |
| Treating yellow as "concern" | Yellow is neutral in Staircase | Reserve red for at-risk; yellow stays neutral |
| Count-vs-list mismatch (header says 5, list shows 7) | Erodes trust | Sub-group with sub-headings so the numbers reconcile |
| Observation with no framing | The signal lands flat | Put it in a callout with the "so what" |
| A "next move" rendered as a button | This plugin is read-only; a button implies a write | Read-only, copy-ready text the user acts on elsewhere |
| Interactive when a table would do | Friction, not insight | Ship the table unless the visual adds a dimension |
| Prose escape hatches | Reads as "the system gave up rendering this" | Convert to a callout, a drill-down bullet, or a tooltip |

---

## Cross-references

- **Component markup:** `component-library.md`
- **Interactive experiences:** `interactive-experiences.md`
- **Per-skill chrome:** `per-skill-mappings.md`
- **Content discipline:** `../../../_shared/staircase-output-best-practices.md`

## Versioning

**v1.0 (2026-08-06).** Ported from the gainsight-cs `mcp-app-design` patterns doc, rebranded to Staircase, and stripped of every write pattern (approval cards, pending-write footers, action tee-up sequences, working-mode pickers). Added the interactive-experience decision and pointer. Read-only synthesis only.
