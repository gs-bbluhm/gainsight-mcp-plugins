---
name: gainsight-account-handoff-onboarding
description: Build a first-90-days onboarding plan for a CSM inheriting an account. Scans Staircase for accounts with a Handoff Analysis, then synthesizes stakeholders, why-they-bought, goals, risks, and a week/30/90 action plan grounded in Gainsight.
user_type: ic
---

# Account Handoff Onboarding

## Discovery

**Auto-trigger phrases:**
- "I'm taking over [account]"
- "build me an onboarding plan for [account]"
- "new CSM brief for [account]"
- "scan my accounts with handoff analyses"
- "which accounts have handoffs"

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — Staircase query patterns
- `../staircase-mcp-expert/references/anti-patterns.md` — Staircase gotchas
- `../staircase-mcp-expert/references/analyst-data-models.md` — structured queries per analysis type (Handoff, Expansion, Risk, Churn, Renewal, Summary)
- `../gainsight-cs-mcp-expert/references/tool-inventory.md` — Gainsight CS tool reference
- `../gainsight-cs-mcp-expert/references/org-discovery.md` — Tier/Segment + team-member field discovery (org-bespoke)
- `../gainsight-cs-mcp-expert/references/write-path-patterns.md` — canonical CTA + Task + Timeline + SP recipes with HTML templates
- `../gainsight-cs-mcp-expert/references/anti-patterns.md` — gotchas, custom field requirements, HTML formatting

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md`

---

For the moment when a CSM inherits an account — by promotion, reorg, parental leave coverage, or normal team rotation. The skill turns Staircase's account intelligence + Gainsight's commercial context into a concrete first-90-days plan, so the new CSM walks in with a real point of view instead of starting from a cold company record.

**Two modes:**

1. **Scan** — "which of my accounts have handoff context available?" Returns the cross-portfolio list of accounts with Staircase Handoff Analyses (or sufficient 90-day communication data to synthesize one).
2. **Build** — for a chosen account, produce the onboarding plan: stakeholders, why they bought, current goals, recommended onboarding actions, readiness, risks, and a first-week / first-30-day / first-90-day action plan.

---

## Step 0: Determine mode

If the user says any of these, run **Scan** first:
- "which accounts have a handoff analysis"
- "scan my accounts with handoffs"
- "list accounts ready for handoff"
- vague: "I need to know what handoffs I can build"

If the user names a specific account (e.g., "build me an onboarding plan for <account>", "I'm taking over <account>"), skip Scan and go straight to **Build**.

---

## Step 1 (Scan mode): Cross-portfolio Handoff Query

Call `staircase_ask` with:

```
query="Which of my accounts have a Handoff Analysis available? List the account names, ARR if known, renewal date if known, and indicate handoff analysis date if available."
```

The MCP's open-ended Q&A surface handles this portfolio question even though `staircase_analyze_account` is single-account-scoped.

Present the results as a sortable table:

| # | Account | ARR | Renewal | Notes |
|---|---------|-----|---------|-------|

Ask: "Which account would you like to build the onboarding plan for?"

If the user names an account not in the list, fall back to Build mode and proceed — `analyze_account` can synthesize handoff sections from communications regardless of whether a formal Handoff Analysis document exists.

---

## Step 2 (Build mode): Resolve the account

Fan out:

```
A. staircase_account_lookup(name=<account>) → account_id
B. gainsight resolve_customer(search_name=<account>) → company GSID + relationships
```

If `resolve_customer` returns multiple companies, match against the Staircase-resolved name as tie-breaker. Ask if unclear.

---

## Step 3: Parallel context fan-out

Use the Handoff Analysis template. "Sales handoff" is a first-class AI insight field in Staircase; this query phrasing maps to that internal report type.

```
A. staircase_analyze_account(account_id, query="
   Build a Handoff Analysis for <Account>: account summary, why they
   bought, current goals, stakeholders (champions / decision makers /
   detractors), recommended onboarding actions, onboarding readiness
   assessment, top risks, top expansion opportunities, key context
   for a new CSM.")

B. gainsight fetch_cta_list — open CTAs (DueDate >= today-90d, IsClosed=false)
   ⚠️ Always include the DueDate filter — token budget guard.

C. gainsight fetch_success_plan_list — active success plans, with PercentComplete and OverdueCtas
   where: CompanyId EQ <gsid>

D. gainsight run_query on company object — pull ARR, RenewalDate, Stage,
   the org's team-member field (CSM Owner equivalent), Tier (any custom fields you know about)

E. Optional: pull last 3-5 customer-meeting recaps from your notes destination for tone calibration
```

---

## Step 4: Build the onboarding plan

Structure the output as an artifact + inline summary card. The artifact is the deliverable the new CSM uses on day one.

### Output structure

```
# Handoff Onboarding Plan — <Account>

**Renewal:** <date> · **ARR:** $<amount> · **Tier:** <tier> · **Stage:** <stage>
**Previous CSM:** <name> · **New CSM:** <name or TBD>
**Generated:** <date>

---

## 1. 60-Second Read

3-5 sentences. What does the new CSM need to know in one minute. Lead with the biggest risk + the biggest opportunity.

## 2. Why They Bought

Direct from Staircase synthesis. Original purchase rationale, problem they were solving, the bet they made.

## 3. Current Goals

| Goal | Owner | Status | Source |

## 4. Stakeholders

### Champions
- **Name** — Role, sentiment evidence, last activity
- ...

### Decision-Makers / Sponsors
- ...

### Detractors / Friction Points
- ...

### Recent Stakeholder Shifts (last 60 days)
- ...

## 5. Onboarding Readiness

**Assessment:** <High / Moderate / Fragile / Low>

<2-3 sentence justification>

## 6. Top Risks

Numbered, ranked by severity. Each with a 1-sentence mitigation.

## 7. Top Expansion Opportunities

Numbered, ranked by readiness.

## 8. What's Already in Gainsight

### Open CTAs (<count>)
| Subject | Type | Priority | Owner | Due |

### Active Success Plans (<count>)
| Plan | Owner | % Complete | Due | Open CTAs |

### Recent Activity Patterns
<2-3 sentences if Gainsight timeline is queryable; skip if not>

## 9. First-Week Action Plan

Concrete actions for the new CSM's first 5 working days. Mix of:
- Read these docs / pages
- Have these conversations (internal handoff with prior CSM, exec intro, etc.)
- Update these Gainsight records
- Set up these dashboards / saved views

## 10. First-30-Day Plan

What to accomplish by day 30. Stakeholder meetings, success-plan refresh, risk-CTA disposition, value-realization touch points.

## 11. First-90-Day Plan

What "good" looks like at day 90: relationship established, success plan current, risks dispositioned, first review with the customer landed.

## 12. Open Questions

Things Staircase + Gainsight can't answer. The new CSM should ask the outgoing CSM these on the live handoff call.
```

### Format adaptations

- **In Claude Cowork:** lead with a card showing the 60-second read + readiness badge. Tabs for stakeholders, goals, risks, action plan.
- **In Claude Code:** full markdown to stdout.

---

## Step 5: Confirm and offer follow-on actions

Ask the user if they want to:
- **Post a Timeline activity** to Gainsight summarizing the handoff (Activity Type: `Handover Call` or `Internal Note`)
- **Create a handoff CTA** for the new CSM (with the first-week actions as tasks)
- **Schedule the handoff conversation** (use Calendar MCP if available)
- **Save the plan** to your preferred notes destination under My Customers / <Account>

None of these happen without explicit approval.

---

## Edge cases

| Situation | What to do |
|-----------|------------|
| Staircase has no data for the account | Cannot build. Tell the user and offer to run the skill once communications start flowing. |
| `staircase_ask` portfolio query returns empty | Default to direct account name input — Build mode works even without scan |
| Account has multiple Gainsight companies (e.g., M&A, regional splits) | Show both, ask which to scope to |
| No active success plan in Gainsight | Note in section 8. First-30-day plan should include "create initial success plan" |
| 50+ open CTAs in Gainsight (backlog) | Surface top 10 by recency or priority. Flag the backlog as a "CTA hygiene" item in first-30-day plan. |
| Customer has multiple Staircase product relationships | Build the plan at Company level by default. Note the relationships for the CSM. |

---

## Reference files

- `references/handoff-sections.md` — Detailed prompt templates for each handoff section (in case `staircase_analyze_account` needs section-by-section follow-ups)
- `references/onboarding-action-templates.md` — Reusable first-week / first-30-day / first-90-day action patterns by customer tier and renewal timing

## Output Best Practices (Gainsight writes)

**This skill is the CANONICAL Success Plan creation case.** Follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`, especially the Success Plan methodology and Discovery CTA pattern. Core rules:

1. **User approval gate.** Present the SP plan: outcome goal + measurement + ≥3 CTA recommendations + named stakeholders. Get explicit user approval BEFORE creating the SP.
2. **Pre-create check.** `fetch_success_plan_list(company_id)` first. If an active SP exists with similar scope, UPDATE rather than create.
3. **≥3 CTAs threshold + clear outcome goal + measurable success criteria.** Don't create empty Success Plans (methodology violation). Create standalone CTAs instead.
4. **Adaptive Discovery CTA based on Staircase Handoff Analysis.** If Handoff Analysis exists for this account, the discovery is a VALIDATION SESSION (review pre-sales goals + commitments, fill gaps). If no Handoff Analysis, use the canonical 7 onboarding discovery questions.
5. **HTML formatting** in rich-text fields. No plain-text newlines.
6. **Teammate-facing, customer-focused content.** No internal classification labels in customer surfaces.
7. **Commitment discipline.** PROPOSAL language by default. Verify Before Sending on every Email Task.
8. **Org-specific discovery.** Discover org's SP Types and CTA Types via `prepare_*` calls. Don't hardcode.

### Skill-specific emphasis

The Discovery CTA is the FIRST CTA in any onboarding SP. Its Tasks carry 5-7 standardized discovery questions in their descriptions. When Staircase Handoff Analysis is available, the discovery questions adapt to validate what's already known and surface what's missing — saving the customer from re-answering pre-sales questions. This is the differentiator: a relationship-building first session, not a re-interview.

---

## Learnings

See `.learnings.md` for accumulated wins, misses, and refinements from real-account testing.
