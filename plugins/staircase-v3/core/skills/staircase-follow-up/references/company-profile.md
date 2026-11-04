# Company profile

The one file that holds this organization's own values. Skills never hold org values; they read them here. A `not set` value means live discovery, with the default named in the answer.

Read order for org context: what the Staircase server serves (when it offers org context), then this file, then live discovery.

## Changing it

- **Generated:** the admin pack's `staircase-admin-setup` discovers the values, you confirm them, and it writes this file for every plugin in your company edition.
- **Fork and edit:** change only the block under "Values", keep the keys, then rebuild or re-upload each plugin. The same file sits in every skill's references folder and must be identical everywhere (the build checks). Never edit a skill to hold an org value.
- Configuration only: no account names, contacts or figures.

## Rules for skills

- Read this file once per session.
- `not set`: discover live or use the default, and say "default".
- A number the user states in the ask ("in 30 days") wins over a threshold here.
- A value metadata no longer offers (a renamed tier, a removed field): ignore it, say so, and suggest the admin refresh the profile.
- Ids use metadata form: role fields as `customer.<field>`, products as `productId` option ids, tiers as `tier.id` values.
- `fiscal_year_start_month` decides quarter and fiscal-year asks (`data-rules.md`, Dates); not set means calendar quarters, labeled as the default.
- `role_map` and `teams` change output the most: with both unset, every internal recipient is a guess or `<who>`. When `role_map` is not set, read the account's role holders from `staircase_account_info` by their field labels and print "(from the account's <label> field)"; never assume `Owner` is the CSM.

## Values

```yaml
profile_version: 1
updated: not set

role_map:                    # which customer role field means which job
  csm: not set
  account_manager: not set
  renewal_owner: not set
  sales_owner: not set       # often customer.owner
  exec_sponsor_holder: not set
role_synonyms:               # stakeholder role names that mean the built-in roles
  decision_maker: []
  executive_sponsor: []
  champion: []
  departed: []

segments:
  tiers_live: not set        # tier.id values (from a report rooted on tier) that hold active accounts
  segment_field: not set     # what "segment" means here; not set = customer.tier (scope.md)
  region_field: not set
  product_line_field: not set
  products: not set          # productId options to show by name
fiscal_year_start_month: not set

thresholds:
  quiet_days: 21
  touch_days: 14
  dark_days: 30
  renewal_window_days: 120
  safe_to_ask_read_days: 45

engine:
  stakes_weights: {renewal: 0.40, risk: 0.35, value: 0.25}
  touch_budget: {per_contact_days: 14, per_account_per_30_days: 3}
  ask_budget: {per_contact_days: 90, per_account_days: 30}
  list_size: {full_items: 5, more_options: 7}

exclusions:
  own_org_account_ids: []    # the vendor's own account(s), left out of customer lists
  pooled_user_ids: []        # placeholder users that hold accounts
  automated_senders: []      # shared mailboxes and notifiers that are not a human touch
  test_accounts: []

teams:                       # where Slack asks and notes go
  support: not set
  product: not set
  engineering: not set       # engineering notes from escalations
  enablement: not set        # configuration and how-to asks (or services)
  admin: not set
  escalation: not set

gainsight_cs:
  cta_reasons: not set
  timeline_activity_type: not set

resources: []                # links Claude may share in customer drafts: {name, url}
saved_reports: []            # {name, definition, config, cadence}
terminology: {}              # your words for Staircase terms, for example {book: portfolio}
```
