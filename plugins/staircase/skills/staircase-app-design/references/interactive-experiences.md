# Interactive Experiences

**Audience:** Any Staircase skill whose data has structure a static table flattens.

**Purpose:** Codify how to build and ship a rich, self-contained interactive HTML app inside a skill. This is the maturing edge of the app-design system: beyond components, some reads deserve a small purpose-built visualization the user can explore. The `staircase-risk-radar` polar radar is the first. This doc is the standard every Staircase interactive experience follows.

---

## When to build one (the heuristic)

Default to the component library. An interactive experience has to earn its place by adding a dimension a sorted table cannot show.

**Build an interactive experience when all of these hold:**
- Two or more dimensions matter at the same time (the radar plots severity, renewal urgency, revenue, dominant lens, and health together).
- The record count is a wall as a table but plottable (roughly 10 to 150).
- Spatial or relational structure reveals a pattern a single sort order hides (clusters, outliers, who is sliding but not yet flagged).
- The surface is Cowork/visual and exploration (hover, filter, toggle) adds real understanding.

**Ship a static table instead when:**
- The answer is a ranked list to scan top-down.
- N is small.
- The user will copy or share the output as text.
- The surface is Code/CLI.
- One clear sort answers the question.

If the visual does not add a dimension over a sorted table, it is slower to read, not faster. When in doubt, ship the table.

---

## The rules every Staircase interactive experience follows

### 1. Single self-contained HTML file, no external calls
- One `.html` file in the skill's `experiences/` folder. Everything inline: styles in a `<style>` block, logic in a `<script>` block.
- **No external network calls.** No analytics, no telemetry, no data leaves the file. This is customer-shippable code that must never phone home.
- **No web fonts that phone home.** Use a system font stack (`system-ui, -apple-system, Segoe UI, Roboto, sans-serif`). A font request leaks the fact of opening plus an IP to a third party; that breaks the guarantee.
- If you genuinely need a library, either inline it, or pin one well-known CDN (jsdelivr, cdnjs, unpkg) and **degrade gracefully** if it fails to load (feature-detect the global; render a legible fallback if absent). Prefer inlining or plain SVG/DOM so the file works fully offline.

### 2. Transparent background
- `html, body { background: transparent; }` so the file embeds cleanly on whatever surface hosts it. Give the app's own panels a surface (white cards with borders) so it stays legible on a light or a dark host.

### 3. Data separated from render
- A `const DATA = [...]` JSON block near the top of the script, visually and structurally distinct from the render code. The skill rewrites **only** that block each run; the render logic never changes per run.
- Also pull run-scoped constants (like the as-of date) into a single clearly labelled place so the skill sets them without touching logic.
- Compute derived values (scores, positions, colors) in code from the raw record fields. Do not bake computed values into the data; keep `DATA` as raw signals so the math stays auditable in one place.

### 4. Progressive disclosure
- Hover (and keyboard focus) shows a compact tooltip: the few facts that identify and rank the item.
- Click (and Enter/Space) opens a detail panel with the full read.
- Never dump everything at once. The overview reads in one glance; depth is one interaction away.

### 5. Accessible and reflowing
- Reflows on narrow widths (the detail panel goes full-width on mobile).
- Every interactive element is keyboard-reachable: `tabindex="0"`, `role="button"`, an `aria-label` that speaks the item, Enter/Space to open, Escape to close a panel, focus returns to the trigger on close.
- The file opens with a visually-hidden `<h1 class="sr-only">` summarizing what the visualization shows for screen-reader users.
- The detail panel is a `role="dialog"` with `aria-modal` and a labelled heading.
- Tooltips stay inside the viewport (flip near the right/bottom edges rather than clipping).
- Visible focus ring on focused elements.

### 6. Semantic signal colors
- Same convention as the components: green healthy/rising, **yellow neutral/average (never "concern")**, red at-risk/declining, blue informational. Brand indigo `#4B53D4` for chrome and primary accents.
- Never color alone; pair every color with a label, a legend entry, or a shape treatment (for example, a dashed hollow node for silent/emerging risk so it does not rely on color).

### 7. Numbers and robustness
- Round every displayed number (`Math.round`, `.toFixed(n)`, `toLocaleString()`); float math leaks artifacts.
- No console errors. Guard against missing fields (nullable `risk_level`, unknown labels) with sensible defaults.
- Legible node/element min and max sizes; never let a value collapse an element to invisibility or blow it up past its neighbors.

---

## The DATA-separated skeleton

A copy-ready shape. Keep `DATA` raw; keep scoring, layout, and render as stable functions the skill does not touch.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Staircase &lt;experience name&gt;</title>
<style>
  /* self-contained; system fonts only; transparent background */
  html,body{margin:0;background:transparent;}
  body{font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#1B1D2B;}
  .sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);}
  /* brand + semantic tokens: --brand #4B53D4; green/yellow/red/blue signal colors */
</style>
</head>
<body>
<h1 class="sr-only">One sentence describing what this visualization shows and how to read it.</h1>

<!-- app header, controls (toggles/legend), the visual, and a detail panel -->

<script>
/* ============ DATA: the skill repopulates ONLY this block per run ============ */
const DATA = [
  /* { raw signal fields per record; no precomputed positions or colors } */
];
const TODAY = new Date("2026-08-06T12:00:00");   /* run-scoped; the skill sets this */

/* ============ render logic below is stable across runs ============ */
// 1. scoring: pure functions of a record's raw fields
// 2. layout: map scores to geometry (with legible min/max, de-clumping)
// 3. draw: build DOM/SVG from DATA
// 4. interactions: hover tooltip (viewport-aware), click/Enter detail panel (ARIA),
//    Escape to close, focus management, a color/mode toggle, a legend
</script>
</body>
</html>
```

**How the skill repopulates it:** the workflow skill runs its Staircase queries, shapes each account into the record schema the experience expects, and rewrites the `DATA = [...]` block (and `TODAY`). It touches nothing else. Because scoring and render are pure functions of the raw fields, a fresh `DATA` block produces a correct, consistent visualization with no other edits.

---

## Worked example: the Risk Radar

`../../staircase-risk-radar/experiences/risk-radar.html`. Accounts on a polar plot; the riskiest and most urgent sit nearest the center.

**Record schema** (`DATA` element):
`{name, revenue, risk_level (number|null), renewal_date, health_label, health_score, engagement_label, sentiment_label, stakeholders_count, multi_threaded, dominant_lens, silent_risk}`.

**Composite scoring (pure functions of the record):**
- `sentiment_penalty`: Issues detected = 1.0, Negative = 0.85, Neutral = 0.5, Positive = 0.0.
- `engagement_penalty`: Low = 1.0, Average = 0.5, High = 0.0.
- `flagged` = risk_level present ? risk_level / 5 : 0.
- `risk_severity` = 0.35 x flagged + 0.25 x (1 - health_score/100) + 0.20 x sentiment_penalty + 0.20 x engagement_penalty, clamped 0..1.
- `renewal_urgency` from days-to-renewal: <30d = 1.0, <60 = 0.8, <90 = 0.6, <180 = 0.4, <365 = 0.2, else 0.1.
- `placement_radius` = 1 - (0.7 x risk_severity + 0.3 x renewal_urgency). Smaller is nearer the center. Mapped to pixels between an inner and outer margin.

**Visual encoding:**
- Radial position (radial-axis toggle): **Acuteness** = placement_radius (acute nearest center; bands labelled acute / elevated / watch), or **Renewal timing** = banded by fiscal quarter, derived from the run's as-of date and the org's fiscal calendar rather than hardcoded (this quarter / next quarter / within a year / beyond a year), soonest innermost. In renewal-timing mode radius no longer encodes severity, so severity moves to fill opacity (solid nodes) and ring weight (hollow nodes) so you still read "how acute" within a timing band.
- Node size: revenue (sqrt scale, legible min/max).
- Angle: dominant lens in five sectors (renewal, value, competitive, stakeholder, product); flagged-but-unclassified records go to a neutral sector, and silent-risk records get their own labelled "Emerging (silent)" sector. Sectors are labelled.
- Color: health label (green/yellow/red), with a toggle to color by dominant lens instead.
- Silent/emerging risk (`silent_risk: true`, no fired `risk_level`) gets a hollow, dashed treatment so the leading-indicator cohort reads distinctly from the flagged one.
- An ambient radar sweep line rotates slowly for radar-scope feel; it is `pointer-events: none` and gated by a `prefers-reduced-motion` media query.

**Views (view toggle):** a Radar / Table switch. The table lists every account, sortable by acuteness (severity desc) and renewal date (asc) via clickable headers, with account, revenue, renewal + days-out, state (Flagged / Silent), severity, dominant lens, health / sentiment / engagement signal pills, and stakeholders. A row click opens the same detail panel the nodes use.

**Interaction model:** hover or focus gives a compact tooltip (account, revenue, severity, renewal in N days); click or Enter opens a progressive-disclosure side panel (signals, coverage, a read-only recommended next move, and a blockers/evidence area the skill repopulates). Legend plus three toggles (view, radial axis, color) sit above; Escape closes the panel.

**Legibility note:** with many records in one sector, a light force simulation de-clumps nodes into the free radial space inside their wedge (or renewal band) while a spring keeps each near its true position, so the center-out ordering is preserved and nothing overlaps. In the banded renewal-timing mode the crowded bands (near-term and long-tail) are given more radial room than the sparse middle bands. Radial position stays the source of truth for the tooltip and severity; only crowded cells spread for readability.

---

## Cross-references

- **Components (the static path):** `component-library.md`
- **Rendering patterns and surface detection:** `patterns.md`
- **Content discipline:** `../../../_shared/staircase-output-best-practices.md`
- **First experience:** `../../staircase-risk-radar/experiences/risk-radar.html`

## Versioning

**v1.0 (2026-08-06).** New in the Staircase port. Codifies the self-contained interactive-experience standard (no network calls, transparent background, data separated from render, progressive disclosure, accessibility, semantic colors with yellow = neutral) and the static-vs-interactive heuristic. Grounded in the Risk Radar build.
