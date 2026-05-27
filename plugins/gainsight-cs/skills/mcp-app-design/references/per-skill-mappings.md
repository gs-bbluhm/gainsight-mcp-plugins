# Per-Skill App Design Mappings

For each user-facing skill in the plugin, this doc specifies the chrome (tabs, components, patterns) the skill should render. Skills look up their own mapping below and render accordingly.

This is the bridge between the design system (`patterns.md` + `component-library.md`) and the individual skills. The mappings here are **hardcoded** — the chrome doesn't adapt per-run; only the content within it does.

---

## How to read this doc

Working on a skill's output? Look up its mapping below. Each mapping tells you:

- **Brand** — color + icon for the colored app header (`component-library.md` §1)
- **Title** — short skill name for the header
- **Tabs** — which tabs, in what order, with what counts
- **Per-tab components** — which visual primitives go in each tab + key behavioral rules
- **Working mode picker** — present or not, default mode
- **Action tee-up pattern** — one-at-a-time vs batch vs briefing-grade
- **Sticky footer** — enabled or not
- **Preference questions** — where they typically surface
- **Approval card variant** — email / CTA / SP / Timeline / Slack

Then render. Content is adaptive; chrome is fixed.

---

## Brand palette

| Plugin | Brand color | Use |
|---|---|---|
| `gainsight-cs` | Gainsight orange `#FF7A00` | App header strip, primary CTAs, focused states |

All skills in `gainsight-cs` use the same brand color. Skill-specific identity comes from the **icon** in the colored header.

---

## gainsight-csm-book-pulse

**Brand:** gainsight orange · **Icon:** 📊 · **Title:** Book Pulse

**Tabs (4):**
| # | Tab | Count source |
|---|---|---|
| 1 | At a glance | — (no count) |
| 2 | Priorities | Top N priority accounts (default 8-10) |
| 3 | Active work | Open CTAs + Active SPs (excluding closed/done) |
| 4 | Briefing | Past-renewal + briefing notes total |

**Tab 1 components:**
- Colored app header
- 3+3 metric grid (signal stripes: Risk → red, EBRs → amber, Expansion → blue; others neutral)
- Amber `--warning` section callout for past-renewal observation (with action button)
- Primary CTA button → Tab 2

**Tab 2 components:**
- Working mode picker (full state on first visit, collapses to single line after selection)
- Ranked table (sortable with chevrons, signal-pill color tie-back, default sort = priority descending)
- `[ Show watch list (N) ]` expand button below table
- Drill-down card on row click (State + Stakeholders + Next Moves)
- Sticky pending-action footer (appears on first action approval)

**Tab 3 components:**
- Top-of-tab counts strip: `Open CTAs · N` `Active SPs · N` `Closed SPs (recent) · N` `Cleanup actions · N`
- Open CTAs section (each row with context callout where relevant, inline action button)
- Success Plans section (done-state badge for 100%-complete, primary button for active)
- Cleanup recommendations (each bullet has inline action button matching recommendation)

**Tab 4 components:**
- Past-renewal sub-grouped (`5 past · 2 borderline` style) — each account with `[ Check status ]` button
- Briefing notes with severity icons (⚠ concerning, ℹ structural) — each concerning note with `[ Investigate ]` button
- Optional "What's NOT here" section with contextual action buttons

**Working mode picker:** YES, default `One at a time (Recommended)`
**Action tee-up:** one-at-a-time (default mode) or batch (per mode selection)
**Sticky footer:** YES, appears once user approves first action
**Preference questions:** per-account approach (save-with-incentive / offboarding-first / multi-thread)
**Approval card variants:** email · CTA · SP · Timeline

---

## gainsight-account-workspace

**Brand:** gainsight orange · **Icon:** 🧭 · **Title:** Account Workspace

**Tabs (4):**
| # | Tab | Count source |
|---|---|---|
| 1 | Account state | — |
| 2 | Recommended actions | Proposed moves |
| 3 | Existing work | Open CTAs + Active SPs |
| 4 | Briefing | Relationship notes + signal observations |

**Tab 1 components:** colored header · account-stats metric grid · stakeholder map · recent activity timeline.
**Tab 2 components:** ranked list of proposed moves · drill-down on tap · sticky pending-action footer.
**Tab 3 components:** Open CTAs + Active SPs (same patterns as book-pulse Tab 3).
**Tab 4 components:** relationship state notes · risk + expansion summary.

**Working mode picker:** NO (single-account, doesn't need it)
**Action tee-up:** one-at-a-time
**Sticky footer:** YES
**Preference questions:** per-action approach
**Approval card variants:** email · CTA · SP · Timeline

---

## gainsight-meeting-processor

**Brand:** gainsight orange · **Icon:** 📞 · **Title:** Meeting Recap

**Tabs (5 — Review Packet structure):**
| # | Tab | Count source |
|---|---|---|
| 1 | Email recap | 1 (draft) |
| 2 | Timeline activity | 1 (draft) |
| 3 | CTAs | Risk CTA + any action-item CTAs |
| 4 | SP updates | Touched objectives |
| 5 | Wins | Captured advocacy quotes + Verified Outcomes |

**Per-tab components:** action proposal card for each artifact (one per tab, approve/edit/skip buttons).

**Working mode picker:** NO (sequential approval per artifact is the inherent flow)
**Action tee-up:** sequential per artifact
**Sticky footer:** YES, shows the queued artifact count + Review all
**Preference questions:** rare (per-artifact "approve / edit / skip" handles most branches)
**Approval card variants:** all 5 used (email · CTA · SP · Timeline · slack if applicable)

---

## gainsight-exec-renewal-radar

**Brand:** gainsight orange · **Icon:** 🎯 · **Title:** Renewal Radar

**Tabs (4):**
| # | Tab | Count source |
|---|---|---|
| 1 | Enterprise | Enterprise renewals in window |
| 2 | Mid-Market | MM renewals in window |
| 3 | SMB | SMB renewals in window |
| 4 | Themes + Resource Allocation | Cross-tier patterns |

**Per-tier tab components:** ranked top-5 table (sortable, signal-pill color tie-back) · per-account expandable drill-down · briefing-grade narrative summary.
**Themes tab components:** cross-account theme cards (with affected accounts + evidence) · resource allocation recommendations as cards.

**Working mode picker:** NO (briefing-grade, not a working surface)
**Action tee-up:** briefing-grade. Optional handoff CTAs to CSMs (action proposal cards if user explicitly requests writes).
**Sticky footer:** Optional — only if user starts queueing handoff CTAs
**Preference questions:** "Drill into a tier?" / "Drill into a theme?"
**Approval card variants:** CTA (for handoff CTAs to CSMs)

---

## gainsight-renewal-priority-planner

**Brand:** gainsight orange · **Icon:** 🗓 · **Title:** Renewal Planner

**Tabs (3):**
| # | Tab | Count source |
|---|---|---|
| 1 | Priorities | Top accounts by movability score |
| 2 | Per-account plans | Generated action plans |
| 3 | Open items | Active CTAs + SPs across the flight |

**Tab 1 components:** colored header · ranked table by movability score · drill-down with merge-classification narrative.
**Tab 2 components:** per-account plan card (action sequence + key talking points + commercial terms outline).
**Tab 3 components:** Open CTAs + Active SPs filtered to the renewal flight.

**Working mode picker:** YES, default `One at a time`
**Action tee-up:** one-at-a-time per account
**Sticky footer:** YES
**Preference questions:** classification-driven (save-with-incentive / save-then-expand / skeptical / expansion-as-save)
**Approval card variants:** CTA · SP · email

---

## gainsight-stakeholder-connect

**Brand:** gainsight orange · **Icon:** 🤝 · **Title:** Stakeholder Connect

**Tabs (3):**
| # | Tab | Count source |
|---|---|---|
| 1 | Stakeholder map | Identified stakeholders |
| 2 | Outreach drafts | Proposed messages |
| 3 | Notes | Relationship signals + recent touches |

**Tab 1 components:** stakeholder grid (chips with role + sentiment + last-touch).
**Tab 2 components:** per-stakeholder outreach action card with tone variant (warm / firm / exploratory).
**Tab 3 components:** relationship-state callouts + recent activity log.

**Working mode picker:** NO (typically one stakeholder at a time)
**Action tee-up:** per-stakeholder outreach card
**Sticky footer:** YES
**Preference questions:** tone choice per stakeholder (warm / firm / exploratory)
**Approval card variants:** email (Gmail send-to-drafts)

---

## gainsight-no-qbr-ebr-scheduler

**Brand:** gainsight orange · **Icon:** 📆 · **Title:** EBR Scheduler

**Tabs (2):**
| # | Tab | Count source |
|---|---|---|
| 1 | Accounts needing EBR | Past-due + due-soon |
| 2 | Scheduled | EBRs on calendar |

**Tab 1 components:** ranked list of accounts · per-account scheduling card with draft EBR-pitch email in Task description.
**Tab 2 components:** calendar list of confirmed EBRs · prep status per item.

**Working mode picker:** NO
**Action tee-up:** per-account scheduling card
**Sticky footer:** YES
**Preference questions:** EBR scope choice (full / mini / async)
**Approval card variants:** email (Gmail) · CTA (Lifecycle/EBR)

---

## gainsight-account-handoff-onboarding

**Brand:** gainsight orange · **Icon:** 🚀 · **Title:** Onboarding Plan

**Tabs (5 — Sequential SP build):**
| # | Tab | Count source |
|---|---|---|
| 1 | Discovery | Discovery sections completed |
| 2 | Validation | Validated vs new info |
| 3 | 90-day plan | Plan objectives drafted |
| 4 | Risks | Identified risks |
| 5 | Open items | Items needing customer input |

**Per-tab components:** sequential content cards, each surfacing in order as user progresses through onboarding workflow.

**Working mode picker:** NO (linear flow)
**Action tee-up:** sequential SP build, validated section-by-section
**Sticky footer:** YES (shows the SP being assembled)
**Preference questions:** validation per section ("Is this still right? Yes / No, adjust")
**Approval card variants:** SP (the canonical SP creation use case) · email (intro emails)

---

## gainsight-exec-pattern-hunter

**Brand:** gainsight orange · **Icon:** 🔍 · **Title:** Pattern Hunter

**Tabs (3):**
| # | Tab | Count source |
|---|---|---|
| 1 | Themes | Identified cross-account themes |
| 2 | Evidence | Source quotes + evidence IDs |
| 3 | Recommendations | Resource / play recommendations |

**Per-tab components:** theme cards · evidence grid · recommendation cards.

**Working mode picker:** NO (briefing-grade)
**Action tee-up:** briefing-grade
**Sticky footer:** NO (typically read-only)
**Preference questions:** "Drill into a theme?" / "Expand evidence for theme X?"
**Approval card variants:** rare — Slack message to team or CTA for follow-up

---

## gainsight-exec-churn-retrospective

**Brand:** gainsight orange · **Icon:** 🔁 · **Title:** Churn Retrospective

**Tabs (4):**
| # | Tab | Count source |
|---|---|---|
| 1 | Cohort | Churned accounts in window |
| 2 | Patterns | Identified patterns + theme rollups |
| 3 | Gaps | Churns without analysis |
| 4 | Recommendations | Process / play recommendations |

**Per-tab components:** ranked tables · theme cards · gap-finding callouts · recommendation cards.

**Working mode picker:** NO (briefing-grade)
**Action tee-up:** briefing-grade
**Sticky footer:** NO
**Preference questions:** "Drill into a pattern?" / "Expand cohort details?"
**Approval card variants:** rare — typically a Slack summary or doc export

---

## gainsight-mcp-setup

**Brand:** gainsight orange · **Icon:** (skip header — linear onboarding, not tabbed)
**Title:** (rendered as setup wizard, not a multi-tab app)

**Layout:** Sequential setup wizard. Each step is a single card:
- Who are you (name + email)
- What role (Executive / CSM / AM / Sales / Admin / Other)
- Filter field discovery (per role)
- Profile write confirmation
- Practice round (2-3 worked examples tailored to role)

**Working mode picker:** NO (single linear flow)
**Action tee-up:** sequential setup steps
**Sticky footer:** NO
**Preference questions:** role choice + filter field choice
**Approval card variants:** none (no Gainsight writes during setup; only profile write to local file)

This skill is the design system exception — the only one without the tabbed-app shell. Setup is inherently a wizard, not a dashboard.

---

## Adding a new skill

When you add a new user-facing skill to the plugin:

1. Pick a brand icon (semantic to the skill — see existing icons for inspiration)
2. Define tabs (3-5 max)
3. Map components per tab (use existing patterns where possible; if a new pattern is needed, add to `patterns.md` + `component-library.md` first)
4. Decide on working mode picker / sticky footer / approval flow
5. Add a mapping section here

Skills that don't render user-facing output (e.g., MCP foundation skills) don't need a mapping.

---

## Versioning

**v1.0 — 2026-05-26.** Initial mappings for 11 skills (10 with full app-shell, 1 setup wizard exception). Drawn from the codified patterns + the per-tab UX feedback from Layer 2 Cowork testing of Demo 1.

Subsequent iterations: as skills evolve (new tabs, refined components, additional preference questions), update the mapping here — the source of truth lives here, not in individual SKILL.md files.
