# Tasks (Kanban): delegate goals to AI running in background

*[Tiếng Việt](21-viec-kanban.md) · **English**

The **Tasks** page is where you delegate a goal to Thansa and let it run in the background without you sitting at the chat window. You write a sentence describing what needs to be done, AI automatically normalizes it into a specification, chooses the worker type, claims the task, and runs; when done it sends the result back to Telegram to the right person.

The most commonly misunderstood point: this is **not a drag-and-drop Trello board**. You don't drag cards, you don't click to run each card. This screen is for **observing the queue and handling exceptions**; the dispatcher handles the running.

## What is this feature

Thansa treats the task queue like a runtime for AI. A task goes through the following lifecycle:

1. **You delegate a goal** (from the Tasks page, or by speaking in chat, or suggested by the Self-learning page).
2. **AI specifies (triage)**: a short run of the background model reads the raw goal and returns JSON containing clear intent, one **capability** (`files`, `research`, `mcp-read`, `code`, `external-write`), one **execution_mode** (`suggest`, `auto`, `full`) and a list of **completion conditions**. This step doesn't execute anything.
3. **Into the queue**: task transitions to ready state, waiting its turn.
4. **Dispatcher claims task**: each task is held by exactly one worker (locked by transaction in SQLite), with a hold time of 90 seconds and a heartbeat of 20 seconds.
5. **Worker runs**: a headless AI process works within the brain, checks the result itself then reports briefly.
6. **Complete**: success, or stop and wait for you (missing info, missing permission, or you ticked "Request result review").

Worker uses the same **background engine** as other background features, so Claude Code, ChatGPT/Codex and API providers (OpenRouter, OpenAI, Anthropic, Google Gemini) can all run this queue. See [Models & engine](10-models-va-engine.md).

Don't confuse three similarly named things:

| Thing | What it is | Read where |
| --- | --- | --- |
| **Tasks** (this page) | One-time task queue, AI runs in background | this page |
| **Recurring Tasks** | Loop that repeats on schedule and reminders with fixed times | [Recurring Tasks & Reminders](08-viec-dinh-ky.md) |
| Checkbox `- [ ]` in note | Task you manually tick in markdown file | [Tasks & Dataview in notes](19-task-va-dataview.md) |

## Where to open in Thansa

On the left navigation bar, open the **Tasks** group then click **Tasks**. Page title is **Tasks (Kanban)** with subtitle "AI automatically specifies, dispatches and runs background tasks".

The board is tied to **the brain selected** at the top of the dashboard. Changing brain changes the task board too; each brain has its own queue.

Right below the title is a circle and text about the dispatcher:

- "Dispatcher running · max 2 workers" (bright circle): the server's dispatcher process is alive.
- "Dispatcher not running" (dark circle): the dispatcher process hasn't started.

Important note: this line only says whether the process is alive, **not** whether this brain's board auto-runs. What decides that is **Dispatcher mode** right below it.

## How to use (step by step)

### Step 1: Choose dispatcher mode

In the **Dispatcher mode** block there are 3 buttons:

| Button | Actual meaning |
| --- | --- |
| **Off** | Default for a new board. AI doesn't auto-claim any tasks. |
| **Observe** | AI also doesn't auto-claim. Use when you want to queue tasks then manually run them. |
| **AI auto-operate** | Dispatcher automatically scans the queue and runs tasks. |

Only **AI auto-operate** makes tasks auto-run. The other two keep the dispatcher still for this brain; the difference is in the **Pause AI** button: that button both sets mode to **Off** and cancels all running workers for this brain.

Mode change takes effect immediately; no restart needed.

### Step 2: Delegate a goal

Click **+ Delegate goal** in the top right to open the form (click again to close). The form has:

- **Goal**: one short sentence saying clearly what needs to be done. Example hint right in the input: "Analyze top-selling products this week and write 3 posts". Leave blank and Thansa says "Enter title".
- **Context and desired output**: multi-line box, natural language is fine. This is where you clarify the output you want (which file, where to put it, how long, data source). Leave blank and Thansa uses the Goal text.
- **Route**: choose **AI auto-chooses worker** (default) to let AI decide, or choose one **Workflow: `<name>`** to force the task through exactly that workflow. Workflow list comes from the selected brain; see [Agents & Workflows](07-agents-va-workflows.md).
- **Priority**: **🔺 High**, **🔼 Medium** (default), **🔽 Low**. High-priority tasks are claimed before the queue gets crowded.
- **Exception**: checkbox for **Request result review**. Tick it and tasks don't auto-close when done; they stop in "Needs review exception" state waiting for you to check.

Click **Delegate to AI** to create, or **Cancel** to close.

One tip on duplicate prevention: if the board still has an unfinished task with a matching title (matched after removing diacritics and special chars), Thansa returns the old task instead of creating a copy.

### Step 3: Read the board

The KPI row has 4 numbers:

| KPI | Counts what |
| --- | --- |
| **Workers running** | Number of workers actually running for this brain |
| **Waiting** | Total tasks waiting for spec, waiting for dependencies, and waiting for turn |
| **Need handling** | Blocked tasks plus tasks waiting for your review |
| **Completed 24h** | Tasks that moved to complete in the last 24 hours |

Below that are 4 frames:

- **Running** (subtitle "N workers"): tasks actually running right now.
- **AI queue** (subtitle "N tasks"): tasks waiting for spec, waiting for dependencies, or waiting for turn.
- **Need handling** (subtitle "N exceptions"): blocked tasks and tasks waiting for review. Empty frame shows "No exceptions. AI operating normally."
- **Recent history** (subtitle "24 hours and newer"): tasks completed and cancelled, max 20 cards.

If a frame has nothing yet it shows "No tasks yet."

Each task card has: priority icon and title, status circle on the top right, metadata line (capability, "attempt 1/3", time changed like "just now" / "12 min ago" / "3 hours ago"), then blocking reason (orange text) or first 240 chars of result, finally an action button row.

The board refreshes itself every 3 seconds, so you don't need to click anything to see progress.

### Step 4: Open details for one task

Click on the card body to slide open a detail panel from the screen edge. Inside:

- Full intent content (version AI specified, not the raw sentence you entered).
- Info line: status, capability, "mode `<suggest|auto|full>`", "priority `<1|2|3>`".
- Action button row same as on the card.
- **Blocking reason** (if any).
- **Result** in full (if any).
- **Run (N)**: each time worker held the task, with run status and start time; if error shows error.
- **Lifecycle log**: every event of the task, e.g. `created`, `claimed`, `specified`, `retry_scheduled`, `blocked`, `completed`, `operator_move`, `auto_archive`.

Close the panel with the **×** button at top, **Esc** key, or clicking the dark background area.

### Step 5: Handle exceptions

Depending on status, the card (and detail panel) shows these buttons:

| Button | Shows when | Does what |
| --- | --- | --- |
| **✓ Review exception** | task waiting for review | Close task as complete |
| **↻ Retry** | task blocked or waiting for review | Push task back to queue for another run |
| **Stop task** | task running | Cancel the running worker |
| **Remove from board** | any task not running | Archive task, off the board but history stays |

**Remove from board** asks to confirm first: "Remove this task from board? Task will be archived to preserve history." Running tasks must **Stop task** first before removal. If action fails, Thansa shows error box with raw server message, or "Cannot update task".

## Task statuses

Here's the full translation table of words shown on the status circle.

| Screen text | Internal status | Meaning |
| --- | --- | --- |
| **AI specifying** | `triage` | New task, waiting for (or being) AI normalized into executable spec |
| **Waiting for dependency** | `todo` | Task has dependencies, must wait for parent tasks to finish first |
| **In queue** | `ready` | Has spec, waiting for turn to be claimed by worker |
| **Running** | `running` | A worker holds it and is executing |
| **Needs review exception** | `review` | Done but you requested result review |
| **Needs handling** | `blocked` | Blocked: missing info, missing permission, or out of retries |
| **Complete** | `done` | All done |
| **Cancelled** | `cancelled` | You stopped it, or worker was cancelled mid-run |
| (not shown on board) | `archived` | Archived: you clicked Remove from board, or auto-cleaned 3 days after completion |

A few notable paths:

- After spec step, task is **not** counted as using one retry; retries are reset so execution gets full 3 attempts.
- Temporary errors (timeout, rate limit, 429, network loss, engine busy) make task **automatically** re-queue, up to 3 retries, logging event `retry_scheduled`. Only when retries run out does it switch to "Needs handling".
- If worker dies mid-run without reporting heartbeat, task is recovered to queue with event `reclaimed`, doesn't stay stuck at "Running".
- If worker detects it needs a decision or data, it returns result starting with `[[NEEDS_INPUT]]`, task switches to "Needs handling" with exactly one reason line.

## Quick reference table of buttons and statuses

| Top button | Does what |
| --- | --- |
| **+ Delegate goal** | Open/close task delegation form |
| **Run tick now** | Force dispatcher to claim and run one ready task for this brain. Works even if mode is Off or Observe. If no ready tasks, nothing happens |
| **↻** | Reload board immediately, don't wait for 3-second tick |
| **Pause AI** | Set mode to **Off** and cancel all running workers for this brain |

## What background workers can and can't do

Worker is a **headless** AI session: no screen, doesn't ask you mid-run, no logged-in browser, no hands to click buttons. It only has the tool set matching the capability that the spec step chose:

| Capability | Can use | Blocked |
| --- | --- | --- |
| `files` | Read/write/organize files in brain | Bash, web search |
| `research` | File tools plus read web and search | Bash |
| `mcp-read` | File tools plus read real data via MCP | Bash, web search |
| `code` | File tools plus Bash (edit and test code) | Read web, web search |
| `external-write` | File tools plus MCP, but see rule below | Bash, web search |

Most important rule: tasks in `external-write` (send message, post, create order, schedule, change something outside) **only run when execution_mode is `full`**. Not enough permission makes task block immediately with reason "Task needs external action. Only mode=full workers can execute." Spec step also doesn't auto-grant `full`: it only keeps `full` when your goal text explicitly said you allow auto-action (phrases like "full control", "auto-send", "auto-post", "no need to ask"). If it doesn't see permission phrase then it downgrades to `auto` so kernel blocks.

In other words: by default Thansa **doesn't** auto-spend money, doesn't auto-send messages, doesn't auto-post from the task queue. To do that you must say so explicitly in the goal.

Besides, workers also can't see source code repos outside the brain, and can't do things that need you personally logged in (cookies, OTP, QR scan, password change).

## Receive results: to the exact place you delegated from

Each task ending at complete, review-waiting, or blocked status **automatically sends one message** back to the exact channel it was delegated from, brief content like:

- `✅ Task '<title>' completed.` with first few lines of result.
- `✅ Task '<title>' done, needs review exception.`
- `⚠ Task '<title>' blocked, needs handling.` with line `Reason: ...`

Every message ends with "See details on Tasks page." because full details are here, not crammed into the message.

Who gets the message, and where:

- **Delegated in chat on dashboard** → result shows straight as one message from Thansa **in that same conversation**. Server writes to session history first then pushes up, so even if you close the tab or F5 and reopen you still see it. If you were viewing a different conversation the message sits in the original session and that session pops up in **History**.
- **Delegated from Telegram chat** → reports back to exactly who sent the message (carries their chat id).
- **Unclear who delegated** (created outside chat) → reports to **first Telegram ID** in whitelist; bot not yet on means skip this step, task runs normally. See [Telegram Channel](11-telegram.md).

> Before 0.9.289 only Telegram route existed. Anyone delegating task on web without Telegram connected got total silence - no status, no response. Now web chat is a real reporting channel, no need for Telegram.

## See background tasks running right in the chat box

From 0.25.2, right above the chat input there's a **background task bar**. It only shows when something is truly alive, and says one thing: right now something is running for you.

| Color | Meaning |
|---|---|
| **Green** | Task **actually running**. Dot blinks. |
| **Yellow** | Task **delegated but not auto-running** because dispatcher mode isn't **AI auto-operate** yet. Bar says where to turn it on. |
| **Gray** | Only loop or reminder waiting to trigger. |

Bar gathers all three sources: Kanban tasks, [loops and reminders](08-viec-dinh-ky.md). Tasks from the current conversation get their own border and separate count ("2 tasks running in background · 1 from this chat"), because "machine is busy" and "my task is running" are different things. Click **Tasks page** at top right to open the full board.

Bar polls server every few seconds, and polls immediately when a chat turn ends or a background task just reported result. No tasks means it hides completely, doesn't take up chat space.

> Why it exists: before this version the chat box said nothing about background tasks, so "Thansa is running something for me" and "Thansa forgot" looked identical. You'd have to guess to open this page, but no one had reason to guess.

## Thansa auto-corrects when it makes a false promise

Also from 0.25.2, after each chat turn server checks if the answer promised feedback ("I'll report back if there's a result", "when done I'll tell you", "just wait a moment for me"), then compares against actual background tasks. If it promised but nothing's running Thansa automatically adds a correction line right below the answer, explaining there won't be any report and what to do instead.

This isn't censorship: it doesn't block or edit the answer, just states the fact below. The reason is one chat turn ends the moment Thansa finishes speaking - there's no mechanism to wake it back up to finish what it promised, so a false promise won't come true ever.

## Delegate tasks by speaking in chat

You don't have to open this page. Speaking directly in chat like "delegate background task: re-check all notes in Wiki this month then list notes missing links" and Thansa auto-creates a task in the queue, keeping who said it so the result reports back to the right place.

Thansa learned to pick the smallest tool that's enough, so it only creates a task when the job is **one-time, needs background run or needs review**. Questions that answer in the current turn get answered right away; jobs that repeat on schedule or have fixed times go to [Recurring Tasks & Reminders](08-viec-dinh-ky.md).

Remember task created via chat still sits in the queue of the brain where the chat is, and still needs **AI auto-operate** mode to auto-run. If board is **Off**, task just waits until you turn it on or click **Run tick now**.

From 0.25.2 Thansa **says that out loud at delegation time**: delegating to a **Off** or **Observe** board it reports back the task is queued not running, including how to turn it on. Before this it always ended with "Background task running, result coming back" no matter the mode - a false promise Thansa itself had no way of knowing was false. The bar above the chat also turns yellow in exactly this case.

This runs on **every brain** from 0.17.1, via tool `javis_task`. Before that only Claude Code and ChatGPT/Codex could delegate from chat, the only route being HTTP call by command that only those two engines can run. API engines (OpenRouter, OpenAI, Anthropic, Gemini, Groq, Ollama) heard the request then did nothing, and didn't report errors. If you ever saw "told it to delegate a task but board stayed empty", odds are this was it.

Two things the tool **doesn't** do, on purpose:

- **Can't create `full`-mode tasks.** Full mode lets task auto-act outside (create order, spend money, run ads, send message) and can't be undone. Thansa creates `suggest` or `auto` only; for full you manually promote on this page, where you see clearly what you're allowing.
- **Doesn't move columns, doesn't cancel tasks, doesn't review waiting tasks.** Those need to see the board, so they stay on this page.

## Tasks suggested by the Self-learning page

The **Self-learning** page has a capability switch named **Tasks (Kanban)** that lets the learning engine suggest background tasks from conversation. This switch is **off by default** in current version, after looking at a real board and seeing most engine-generated tasks are things headless workers can't do (need cookie, need to send message outside, just waiting for someone else to review, touching code outside brain). Tasks now only birth when you tell it straight.

If you turn it back on yourself, these barriers still hold:

- Max 3 tasks per learning run, and only suggestions with high-enough confidence.
- Suggestions containing secret or injection commands get blocked straight away.
- Gate "impossible tasks" blocks ones needing login/OTP/QR/password, ones sending or posting outside (Zalo, Telegram, email, fanpage, comment), ones just waiting for someone else to reply, and ones touching code outside brain. Blocking reason gets logged.
- Tasks from self-learning go straight into the spec stage like manually delegated ones, and **don't** force review: only when missing info, missing permission or you turn on review flag do they need handling.

Details in [Self-learning](22-tu-hoc.md).

## Where board data lives

- **Main source**: file `kanban.sqlite3` in Thansa's state folder (variable `JAVIS_STATE_DIR`, default is `server/` folder). This holds the lifecycle, runs, and event log. Placed outside brain on purpose so running tasks don't get git-synced.
- **Readable copy**: `Thansa/kanban.json` in brain, rewritten each time board changes. This file backs up and lets old Thansa read it; editing it by hand doesn't change the real queue.
- Old board from earlier Thansa versions gets imported once, and tasks stuck at "running" status from old process move back to queue.
- Tasks complete or cancelled over **3 days** auto-archive to keep board from swelling.

## Technical limits

| Spec | Value |
| --- | --- |
| Workers running in parallel | 2 (change with environment var `JAVIS_KANBAN_MAX_WORKERS`, clamp to 1-8, shared across all brains) |
| Dispatcher scan tick | 5 seconds, woken immediately on new task |
| Task hold time / heartbeat tick | 90 seconds / 20 seconds |
| Spec step time ceiling | 3 minutes |
| One worker run time ceiling | 15 minutes |
| Max retries | 3 |
| Result size stored | 20,000 chars |
| Board refresh tick | 3 seconds |

## Call directly by API

The web page doesn't cover everything the server can do. These endpoints exist; use when you want to automate or bulk-clean the board (all params go form-style, with `brain=<name>`):

| Endpoint | What it does |
| --- | --- |
| `GET /kanban` | All board data |
| `GET /kanban/health` | Mode, dispatcher status, status count |
| `GET /kanban/task/show?id=...` | One task with runs and event log |
| `POST /kanban/task` | Create task. Beyond form fields also accepts `chat_id`, `capability`, `execution_mode`, `deps` (comma-separated id list) and `idempotency_key` |
| `POST /kanban/run` | Run exactly one task by id |
| `POST /kanban/task/move` | Move task to different status |
| `POST /kanban/purge` | Delete completed tasks. Default only touches archived and cancelled; add `include_done=1` to also touch complete |
| `POST /kanban/clear` | Wipe board except running tasks. No undo |

The two cleanup endpoints at the end have no button on the UI, exactly as designed: they delete for real.

## Tips

- Write goal as "output is X", not "think about". The **Context and desired output** box the clearer you are about target file, length, data source the better the spec step writes completion conditions, and the less worker wanders.
- Important tasks tick **Request result review**. You spend one click but guarantee you read the result before closing.
- Want to try a task now without turning on auto mode: leave mode **Observe**, delegate, then click **Run tick now**.
- Task needs real data (revenue, calendar, ads) then say the source straight in goal, e.g. "pull from POS". Spec step will pick `mcp-read` and worker gets to open the connections. See [Connections & business data](09-mcp-va-so-lieu.md).
- Board full of dead test tasks then don't delete each card: **Remove from board** for a few important ones you want to keep history for, rest just auto-archive after 3 days.
- Read **Lifecycle log** in detail panel before concluding "AI did it wrong". Very often the answer sits there: task was reclaimed for timeout, or downgraded permission because it's in the external-action group.

## Common problems

**Top line says "Dispatcher running" but no tasks move.**
Two different things. That line says the server's dispatcher process is alive; whether tasks get claimed depends on **Dispatcher mode** of this brain. Set to **AI auto-operate**.

**Clicked "Run tick now" but nothing happens.**
Means no task in ready state: queue empty, or tasks waiting for dependency, or already 2 workers running. Check KPI **Waiting** and **Workers running** to see which case.

**Task stuck at "AI specifying".**
Spec step needs a background model run. If engine isn't ready or out of quota the task re-queues and retries. Check [Models & engine](10-models-va-engine.md) and [Usage: token & cost](23-muc-dung-token.md). When background model can't be called Thansa still has a fallback branch guessing capability by keyword so queue doesn't freeze.

**Task blocked with reason "Task needs external action. Only mode=full workers can execute."**
This is a safety gate, not an error. Your task is in the send-message, post, create-order or change-something group. If you truly want it to auto-act, delegate again and write clear in goal you allow auto-action; if not, let Thansa draft instead and you manually send.

**Task blocked with reason starting "Worker needs more info".**
Worker saw missing decision and guessing would harm. Open detail panel, read reason line, give more clarity by re-delegating a clearer goal, then click **↻ Retry** or delete the old one.

**Can't click "Remove from board" or "↻ Retry".**
Task is running, no status change allowed. Click **Stop task** first, wait for card to leave **Running** frame, then try again.

**Task done but don't see report anywhere.**
Task delegated in web chat needs to carry the chat session code so result reaches that frame. Thansa auto-adds when you delegate by speaking in chat; task created by hand on this page or by curl has no session code so only goes to Telegram. If message went to Telegram and silence: bot not on, no chat id in whitelist, or task doesn't know who delegated so message went to first Telegram ID not the account you thought. See [Telegram Channel](11-telegram.md).

**Thansa promised "I'll wait for tasks to finish then summarize" but never summarized.**
That's a false promise and got banned from 0.9.289: one chat turn ends the moment Thansa finishes speaking - there's no mechanism to wake it up. Task only auto-pushes raw result **to chat**. For a summary version, delegate ONE more task just to summarize (use `deps` pointing to previous tasks), or message again one sentence after results arrive.

**Board empty even though I delegated tasks yesterday.**
Three causes, in order of likelihood: you're on a **different brain** (switch at dashboard top), task finished over 3 days ago so auto-archived, or someone called the bulk-clean endpoint.

**Background tasks eating my quota.**
Each task is a real AI session. Lower parallel workers to `JAVIS_KANBAN_MAX_WORKERS=1`, or set mode to **Off** when not needed. Track spending on [Usage: token & cost](23-muc-dung-token.md), which separates "Thansa auto-runs" from "You typed by hand".

## Related

- [Recurring Tasks & Reminders](08-viec-dinh-ky.md) - tasks that repeat and reminders with fixed times.
- [Self-learning](22-tu-hoc.md) - the engine learns and can suggest tasks.
- [Agents & Workflows](07-agents-va-workflows.md) - workflows used in Route field.
- [Models & engine](10-models-va-engine.md) - which engine is running workers.
- [Telegram Channel](11-telegram.md) - where task reports arrive.
- [Connections & business data](09-mcp-va-so-lieu.md) - real data source for `mcp-read` tasks.
- [Usage: token & cost](23-muc-dung-token.md) - how much background tasks burn.
- [Tasks & Dataview in notes](19-task-va-dataview.md) - checkbox tasks in markdown, different from this page.
- [Configure .env](16-cau-hinh-env.md) - `JAVIS_STATE_DIR`, `JAVIS_KANBAN_MAX_WORKERS`.
