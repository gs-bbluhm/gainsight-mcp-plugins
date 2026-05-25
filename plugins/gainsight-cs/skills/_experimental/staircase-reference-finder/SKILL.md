---
name: staircase-reference-finder
description: Find customer reference candidates for a target account or use case. Surfaces Pulse speakers, case study customers, testimonial recorders, and Advocacy program participants. Profile-similarity match via per-account enrichment workaround.
user_type: experimental
disable-model-invocation: true
---

# Staircase Reference Finder (v0.1 — exploratory)

## Discovery

**Auto-trigger phrases:**
- "find me a reference for [account]"
- "who can I use as a reference"
- "reference customer for [target]"
- "Pulse references"
- "advocacy candidates"

**Validation history:** Reference-pool query verified against real-org data (returns a portfolio-scale list of accounts with Pulse / case-study / testimonial activity + evidence IDs). Profile-similarity matching is a per-account enrichment workaround — Staircase MCP does not support industry filtering or cross-account profile-similarity natively. Currently flagged experimental — waiting on a portfolio-similarity primitive in Staircase.

**Optimized for:** Cowork (interactive cards + approval gates) and Code (markdown + structured prompts). Cowork is the primary optimization target.

## Foundation references

Read these BEFORE composing operations:

**User profile (if exists):**
- `~/.gainsight-mcp/user-profile.md` — name, role, filter field, filter value. Apply role-appropriate defaults + filter automatically. If profile doesn't exist, prompt user to run `gainsight-mcp-setup`.

**Foundation skills (for MCP mechanics):**
- `../staircase-mcp-expert/references/query-patterns.md` — validated phrasings + decompose-and-intersect
- `../staircase-mcp-expert/references/anti-patterns.md` — 15-cap clarification, OR not supported, determinism mitigations
- `../staircase-mcp-expert/references/field-catalog.md` — what's queryable

**Output discipline (for any customer-facing write):**
- `../../_shared/gainsight-output-best-practices.md` (v1.1)

---

Find customer references for a target account or use case. **This skill is exploratory** — Staircase MCP partially supports the use case today, and there's a filed feature request to make it robust. See `references/staircase-feature-request.md`.

## What works today

### Reference pool query (verified against real-org data)
```
staircase_ask("Which of my customers have publicly spoken about us
   or appeared as customer references in the last year — for example
   mentioned in case studies, conference speaker lists, or G2 reviews?")
```

Returns a portfolio-scale list with structured detail: which event, what kind of reference activity (video testimonial, case study, advocacy program participation), and evidence IDs.

### Per-account profile enrichment (for matching)
```
staircase_analyze_account(account_id, query="
   For reference-matching: what industry is <Account> in (inferred from
   communications), how long have they been a customer, what products are
   they using, what are their primary use cases, what is their implementation
   maturity (early / mid / mature / advanced), and what notable outcomes
   have they discussed?")
```

This works per-account but is **slow at portfolio scale** (one MCP call per candidate).

## What doesn't work today

❌ **Industry filtering** in `ask` — Staircase confirmed "filtering by industry is not supported in the customer metadata."
❌ **Cross-account profile similarity** in `ask` — returns a "can't answer from the provided information" response; the available context is the questioner's own account snapshot, not other customer details.
❌ **Combined filters** (industry + size + use case + maturity) — same combined-criteria pattern that breaks at-risk-renewals when over-specified.

## Skill flow (current, with workaround)

### Step 1: Define the target

Either:
- **Mode A — Target account:** "Find references for <account>" → enrich the target via `staircase_analyze_account` to extract its industry, size, use cases, maturity.
- **Mode B — Use case:** "Find references for SaaS companies using our platform for renewal risk" → user provides the profile directly.

### Step 2: Pull the reference pool

Run the reference-pool query above. Parse into a list of {account_name, activity_type, evidence_id}.

### Step 3: Enrich each candidate (in batches of 3 parallel)

For each candidate in the pool, run the per-account profile enrichment query. Cap at the top 10 candidates to keep runtime bounded.

### Step 4: Match client-side

Score each candidate against the target profile:
- Industry match (binary if same; partial if adjacent)
- Size match (within 0.5x – 2x target ARR or stated proxy)
- Product match (same products in use)
- Use case match (shared use cases mentioned)
- Maturity match (similar implementation maturity)

Produce a ranked list with match rationale per candidate.

### Step 5: Produce the report

```
# Reference Candidates — <target account or profile>

**Target profile:** <industry, size, products, use cases, maturity>
**Reference pool size:** <count>
**Top matches surfaced:** <count>

## Top Matches

| Rank | Account | Match score | Why this match | Advocacy activity |

## Match details (top 3-5)
### <Account>
- **Industry:** ... | **Size:** ... | **Products:** ... | **Maturity:** ...
- **Why this is a strong match:** <2-3 sentences>
- **Advocacy activity:** <e.g. "Recorded customer event testimonial, evidence comm_Email_...">
- **Suggested outreach:** <CSM-actionable next step>

## Outreach Plan
- Who to ask (named contact via Gainsight enrichment if available)
- Suggested first email or call open
- What to ask for (case study, intro call, reference call, panel speaker)
```

## Edge cases

| Situation | What to do |
|-----------|------------|
| Target account profile is thin in Staircase | Ask user to provide the profile directly (Mode B) |
| Reference pool query returns empty | Try alternate phrasings: "customers in our advocacy program", "customers who recorded a video testimonial", "customers who spoke at a customer event" |
| User wants more than 10 matches | Note runtime tradeoff; let them expand |

## Open Staircase product gap

The "reference matching" use case is constrained by Staircase MCP's lack of:
- Industry/segment metadata at the customer record
- Portfolio-wide profile-similarity query
- Reference-program structured field (rather than inferring from communications)

The full feature request lives at `references/staircase-feature-request.md`.

## Output Best Practices (when chaining into Gainsight writes)

This skill primarily READS from Staircase. If you chain into Gainsight writes (Opportunity/Activity CTAs to formalize reference-program candidates, Timeline activities sharing reference-pool findings), follow `plugins/gainsight-cs/_shared/gainsight-output-best-practices.md`. Key rules: user approval gate, commitment discipline (never auto-commit a customer to a reference call), HTML formatting, teammate-facing language, reuse-vs-create discipline, org-specific discovery.

---

## Learnings

See `.learnings.md`.
