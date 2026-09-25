# Staircase AI Analyst Agents: Data Models & Validated Queries

The Staircase MCP exposes six per-account AI analyst outputs. Three have rich structured data models with per-section references (Handoff, Expansion, Risk). Three are simpler summary-and-references (Churn, Renewal, Account Summary). The templates below prompt `staircase_analyze_account` to return each in full structure.

## Contents
- Read first: which path gives you what
- 1. Handoff Analysis
- 2. Expansion Analysis
- 3. Risk Analysis
- 4. Churn Analysis
- 5. Renewal Analysis
- 6. AI Summary
- Quick comparison

**Source data models:** derived from the analyst outputs as the Staircase UI renders them. These are the target structures.

> ## Read first: which path gives you what (R4)
> The rich structures below are stored objects the Staircase UI renders; most of their detail is not exposed as structured report fields. Use the deterministic path wherever one exists, and the templates only for what's left:
>
> | You need | Deterministic path | Otherwise |
> |---|---|---|
> | Risk level, health, renewal, revenue, next QBR | Report fields (`book.context`) | |
> | Per-opportunity expansion detail (category, momentum, confidence, decision maker, budget, technical status, timeline, competitors, user count) | The `expansion_opportunity` entity (`expansion.pipeline`) | |
> | A meeting's issues and action items | `staircase_list_communications` on the account's lifecycle events (`lifecycle.evidence`) | |
> | Churn reasons | `customer.churn.issues` and `customer.churn.synopsis` | |
> | Risk reasons, playbook, stakeholder stance; handoff goals and commitments | | Prompt `staircase_analyze_account` with the templates below |
>
> `staircase_analyze_account` re-derives its answer each time, so it is approximate: the same prompt can return a different number of reasons or stakeholders. Treat its output as narrative, ground every item in a fetched evidence id (`staircase_fetch_evidence`), and never rely on exact counts or completeness.

---

## 1. AI Hand-off Analysis (most mature, richest structure)

Fires when a new account has handed off from sales to CS. Most mature analyst, clickable sections, per-section references.

### Section structure

| Section | What's in it |
|---|---|
| **Header** | "Detected on date" + Account + urgency badge (High/Medium/Low) |
| **High-level summary** | Why-they-acted-now narrative paragraph |
| **Main driver** | Category tag (Operational/Technical/Business/Financial) + urgency + 1-line description |
| **Goals** | List, each with: priority badge (Critical/High/Medium/Low), description, timeline constraint, owner |
| **Expected Outcomes** | Bulleted list |
| **Open Concerns** | List, each with status (Partial/Resolved/Unresolved) + resolution note |
| **Commitments Made** | List, each with: commitment text, timeline constraint, "Made by then Made to" (named) |
| **Purchase Context** | Why They Bought (with Business/Technical/Financial category tags), Why They Chose Us (paragraph + Decision makers + Differentiator 1/2/3) |
| **Onboarding Readiness** | Blockers & Pressures, Gaps to Fill, Intake Questions, Integrations (with status badges), Implementation Context, Change Management |
| **Hand-off Actions** | List, each with: action, rationale, priority badge |
| **Key Stakeholders** | List, each with: name, role label (e.g., "project lead/champion", "economic buyer/signatory"), bulleted stake items |

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Hand-off Analysis for <Account> in full structure. Return:
1. High-level summary (why they acted now, narrative)
2. Main driver (category tag + urgency + description)
3. Goals, each with priority badge (Critical/High/Medium/Low), description, timeline constraint, owner
4. Expected outcomes (bulleted)
5. Open concerns, each with status (Partial / Resolved / Unresolved) and resolution note
6. Commitments made, each with timeline, made-by, made-to (named people)
7. Purchase context: Why They Bought (with category tags Business/Technical/Financial), Why They Chose Us, named decision makers, three differentiators
8. Onboarding readiness: blockers & pressures, gaps to fill, intake questions, integrations (with status), implementation context, change management
9. Hand-off actions, each with rationale and priority badge
10. Key stakeholders: name, role label, what they care about
Cite evidence IDs per section where applicable.")
```

---

## 2. AI Expansion Analysis (rich, opportunity-level drill-down)

Fires when expansion signals are detected. Has account-level header data AND per-opportunity drill-down with its own data model. **Get the per-opportunity drill-down from the `expansion_opportunity` entity** (deterministic, one row per opportunity); use the template below for the account-level narrative and for action plans and questions to explore.

### Account-level header

| Field | Example |
|---|---|
| Status badge | Heating / Steady / Cooling |
| Readiness | X/5 (e.g., 4/5) |
| High-level summary | Multi-sentence narrative paragraph |
| **ARR potential** | low / moderate / high (a directional signal from communications, not a CRM dollar figure) |
| **Products** | Named products |
| **Executive sponsor** | Paragraph naming sponsors + context |
| **Momentum context** | Paragraph |
| **Recent activity** | Last-14-days paragraph |
| **Timeline pressure points** | Paragraph |

### Per-Opportunity drill-down (each opportunity has all of these)

| Field | Example |
|---|---|
| Opportunity name | "Post-launch TAM support" |
| 1-line description | "Add dedicated TAM coverage after go-live..." |
| **Tags row** | Category (Services/Cross-sell/Upsell), AI confidence (High/Medium/Low), Budget (Pending/Unknown/Confirmed), Technical (Validated/In Progress/Not Started) |
| Description paragraph | Why this opportunity is real |
| **Details** | Timeline, Decision maker, Competitors mentioned, Number of users/licenses mentioned |
| **Action plan** | Numbered list (3-4 steps) |
| **Questions to explore** | Bulleted list (3-4 questions) |
| References | Per-opportunity |

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Expansion Analysis for <Account> in full structure. Return:

ACCOUNT-LEVEL HEADER:
- Status (Heating / Steady / Cooling) + Readiness rating X/5
- High-level summary narrative
- ARR potential (low / moderate / high)
- Products (named, which products the expansion involves)
- Executive sponsor (named + context)
- Momentum context
- Recent activity (last 14 days)
- Timeline pressure points

PER-OPPORTUNITY DRILL-DOWN (for each named opportunity):
- Opportunity name + 1-line description
- Category (Services / Cross-sell / Upsell)
- AI confidence (High / Medium / Low)
- Budget status (Pending / Unknown / Confirmed)
- Technical status (Validated / In Progress / Not Started)
- Description paragraph (why this opportunity is real)
- Details: timeline, decision maker (named), competitors mentioned (if any), number of users/licenses (if mentioned)
- Action plan: numbered 3-4 steps
- Questions to explore: 3-4 bulleted questions
- Evidence IDs supporting the opportunity

Cite evidence IDs per opportunity.")
```

Note: ARR potential here is a directional read from the communications (low / moderate / high), not a dollar figure. The authoritative expansion dollar value lives in your CRM.

---

## 3. AI Risk Analysis (rich, per-risk drill-down)

Fires when risk signals are detected. Has account-level header + per-risk drill-down + playbook + stakeholders.

### Account-level header

| Field | Example |
|---|---|
| Status badge | Stable / Heating / Cooling |
| Risk level | X/5 (e.g., 4/5) |
| High-level summary | Multi-sentence narrative |
| **Products** | Named products at risk (e.g., "Core platform; an in-flight migration from one tool to another") |

### Risk Reasons (each with its own structure)

| Field | Example |
|---|---|
| Risk title | "Core BU adoption remains low; measurable wins still needed" |
| **Signal type tags** | "Low usage, training gaps, change resistance" |
| **Timeline urgency** | "Measurable wins needed within Q2 2026" (when applicable) |
| **Severity** | High / Medium / Low |
| References | Per risk reason |

### Playbook

List of recommended actions, each with:
- Action description (paragraph)
- **Timeline**: immediate / short-term / medium-term / long-term
- **Owner role**: CSM / Product / Account Executive / Executive

### Stakeholders (with engagement guidance)

For each named stakeholder:
- Name + Title
- **Sentiment badge**: Champion / Neutral / Detractor
- Recommended approach paragraph (how to engage them given the risk)

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Risk Analysis for <Account> in full structure. Return:

ACCOUNT-LEVEL HEADER:
- Status (Stable / Heating / Cooling) + Risk level X/5
- High-level summary narrative
- Products at risk (named, including any specific product workstreams)

RISK REASONS (for each):
- Risk title (specific, not generic)
- Signal type tags (e.g. 'Low usage, training gaps', 'Contract disputes')
- Timeline urgency (when applicable)
- Severity (High / Medium / Low)
- Evidence IDs per risk reason

PLAYBOOK (recommended actions):
- For each action: description paragraph
- Timeline (immediate / short-term / medium-term / long-term)
- Owner role (CSM / Product / Account Executive / Executive)

STAKEHOLDERS (with engagement guidance):
- Name + Title
- Sentiment (Champion / Neutral / Detractor)
- Recommended approach for this stakeholder given the risk

Cite evidence IDs per risk reason.")
```

---

## 4. AI Churn Analysis (simpler, summary + issues + references)

**Important correction:** Churn Analysis fires when a **verified churn** is detected (typically from Churn Notification communications). It is **not the same as Churn Risk**. Churn Risk is forward-looking signal; Churn Analysis is retrospective on confirmed loss.

**Critical gap:** Churn Analysis does not always fire even when an account has churned. To find churned accounts that lack analysis, cross-compare your CRM's `Status = Churned` list against the accounts that have a Churn Analysis in Staircase.

### Structure (simpler than the rich-data analysts)

| Field | Example |
|---|---|
| Header | "Detected on date" + Account |
| High-level summary | Paragraph with ARR impact, primary drivers, mitigation attempts, outcome |
| **Issues** | Bulleted list of specific problems |
| **References** | Evidence IDs (calendar / email / ticket icons) |

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Churn Analysis for <Account> (only fires if a verified churn
was detected from communications). Return:
- Detected date
- High-level summary: ARR impact if known, primary churn drivers, mitigation
  efforts attempted, final outcome
- Issues: bulleted list of specific problems that led to churn
- Supporting evidence IDs

If no Churn Analysis exists for this account, respond explicitly:
'No Churn Analysis found' and offer to retrieve Churn Risk signals instead.")
```

### Cross-account: detecting churned accounts that lack Churn Analysis

One report does it: root `customer`, filter `customer.status In ["Churned"]` plus `customer.churn.issues NotDefined`, columns account id, name, tier, revenue, renewal date. Those are the churned accounts with no churn analysis, the ones that need a manual read. A pair of scalar COUNTs (with and without `customer.churn.issues Defined`) gives the coverage rate to state alongside any churn-reason percentages.

When they churned comes from `customer.churn.churn_date`; if it's empty, the past renewal date is the fallback indicator (say so).

---

## 5. AI Renewal Analysis (simpler, fires AFTER renewal)

**Important correction:** Renewal Analysis fires **after** a renewal has happened to summarize what occurred. It is retrospective, not a forward-looking renewal prep tool. (For pre-renewal planning, use the Risk Analysis + Expansion Analysis, and pull the authoritative renewal date from your CRM.)

### Structure (simpler than the rich-data analysts)

| Field | Example |
|---|---|
| Header | "Detected on date" + Account |
| High-level summary | Paragraph on what happened at the renewal: outcome, key dynamics, terms, lessons |
| **References** | Many evidence IDs supporting the summary |

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Renewal Analysis for <Account> (fires after a renewal has
completed). Return:
- Detected date
- High-level summary of the renewal: outcome (renewed flat / upsell /
  downsell / churn), key dynamics that drove the result, terms,
  lessons learned, named stakeholders
- Supporting evidence IDs

If no Renewal Analysis exists for this account, respond:
'No Renewal Analysis found yet, this account has not been through a
renewal cycle in the analyzed period.'")
```

---

## 6. AI Summary (simplest, summary + references)

The catch-all narrative summary. Less structured than the four rich analysts.

### Structure

| Field | Example |
|---|---|
| High-level summary | Multi-paragraph narrative across health, sentiment, themes |
| References | Evidence IDs |

### Validated query

```
staircase_analyze_account(account_id, query="
Generate the AI Summary for <Account>: company overview, current state,
top 3 themes from the last 60 days, key relationships, commercial position,
most important context. Cite evidence IDs.")
```

---

## Quick Comparison

| Analyst | Has data model? | Per-section references? | Plugin use case |
|---|---|---|---|
| Hand-off Analysis | **Rich** (11 sections) | Yes (most mature) | New CSM onboarding: `staircase-account-handoff` |
| Expansion Analysis | **Rich** (header + per-opp drill-down) | Yes (per opportunity) | Expansion play prep: `staircase-expansion-scout` |
| Risk Analysis | **Rich** (reasons + playbook + stakeholders) | Yes (per risk reason) | Save plays: `staircase-risk-check`, `staircase-risk-radar`, `staircase-renewal-watchlist` |
| Churn Analysis | Simple (summary + issues) | Yes (refs at bottom) | Churn retrospective: `staircase-churn-review` |
| Renewal Analysis | Simple (summary) | Yes (refs at bottom) | Post-renewal learning |
| AI Summary | Simple (narrative) | Yes (refs at bottom) | Default account read: `staircase-account-deep-dive`, `staircase-meeting-prep` |

## Source PDFs

Data models derived from Staircase UI exports of each analyst's output PDF. Run any analyst in your own org and download the PDF to compare against the structure documented above.
