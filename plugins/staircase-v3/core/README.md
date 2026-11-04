# Staircase (core)

Staircase AI for Claude, for anyone who works with customers. Four skills:

| Skill | What it does |
|---|---|
| `staircase-ask` | Answers and reports you can trust: counts, lists, rollups and rankings, each saying whose accounts it covers, the window, and what Staircase couldn't see |
| `staircase-account-brief` | One account on one screen: where it stands, what's open on both sides, who's engaged or gone quiet, and the next move with a draft ready |
| `staircase-follow-up` | The recap after a call, who you owe a reply, and coverage notes before time off |
| `staircase-voice` | What customers are saying across a group of accounts, ranked, with quotes checked against the source |

It also carries the shared rules every Staircase pack uses (scope, evidence, action priority, action types, trust, delivery, company profile), copied into each skill's own `references/` folder so every pack works when installed alone. Requires the Staircase AI connector. It reads Staircase and never sends or writes anything without your yes.

Org-specific values live in one file, `company-profile.md`, in every skill's references folder. To make your own company edition, edit that file only and rebuild; the skills stay generic.

## Install (beta)

```
/plugin install staircase-v3 --marketplace gs-bbluhm/gainsight-mcp-plugins
```

The beta guide, with what to try and the Claude app zips: [`../README.md`](../README.md).
