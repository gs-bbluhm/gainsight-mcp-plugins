# Gainsight CS MCP — Org Discovery Procedure

Every customer Gainsight org names its fields differently. **Never assume** — always discover. This procedure runs once per new org (typically inside `gainsight-mcp-setup`) and gets cached for the session. Power users can run it manually too.

The discoveries you must complete BEFORE production use against any new org:

1. Segmentation / tier field (on `company`)
2. Team-member / assignment field (on `company`) — the "who owns this account" field
3. Required custom fields on `activity_timeline`
4. SP types (org-bespoke 5-25 types)
5. CTA types + reasons + priorities + statuses (org-bespoke)
6. Activity types (org-bespoke; some have required custom fields)

---

## 1. Segmentation / tier field discovery

**Why:** Almost every exec-grade and tier-stratified skill needs this. Without it, you fall back to ARR or some other proxy that misses the org's actual segmentation strategy.

**Procedure:**

```
get_object_metadata(object_name="company")
  → scan returned fields for picklist fields whose name smells like tier/segment

Common candidates by name:
  - Tier                  (used by some orgs verbatim)
  - Segment               (very common alternate)
  - CS_Segment__gc        (CS-team segment)
  - {Product}_Segment__gc (per-product variants)
  - Customer_Tier__gc     (org-bespoke)

Once you find a candidate field:
get_picklist_values(object_name="company", field_name="<chosen field>")
  → confirms allowed values

Typical value sets:
  - Enterprise / Strategic / Scale
  - High Touch / Mid Touch / Tech Touch
  - Tier 1 / Tier 2 / Tier 3
  - Org-bespoke

If multiple plausible candidates surface, ask the user which their team uses.
```

**Cache:** field name + allowed values. Sibling skills use this to filter exec-grade reads.

---

## 2. Team-member / assignment field discovery (THE user-filter field)

**Why:** This is THE field that resolves "my accounts" / "my book" into an actual query. Without it, every IC-tier skill is broken or requires user-typed filters every time.

**The hard rule:** Staircase exposes a standard `Owner` field that's universal across orgs. Custom team-member fields are org-bespoke — different orgs name this differently. Some use `CSM`, some use a custom `Account Manager` field, some use SFDC-sync `Account Owner`, some have an org-bespoke variant. Some orgs have multiple team-member fields (e.g., separate CSM and AM fields). Discover; do not assume.

**Procedure:**

```
get_object_metadata(object_name="company")
  → scan for LOOKUP fields (to gsuser) or STRING fields holding a person's name/email

Typical candidates:
  - Owner                          (standard, universal across orgs)
  - CSM                            (very common custom field)
  - Account_Manager__gc            (post-sale AM role)
  - AM                             (variant)
  - Renewal_Owner__gc              (when org separates renewals from CS)
  - Account_Owner__gc              (often SFDC-sync, sales-leaning)
  - Opportunity_Owner__gc          (sales-leaning, lives on opportunity but joins to company)
  - Primary_CSM__gc                (when org distinguishes primary vs secondary)
  - CS_Lead__gc                    (some orgs prefer "lead" terminology)
  - org-bespoke variants

Present candidates to the user. Let them pick the one that captures their assignment.

Once chosen, capture the filter value:
  - LOOKUP fields → user's GSID (resolved via resolve_user)
  - STRING fields → user's name string (resolved via resolve_user, exact-match by name)
```

**Filter value examples:**
```
filter_field = "CSM"
filter_value = "<CSM Name>"                                   # if STRING field
       OR
filter_value = "1P01...<user GSID>..."                        # if LOOKUP field, user's GSID
```

**Cache in user profile:** `~/.gainsight-mcp/user-profile.md` (location pending Cowork validation). Sibling IC-tier skills read this profile and apply the filter automatically.

**Edge cases:**
- **User has multiple roles** (e.g., CSM on some accounts, AM on others) → capture both fields. Profile supports `filter_field` as a list.
- **User is a leader** with no direct assignment → skip this discovery for them. Profile marks `filter_field = null`, scope works portfolio-wide.
- **Sales users** typically need both `Account Owner` and `Opportunity Owner` — capture both.

---

## 3. Required custom fields on Timeline activities

**Why:** Some orgs silently require a custom field (e.g., a `Status` STRING field with allowed values like Green / Yellow / Red / N/A - Internal Update) on every Timeline activity. First write attempt fails until you pass it. The tool description doesn't surface this requirement up front (filed as G3.1).

**Procedure:**

The fastest discovery is "fail, read the error, retry":

```
First call:
create_timeline_activity(company_id=..., activity_type=..., subject=..., content=..., date=...)

If it fails with:
  "Missing required custom fields: 'Status' (type: STRING, allowed values: ['Green', 'Yellow', 'Red', 'N/A - Internal Update'])"

Capture: field name + allowed values from the error message.

Retry:
create_timeline_activity(..., custom_field_values={"Status": "Yellow"})
```

**Pre-emptive discovery** (slower but cleaner):
```
get_object_metadata(object_name="activity_timeline")
  → scan for fields marked required=true that aren't standard
get_activity_types_config()
  → some activity types have type-specific required custom fields
```

**Cache:** session-level. Apply on all subsequent Timeline writes.

---

## 4. Success Plan types discovery

**Why:** SP types are highly org-specific. Orgs commonly carry 5-25 types. Picking the right one for the use case is workshop-grade work (G3.3).

**Procedure:**

```
manage_success_plan_actions(mode='prepare_sp')
  → returns list of SP types + statuses available

Typical types you'll see (names vary per org):
  - Renewal Success Plan
  - ROI / Value Realization variants (often per-product)
  - Onboarding variants
  - Customer Success Plan (generic catch-all)
  - Org-bespoke templates

Selection logic by use case:
  - Renewal motion → "Renewal Success Plan"
  - Adoption + value realization → product-specific ROI / value SP
  - New customer onboarding → org's onboarding SP
  - Cross-product expansion → look for an org-bespoke expansion SP type

If no obvious match, prefer the most generic ("Customer Success Plan" or equivalent).
```

**Cache:** the full SP type catalog for the session.

---

## 5. CTA types + reasons discovery

**Why:** Picking the wrong CTA type/reason makes the artifact harder to find later + breaks downstream reporting. The right reason is workshop-grade specificity.

**Procedure:**

```
manage_cockpit_actions(mode='prepare_cta')
  → returns ~19 CTA Type options
    Common types:
    - Risk                (most common for save plays)
    - Renewal Risk        (when explicit churn intent)
    - ROI Risk            (when value scrutiny is the core blocker)
    - Adoption Risk       (when usage / deployment is the core blocker)
    - Stakeholder Risk    (when champion departure or sponsor loss is the core blocker)
    - Activity            (positive momentum, e.g., expansion play)
    - Objective           (strategic outcome track)
    - EBR                 (business review touchpoint)
    - Lifecycle           (onboarding / handoff / renewal stages)
    - Competitor          (active competitive threat)
    - CSQL                (sales-qualified lead handoff)
    - Other               (catch-all; avoid when a better fit exists)

manage_cockpit_actions(mode='prepare_cta', type_id=<chosen>)
  → returns dependent picklists for that type:
    ~34 reasons, 4 priorities, 9 statuses, ~44 playbooks
```

**Reason-selection cheatsheet** (matched to merge classifications from output best practices):
- **Save-then-Expand** → Risk CTA + Renewal Risk reason; Opportunity CTA paired
- **Skeptical Read** → Risk CTA only; reason matches the dominant signal (Adoption Risk if deployment, ROI Risk if value, Stakeholder Risk if champion)
- **Expansion-as-Save** → Opportunity / Activity CTA + appropriate reason (e.g., Renewal Opportunity)

**Cache:** type + reason catalog for the session.

---

## 6. Activity types discovery

**Why:** Some activity types (EBR, Verified Outcome) have type-specific required custom fields. Surfacing them up front avoids the "fail then retry" pattern.

**Procedure:**

```
get_activity_types_config()
  → returns the org's full activity types + per-type custom fields

Common activity types:
  - Meeting                       (default for ambiguous)
  - Onboarding Call
  - Planning Call
  - Training Call
  - Executive Business Review     (rich required fields — Meeting Type, Risk Status, Exec Present)
  - Escalation Call
  - Renewal Call
  - Handover Call
  - Implementation Review
  - Internal Note                 (internal-only, no customer-facing rendering)
  - Update                        (for async product intel, etc.)
  - Verified Outcome              (requires Metric Type + Metric — proof of value)

Custom fields per activity type (examples — varies per org):
  - Status (common org requirement)                   → Green/Yellow/Red/N/A
  - Meeting Type, Risk Status, Trending               → on EBRs
  - Metric Type, Metric                               → on Verified Outcomes
  - Internal Attendees, External Attendees            → on most call types
  - Discussed Product                                 → on product engagement updates
```

**Cache:** session-level.

---

## Profile output (consumed by gainsight-mcp-setup)

After running this discovery for a new user/org, the resulting profile schema:

```yaml
# ~/.gainsight-mcp/user-profile.md (location pending Cowork validation)
user:
  name: "<Full Name>"
  email: "<work email>"
  user_id: "<Gainsight user GSID from resolve_user>"
  role: "CSM"                              # Executive | CSM | AM | Sales | Admin | Other

filter:
  field: "CSM"                             # the chosen team-member field on company
  value: "<CSM Name>"                      # name string OR GSID depending on field type
  field_type: "STRING"                     # or "LOOKUP"

org:
  segmentation_field: "<chosen segmentation field>"
  segmentation_values: ["High Touch", "Mid-Touch", "Tech Touch"]
  timeline_required_custom_fields:
    Status:
      type: "STRING"
      default: "Yellow"
      allowed: ["Green", "Yellow", "Red", "N/A - Internal Update"]
  sp_types: [...]                          # cached list from prepare_sp
  cta_types: [...]                         # cached list from prepare_cta
  activity_types: [...]                    # cached list from get_activity_types_config
```

Sibling skills read this profile and apply role-appropriate defaults + filters automatically. If profile doesn't exist, the sibling skill prompts the user to run `gainsight-mcp-setup`.

---

## Source

- `gainsight-mappings.md` (object map + field catalog)
- DS rec G3.1 (Timeline required custom fields), G3.3 (SP type org-specificity)
- Validated against real-org data
