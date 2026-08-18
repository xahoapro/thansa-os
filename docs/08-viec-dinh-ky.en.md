# Scheduled Tasks & Reminders

*[Tiếng Việt](08-viec-dinh-ky.md) · **English***

The **Scheduled Tasks** page is where you assign Thansa jobs that run automatically when you're not at the machine: repeating tasks according to a cycle (called **loop**) and reminders at specific times. Each repeating task wakes up on schedule, does exactly one task you describe, self-verifies then logs and sends results to Telegram.

This page combines tasks from **all brains**, not just the currently selected brain in the sidebar.

## What is this feature

Two types of tasks live on the same page:

| Type | Nature | Saved at |
|---|---|---|
| 🔁 **Loop** (repeating task) | Every N minutes it wakes up to do exactly one job then stop. Runs indefinitely until you turn it off. | One `.md` file in `Javis/loops/` of the brain |
| ⏰ **Reminder** | A specific time point ("30 minutes from now", "8:30 AM"), or a cron schedule ("7 AM every day"). | `Javis/reminders.json` of the brain |

Key difference: repeating task counts by **time interval** between runs, reminder counts by **time point**. "Every 2 hours scan orders" is a loop; "7 AM every morning report revenue" is a reminder using cron.

You can create **many loops in parallel**, each with its own file. But they run **sequentially**: at any given time only one loop is running system-wide. Thansa's scheduler checks every 30 seconds, each check picks **one** overdue loop that's furthest behind to run. So actual run time may lag a few seconds behind your cycle, and if you set many at once they queue up instead of overlapping.

Loop **reads real data through MCP** (POS, ads, calendar, analytics...) to work. Whether it can write files or perform actions outside depends on **permission level** you choose, see "Three permission levels" below.

Loop is edited directly by opening its `.md` file in Obsidian or [File management](05-quan-ly-tep-tin.md). Run state (last run, today's cycle count, error chain) lives separately in `Javis/loop-state.json`, owned by server, so you edit the definition without worrying about stepping on concurrent writes.

## Where to open in Thansa

1. Open Thansa dashboard (default `http://localhost:7777`).
2. Look at the left navigation bar, click **Tasks** group to expand.
3. Click **Scheduled Tasks**.

Page opens with subtitle "Scheduled tasks + reminders waiting". From top to bottom you see: a short intro paragraph, button line **+ Add task** and **■ Stop running task**, search field, list of task cards grouped by brain, finally **Recent log** block.

Form to create/edit tasks is hidden until you click **+ Add task** or **Edit** on a card.

## How to use (step by step)

### Step 1: Click "+ Add task"

Form appears right below the button line.

### Step 2: Choose task type

In **Task type** section there are two buttons: **🔁 Loop** (pre-selected) and **⏰ Reminder**. Click to switch. Switching task type changes the form fields below.

Note: when you click **Edit** on an existing card, these two buttons are locked and grayed out. Form can only edit loops; reminders can only be canceled or moved to different brain right on the card.

### Step 3: Set name and description

- **Name**: short name shown on card, example "Scan email every 2 hours". Leave empty and it says "Enter name".
- **Task description (each loop Thansa does exactly this)**: this is a **required** field and the most important one. Thansa doesn't self-invent work; each loop it does exactly what you write in this field then stops. Leave empty and it says "Enter task description (Thansa needs to know what to do each loop)".

When you choose **⏰ Reminder**, the description field label changes to "Reminder content (Thansa will remind or do exactly this)", and error when empty is "Enter reminder content".

Write description as specific as possible: say clearly what to read, what to do, where to save. Write self-sufficiently, don't depend on current chat context, because the task runs when no one's there. Examples:

> Each loop read 1 unprocessed source in 06 - Sources then suggest Wiki page to create.

> Read today's order count via MCP POS, if low then draft 1 caption to push inventory into 05 - Projects.

### Step 4a (loop): Choose mode and cycle

- **Mode**: three buttons **Suggest (read-only)**, **Auto (safe)**, **⚠ Full power**. New task defaults to **Suggest (read-only)**. See "Three permission levels" section before switching.
- **Cycle (minutes, minimum 5)**: minutes between runs. Field pre-fills **120**. Enter less than 5 and server auto-raises to 5.

Below form there's a reminder line: "Suggest = read-only + suggestions. Auto (safe) = draft file writes + MCP reads, NO money/orders/posting. Full power = auto-operate anything."

### Step 4b (reminder): Set "When" and "Type"

- **When**: time input field. See "What the 'When' field understands" section below for full formats it understands. Leave empty and error is `Enter time (ex "30 minutes from now", "8:30 AM", "0 7 * * *")`.
- **Type**: two buttons **⏰ Remind only** (pre-selected) and **🤖 Auto then report**.
  - **⏰ Remind only**: at the time Thansa shoots a straight Telegram message, beginning with "⏰ Reminder: " then to content you write. Doesn't call model, uses no tokens.
  - **🤖 Auto then report**: at the time Thansa runs engine to **do** that job then send result to Telegram.
- **What it's allowed to do** (only shows when choosing 🤖 Auto then report): three levels, default **Full power**.
  - **Read-only**: read real data via MCP and read files, then report back. Write nothing, do nothing outside.
  - **Can write files**: add permission to write draft files in brain. Still blocked hard from money, orders, ads, posting, sending messages.
  - **Full power** (default): use all tools you've authorized, including outside actions. This is the only level that can do jobs like "at time then send message", "at time then post", "at time then schedule".

  Why default is full power: reminder does **exactly one job you already wrote and timed**, i.e. a chat command moved to a different time, so constraining it tighter than when you're sitting chatting becomes you saying "10 AM tomorrow send for me" but at 10 AM it reports it's not allowed to send. In exchange, when choosing this level the form shows one red warning field, and the task card gets a **full power** label so you glance and know. Remember: **task runs with no one sitting next to it**, no approval step for each part, and real actions can't be undone. Only assign what you're ready to let it do.

### Step 5: Choose brain

The **Brain** (where to save task) field lets you pick which brain will hold this task, default is the brain you're viewing in the sidebar. When **Editing** an existing loop, this field is locked to its original brain. To move the task to another brain use **Move brain…** on the card, not by changing during edit.

### Step 6: Save

Click **💾 Save**. Button changes to "Saving..." then returns. Form auto-closes and list reloads after save. Errors show right next to button as "⚠ ..." in yellow.

If you choose **⚠ Full power** mode, before saving there's a confirmation dialog warning again about risk. Click cancel there and nothing saves at all.

### Step 7: Turn task on

**New loop created from dashboard is always OFF.** This is intentional for safety: you review the description, then click **Turn on** on its card. Until you click Turn on, it never runs by itself.

Reminder is different: timed and enqueued right after creating, no need to turn on.

## Three permission levels (loop mode)

| Button on form | Label on card | What Thansa can do |
|---|---|---|
| **Suggest (read-only)** | suggest | Only use read tools, including reading real data via MCP. **No file writes**. Each loop suggest 2-3 specific action options. Safest, default. |
| **Auto (safe)** | auto (safe) | Read MCP + **can write** draft files in brain (create/edit note drafts). Still hard-blocked from money, orders, ads, posting, sending. Plus self-verify step after each loop. |
| **⚠ Full power** | ⚠ full power | Open all: every tool and MCP, **outside actions no need to ask**. |

Choosing **⚠ Full power** shows one red warning block in the form, opening with: "**⚠ FULL POWER MODE - high risk.** Loop will auto-operate REALLY via MCP without asking: can **create/edit orders, run ads (spend real money), send messages/email, post**."

Read carefully here: full power loop runs in background on schedule, **no one approves each step**, and **real actions can't be undone**. Thansa asks confirmation twice (once saving, once when you click **Turn on**) exactly for that. If you need this mode, run on **Suggest (read-only)** a few loops first, read the log to see what it plans, and write the task description very narrow on scope.

## The "When" field understands what

Field accepts four formats, hints pre-filled in field: `30 minutes from now · 8:30 AM · 0 7 * * * · 2026-07-20 09:00`:

| You type | Thansa understands |
|---|---|
| `30 minutes from now`, `2 hours from now`, `1.5 hours`, `3 days` | Count down from right now. Units accepted: minutes, hours, days (with or without diacritics). |
| `8:30 AM`, `8:30`, `8 AM` | Time of day. If that time already passed, auto-move to **tomorrow**. |
| `2026-07-20 09:00` | Specific date and time. |
| `0 7 * * *` | Cron expression 5 fields (minute, hour, day, month, weekday). This is **repeat schedule**: run at that time, after run auto-calc next time. `0 7 * * *` = 7 AM every day. Macros `@daily`, `@hourly`, `@weekly`, `@monthly` also work. |

All times in Vietnam time (UTC+7). First three formats are **one-time** (after running they vanish from queue); cron repeats forever until you cancel. One-time can't be more than roughly one year away.

## Task list

### Grouped by brain

Each brain is one block with title `🧠 <brain name>`, small label **viewing** for the brain you're currently viewing in sidebar and **default** for default brain. Brain being viewed gets pushed to top. Brain with no tasks and not the viewing brain gets hidden for cleanliness.

Within each block, loops are listed first, then **Reminders waiting** section.

Brain you're viewing but has no tasks shows "No tasks in this brain. Click **+ Add task**, or tell Thansa in chat." No tasks system-wide shows "No scheduled tasks or reminders."

### Search field

Field **🔍 Find task by name...** above list filters cards as you type, **removes Vietnamese diacritics** so typing "kho" still matches "khô", typing "email" still matches "Email". Brain block with no matching cards auto-hides. No matches at all shows "No tasks matched."

### Reading a loop card

Card starts with `🔁 <task name>` with slug (file name) dimmed beside, status in top right:

| Status | Meaning |
|---|---|
| ⏳ running | This task's loop is running right now |
| ⚠ auto-paused | Failed 3 times in a row so Thansa locked it, see "Auto-pause" section |
| ● on | On, will run per cycle |
| ○ off | Off, won't run (card appears dimmed) |

Line two shows mode and cycle, like `auto (safe) · every 120 minutes`, plus extra info if any: old task type name (when different from "Custom"), `silent 23-07`, `max 3/day (done 1)`, `⚙ code · <folder>`.

Line three is quick history: `last HH:MM` (or `never run`), latest verify result (` · ok` if clean, or `· ✓ Passed: ...` / `· ✗ Not passed: ...`), and `· next ~HH:MM` if on. Auto-paused task has an extra line `⚠` with reason and time.

### Reading a reminder card

Reminder card is more compact: name (or content if no name), then one sub-line with time and type. Type is `remind` (remind only), `auto + report`, or `script`. Only `auto + report` adds permission label (`read-only`, `can write file`, or red `full power`).

Time always says **when to run**, no guessing cron:

- One-time: `one time, next 08:30 tomorrow (14 hours left)`.
- Cron schedule: schedule translated to words then next run time, example `7:00 AM every day · next 07:00 tomorrow (14 hours left)`. Raw expression still shown beside `0 7 * * *` for anyone wanting to check.
- Interval repeat: `every 60 minutes · next 15:20 today (12 minutes left)`.

Time in day shows `today HH:MM`, tomorrow shows `tomorrow HH:MM`, further shows `HH:MM DD/MM`.

If prior run had error (e.g. failed to send), card has extra line `⚠ prior run error: ...` so you know to handle, instead of silently running wrong every day.

### Buttons on card

All buttons target the card's own brain, not the brain selected in sidebar.

On loop card:

- **Turn on** / **Turn off**: toggle state. Turning on a **⚠ Full power** task asks confirmation. Turning on also clears auto-pause state.
- **▶ Run now**: run one loop right now, don't wait for cycle. Button changes to "Running..." and list auto-reloads after about 2.5 seconds. Note: this button **doesn't** save unsaved form, it runs what's already saved in file. Clicking Run now also clears auto-pause since this is your deliberate action.
- **Edit**: open form again with this task's content.
- **Delete**: ask confirm then delete file `Javis/loops/<slug>.md`.
- **Move brain…**: dropdown to move task to different brain, keep file and run state. If destination brain already has task with same name, Thansa refuses and errors, no overwrite. Running task can't move, try again later.

On reminder card:

- **Edit**: open form again with this reminder's content. Can change name, content, type and time. For cron schedule the "When" field pre-fills old expression, edit then Thansa auto-recalc next run time. For one-time the field stays empty and shows current time in hint: **empty means keep old time**, only type if you want to change.
- **Cancel**: stop running but record stays in history to look back.
- **Delete**: gone for good, no undo.
- **Move brain…**: move to different brain, keep id and all settings.

## No Telegram? Thansa won't create schedule

Reminders and "auto then report" jobs only matter when at the time it **tells someone**, and the only reporting channel now is Telegram. If bot Telegram not enabled, no token, or no Chat ID allowed, Thansa **refuses to create** and says clearly what's missing with link to [Kênh](11-telegram.md) page to set up.

This is where the most misunderstanding happened before: Thansa builds job "report email and schedule each morning", job runs at exact time, but result sends to nobody and no one tells you it's missing Telegram.

If you still want to create (e.g. plan to set up Telegram later), click **Create anyway** next to warning. Job will run at exact time, result saves in Thansa, just hasn't sent anywhere yet.

When Scheduled Tasks page detects no reporting channel, it shows a warning bar at page top, since jobs already created still run but haven't reached you.

Creating schedule by voice in chat also follows this rule: Thansa checks first if data source already set up and there's place to report result, missing then it says so and asks you, never creates if unsure.

## Run now and stop running task

Button **■ Stop running task** at page top cancels the task **currently running system-wide**, regardless which task it is. Since only one loop runs at a time this button doesn't need task selection. It just cuts the running process, **doesn't turn off the task**: next cycle it runs again. To stop for good, click **Turn off** on the card.

This button doesn't touch "🤖 Auto then report" reminders running.

While one loop is running, page auto-refreshes every 5 seconds so you see state changes.

## Auto-verify step

With **Auto (safe)** and **⚠ Full power** modes, after doing the work, Thansa runs an extra check pass: a "reviewer" assumes the result is WRONG, reads back related files to cross-check. This verify pass **always read-only**, even for full power jobs.

This step skips if the prior loop errored, or if result says "no new work".

Check criteria change by job type:

- Regular job: result hit target, reasonable and doable, didn't make up or wreck files.
- Job touching business numbers: suggestion stuck to real numbers, reasonable and specific, didn't make up numbers.
- Job thickening Wiki: followed Wiki rules, didn't make up or miss citations, didn't wreck links.
- Job using profile `code` (set in `.md` only): must run `python -m py_compile` or `node --check` on each edited file and all pass, plus diff small (under ~80 lines).

With **Suggest** and **Auto (safe)** there's also one hard criteria: detect any money/order/ad/post/message action via MCP is **fail right away**. Only **⚠ Full power** mode allows real actions, so criteria change to: fail only if did wrong or over scope, causing clear harm, or hitting stuff outside your intent.

Result shows **✓ Passed** or **✗ Not passed** with brief reason, both on card and in log.

## Auto-pause after 3 failures

If a loop fails **3 times in a row** (engine error, or verify ✗ Not passed), Thansa auto-locks it and notes "Auto-paused 20/07 14:35: 3 errors/verify failures in a row". Card changes to **⚠ auto-paused** and won't run by itself until you step in.

This reason goes in runtime state, **doesn't** edit your `.md`. To run again, click **Turn on** or **▶ Run now** on card, both clear lock and reset error chain. Before turning back on, read log to see why it failed.

## Report to Telegram

This is Thansa's default behavior: **each loop completes it auto-sends result to Telegram** for whoever requested it. Message starts with `✅ Loop '<task name>' just ran...` (or `⚠` if errored), then summary and verify line.

Send to who:

- Loop created via chat has the requester's chat_id pinned, so reports to that exact person.
- Loop created on dashboard doesn't know who you are, so reports to **first Telegram ID** in the allow list.

Want a loop to stop reporting each loop because it's too noisy, open file `Javis/loops/<slug>.md` and set `notify: false` in frontmatter.

Reminders also shoot to Telegram. Reminder created on dashboard doesn't know recipient so sends to **all IDs** in allow list; reminder set by voice in chat sends to the person who set it.

Both need bot enabled, see [Kênh Telegram](11-telegram.md). No bot yet then job still runs and logs, just no report.

## Recent log

Block at page end. Beside title there's one dropdown to filter:

- **Log for viewing brain**: combine all loops of the brain you're viewing in sidebar.
- Or select exact one task, showing `<task name> · <brain name>`.

Thansa loads 200 recent items then splits page **10 items** per page, buttons **← Prior** and **Next →**, line counting "Page 1/5 · 47 items". Nothing yet shows "No log."

Each item starts header line like `## [2026-07-20 14:35] doc-source · loop (custom/auto) - scheduled`, where `scheduled` means ran per schedule, `manual` means you clicked **▶ Run now**. Below is summary of what it did, **Verify** line if any, and warning line if this exact loop triggered auto-pause.

Log also lives as real file in brain: `Javis/loop-log/YYYY-MM-DD.md`, one file per day. Open via [File management](05-quan-ly-tep-tin.md) if you want to see beyond 200 items.

## Create schedule by voice in chat

You don't have to enter this page. Tell Thansa straight in [Chat](02-tro-chuyen-va-giong-noi.md) or Telegram also works, example:

- "Create for me a task every 2 hours scanning orders then summarizing."
- "7 AM every morning remind me to check yesterday's revenue."
- "30 minutes from now remind me to call customer."
- "Any tasks running?"
- "Cancel order scan task."

Thansa uses tool `javis_schedule` (a bundled plugin) to auto-pick right storage: repeat loop by time interval goes to file in `Javis/loops/`; fixed time point repeating or one-time goes to reminder storage. Tool auto-sets slug to spec and **blocks name collision**: already have same-name task then it errors and tells you to edit old, never creates a copy.

Two hard safety fences of this path, no parameter changes:

- Loop created via chat **always** at `enabled: false` and `mode: suggest`. You must go to Scheduled Tasks page click **Turn on** for it to really run.
- Unclear cycle (e.g. you just say "each morning" without time) then tool errors and asks again, never guesses.

## Advanced fields (edit in `.md` only)

Dashboard form stays compact. Things below must open `Javis/loops/<slug>.md` and edit frontmatter part (via [File management](05-quan-ly-tep-tin.md) or Obsidian). Save done, dashboard reads again, no restart needed.

| Field | Meaning |
|---|---|
| `quiet_hours` | Silent hours, format `23-07` (don't run 11 PM to 7 AM, Vietnam time). Only accepts whole hour numbers. |
| `max_runs_per_day` | Limit loops per day. `0` = no limit. Card shows `max N/day (done M)`. |
| `workspace` | `vault` (default, run in brain) or absolute folder path. Folder not exist then run errors right away. |
| `tools_profile` | `vault-safe` (default) or `code`. `code` profile opens Bash, WebFetch, WebSearch and works in `workspace`, but **turns off all MCP**. This profile is for loop editing code in folder you assign, and it really edits files there, think carefully. |
| `ambient_mcp` | Off by default. Set `true` to let loop see connectors installed on machine (Gmail, Drive, calendar via claude.ai). Turn on still blocks Bash, WebFetch, WebSearch hard. |
| `owner_chat` | Telegram chat_id to receive reports. Leave empty then reports to first ID in allow list. |
| `notify` | `false` to turn off report every loop of this task alone. |
| `goal` | Job type. Default and what dashboard always creates is `custom`, each loop does body of file exactly. Old values `business`, `brain`, `product` still work for hand-written files, and when different from `custom` card shows extra label. |

**File body** (below second `---`) is the "Task description" field you type on form.

## Quick reference: buttons and status

| You see | Meaning / action |
|---|---|
| **+ Add task** | Open form to create new task |
| **■ Stop running task** | Cancel task running system-wide, don't turn off task |
| **🔁 Loop** / **⏰ Reminder** | Choose task type (lock when editing) |
| **Suggest (read-only)** | Read-only, no file write. Default |
| **Auto (safe)** | Write draft files in brain, block money/orders/posting |
| **⚠ Full power** | Can do outside actions. Ask confirm 2x |
| **⏰ Remind only** | At time shoot Telegram "⏰ Remind: ..." |
| **🤖 Auto then report** | At time run engine do job then report result |
| **What it's allowed to do** | Permission level of Auto type: Read-only / Can write / Full power (default) |
| **💾 Save** / **Cancel** | Save or close form |
| Field **🔍 Find task by name...** | Filter cards by name, remove diacritics |
| **Turn on** / **Turn off** | Gait run state of loop |
| **▶ Run now** | Run one loop right now, clear auto-pause |
| **Edit** / **Delete** | Edit or delete loop file |
| **Move brain…** | Move task to different brain |
| **Edit** (on reminder) | Change name, content, type, time or cron |
| **Cancel** (on reminder) | Stop running, keep in history |
| **Delete** (on reminder) | Delete record, no undo |
| **Create anyway** | Create schedule even without reporting channel |
| ⏳ running | This loop running |
| ⚠ auto-paused | Failed 3 times, self-locked |
| ● on / ○ off | Auto-run or don't |
| ✓ Passed / ✗ Not passed | Result of verify step |
| **← Prior** / **Next →** | Flip log page, 10 items per page |

## Tips

- **Start with Suggest (read-only).** Let it run a few times, read log see quality of suggestions, then bump up to **Auto (safe)**.
- **Don't set cycle too tight.** 5-10 minutes a loop burns tokens and real machine load. Most needs only a few hours once. Monitor spend at [Usage: tokens & cost](23-muc-dung-token.md).
- **Use cheap model for background job.** [Models & engine](10-models-va-engine.md) has "Background job model" block applies to all loop, Kanban job, reminder, self-teach. Pick a cheap model there saves a lot.
- **Set `quiet_hours` for overnight jobs.** If you leave Telegram report on, job at 3 AM wakes you up. Add `quiet_hours: 23-07` to file, or set `notify: false`.
- **One job = one task.** Description trying to do many things means each loop does one piece half-done. Split into many loops, each one cycle, much easier to read logs.
- **Job that needs no thinking don't call model.** Remind type "⏰ Remind only" uses no tokens at all.

## Common trouble

**Created task but it never runs.** Loop created from dashboard (and from chat) defaults **off**. Check card is at **● on**; if it's **○ off** then click **Turn on**.

**Clicked ▶ Run now but see nothing.** Three possibilities. One is another loop somewhere running already (system only runs one) so request silently dropped; wait a bit then try again. Two is the loop needs time, wait then reload page and check **Recent log**. Three is engine not ready, see section below.

**Card shows ⚠ auto-paused.** This job failed 3 times in a row. Open log, filter to this task, read reason. Fix task description then click **Turn on** or **▶ Run now** to unlock.

**Verify keeps saying ✗ Not passed.** Verify step sees result not good (made up numbers, wrong Wiki rule, out of scope). Read reason in log, open related file via [File management](05-quan-ly-tep-tin.md) to check. Usually task description too vague so each loop it understands different.

**Result says "Claude CLI not installed".** Brain not ready on machine. See [Start & setup first](01-bat-dau-thiet-lap.md) and [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

**Run with ChatGPT says `bwrap: Failed to make / slave: Permission denied`.** Codex (ChatGPT) wraps all file read/write by bubblewrap, but bubblewrap won't start in Docker container, so background job can't read any file. Docker image from 0.25.9 pre-disabled that sandbox (`JAVIS_CODEX_SANDBOX=off`) so just **upgrade to newer version** and done. Self-built container set that env var, or switch background job brain to Claude. Details at [Env settings](16-cau-hinh-env.md).

**Loop says no business numbers.** It only reads real numbers when you already set up source. Go to [Connect & business numbers](09-mcp-va-so-lieu.md) to hook POS, ads or sales channel. No source then that loop stops and reports back one line.

**Can't load task list.** Page shows "Can't load task list (slow network or timed out)" with **Retry** link. On weak VPS or huge brain, first load can be long; Thansa auto-tried once before reporting. Click **Retry**.

**Created task via Telegram then don't see it on dashboard.** Task fell into different brain. This page combines all brains so scroll down to other `🧠` blocks, or type task name in search. To move to right place use **Move brain…** on card.

**Didn't get Telegram report.** Check bot on and Chat ID in allow list, see [Kênh Telegram](11-telegram.md). Also check loop file isn't set `notify: false`.

**Edit `.md` file then loop vanishes.** File corrupted frontmatter (missing `---` pair, or bad YAML) so Thansa skips it. Reopen file, compare with another working loop file, fix to proper format.

## Related

- [Tasks / Kanban](21-viec-kanban.md) - queue of one-time jobs run by AI dispatcher, different from loops on this page.
- [Self-teach](22-tu-hoc.md) - separate background job for memory and Wiki, has Curator and LINT Wiki.
- [Kênh Telegram](11-telegram.md) - turn on bot to receive reports each loop and reminders.
- [Connect & business numbers](09-mcp-va-so-lieu.md) - hook up data source so background job reads real numbers.
- [Models & engine](10-models-va-engine.md) - pick cheap model for background job.
- [File management](05-quan-ly-tep-tin.md) - open task definition file and log file.
- [Chat & voice](02-tro-chuyen-va-giong-noi.md) - create task and reminder by voice.
- [Plugins](20-plugins.md) - understand `javis_schedule` and bundled tools.
