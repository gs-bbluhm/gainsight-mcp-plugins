# Staircase AI Analyst Agents — Data Models & Validated Queries

The Staircase MCP exposes six per-account AI analyst outputs. Three have rich structured data models with clickable per-section references (Handoff, Expansion, Risk). Three are simpler summary-and-references (Churn, Renewal, Account Summary). Use the queries below to pull each in full structure.

**Source data models:** Derived from actual Staircase UI exports of the analyst output PDFs.

---

## 1. AI Hand-off Analysis (most mature, richest structure)

Fires when a new account has handed off from sales to CS. Most mature analyst — clickable sections, per-section references.

### Section structure

| Section | What's in it |
|---|---|
| **Header** | "Detected on date" + Account + urgency badge (High/Medium/Low) |
| **High-level summary** | Why-they-acted-now narrative paragraph |
| **Main driver** | Category tag (Operational/Technical/Business/Financial) + urgency + 1-line description |
| **Goals** | List, each with: priority badge (Critical/High/Medium/Low), description, timeline constraint, owner |
| **Expected Outcomes** | Bulleted list |
| **Open Concerns** | List, each with status (Partial/Resolved/Unresolved) + resolution note |
| **Commitments Made** | List, each with: commitment text, timeline constraint, "Made by → Made to" (named) |
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
3. Goals — each with priority badge (Critical/High/Medium/Low), description, timeline constraint, owner
4. Expected outcomes (bulleted)
5. Open concerns — each with status (Partial / Resolved / Unresolved) and resolution note
6. Commitments made — each with timeline, made-by, made-to (named people)
7. Purchase context: Why They Bought (with category tags Business/Technical/Financial), Why They Chose Us, named decision makers, three differentiators
8. Onboarding readiness: blockers & pressures, gaps to fill, intake questions, integrations (with status), implementation context, change management
9. Hand-off actions — each with rationale and priority badge
10. Key stakeholders — name, role label, what they care about
Cite evidence IDs per section where applicable.")
```

---

## 2. AI Expansion Analysis (rich, opportunity-level drill-down)

Fires when expansion signals are detected. Has account-level header data AND per-opportunity drill-down with its own data model.

### Account-level header

| Field | Example |
|---|---|
| Status badge | Heating / Stable / Cooling |
| Readiness | X/5 (e.g., 4/5) |
| High-level summary | Multi-sentence narrative paragraph |
| **ARR potential** | low / moderate / high |
| **Products** | Named products (Gainsight CS, PX, Skilljar, Professional Services/TAM) |
| **Executive sponsor** | Paragraph naming sponsors + context |
| **Momentum context** | Paragraph |
| **Recent activity** | Last-14-days paragraph |
| **Timeline pressure points** | Paragraph |

### Per-Opportunity drill-down (each opportunity has all of these)

| Field | Example |
|---|---|
| Opportunity name | "Post-launch TAM support" |
| 1-line description | "Add dedicated TAM coverage after go-live..." |
| **Tags row** | Category (Services/Cross-sell/Upsell) · AI confidence (High/Medium/Low) · Budget (Pending/Unknown/Confirmed) · Technical (Validated/In Progress/Not Started) |
| Description paragraph | Why this opportunity is real |
| **Details** | Timeline · Decision maker · Competitors mentioned · Number of users/licenses mentioned |
| **Action plan** | Numbered list (3-4 steps) |
| **Questions to explore** | Bulleted list (3-4 questions) |
| References | Per-opportunity |

### Validated query

```
staircase_analyze_account(account_id, query="
Pull the AI Expansion Analysis for <Account> in full structure. Return:

ACCOUNT-LEVEL HEADER:
- Status (Heating / Stable / Cooling) + Readiness rating X/5
- High-level summary narrative
- ARR potential (low / moderate / high)
- Products (named — which products the expansion involves)
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

---

## 3. AI Risk Analysis (rich, per-risk drill-down)

Fires when risk signals are detected. Has account-level header + per-risk drill-down + playbook + stakeholders.

### Account-level header

| Field | Example |
|---|---|
| Status badge | Stable / Heating / Cooling |
| Risk level | X/5 (e.g., 4/5) |
| High-level summary | Multi-sentence narrative |
| **Products** | Named products at risk (e.g., "Gainsight CS; Customer Education (Northpass → Skilljar migration)") |

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
- **Timeline** — immediate / short-term / medium-term / long-term
- **Owner role** — CSM / Product / Account Executive / Executive

### Stakeholders (with engagement guidance)

For each named stakeholder:
- Name + Title
- **Sentiment badge** — Champion / Neutral / Detractor
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

## 4. AI Churn Analysis (simpler — summary + issues + references)

⚠️ **Important correction:** Churn Analysis fires when a **verified churn** is detected (typically from Churn Notification communications). It is **not the same as Churn Risk** — Churn Risk is forward-looking signal; Churn Analysis is retrospective on confirmed loss.

**Critical gap:** Churn Analysis doesn't always fire even when an account has churned. Need a mechanism to cross-compare Status=Churned accounts against accounts with Churn Analysis to find churned accounts that lack analysis.

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

```
Step 1: gainsight run_query on company where Status = 'Churned'
        → list of churned accounts (authoritative from Gainsight)
Step 2: staircase_ask("List my accounts that have an AI Churn Analysis available")
        → list of accounts with churn analysis (from Staircase)
Step 3: client-side set difference: Churned ∖ Has-Churn-Analysis
        → churned accounts that need manual review

Note: "WHEN they churned" can use Gainsight churn_date__gc, or fall back
to past-renewal-date as an indicator if churn_date is empty.
```

---

## 5. AI Renewal Analysis (simpler — fires AFTER renewal)

⚠️ **Important correction:** Renewal Analysis fires **after** a renewal has happened to summarize what occurred. It's retrospective, not a forward-looking renewal prep tool. (For pre-renewal planning, use the Risk Analysis + Expansion Analysis + the new `gainsight-renewal-priority-planner` skill.)

### Structure (simpler than the rich-data analysts)

| Field | Example |
|---|---|
| Header | "Detected on date" + Account |
| High-level summary | Paragraph on what happened at the renewal — outcome, key dynamics, terms, lessons |
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
'No Renewal Analysis found yet — this account has not been through a
renewal cycle in the analyzed period.'")
```

---

## 6. AI Summary (simplest — summary + references)

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

| Analyst | Has data model? | Per-section references? | Workshop use case |
|---|---|---|---|
| Hand-off Analysis | **Rich** (11 sections) | Yes (most mature) | New CSM onboarding — `gainsight-account-handoff-onboarding` |
| Expansion Analysis | **Rich** (header + per-opp drill-down) | Yes (per opportunity) | Expansion play prep — `staircase-expansion-scout` + `gainsight-renewal-priority-planner` |
| Risk Analysis | **Rich** (reasons + playbook + stakeholders) | Yes (per risk reason) | Save plays — `staircase-at-risk-renewals` + `gainsight-renewal-priority-planner` |
| Churn Analysis | Simple (summary + issues) | Yes (refs at bottom) | Churn retrospective — future `gainsight-churn-retrospective` skill |
| Renewal Analysis | Simple (summary) | Yes (refs at bottom) | Post-renewal learning — future `gainsight-renewal-learnings` skill |
| AI Summary | Simple (narrative) | Yes (refs at bottom) | Default account read — multiple skills |

## Source PDFs

Data models derived from Staircase UI exports of each analyst's output PDF. Run any analyst in your own org and download the PDF to compare against the structure documented above.
