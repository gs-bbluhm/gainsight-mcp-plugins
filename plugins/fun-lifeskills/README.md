# fun-lifeskills

Personality-driven life skills for the kitchen and beyond. The skills in this plugin are not for work — they're for the parts of your life where a sharper edge actually makes you better at the thing.

## Skills

### chef-gordon

A profane, brilliant kitchen tyrant in the spirit of Gordon Ramsay mid-service. Teaches real technique through targeted verbal abuse. The user is cooking in real time and finds the insults funny.

**What it does:**
- Opens every cooking conversation with an options menu — the Master Class gambit (an absurdly complex 12-hour dish presented as the obvious choice) plus 2–3 real options the user can actually pick
- Walks through recipes with Gordon's voice woven into every step — never a separate "quip field" bolted onto neutral chef-school instructions
- Saves recipes the user loved, grudgingly, so they can cook them again
- Holds the persona across long conversations through structural design (response shape + a single self-check), not through long lists of forbidden phrases that decay across turns

**Why the persona sticks (the design choice that matters):**
Most "rude chef" prompts work for one turn and then drift toward polite helpfulness. This one fights drift with structure: every response follows a three-beat shape (opening attitude line → content with attitude woven in → non-praise closer), and a single closer self-check replaces every forbidden-phrases list: *"If my closing line would feel good to read, rewrite it until it stings."*

## Two ways to use this

### Option A — As a Claude Project (recommended for cooking in real life)

Most cooking happens phone-in-greasy-hand. Claude Code on your phone isn't realistic. A Claude Project on claude.ai is.

1. Go to [claude.ai](https://claude.ai) → **Projects** → **New Project**
2. Name it "Chef Gordon"
3. Open [`skills/chef-gordon/project-prompt.md`](skills/chef-gordon/project-prompt.md)
4. Copy everything below the `---` line into the Project's **Custom Instructions** field
5. (Optional) Create an empty `recipes.md` file and upload it to the Project's knowledge — saved recipes can be pasted in there to survive across chats

Then start a new chat in the project and say something like *"I want to cook dinner. I have chicken thighs and an hour."* He'll take it from there.

### Option B — As a Claude Code / Cowork skill

Useful if you cook at a laptop, or if you want recipes saved automatically as markdown files in a folder you can git-track.

1. Install this plugin (see the parent repo's [README](../../README.md) for marketplace install instructions)
2. In Claude Code or Cowork, invoke the skill: *"Chef Gordon, I want to cook dinner."*
3. Saved recipes land in `skills/chef-gordon/recipes/` as individual markdown files

## How saved recipes work

**In the Project version (Claude Projects):**
Claude can't write files in a Project. When you say *"save this"*, Gordon outputs a clearly-marked recipe block in chat that you copy/paste into your Project's `recipes.md` file or anywhere else you keep recipes. He'll tell you this once. He won't repeat himself.

**In the skill version (Claude Code / Cowork):**
When you say *"save this"*, the skill writes `recipes/{slug}.md` with frontmatter (title, date saved, complexity tier, serving size, Gordon's verdict) and the full recipe body. Ask *"what have I cooked"* and the skill globs the folder and reads them back to you with fresh Gordon commentary on each.

## Adding more skills to this plugin

`fun-lifeskills` is a home for personality-driven skills outside of work. If you build another one, drop it in `skills/{skill-name}/` with a `SKILL.md` and you're done — the plugin will pick it up automatically.

## License

MIT (see repo root [LICENSE](../../LICENSE)).
