# Feature Request — Reference & Profile-Match MCP Capability

**Source:** `staircase-reference-finder` exploratory build
**Priority recommendation:** P2 — Useful (not blocking)

---

## Problem

When a CSM or AE needs a reference customer to support a sales conversation, expansion play, or renewal save, they need to find a customer who is:

1. Similar in **industry, size, use case, and implementation maturity** to the target account
2. **Actively willing** to participate as a reference (case study, intro call, customer event speaker, panel)

Today the Staircase MCP cannot do this end-to-end. The user has to either rely on tribal knowledge (the CSM's memory) or run dozens of per-account queries and join the results client-side.

---

## Current state (verified against real-org data via `staircase-reference-finder` build)

### What works
- `staircase_ask` can surface the **reference pool** when asked in plain language: "Which customers have publicly spoken about us or appeared as references in the last year?" Returns a portfolio-scale list with structured detail (event videos, testimonial status, advocacy activity).
- `staircase_analyze_account` per-account can extract industry, products, use cases, maturity from communications — but slowly, one account at a time.

### What's broken / missing
1. **No industry metadata in customer records.** When asked "which customers are in financial services?", Staircase replies: *"filtering by industry (such as 'financial services') is not supported in the customer metadata."*
2. **No portfolio-wide profile-similarity query.** When asked "find customers similar to <target>", Staircase replies it can't answer from the provided information — the available context is the target's own account snapshot, not other customer details.
3. **No structured reference-program field.** Reference activity must be inferred from communications. Works for high-volume activity (event testimonials, case studies under coordination) but misses one-off references and customer-led promotion.
4. **Combined-criteria queries fail consistently.** This is a known pattern across `staircase-at-risk-renewals`, `staircase-expansion-scout`, and `staircase-reference-finder`. The MCP requires single-dimension queries + client-side intersection. For reference matching, that means many enrichment calls per candidate — too slow for a live conversation.

---

## Proposed capabilities

### Tier 1 (highest leverage)

1. **First-class industry / vertical metadata on Customer records.** Sourced from CRM or LinkedIn enrichment at sync time. Expose via `staircase_query` as a filterable field.
2. **Reference / advocacy structured field.** Boolean + activity tags (`event_speaker`, `case_study`, `testimonial`, `intro_call_willing`, `g2_reviewer`). Sourced from CRM advocacy modules + manual CSM input.

### Tier 2

3. **`staircase_find_similar` tool.** Takes a target account_id and similarity criteria (industry, products, use cases, maturity, ARR band). Returns ranked candidates. Native portfolio-similarity primitive — replaces the per-account-enrichment workaround.
4. **Multi-dimension query support in `staircase_ask`.** Either fix the combined-criteria failure case, or expose a `staircase_query` builder that combines filters reliably.

### Tier 3

5. **Reference outreach assistant.** Given a target account and a selected reference candidate, draft the introduction email and the customer ask. Pair with CRM CTAs/Timeline.

---

## Workaround the skill uses today

`staircase-reference-finder` skill:
1. Pulls the reference pool via `staircase_ask` (works)
2. Enriches each candidate via per-account `staircase_analyze_account` (slow but works)
3. Joins client-side against target profile

Runtime: ~30-60 seconds for a top-10 match. Acceptable for an exploratory skill, not for a live in-conversation tool.

---

## Related skills that would benefit
- `staircase-at-risk-renewals` (would benefit from multi-criteria query support)
- `staircase-expansion-scout` (would benefit from industry segmentation)
- `staircase-reference-finder` (the primary requester)
- A future cross-customer pattern-detection skill — currently blocked entirely without these
