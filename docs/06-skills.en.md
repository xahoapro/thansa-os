# Skills

*[Tiếng Việt](06-skills.md) · **English***

A skill is "packaged expertise" for Thansa: a pre-written guide to do exactly one type of task your way (like writing a sales email, building a landing page, deep research). When you ask something matching a skill's description, Thansa loads that guide automatically and uses it, no need to paste the process every time.

This page guides you through managing skills in the dashboard: view by group, search, enable/disable, add, edit, delete, import/export, call manually via the command menu, and how to ask Thansa to create skills by talking.

## What is this feature

A skill in Thansa is a folder containing a `SKILL.md` file, placed at `skills/<slug>/SKILL.md` inside the selected brain (Thansa auto-mirrors to `.claude/skills` so Claude Code loads native; old brains in `.claude/skills` auto-migrate to `skills/`). This file has 3 important header fields:

- `name`: display name of the skill.
- `description`: short description, this is the **trigger** - determines WHEN the skill activates. This field has special writing rules; read the section right below before filling it.
- `group`: group name to organize skills (like Marketing, Sales, Content). Required; if empty, falls into "General".

The rest of the file is detailed guidance for AI when the skill runs.

The canonical version lives at `skills/<slug>/SKILL.md` - exactly what the dashboard shows and Thansa loads through the router. Thansa also keeps a **mirror** at `.claude/skills/<slug>` for Claude Code to load native. The mirror is identical except: if `description` exceeds 150 characters, the mirror is trimmed to 150 with "…" (the version in `skills/` keeps your exact text). This only happens with imported skills or manually-edited ones, since the dashboard form caps it beforehand.

## Rule for writing `description` (read before creating a skill)

This is where users often get stuck without understanding why. When you click **💾 Save**, the server checks `description` and **refuses to save** if it breaks one of two rules:

**1. Maximum 150 characters.** Not a style thing. Thansa trims the description to exactly 150 characters when putting it into system prompt and into the `javis_use_skill` tool description, so overflow vanishes silently and the skill won't route. Rejection message explains: "description is N characters, over the 150 cap. Router trims exactly at 150 so the rest VANISHES and skill won't route. Move trigger examples to the '## When to use' section in the file body."

**2. Don't start with empty boilerplate.** Blocked phrases: "Activate when...", "Use this skill when...", "Use skill this when...", "This skill uses / This skill is used when...", "Use this skill when...", "Activate when...". Every skill starts the same way so these eat up your character budget without distinguishing skills. Rejection explains: name the ability directly, e.g. "Summarize meeting notes into action items."

Write correctly: one sentence stating what the skill **does**, under 150 characters. Long trigger lists, keyword sets, detailed scenarios go in the `## When to use` section in the **file body** `SKILL.md` - no cap there and only read when the skill loads. Short form: description for FINDING, body for DOING.

This rule applies to both the dashboard form and skills the **Self-learning** page suggests (violating skills get skipped).

## How triggers work

Skills auto-activate based on the `description` field (you also call manually, next section). When you type or speak a request, Thansa matches it against the `description` of enabled skills; if it matches, it loads that guide. On Claude Code it loads native; on other engines Thansa puts the skill list in system prompt and loads via the `javis_use_skill` tool.

So skill quality depends heavily on how you write `description`. Good description names the ability and includes keywords, the skill triggers right. Vague description means it never fires, or fires wrong.

Note: skills work on **every engine**. Claude Code loads native; ChatGPT/Codex, OpenRouter, OpenAI/Anthropic/Google Gemini API use skills via router (Thansa puts skill list in system prompt) and tool `javis_use_skill`. See [Models & Engines](10-models-va-engine.md) for each engine's details.

## Call skills manually: "/" command menu

You don't always have to wait for triggers. Type **`/`** in the chat for a menu above the input:

- Three session commands at top: **`/new` New conversation**, **`/reset` Reset session**, **`/stop` Stop**.
- Below are all skills of the selected brain, each line showing `/slug`, skill name, and description.

How to use: type a few more characters to filter (matches slug first, then names). Use **arrow keys up/down** to choose, **Enter** or **Tab** to confirm, **Esc** to close. Clicking a line also works.

Pick a skill and the chat box fills with `/slug ` and your cursor is ready - type the rest of your request then Enter. Thansa translates it: "Use skill `<slug>` with request: ... If this skill doesn't exist, just handle my request normally." Pick a session command and it runs immediately, no Enter.

On Telegram, send `/<slug>` (with content after if needed) for the same effect. Exception: when using OpenRouter engine, Thansa replies "⚠ Skill needs Claude CLI engine. Send /cli to switch, then /<slug> again."

## Router's 20-skill cap

The skill list that Thansa puts into system prompt and into the `javis_use_skill` tool description is **capped at 20 skills**. Overflow shows one line "+ (N more skills - see `Javis/index.md`)".

What matters: if your brain has over 20 enabled skills, skills ranked 21+ **don't fit the router**, so on engines using router (ChatGPT/Codex, OpenRouter, OpenAI/Anthropic/Google Gemini API) they won't auto-trigger. They're still there and still callable: call manually via `/slug` and they run fine, because the `javis_use_skill` tool takes all enabled slugs, not just the 20 listed.

How to fix: disable skills you don't actively use, keeping the router's 20 slots for skills you want Thansa to catch automatically.

## System skills and your skills

Thansa splits skills into 2 types:

- **System skills** (badge says "system"): default Thansa OS functions, currently 6:

  | Slug | What it does |
  |---|---|
  | `javis-builder` | Create or edit Thansa capabilities: agents, skills, workflows, loops, plugins |
  | `ingest-source` | Digest raw source into Second Brain, curate into wiki knowledge |
  | `query-wiki` | Search Second Brain knowledge, return cited answers |
  | `lint-wiki` | Audit wiki health, return issues list |
  | `notes` | Save current message exactly as-is to `sources/` (with images), auto-curate to wiki if worthy |
  | `html-to-webcake` | Convert an HTML page to `.pke` file, openable in Webcake page builder |

  Live in the app's settings folder (not your brain), so they **exist in every brain** and **auto-update when you upgrade Thansa OS**. Can't delete from dashboard (delete manually and they reinstall on next boot); to stop using them, just **disable** like normal skills - disable state persists across updates.

- **Your skills**: made via + Skill button, via chat, imported from `.zip`, or suggested by Self-learning page. This is vault data - switch brains and skills change with it. Update the app and doesn't affect them.

You can still **Edit** system skills. When you do, you create your own version: Thansa keeps your edits and stops auto-updating that one. To go back to standard (with auto-updates), delete the skill folder from `skills/` in the brain (using Files page) then restart - fresh system version installs.

## Skills vs Plugins

Two separate things in the **Capabilities** group on the sidebar.

| | Skill | Plugin |
|---|---|---|
| Essence | Knowledge **HOW-TO**: a guide file AI reads then follows | **Real Python code** running in the server process |
| Output | A process, template, rulebook | A new **tool** all engines can call, and/or **hook** firing around each tool call |
| Location | `skills/<slug>/SKILL.md` in the brain | Folder `plugins/<slug>/` (with `plugin.yaml` + `plugin.py`) |
| Activation | Check box on the card | Plugin you installed still needs `JAVIS_ENABLE_USER_PLUGINS=true` env var then restart |

Pick: need **guidance** for doing something with existing tools? Write Skill. Need a **specific Python action** not yet covered (calculate, transform data, call one simple API)? Write Plugin. Or it's an outside data source with a ready MCP? Use MCP on Connections page, don't write plugin. Full details at [Plugins](20-plugins.md) and [Connections & Business Data](09-mcp-va-so-lieu.md).

## Where to find it in Thansa

Open the dashboard (default port 7777), look at the left navigation bar, open **Capabilities** group then click **Skills**. This group has 4 sections: Agents, Skills, Workflows, Plugins.

Top of the page shows **Skills** title with a status line, like "3/5 enabled · source `skills/`". The numbers show how many skills are on vs total, and remind you skills come from the `skills/` folder of the current brain.

Right of the title are two buttons: **⤒ Import** (bring skill packages from outside) and **+ Skill** (create new).

If the brain has no skills, the page shows "Brain has no skills. Click + Skill to create (auto-saves to `skills/` + organizes)".

## Skills page layout

With skills present, the screen splits into 2:

- **Group column (left):** lists groups, starting with **All**, then each group in alphabetical order. Each line shows skill count in that group. Click a group to filter the list to only that group's skills.
- **Skill list (right):** title shows which group you're viewing, skill count shown, and a **Find skill…** box. Below are skill cards.

Each skill card shows:

1. Checkbox at the start for enable/disable.
2. Skill name (with 🧩 icon). System skills get a **system** badge.
3. Description line (the `description` field).
4. Last line: 📂 group name · slug. If from `.agents` folder, gets an ".agents" note. End of this line also shows usage (see right below).

Disabled skills appear dimmed. Hover a card and edit/export/delete buttons appear on the right: **Edit**, **⤓ Export**, **Delete**. **System** skills only have **Edit** (can't export or delete). On narrow screens under 860px, buttons always show at the card bottom since there's no hover.

### "Used N times" and "never seen using" lines

At the end of the group · slug line, Thansa shows one of two:

- **"used N times, last <date>"** if the skill was loaded at least once.
- **"never seen using"** (faded, italic) if it's been over 30 days without a use signal.

This is **one-way signal**, understand it right: Thansa only counts loads through the `javis_use_skill` tool. Claude Code loads native via `.claude/skills` and **doesn't** go through the counter. So "used N times" is definitely right, "never seen using" just means no evidence, **not** that the skill is useless. Hover over the label and you see this explanation. Nothing auto-disables or auto-deletes based on this label - you decide.

This data is stored in `Javis/skill-usage.json` in the brain, separate from `SKILL.md` so each skill use doesn't create noise in your brain's git.

## Find skills

Type in the **Find skill…** box at the top of the list. Thansa filters as you type, matching keywords against skill name, description, and slug. The search filter layers on top of the group filter: if you're in a specific group, search runs only there; to search everything, click **All** first.

## Enable and disable skills (one by one)

1. Go to **Skills** page.
2. Find the skill to toggle.
3. Click the checkbox at the start of the card. Checked = enabled, unchecked = disabled.

When you disable a skill, Thansa moves its folder to a subfolder called `.disabled` (path becomes `skills/.disabled/<slug>`) and removes the mirror in `.claude/skills`. This is **real disable**: skill in `.disabled` won't be loaded by any engine, so Thansa stops using it. Enable it again and the folder moves back to `skills/<slug>` and mirror restores for Claude native.

Enable/disable doesn't erase skill content. You can disable temporarily then re-enable anytime without losing the instructions.

If status change errors, Thansa says "Can't toggle status" with a reason.

## Add new skill (step by step)

1. On **Skills** page, click **+ Skill**.
2. Fill in the form:
   - **Skill name**: memorable name, e.g. "Write sales email".
   - **Group**: type a group name, e.g. "Marketing". This box suggests groups you've used before so you can pick for consistency. Don't leave blank (falls to "General").
   - **Description (trigger - when skill activates)**: one sentence naming what skill does, **under 150 chars**, don't start with "Activate when...". Wrong format gets rejected (read "Rule for writing `description`" above). The `## When to use` section in the file body is where full trigger details go.
   - **Content (SKILL.md - guide for AI)**: write detailed guidance for AI when skill runs (steps, templates, rules). Here's where to add `## When to use` with full examples. If blank, Thansa creates minimal content from name and description.
3. Click **💾 Save**. Or click **Cancel**.

On save, Thansa auto-generates **slug** from the name: lowercase, remove Vietnamese marks, replace spaces with hyphens (e.g. "Write email" becomes `write-email`). ASCII-safe slugs help all engines load skills better. Folder `skills/<slug>/SKILL.md` is created automatically.

## Edit skill

1. Hover a skill card, click **Edit**.
2. The form reappears with current skill details (name, group, description, content).
3. Change what you need.
4. Click **💾 Save**.

Editing keeps the old slug and folder, just overwrites `SKILL.md`. This is where you fine-tune `description` for better triggering or add steps to the guide.

Editing a **disabled** skill keeps it disabled after save; Thansa doesn't auto-enable.

## Change skill group

Easiest: click **Edit** on the skill, change the **Group** field, **💾 Save**. Group is just a label in the frontmatter; changing it doesn't affect whether the skill loads, only which group it shows up in.

## Delete skill

1. Hover a skill card, click **Delete**.
2. Thansa asks: `Delete skill "<name>"? Will delete the entire skills/<slug> folder.`
3. Click OK to delete.

Delete is final: the entire skill folder is removed from disk, not moved to trash. If you just want to stop using it temporarily, **disable** instead. System skills don't have a Delete button.

## Export and import skills

- **⤓ Export** (on each card): download a `.zip` package of that skill to send to someone. System skills don't have this since every brain already has them.
- **⤒ Import** (top of page, next to + Skill): pick a file to bring into the brain. Accepts `.zip` (Thansa package), loose `.md`, or Claude's `.skill` package (Thansa auto-detects `SKILL.md` and puts it in the right folder). Thansa asks first: "If agents/skills/workflows share NAMES, replace with new version?" - click OK to overwrite, Cancel to keep old and only import what's missing. After import, Thansa lists what went in and what was skipped.

Note: skill content is guidance for AI to follow, so only import packages you trust. Details on packaging with dependencies at [Agents & Workflows](07-agents-va-workflows.md).

## Ask Thansa to create skills by talking

You don't have to fill the form. Open chat and ask Thansa to create a skill, like: "Create a skill for writing Facebook captions for beauty products, trigger when I ask for sales captions." Thansa writes `SKILL.md` and saves to `skills/`. Chat conversation details at [Chat & Voice](02-tro-chuyen-va-giong-noi.md).

When creating a new skill, Thansa groups it correctly: it reads existing skills (`skills/*/SKILL.md` → `group` field) to see what groups you use, then picks the closest fit. Only if no group fits does it make a new one, using a short domain name (Marketing, Sales, Content, Operations, Finance, AI, Productivity, Personal). So new skills don't scatter into "General".

## Skills and Agents

On the **Agents** page, creating or editing an agent shows a **Skills** section listing available skills for you to check and assign to that agent. Agents only see skills when your brain has skills in `skills/`; if none exist, the section notes "Brain has no skills in skills/ - agents still create, assign later". See [Agents & Workflows](07-agents-va-workflows.md).

## Quick reference for buttons and states

| You see | Means / action |
|---|---|
| **⤒ Import** | Bring `.zip` / `.md` / `.skill` packages into the brain |
| **+ Skill** | Open form to create new skill |
| Checkbox at card start | Checked = enabled; unchecked = disabled (move to/from `.disabled`) |
| **Edit** | Open form to edit skill |
| **⤓ Export** | Download skill as `.zip` package to share (not on system skills) |
| **Delete** | Permanently erase skill folder (confirm first; not on system skills) |
| **💾 Save** | Save skill (create or overwrite) |
| **Cancel** | Close form, no save |
| **Find skill…** box | Filter by name, description, slug |
| **Group** column / **All** | Filter list by group |
| **system** badge | Skill comes with app, exists in all brains, only disable not delete |
| Card appears dimmed | Skill is disabled |
| Line "x/y enabled" | x skills on out of y total |
| "used N times, last …" | Skill was loaded via `javis_use_skill` tool N times |
| "never seen using" | Over 30 days no use signal; just info, not a judgment |

## Tips

- Write `description` like a headline: state the ability directly, under 150 chars. Move full trigger examples and keywords to `## When to use` in the file body - no cap there, won't cut off.
- Count characters before saving. 150 is shorter than you think, about two short sentences.
- One skill does one clear job. Too broad and triggers misfire; split into multiple skills in the same group, easier to manage.
- Keep enabled skills under 20 to fit all in the router. Disable skills you don't actively use.
- Use consistent group names. When typing the **Group** field, pick from the suggestions instead of making new ones, keeps the group column from fragmenting.
- Experimenting with a new skill? Create it then **disable** when not needed, rather than delete and recreate.
- To be sure a skill runs for the right task, call it manually with `/slug` instead of waiting for auto-trigger.

## Common issues

- **Clicked 💾 Save but skill doesn't show in list:** likely your `description` breaks the rule (too long over 150 chars, or starts with "Activate when..."). Server rejects and returns to list without error. Click **+ Skill** again, trim description under 150 and remove boilerplate start, save again.
- **Created skill but Thansa doesn't use it automatically:** check three things in order. One, is the skill **enabled** (card not dimmed, checkbox ticked)? Two, does `description` state the ability right? Three, is your brain over 20 enabled skills - if so, yours might be outside the router; disable others or call manually with `/slug`.
- **Skill list empty even though created some:** make sure you're on the right brain. Skills source is `skills/` of the current brain; switch brain and list changes.
- **Enabling/disabling says error "Can't toggle status":** usually a permissions issue on the folder or it's locked. See [Troubleshooting & FAQ](17-khac-phuc-su-co.md).
- **Skill says "never seen using" but you know it ran:** normal. Thansa only counts via `javis_use_skill` tool; Claude Code loads native and doesn't go through the counter. Don't delete just because of this label.
- **Card missing Delete button:** that's a system skill. To stop using, disable it.
- **Accidentally deleted:** delete is final, no recovery from the dashboard. Future prevention: save `conversations.db` backups regularly (see "Sync when changing machines").
- **Group fell into "General":** group field was empty on save. Click **Edit** and fill in a group name.

## Related

- [Agents & Workflows](07-agents-va-workflows.md) - assign skills to agents, build task chains, export/import packages with dependencies.
- [Plugins](20-plugins.md) - when you need a tool running real code instead of a how-to guide.
- [Models & Engines](10-models-va-engine.md) - skills work on all engines; see differences between native (Claude Code) vs router (`javis_use_skill`).
- [Chat & Voice](02-tro-chuyen-va-giong-noi.md) - ask Thansa to create skills by talking, and "/" command menu in chat.
- [Self-learning](22-tu-hoc.md) - where Thansa suggests new skills from past chats.
- [Second Brain: Memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) - understand what a brain is where skills live.
