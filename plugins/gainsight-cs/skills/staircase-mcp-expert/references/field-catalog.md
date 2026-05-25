# Staircase MCP — Field Catalog

Every queryable field, validated against a real Staircase org. Use this as a lookup table before composing queries.

Organized: **Standard fields** → **Scores** → **ARR breakdown** → **Stakeholder/engagement** → **Custom team-member (org-bespoke)** → **AI analyses** → **Lifecycle events** → **Insights**.

---

## Standard Account Fields (consistent across Staircase orgs)

| Field | Queryable | Example values |
|---|---|---|
| Account name | Required | Free text (the customer's company name) |
| Tier | ✅ filter | Enterprise / Strategic / Mid-Market / SMB / Unguided |
| Revenue (ARR) | ✅ filter + sort | Number |
| Owner | ✅ filter — **STANDARD field** | Free-text name |
| Status | ✅ filter | Active / Churned / Prospect |
| Renewal date | ✅ filter + sort | Date |
| Contract start date | ✅ filter | Date |
| Churn date | ✅ filter (when populated) | Date |
| Journey phase | ✅ filter | Onboarding / Adoption / Renewal / etc. |
| CRM ID | ✅ filter | String |
| Staircase Account Page | URL field | Direct link to account |

## Health & Sentiment Scores (numeric)

| Field | Scale | Notes |
|---|---|---|
| Health score | 0-100 | Synthesized from all signals |
| Engagement score | 0-100 | Activity volume + diversity |
| Sentiment score | 0-100 | Tone analysis of communications |
| Open items score | 0-100 | Lower = more unresolved items (inverse signal) |
| Response time score | 0-100 | Customer response patterns |
| Risk level | 1-5 (portfolio query) / 0-10 (per-account `analyze_account`) | Different scales — do NOT assume they map |
| Expansion readiness level | 1-5 (portfolio query) / 0-10 (per-account `analyze_account`) | Different scales — do NOT assume they map |

**Scale-of-readiness clarification:** The portfolio query's 1-5 is categorical pipeline-stage. The per-account 0-10 is a continuous-ish maturity assessment. Document gap filed for DS.

## Multi-Product ARR Breakdown

`ST ARR`, `CS ARR`, `CC ARR`, `CE ARR`, `PX ARR` — per-product revenue split.

## Stakeholder & Engagement

| Field | Queryable | Notes |
|---|---|---|
| Multi threaded | ✅ filter | Boolean — opposite is single-threaded risk |
| Stakeholders count | ✅ filter | Number of named contacts |
| Last engagement | ✅ sort + filter | Timestamp |
| Last reach-out | ✅ sort + filter | Timestamp |
| Last touch DM (decision-maker) | ⚠️ limited via `ask` | Included in Risk Analysis stakeholder section |
| Last meeting date | Available in CSV exports | Surface via per-account analyze |
| Last DM meeting date | Available in CSV exports | Surface via per-account analyze |
| Next meeting date | Available in CSV exports | Surface via per-account analyze |
| Owner effort (hours) | ⚠️ available in exports, NOT reliable via `ask` | Filed for DS |

## CRM-Synced Custom Team-Member Fields (NAMES VARY PER ORG)

⭐ **Critical:** these are NOT standard Staircase fields. They're synced from the customer's CRM. **Field names and which roles exist differ in every org.**

The standard Staircase `Owner` field is universal. Beyond that, every other team-member field is org-bespoke. Possible names include `CSM`, `Account Manager`, `AM`, `Account Director`, `Renewal Owner`, `TAM`, `AE`, `SE`, `Customer Engineer`, `CS Lead`, or org-specific variants — never assume.

**Discovery procedure:**
1. Pull a sample account via `staircase_analyze_account` and inspect the "Internal account team" section — Staircase surfaces named team members with roles.
2. Ask: `"What custom team member fields exist on accounts in our Staircase org? List the field names and roles."`
3. Cross-check with Gainsight via `get_object_metadata("company")` (typically the source-of-truth for these fields).
4. Fall back to **Owner** (standard field) if uncertain.

For the productized lookup: `gainsight-mcp-setup` captures this field name into the user profile so sibling skills auto-apply the filter.

## AI Analyses (full structured outputs per account)

See `references/analyst-data-models.md` for full section structures.

| Analysis | Data model richness | Fires when |
|---|---|---|
| AI Hand-off Analysis | Rich — 11 sections | New account hand-off from sales to CS |
| AI Expansion Analysis | Rich — account header + per-opportunity drill-down | Expansion signals detected |
| AI Risk Analysis | Rich — risk reasons + playbook + stakeholders | Risk signals detected |
| AI Churn Analysis | Simpler — summary + issues + references | Verified churn (from Churn Notification) — doesn't always fire |
| AI Renewal Analysis | Simpler — summary + references | After a renewal completes |
| AI Summary | Narrative + references | Always available |

---

## Lifecycle Events (date-stamped per-account)

Each event is a date column on the account — either has a date (event detected) or null (no event).

| Event | What it signals | Validation status |
|---|---|---|
| Churn risk event | Predictive churn risk signal | ✅ single-criterion |
| Extremely negative message event | Detected escalation / frustration | ⚠️ may need retry |
| Churn notification event | Customer formally stated non-renewal | ✅ (powers Churn Analysis trigger) |
| Commercial discussion event | Pricing / contract activity | ✅ |
| Account personnel changes event | Stakeholder shift on customer side | ✅ |
| Internal personnel changes event | Stakeholder shift on the vendor side | ✅ |
| Renewal event | Renewal motion detected | ⚠️ may need retry |
| Highly positive message event | Customer-articulated positive value | ❌ may fail; report to your data team if so |
| Exec to exec connect event | Executive-level connection occurred | ✅ |
| EBR event | EBR scheduled / held | ⚠️ untested |
| Onboarding event | Onboarding milestone | ⚠️ untested |

---

## Insights (boolean flags on accounts)

Single-criterion queries against these return long lists reliably.

| Insight | Validation status | Notes |
|---|---|---|
| Account Dark | ✅ | No communication signal at all |
| No QBR | ✅ | Quarterly Business Review missing |
| No Reach Out | ✅ | No outbound from CSM |
| No Stakeholder Reach Out | ⚠️ variant | Similar surface |
| Stakeholder Title Change | ⚠️ may need retry | Internal change at customer |
| Stakeholder Roles Not Defined | ⚠️ may need retry | Staircase doesn't have roles tagged |
| Stakeholder Not Engaged | ⚠️ frequently fails — report to data team | CSV exports show flag IS populated |
| Account Responds Slower Than Usual | ⚠️ untested | Engagement decline signal |
| Positive Sentiment Trend | ⚠️ untested | |
| Negative Sentiment Trend | ⚠️ untested | |
| Account Personnel Changes | ✅ | Champion attrition surface |
| No Renewal Discussion | ❌ may return empty | Population varies per org |
| Upcoming Renewal | ⚠️ may need retry | |
| No Next Meeting Scheduled | ⚠️ untested | |
| Churn Notification | ⚠️ untested | |
| No Exec to Exec Connect | ⚠️ untested | Executive engagement gap |
| No Meetings with Account | ⚠️ untested | |
| **Single Threaded with Stakeholder** | ✅ | **Often portfolio-wide risk pattern — surfaces dozens-to-hundreds of accounts per org** |

The Single Threaded with Stakeholder flag is often a portfolio-wide risk surface — many orgs find hundreds of accounts relying on a single customer-side contact. Champion attrition risk at scale.

---

## What Staircase does NOT have (use Gainsight instead)

| Field | Use this MCP instead |
|---|---|
| Industry filter | Gainsight `industry__gc` |
| Open CTAs / Cockpit | Gainsight `fetch_cta_list` |
| Authoritative ARR / Renewal Date | Gainsight Company object |
| Time-window deltas ("what changed in 24h") | Gainsight time-bounded filters |
| Authoritative Churn / Renewal status | Gainsight `Status` field |

---

## Source

- Validated against real-org Staircase data
- CSV ground-truth cross-check via the Account Details export
