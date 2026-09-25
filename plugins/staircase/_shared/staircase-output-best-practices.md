# Staircase Output Best Practices

Plugin-wide discipline for every Staircase skill. Read this before composing any query or producing any artifact. Validated against live MCP testing (June 2026). Companion: `skills/staircase-mcp-expert/` for the full query mechanics.

> No em dashes in any output.

---

## The house style (every query and every artifact)

These five rules drive quality on every Staircase surface.

1. **Scope it.** Name the account for single-account work, or scope to "my accounts" (the user's resolved scope) for cross-account work. Never unbounded "all customers".
2. **Demand evidence.** Ask for and cite the specific email, meeting, or ticket behind each claim. Carry evidence IDs where the tool returns them.
3. **Separate evidenced from inferred.** Mark what the communications say versus what you are interpreting.
4. **End in a next action.** Every artifact closes with the concrete next step, owner, and (where relevant) timing.
5. **Lead with communication signals.** Staircase derives health, risk, and renewal readiness from communications. Revenue and renewal dates are queryable and usable when populated, but the CRM is authoritative for the contracted figure and date; seat counts and product usage live in the CRM. Say so when a conclusion depends on a CRM-authoritative value.

---

## Query discipline (MCP): report-first

- **Lists / filters / rankings / counts → ONE structured report.** Build it with `staircase_run_report` by default (name the field ids from `staircase_report_metadata`); `staircase_generate_report` (natural language, resolves owner names) is the fallback. **Multi-criteria AND/OR belong in the report filter**: combined criteria work (verified live); do NOT decompose a filterable list into single-dimension prose queries. The old "one dimension per query, AND/OR returns empty" rule was a limitation of the `staircase_query` prose path, not the report layer.
- **Reports carry the analysis, not just the fields.** The analyst outputs (risk, expansion, churn, handoff, renewal) are structured columns; read them directly. Reserve `analyze_account` for per-account narrative/evidence, and `staircase_query` for open-ended KB Q&A.
- **Verbose columns:** analyst *summary/narrative* fields are large; select lean columns for full-book listing, pull narrative columns only for the shortlist (`customer.id In [...]`).
- **The analysis cap is for parallel analysis, not list size.** Reports return 25 to 100+ rows; the parallel per-account analysis cap (10 today) applies only to the `analyze_account` fan-out.
- **Long-list, prioritize, drill.** Structured report → client-side priority sort (the report does not compute abstract scores) → deep-dive the top N in parallel.
- **Match the tool to the job:** `staircase_run_report` (with `generate_report` as fallback) for lists/rankings/aggregates and analyst fields, `staircase_analyze_account` for single-account depth, `staircase_account_info` for one account's stored fields, `staircase_semantic_search` for theme/evidence, `staircase_query` for open-ended Q&A, `staircase_fetch_evidence` for full evidence text, `staircase_account_lookup` to resolve a name to an account_id.
- **Handle non-determinism.** `analyze_account`/`query` are non-deterministic: retry the same phrasing up to twice, then switch. Reports are deterministic. Trust honest negatives ("no usable evidence in the 90-day context" is real).
- **Commercial fields exist in the report/info layer.** `revenue` and `renewal_date` are queryable and often populated; use them, and flag the CRM as authoritative for the exact contracted figure/date. The ~90-day communication window still bounds narrative depth; older history comes from the CRM.

See `skills/staircase-mcp-expert/references/` for the full field catalog, validated phrasings, anti-patterns, and analyst data models.

---

## Output and export discipline

This plugin reads and synthesizes. It does not write to a system of record. There are no approval gates for writes because there are no writes. Instead:

- **Produce a clean artifact** the user can copy where they need it: a markdown report, a brief, or a draft email.
- **Lead with the answer.** TLDR or headline first, then the structured detail, then sources. Tables over paragraphs.
- **Make it verifiable.** Include the source communications or evidence IDs so the user can check before acting.
- **Draft, do not send.** When a skill produces an email or outreach, present it as a draft for the user to review and send themselves. Never claim something was sent.
- **Format adaptation:** in Cowork, lead with a card (headline + table, drill-downs as expandable cards). In Code, full markdown to stdout plus an optional file artifact.

---

## Scoping without a CRM (solo plugin note)

The joint Gainsight plugin scopes "my accounts" via a Gainsight team-member field. This solo plugin has no Gainsight. Scope is resolved automatically on the first call by the `staircase-mcp-expert` first-call contract (it works out which role fields the user is on and asks only when that is ambiguous), then cached in `~/.staircase-mcp/user-profile.md`. `staircase-setup` can run the same resolution up front as an optional welcome. Sibling skills read that profile and apply the scope automatically; never assume the `Owner` field is the book-owner role.

---

## Frontmatter and structure conventions (every SKILL.md)

- Standard Claude Code frontmatter: `name`, `description` (double-quoted, third person, tight, with natural trigger phrases inline), and `allowed-tools` only for non-Staircase tools a skill needs (e.g. `mcp__visualize__show_widget`). Never hardcode `mcp__staircase-ai__*` tool names; the server prefix varies by install. Add `disable-model-invocation: true` to experimental or partial skills.
- Plugin-internal `user_type`: `foundation` | `ic` | `exec` | `experimental`.
- Keep SKILL.md tight (orientation + top patterns). Push dense material to `references/`.
