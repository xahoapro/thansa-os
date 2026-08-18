# Plugins: add native tools for any engine

A plugin is a way to add **new tools** to Thansa without changing the source code: a Python folder dropped in the right place, Thansa loads it, and from then on every engine (Claude Code, ChatGPT/Codex, OpenRouter, OpenAI, Anthropic, Gemini) can call that tool.

This page explains how to read the plugin list in the dashboard, toggle each one, understand the 7 built-in plugins, and safely install custom plugins plus mandatory safety guards to know before you do.

## What this feature is

A plugin is **a folder** with 2 files:

- `plugin.yaml`: declares name, slug, description, version, on/off state, minimum permissions, and lists tools and hooks.
- `plugin.py`: Python code, must have `register(ctx)` function. Inside you call `ctx.register_tool(...)` to add tools, and/or `ctx.register_hook(...)` to add hooks.

A plugin gives Thansa two things:

- **Tool**: a tool engines can call, e.g., `javis_now` (ask what time it is in Vietnam) or `javis_generate_image` (make an image). Plugin tools go through the MCP Hub so **every engine can use it**, not just Claude Code.
- **Hook**: code that runs **around every tool call**. Currently supports two events: `pre_tool_call` (before a tool runs) and `post_tool_call` (after it finishes). When no plugin registers a hook, Thansa doesn't wrap anything, so no overhead.

Plugin tools **respect exactly 3 permission levels** like all other tools, so a loop in read-only mode won't auto-call a write-level plugin tool.

## Plugin vs Skill vs MCP - how to tell

Three things that get mixed up. Use this question to pick:

| Missing | Use | Nature |
|---|---|---|
| Thansa doesn't know **how to do** a task in your style | **Skill** | A `SKILL.md` file with instructions. No code runs, just teaches AI the right process. See [Skills](06-skills.md). |
| Need a **real action** in Python (calculate, transform data, call simple API, read/write files by custom rules) that no source covers | **Plugin** | Real Python code runs, adds tools/hooks for all engines. |
| Need **outside data source** already having a server (POS, ads, calendar, email, notes...) | **Connection (MCP)** | Plug a server on the Connections page, no code to write. See [Connections & Business Data](09-mcp-va-so-lieu.md). |

Short: **Skill** = knowledge of how to do it; **Plugin** = real code; **MCP** = outside data. If a task already has MCP, don't write a plugin.

## Where in Thansa to find it

Open the dashboard (default port 7777), look at the left nav bar, click the **Capabilities** group to expand, then click **Plugins**. The page title is **Plugins** with subtitle "Native tools/hooks for all engines".

Just below the title are three intro boxes:

1. Description: "Plugins add **tools** (callable by engines) and **hooks** native to Thansa without modifying core - work in ALL engines (Claude Code, Codex, API) via hub, respect 3 permission levels like other tools."
2. Warning box in orange (only shows if not unlocked yet): "**⚠ Plugins you installed are blocked.** Plugins run real Python code in your server, so OFF by default. To enable: set `JAVIS_ENABLE_USER_PLUGINS=true` env var then restart Thansa. Built-in plugins still run normally."
3. Gray instruction line: "Drop global plugins (used by ALL brains) into `<actual path on your machine>` · each plugin is a `plugin.yaml` + `plugin.py` pair. Or ask Thansa in chat: 'make a plugin ...'."

The path in line 3 is the **actual** path on your machine running Thansa, copy from the screen rather than typing from docs.

Below is the plugin card list, sorted by source: Built-in first, then Global, then This brain; within each group sorted by name. If no plugins exist yet, the page shows "No plugins. Drop a plugin folder into `<path>` then reload."

## Reading a plugin card

Each plugin is one card. Read top to bottom:

**Top line (left):** 🧩 icon, plugin display name, then small faint **slug** (the folder name), then a source label:

| Source Label | Means | Located at |
|---|---|---|
| **Built-in** (green) | Comes with app, Thansa-made, trusted | `system/plugins/<slug>/` in install folder |
| **Global** (blue) | You installed it, used by **all brains** | Thansa state folder, `<JAVIS_STATE_DIR>/plugins/<slug>/` |
| **This brain** (orange) | You installed it, used by **one brain** | `<brain>/plugins/<slug>` (older brains might have `<brain>/Javis/plugins/<slug>/`) |

Slug clash means later source overrides: a "This brain" plugin named `datetime-vn` replaces the "Built-in" one same name.

**Top line (right):** current status (see table in "Quick reference of buttons and status" section).

**Description line:** content of `description` field in `plugin.yaml`.

**Info line:** joined by dots, shows "minimum permission: ..." then version (`v1.0.0`) then author. E.g., "minimum permission: read-only · v1.0.0 · Thansa (bundled)".

**Chip row:** each tool the plugin provides is one chip with 🔧 icon and tool name; each hook is a chip 🪝 with event name. These are the exact names engines will call, so if you want Thansa to use a specific tool, mention the name in the chip.

**End button:** **Enable** or **Disable** (label changes per state).

Non-running plugins appear faded. If a plugin errors, an error reason line appears red right below the chips.

## How to use (step-by-step)

### Step 1: See what plugins are running

Go to **Capabilities > Plugins**. Look at the status column on the right of each card. Only cards saying **● running** actually have tools available to engines. Faded cards don't work right now.

### Step 2: Enable or disable a plugin

1. Find the plugin card you want to change.
2. Click the **Enable** (or **Disable**) button at the end.
3. The list reloads, status changes immediately.

For **built-in** plugins, Thansa doesn't edit app files: on/off choice is saved to `plugins.json` in state folder. This way updating Thansa to a new version **doesn't lose** your settings.

For **global** and **this brain** plugins, Thansa writes `enabled: true/false` straight into their `plugin.yaml`.

Enable/disable takes effect immediately, no restart needed: Thansa refreshes the hub cache so tools appear or vanish at the next chat, and the brain's `Javis/index.md` capability index rebuilds.

One exception: if you enable a **global/this brain** plugin while the env gate isn't unlocked yet, Thansa shows a dialog: "Enabled in manifest BUT user-installed plugins only run when you set `JAVIS_ENABLE_USER_PLUGINS=true` then restart (protects against malicious code)." The card switches to **⚠ waiting for env**.

### Step 3: Check tools reached the engine

Open a chat and ask directly, e.g., "what time is it" (plugin `datetime-vn`) or "list my Facebook Pages" (plugin `meta-pages-graph`). Thansa knows which plugins are running because a list "Running plugins" with tool names gets included in the chat context.

If a tool is blocked by permissions, the answer contains the exact error starting with `ERROR: tool '<name>' requires higher permission`. If a tool needs a connection you haven't set up, the error says which page to go to.

## Built-in plugins

These come with the app (label **Built-in**). All enabled by default except `tool-audit`.

| Card Name | slug | Tools it provides | Minimum permission | Default |
|---|---|---|---|---|
| Time & date (VN) | `datetime-vn` | `javis_now`, `javis_date_add` | read-only | On |
| Schedule tasks & reminders | `javis-schedule` | `javis_schedule` | write (safe) | On |
| Kanban task dispatch | `javis-task` | `javis_task` | write (safe) | On |
| Add MCP connection | `javis-connect` | `javis_add_mcp` | write (safe) | On |
| Generate images (ChatGPT) | `image-chatgpt` | `javis_generate_image` | write (safe) | On |
| Meta Ads (Graph API) | `meta-ads-graph` | `meta_ads_accounts`, `meta_ads_insights`, `meta_ads_campaigns`, `meta_ads_get` | read-only | On |
| Facebook Pages (Graph API) | `meta-pages-graph` | `fb_pages_list`, `fb_page_posts`, `fb_page_comments`, `fb_page_post`, `fb_page_photo`, `fb_page_album`, `fb_page_video`, `fb_page_edit`, `fb_page_delete`, `fb_page_reply` | full | On |
| Monitor Facebook (Apify) | `fb-monitor-apify` | `fb_monitor` | read-only | On |
| Send images & files via Zalo | `zalo-image` | `zalo_send_image` | full | On |
| Tool usage log | `tool-audit` | `javis_tool_stats` + hook `post_tool_call` | read-only | **Off** |

What each does:

- **Kanban task dispatch**: dispatch a task to the queue right from chat (`op=add`) and see how far it's running (`op=list`). Since 0.17.1. Before that, the only way was `POST /kanban/task`, which needed shell access - only Claude Code and Codex could do it despite promising any brain could. This tool calls the in-process queue directly, no new HTTP endpoint. Two hard constraints: **can't create `full` mode tasks** (those spend money, create orders, send messages - you set those on the Tasks page), default is `suggest`. Switching columns, canceling, approving pending tasks still happens on the Tasks page.
- **Add MCP connection**: ask Thansa to wire in a new MCP source right in chat, it **shows up on the Connections page** in the "Connected" section like you added it by hand, shared for all brains. Before this plugin Thansa had no way to write to the connection store, it could only run `claude mcp add` - that lives in Claude Code's personal config, the other 5 brains don't see it, and on the Connections page it appears in the folded "Built-in connections of Claude Code and Codex" section (hidden by default), making it look like nothing was added. Three safety layers: default permission is **read-only** (you elevate on Connections page if you want write); sources running via machine **commands** (stdio) add in **off** state so you read the command first; services already in the Connection Hub (Gmail, Calendar, POS...) just get pointed to the right card instead of spawning a duplicate. Failed connection test still **stays on the page** with the reason, doesn't silently vanish.
- **Send images & files via Zalo**: send images (e.g., Thansa just created) or files with a message via Zalo, using the account already QR-scanned on the Connections page. Exists because the standard MCP tool `zalo_send_message` only sends text, but the underlying library has long supported attachments and 1.6.2 is latest so waiting upstream is forever. Only sends files inside the current brain - intentional gate because sent Zalo messages can't be recalled. Needs Node.js 20+. Details at [Zalo](12-zalo.md).
- **Time & date (VN)**: tells Thansa what today is, current time, day of week in Vietnam time (UTC+7), and relative dates ("3 days from now", "last week"). Pure stdlib, no network. Also the simplest plugin example to read if you want to write your own.
- **Schedule tasks & reminders**: create, list, cancel scheduled tasks and reminders **right in chat**, skip typing YAML by hand. Recurring tasks and running ones write to `Javis/loops/<slug>.md` (editable in Obsidian); one-time or cron reminders go to the reminder store. Details at [Scheduled Tasks & Reminders](08-viec-dinh-ky.md).
- **Generate images (ChatGPT)**: make images from description using the **ChatGPT account** you're logged into (OAuth), no separate OpenAI API key needed. Images save to `attachments/` of the brain then embed in the answer. Needs ChatGPT connected on the **Models** page; if not, the tool replies "ChatGPT not connected (OAuth). Go to Models page to log in then try again...".
- **Meta Ads (Graph API)**: read ad performance numbers (list ad accounts, campaigns, metrics). **Read-only, no spending.** Needs "Meta Ads (custom app - Graph API)" connection wired on the Connections page.
- **Facebook Pages (Graph API)**: manage Pages/Fanpages. Reading Pages, posts, comments is read-only; posting, adding photos, adding videos, editing text, deleting posts, replying to comments are **real, public actions** needing full permission. Needs "Facebook Pages (custom app - Graph API)" connection.
- **Monitor Facebook (Apify)**: track public Pages and Groups to find high-engagement posts via Apify. Read-only, doesn't touch personal account, runs on VPS. Needs Apify Personal API token pasted into "Monitor Facebook (Apify)" connection.
- **Tool usage log**: counts how many times **each** tool gets called by engines (via `post_tool_call` hook) then shows stats of most-used tools. This is an example of how hooks work, so off by default; enable on the Plugins page, chat a bit with tool calls, then ask Thansa "what's the most used tool".

Note on "Minimum permission" column: that's the setting for **the whole plugin** shown on the card. Individual tools inside still have their own levels. E.g., `meta-pages-graph` shows "full" on card, but three of its read-only tools need only read-only, the rest need full.

## Permission levels and run modes

Each plugin tool declares a minimum permission level; each run of Thansa has a permission ceiling. A tool only runs when the ceiling is high enough.

| Tool's minimum level (card label) | Meaning | Runs in which modes |
|---|---|---|
| `readonly` - "read-only" | Only read or calculate, no changes | All modes |
| `safe` - "write (safe)" | Writes files or uses quota | Auto safe mode and Full mode |
| `full` - "full" | Real action outside (post, delete, send) | Only Full mode |

The chat box you type in runs at full ceiling so it can call all three types. A [scheduled task](08-viec-dinh-ky.md) in **suggest** mode can only call read-only tools; if it hits a higher tool it returns `ERROR: tool '<name>' requires higher permission (...)` and stops. This is a hard gate in the code, not a prompt suggestion, so the model can't trick around it.

## Install your own plugin

### Step 1: Pick a location

Two choices, your call on shared vs. single-brain:

- **Global** (recommended): `<JAVIS_STATE_DIR>/plugins/<slug>/`. All brains see this plugin, all engines can call it. Real path shown on the Plugins page, copy from there. Default `JAVIS_STATE_DIR` is the repo's `server/` folder; on Docker/VPS usually `/data/state`.
- **One brain only**: `<brain>/plugins/<slug>/`. Only that brain uses it. Good when plugin is tied to a specific brain's data.

`<slug>` is the folder name, must be ASCII lowercase no accents, start with letter or digit, contain only letters, digits, dots, underscores, hyphens. Wrong format and Thansa skips it with a "invalid slug" warning.

### Step 2: Write plugin.yaml

```yaml
name: Shipping fee calculator
slug: tinh-tien-ship
version: 1.0.0
description: Calculate shipping by weight and region from the shop's price list.
author: You
enabled: false            # always start DISABLED, enable after reading code
min_mode: readonly        # readonly | safe | full
tools: [tinh_tien_ship]
hooks: []                 # example: [post_tool_call]
```

The `tools` and `hooks` lists here are just for **displaying chips on the card**. The real tools come from the code in `plugin.py`, so keep these lists in sync with your code to avoid confusion.

### Step 3: Write plugin.py

```python
def register(ctx):
    def handler(args, ctx):        # args is dict; return string. Errors return "ERROR: ..."
        kg = float((args or {}).get("kg") or 0)
        return f"Shipping fee: {int(kg * 5000)} VND"

    ctx.register_tool(
        name="tinh_tien_ship",
        description="Calculate shipping fee by weight (kg). Use when customer asks about shipping cost.",
        handler=handler,
        min_mode="readonly",
        schema={"type": "object",
                "properties": {"kg": {"type": "number", "description": "Package weight"}},
                "required": ["kg"]},
    )
```

Tips for writing:

- Tool name starts lowercase, only lowercase, digits, underscores.
- `description` is what engines read to decide **when** to call it, so be clear on the situation and parameters. Vague description and the tool sits silent.
- Handler can be regular or `async` function. Return string is simplest; return dict and Thansa auto-converts to JSON.
- `ctx` has `ctx.slug`, `ctx.vault_root` (working brain) and `ctx.data_dir` (plugin's own state folder, **not** inside brain so doesn't clutter your notes).
- To self-refuse when not ready (not logged in, missing key), pass `check_fn=` a function returning `None` when OK or a Vietnamese sentence explaining why not.
- One broken plugin **doesn't crash** Thansa: every load step and tool call is wrapped, errors only show on that plugin's card.

### Step 4: Unlock with env var

User-installed plugins are **blocked by default**, even if `enabled: true`. To unlock:

1. Open `.env` file in the repo root (create if missing, see [.env Configuration](16-cau-hinh-env.md)).
2. Add line: `JAVIS_ENABLE_USER_PLUGINS=true`
3. Save and **restart Thansa**.
4. Back on **Plugins** page: the orange warning box vanishes, enabled plugins show **● running**.

Values accepted: `1`, `true`, `yes`, or `on` (case-insensitive). Old name `JAVIS_ENABLE_VAULT_PLUGINS` still works for backward compat, but use the new name.

## Safety guardrails (read before installing unknown plugins)

This is the most important part of this page.

- **User-installed plugins run REAL PYTHON CODE, inside Thansa's server process.** They get the process's permissions: read/write files, call network, read env vars. So Thansa **hard-gates by default** and only runs when you manually set `JAVIS_ENABLE_USER_PLUGINS=true` then restart. This blocks someone from dropping a malicious folder into a brain and getting code execution on your machine.
- **Only unlock after YOU READ THE CODE** of every plugin in those two folders. The env var unlocks **all** user plugins, not individually.
- **Built-in plugins (label "Built-in") skip this gate** because they come with the Thansa release. They run normally when the env gate isn't set.
- **Plugins Thansa creates in chat always start disabled** (`enabled: false`) and read-only mode. Thansa won't auto-enable; you read the code then click **Enable**.
- **Don't write plugins for money/order/message/post actions.** Those belong in MCP connections and permission layers where they're logged and gated. Plugins should `min_mode: readonly` unless you explicitly need different.
- **Don't duplicate built-in plugins into your brain.** They ship with the app and self-update; a copy in your brain shadows the original and won't update anymore.

## Ask Thansa to make a plugin by speaking

You don't have to type the two files by hand. Open a chat and speak, e.g.: "Make me a plugin to calculate shipping by weight, price table is 5k per kg, below 1kg charge flat rate."

Thansa auto-picks the right capability first (if only instructions needed, makes a skill; if it's a data source, suggests MCP), checks for duplication with what the brain already has, then writes the plugin folder. When done it tells you the file name and reminds you the plugin starts disabled plus how to unlock the env var.

Then you do 3 things: open `plugin.py` and read the code (use **Files** page if it's in a brain), set the env var if you haven't, then go to **Plugins** and click **Enable**.

## Hooks: run around every tool call

Beyond tools, plugins can register hooks. Currently two events supported:

| Event | Fires when | Receives |
|---|---|---|
| `pre_tool_call` | Right before any tool runs | `tool_name`, `args`, `mode`, `vault_root` |
| `post_tool_call` | Right after tool finishes | plus `result` |

Hooks wrap **every** tool call, including MCP and core tools, not just this plugin's. Use for logging, counting, alerting. When no plugin registers a hook, Thansa doesn't wrap, so zero overhead. Plugin `tool-audit` is a working example: enable it, chat a bit with tool calls, ask Thansa "which tool is used most".

## Quick reference of buttons and status

| You see | Means / Action |
|---|---|
| **● running** (green) | Plugin loaded, tools available to engines |
| **⚠ waiting for env** (orange) | You enabled it but haven't set `JAVIS_ENABLE_USER_PLUGINS=true`, or set it but haven't restarted |
| **⚠ error** (red) | Manifest broken or code won't load; reason shown below chips |
| **○ off** (gray) | Plugin present but disabled, no tools out |
| **● enabled (not loaded yet)** (orange) | Rare: enabled but loading failed for another reason. Reload page, if same check server log |
| Label **Built-in** / **Global** / **This brain** | Plugin source (app / global folder / one brain) |
| Chip **🔧 name** | One tool from this plugin; this is the name engines call |
| Chip **🪝 name** | One hook this plugin registers (`pre_tool_call` or `post_tool_call`) |
| "minimum permission: read-only / write (safe) / full" | Minimum permission for this plugin's tools |
| Button **Enable** | Turn on plugin (card currently off) |
| Button **Disable** | Turn off plugin (card currently on) |
| Card appears faded | Plugin not running |
| Orange warning box at top | User plugins blocked; built-in ones run |

## Tips

- Before writing a plugin, ask: is the missing thing **how to do it** or an **action**? How → write skill, cheaper and easier to fix. Action → plugin. Data source → MCP.
- Read `system/plugins/datetime-vn/plugin.py` as starter template: short, pure stdlib, full example of a read-only tool. To see a hook example, read `tool-audit`.
- Put plugin in **Global** unless you have reason to bind it to one brain. Global doesn't depend on brain so you can switch brains and still use it.
- Not using a plugin? **Disable** it instead of deleting, next time enable it back.
- Disabling unused plugins also shortens the tool list sent to the model, helps it pick tools better.
- Want to know what capabilities Thansa sees (agents, skills, workflows, loops, plugins)? Open `Javis/index.md` in the brain via **Files** page; this file auto-rebuilds each time you toggle a plugin.

## Common issues

- **Card says "⚠ waiting for env":** you didn't set `JAVIS_ENABLE_USER_PLUGINS=true`, or set it but didn't restart. This var is only read at startup.
- **Set env var but still blocked:** check `.env` is in the repo root folder, line isn't commented with `#` at start, and value is `true` (or `1`/`yes`/`on`). On Docker, set the var in container Environment, not a file on the host.
- **New plugin folder dropped but doesn't appear:** must be **directly** in the plugins folder (no extra nesting), and must have `plugin.py` inside (or `__init__.py`). Missing one and Thansa doesn't treat it as a plugin. Folder name must be valid slug too (lowercase no accents).
- **Card says "⚠ error" with "missing plugin.py":** folder only has `plugin.yaml`. Add the code file.
- **Card says "⚠ error" with "manifest error: ...":** `plugin.yaml` has YAML syntax wrong. Common: description with colons not quoted.
- **Card says "⚠ error" with "missing register(ctx) function":** `plugin.py` doesn't have a `register` function, or you named it differently. Must be exactly `register` and take one parameter.
- **Card says "⚠ error" with a Python error name (e.g., `ModuleNotFoundError`):** plugin code uses a library not installed in Thansa's Python. Install it in Thansa's venv, restart.
- **Plugin running but engine doesn't see tool:** likely tool name **duplicates** an existing MCP or core tool. Thansa doesn't let plugins shadow core tools, skips the duplicate and logs once to server. Rename your tool (prefix it uniquely). Core reserved names: `javis_connections`, `javis_read_file`, `javis_list_dir`, `javis_write_file`, `javis_use_skill`.
- **Tool returns `ERROR: tool '<name>' requires higher permission`:** the run is permission-capped. If it's a scheduled task, raise its mode (see [Scheduled Tasks & Reminders](08-viec-dinh-ky.md)); if your plugin, check `min_mode` in `register_tool`.
- **Tool returns "Not connected ...":** plugin needs a connection you haven't wired. Follow the exact instruction in the error, usually go to **Connections** (or **Models** for image plugin).
- **Click Enable reports "plugin not found":** on-screen list stale compared to disk (you deleted or renamed the folder). Reload page.
- **Click Enable reports "write manifest error":** Thansa can't write `plugin.yaml`, usually file permissions or it's locked by another app. See [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Related

- [Skills](06-skills.md) - when the missing thing is instructions, not code.
- [Connections & Business Data](09-mcp-va-so-lieu.md) - wire outside data; Meta Ads, Facebook Pages, Apify plugins pull tokens from here.
- [Models & Engine](10-models-va-engine.md) - why all engines can call plugin tools.
- [Scheduled Tasks & Reminders](08-viec-dinh-ky.md) - three permission levels for background tasks; plugin `javis-schedule`.
- [Zalo Agent MCP](12-zalo.md) - Zalo now uses standard MCP, no separate plugin.
- [.env Configuration](16-cau-hinh-env.md) - how to set env vars and restart.
- [Agents & Workflows](07-agents-va-workflows.md) - other capability types of Thansa.
