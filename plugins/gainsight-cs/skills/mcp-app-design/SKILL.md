---
name: mcp-app-design
description: Foundation skill for MCP App design. Codifies how this plugin's skills render output as an app (not a markdown dump) — colored headers, tabs, sortable tables, action tee-up cards, approval gates, sticky footers. Skills read this before producing any user-facing Cowork output.
user_type: foundation
---

# MCP App Design

## What this skill is for

This plugin's output is the product. Whether you're surfacing a CSM's book pulse, briefing an exec on portfolio risk, or running a meeting recap, the user experience is as critical as the data behind it. This skill codifies the design system: visual primitives, rendering patterns, and per-skill chrome mappings that decide which components each skill uses.

The premise: making AI workflows intuitive for non-AI-proficient users — CSMs, account managers, leaders — depends on rendering output that feels like an app, not a markdown dump. Cowork has the interactive primitives (cards, tabs, buttons, inline choices, approval gates). This skill is how the plugin uses them consistently.

## When to invoke

Foundation skill — usually not invoked directly. Sibling skills read it before producing user-facing output.

**Direct invocation triggers:**
- "How should `<skill>` render its output?"
- "What's the design system pattern for `<component>`?"
- "Show me the design system."
- "What tabs / components / approval pattern does `<skill>` use?"

**Sibling-skill reference triggers** (every skill that produces user-facing Cowork output reads this):
- `gainsight-csm-book-pulse`, `gainsight-account-workspace`, `gainsight-meeting-processor` — IC operational skills
- `gainsight-exec-renewal-radar`, `gainsight-exec-pattern-hunter`, `gainsight-exec-churn-retrospective`, `gainsight-renewal-priority-planner` — Exec briefing skills
- `gainsight-stakeholder-connect`, `gainsight-no-qbr-ebr-scheduler`, `gainsight-account-handoff-onboarding` — IC action skills

## The architecture — chrome vs content

This skill hardcodes two layers. The third stays adaptive:

| Layer | What | Where it lives |
|---|---|---|
| **1. Chrome** | Which tabs, which components, in what order, per skill | `references/per-skill-mappings.md` |
| **2. Components** | Exact markup, behavior, structure of each visual primitive | `references/component-library.md` |
| **3. Content** | The strings, data, framings, severity calls | Adaptive — generated per-run in each skill |

Chrome decisions are deterministic (every Book Pulse run produces the same 4 tabs in the same order with the same components). Content within is adaptive (metric values, table rows, drill-down state come from live data + the agent's judgment).

This is the boundary. **Hardcode chrome + components for reliability. Adapt content for intelligence.**

The first Demo 1 Cowork run is the proof that "optimize on the fly" doesn't bind — the agent had instructions but no enforcement and defaulted to a 1000-word markdown wall. Hardcoded chrome was the fix.

## Reference library

| File | What's there | When to read |
|---|---|---|
| `references/patterns.md` | Canonical rendering patterns (14 sections). The "WHAT to render and WHY" doc. | Before producing any user-facing output. Top-of-doc checklist is mandatory pre-render. |
| `references/component-library.md` | Concrete HTML markup for each visual primitive (12 components). The "HOW to render" doc. | When you need the exact markup for a header, metric grid, drill-down, action card, sticky footer, etc. |
| `references/per-skill-mappings.md` | For each skill in the plugin: which tabs, which components, which patterns, which mode picker, which approval flow. The bridge between this skill and the rest. | First thing you read when working on any sibling skill's output. |

## The methodology

Step-by-step when a sibling skill needs to render output:

1. **Detect surface.** Cowork (app rendering) or Code (CLI markdown)? See `patterns.md` mode-detection section.
2. **Look up your skill's chrome mapping** in `per-skill-mappings.md`. This tells you which tabs / components / patterns to use. Don't improvise.
3. **Generate content adaptively** from your skill's data + the user's situation.
4. **Render each component** using the markup in `component-library.md`. Substitute placeholder values with your content.
5. **Surface to the user.** Approval gates per `_shared/gainsight-output-best-practices.md` (the sister content-discipline doc).

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Skipping the chrome mapping and improvising tabs/components per run | Inconsistency breaks app-feel; each run looks different |
| Hardcoding the content (e.g., template strings that don't adapt to data) | Templates look forced when the data is thin or off-shape |
| Markdown walls in Cowork | The single biggest failure mode — the agent drifts to prose when it should use components. See `patterns.md` §12. |
| No approval gate before any external write | Violates the output discipline. See `_shared/gainsight-output-best-practices.md`. |
| Treating the design system as suggestions | The chrome IS the app. If a skill renders without it, the user gets a chat, not an app. |

## Cross-references

- **Sister content-discipline doc:** `../../_shared/gainsight-output-best-practices.md` — the "what to write" doc (CTA structure, Task content, Timeline format, write-gate checklist). This skill is the WHAT, that doc is the HOW-it-reads.
- **MCP foundation skills:** `../staircase-mcp-expert/` + `../gainsight-cs-mcp-expert/` — query + write discipline for the underlying MCPs. Reads + writes flow through those; rendering flows through this one.

## Versioning

**v1.0 — 2026-05-26.** Initial codification, extracted from Layer 2 Cowork testing of Demo 1 (CSM Book Pulse on Hannah Lee). The wall-of-text failure mode triggered the patterns doc; Brady's per-tab UX feedback drove the polish pass + component library; the strategic call to position this as the plugin's "MCP App design system" elevated it to a foundation skill.

Subsequent iterations: as Cowork ships new primitives, add components. When a pattern matures into a standard or proves not to work in actual Cowork rendering, update or deprecate (don't delete — historical reasoning survives).
