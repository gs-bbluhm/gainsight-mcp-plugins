---
name: staircase-app-design
description: "Foundation skill for how the Staircase plugin renders output as an in-chat app, not a markdown dump. Codifies the deterministic chrome (colored header, metric cards, tabbed nav with counts, ranked tables with signal pills, drill-down cards, empty states) plus the interactive-experiences pattern for shipping rich self-contained HTML (the Risk Radar is the first). Read-only synthesis only, no writes. Sibling Staircase skills read this before producing any user-facing output."
user_type: foundation
---

# Staircase App Design

## What this skill is for

The Staircase plugin's output is the product. A CSM or CS leader reading a risk scan, a portfolio pulse, or a voice-of-customer roll-up needs an app: a colored header, metric cards, tabbed navigation, a sortable account table with signal pills, drill-down detail, and where the data earns it, an interactive experience they can explore. Not a 1,000-word markdown wall, which is the single biggest failure mode.

This skill defines two things:
1. **The deterministic chrome** (which components, in what order, per skill). The chrome is fixed for reliability; the content inside is adaptive per run.
2. **The interactive-experiences pattern** (new): how to ship a rich, self-contained interactive HTML app inside a skill. The `staircase-risk-radar` polar radar is the first.

**Hardcode chrome plus components for reliability. Adapt content for intelligence. Reach for an interactive experience when the data has structure a table hides.**

## This plugin is read-only

Staircase reads and synthesizes communication signals. It never writes to a system of record. There are no CTAs, no timeline writes, no cockpit actions, no approval gates for writes, because there are no writes. Every component here surfaces or explains; none of them commit anything. When a component recommends a next move, it renders that move as read-only, copy-ready text the user acts on in their own tools. Content discipline lives in `../../_shared/staircase-output-best-practices.md`.

## Brand

Staircase dashboards use a vivid indigo brand mark, deliberately deeper and more violet than a generic sky blue so the plugin reads as its own product.

- **Staircase primary:** `#4B53D4` (indigo). Header strip, brand mark, focused/active states, primary accents.
- **Logo motif:** three white ascending stair-bars in a solid indigo circle. It doubles as a metaphor for climbing out of risk. Use it as the app-header icon (an inline SVG of three rising bars); a simple ascending-bars glyph or a neutral chart glyph is an acceptable fallback where an image cannot render.
- **Signal colors** stay semantic and independent of the brand:
  - green = healthy / rising
  - **yellow = neutral / average (Staircase convention, never "concern")**
  - red = at-risk / declining
  - blue = informational
  Keep signal-blue lighter than the brand indigo so pills do not blend into the header.

## The architecture: chrome vs content

| Layer | What | Where it lives |
|---|---|---|
| **Chrome** | Which tabs / sections / components, in what order, per skill | `references/per-skill-mappings.md` |
| **Components** | Exact markup, behavior, structure of each visual primitive | `references/component-library.md` |
| **Interactive experiences** | How to build and ship a self-contained interactive HTML app | `references/interactive-experiences.md` |
| **Content** | The strings, data, framings, severity calls | Adaptive, generated per run in each skill |

Chrome decisions are deterministic: every Risk Radar run produces the same header, the same tab order, the same components. Content within is adaptive: metric values, table rows, drill-down state, and the interactive experience's `DATA` block come from live signals plus the agent's judgment.

## Reference library

| File | What's there | When to read |
|---|---|---|
| `references/patterns.md` | Rendering patterns and the surface-detection rule (Cowork app vs Code markdown). The "what to render and why" doc. Top-of-doc checklist is the pre-render gate. | Before producing any user-facing output. |
| `references/component-library.md` | Concrete HTML markup for the seven read/synthesis components. The "how to render" doc. | When you need the exact markup for a header, metric grid, table, drill-down, empty state. |
| `references/interactive-experiences.md` | How to build a rich self-contained interactive HTML app that ships inside a skill: the self-contained rules, data-separated-from-render, progressive disclosure, accessibility, and the when-to-use heuristic. | When a skill's data has structure a static table hides and you are considering an interactive view. |
| `references/per-skill-mappings.md` | For each Staircase skill: which header, tabs, components, and (where relevant) which interactive experience. | First thing you read when working on any sibling skill's output. |

## The methodology (per render)

1. **Detect the surface.** Cowork (app rendering) or Code/CLI (markdown)? See the detection rule in `patterns.md`. Cowork is the primary target; Code degrades to scannable markdown with the same section structure.
2. **Look up the skill's chrome** in `per-skill-mappings.md`. Which header, tabs, components, in what order. Do not improvise the chrome.
3. **Decide static vs interactive per section** using the heuristic below (full version in `interactive-experiences.md`).
4. **Generate content adaptively** from the skill's Staircase signals plus the user's scope.
5. **Render each component** using the markup in `component-library.md`, substituting placeholders with your content.
6. **Surface a clean, verifiable artifact.** Lead with the answer, cite evidence IDs, close on a concrete next step. No writes, ever. See `../../_shared/staircase-output-best-practices.md`.

## Interactive experiences (the maturing part)

Some Staircase reads are multi-dimensional in a way a table flattens. Churn risk, for example, is severity and renewal urgency and revenue and which lens is firing and health, all at once. A ranked table shows one sort order; a polar radar shows all of it in one glance. That is when a skill ships an **interactive experience**: a single self-contained HTML file living in the skill's `experiences/` folder, seeded with a `DATA` block the skill repopulates per run.

**The rules every Staircase interactive experience follows** (full detail and a copy-ready skeleton in `references/interactive-experiences.md`):

- **Single self-contained HTML file.** No external network calls: inline any library, or pin one well-known CDN and degrade gracefully if it fails to load. No web fonts that phone home (use a system font stack); no analytics; no data leaves the file. This is customer-shippable code.
- **Transparent background** so it embeds cleanly on whatever surface hosts it. Legible on light or dark.
- **Data separated from render.** A `const DATA = [...]` JSON block near the top, distinct from the render code. The skill rewrites only that block each run; the render logic is stable.
- **Progressive disclosure.** Hover gives a compact tooltip; click opens a detail panel. Never dump everything at once.
- **Accessible, and reflows on narrow widths.** Interactive elements are keyboard-reachable (`tabindex`, Enter/Space, Escape to close), carry ARIA labels, and the file opens with a visually-hidden summary for screen readers. Tooltips stay inside the viewport.
- **Semantic signal colors**, same convention as the components: green healthy/rising, **yellow neutral (never "concern")**, red at-risk/declining, blue informational. Never color alone; pair with a label.
- **Round every displayed number.** Float math leaks artifacts.

### When to render an interactive experience vs a static table

Default to the component library (static table plus cards). Reach for an interactive experience only when the data earns it.

| Render a static table/component when | Render an interactive experience when |
|---|---|
| The answer is a ranked list to scan and act on top-down | Two or more dimensions matter at the same time (e.g. severity x urgency x revenue x lens) |
| N is small (a handful of rows) | N is a wall as a table but plottable (~10 to ~150 records) |
| The user will copy or share the output as text | Spatial or relational structure reveals a pattern a single sort order hides |
| The surface is Code/CLI | The surface is Cowork/visual and exploration (hover, filter, toggle) adds real understanding |
| One clear sort answers the question | The user needs to compare, cluster, or spot outliers |

When in doubt, ship the table. An interactive experience that does not add a dimension over a table is just slower to read.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Markdown wall in Cowork | The number-one failure mode: prose where components exist. |
| Improvising tabs/components per run | Breaks the app-feel; each run looks different. |
| Treating yellow as "concern" | Yellow is neutral/average in Staircase. Miscoloring erodes trust in the signal system. |
| An interactive experience that phones home | External fonts, CDNs without fallback, or analytics break the self-contained, customer-shippable guarantee. |
| Interactive when a table would do | If the visual does not add a dimension over a sorted table, it is friction, not insight. |
| A "next move" that implies a write | This plugin is read-only. Recommendations render as copy-ready text, never as a button that commits. |
| Color alone conveying meaning | Always pair color with a label or icon (accessibility). |

## Cross-references

- **Content discipline:** `../../_shared/staircase-output-best-practices.md` (scope, evidence, draft-do-not-send, no writes).
- **Query mechanics:** `../staircase-mcp-expert/` (what to render; this skill is how it reads).
- **First interactive experience:** `../staircase-risk-radar/experiences/risk-radar.html`.
