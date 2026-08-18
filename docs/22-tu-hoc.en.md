# Self-learning: Thansa gets smarter over time

*[Tiếng Việt](22-tu-hoc.md) · **English**

Every time you chat with Thansa there's information worth keeping flowing past: a fact about your work, a concept just explained, a process just done. The **Self-learning** page loops through that, picks those things up and writes them into the brain, so next time Thansa doesn't have to ask again.

This page guides turning self-learning on, picking its strength level, understanding what it learns and what it blocks, and undoing when it learns wrong.

## What is this feature

After a few chat turns, Thansa opens a **separate learning process** to re-read the exchange just now and extract knowledge. This process is locked down very tight:

- **Read-only.** It only gets `Read`, `Glob`, `Grep`, `LS`. Tools like `Bash`, `WebFetch`, `WebSearch`, `Task` are straight blocked.
- **Isolated, no MCP.** It runs with empty MCP config in strict mode, so it can't reach POS, ads, Zalo or any data source you already connected. If empty MCP config can't be made Thansa refuses to run, instead of running temporarily with the machine's MCP.
- **Pinned in brain**, with 240-second ceiling per learning run.
- **It DOESN'T write files.** The only output is one JSON chunk saying "should learn what". Python code in Thansa does the writing. So there's no case where model overwrites MEMORY.md by accident, writes outside brain, or erases your notes.

Before writing, code still scans two more layers: **scans for leaked secrets** (API key, Telegram token, JWT, database connection string, lines tagged "password"/"mật khẩu") and **scans for injection attempts** like "ignore all prior instructions". Anything caught gets blocked, not written, reason logged. Reverse too: conversation content fed to learning process has injection commands disabled, so a message from a guest can't hijack the learning loop.

Finally, Thansa only lets writing go to exactly these folders: `memory/`, `Memory/`, `Wiki/`, `skills/`, `.claude/skills/`, `Javis/` in the brain. Any path escaping this list gets restored immediately.

## Open where in Thansa

On the left navigation bar, open **Brain** group, then click **Self-learning** (brain icon 🧠). Top of page shows title **Self-learning** with subtitle "Rewire Memory · Wiki · Skill (safe, undo works)".

The page works on **the brain selected**. Switch brain at the top then come back here and every stat, commit and log switches to the new brain too.

## How to use (step by step)

### Step 1: Turn on self-learning

At **Turn on self-learning** box, click the button. Button switches between two labels:

| Button label | Meaning |
| --- | --- |
| `● On` | Thansa is self-learning after every few chat turns |
| `○ Off` | Learning nothing, even if you chat a lot |

First time you click on, button shows "Git-initing..." for a moment: Thansa turns the brain folder into a local git repo. This happens once only and **doesn't push anything online**. With git, each learning is one commit, so you can see it again and undo with one click.

After that, note line right below changes to actual result, like "Git-inited brain → auto-write safe/undo works.". If machine has no git, that line starts with "⚠ Not git-able (missing git?)". The note still says "auto will self-downgrade dry-run", but that's old text: from current version, self-learning **still writes files normally even without git**, just loses one-click undo and backup route. See "Machine has no git, what then" below.

Click the button again to turn off. When off, Thansa saves the off state right away, no need to click Save config.

### Step 2: Choose write mode

**Write mode** box has three buttons. Click one to choose; description line below changes.

| Button | Description shown | Reality |
| --- | --- | --- |
| **Try run** | "Only log 'will learn' - DON'T touch files. Safest." | Still runs analysis and logs to learn log, but creates no files in brain |
| **Suggest** | "Like try run, let you check first." | Exactly like try run for files: lists what it plans to learn, not touching |
| **Auto-write** | "Write straight to Memory/Wiki - git-commit + undo works." | The only mode actually writing files. With git comes a commit |

**Default for fresh install is Auto-write.** If you want to observe for a few days before letting Thansa touch brain, switch to Try run then read the learn log for a while.

### Step 3: Choose what to learn

**Learn what** box has four switches. Filled circle `●` is on, empty circle `○` is off. Click to toggle.

| Switch | Default | Learns what |
| --- | --- | --- |
| **Memory (Memory)** | On | Steady facts about you and your business, saved as files in `memory/facts/` and one line added to `MEMORY.md` |
| **Knowledge (Wiki)** | On | Concepts, frameworks, reusable processes, saved as notes in brain's Wiki folder |
| **Skill (Skill)** | On | Multi-step processes Thansa just did and sees repeated, saved as `skills/<slug>/SKILL.md` |
| **Tasks (Kanban)** | **Off** | Suggest background tasks, push to board on **Tasks** page |

Hint line under the four buttons: "Wiki/Skill should turn on after you're used to Memory (phase 2/3 roadmap). Tasks = learned and suggest background task to Tasks board (Kanban) - only actually creates when Auto-write mode, and task always waits for you to review."

About the **Tasks** switch: it defaults off and Thansa **actively turns it off once** for machines that had it on. The reason is very practical: looking at a real board, nearly every engine-generated task is something headless workers can't do (needs login, needs to send outside, just waits for someone else, needs to touch code outside brain). From then on tasks only birth when you **tell it straight** in chat. Switch is still here for anyone wanting to turn it back on.

**Recommended gradual turn-on:** turn on Memory first, run for a few days then open `MEMORY.md` to see if Thansa remembers right. OK then turn on Wiki Knowledge. After practice turn on Skill too, since wrong skill breaks how Thansa handles going forward. Leave Tasks for last, and only when you truly want Thansa to self-suggest background tasks.

### Step 4: Turn on Curator if you want periodic maintenance

**Curator (periodic maintenance)** box has one button `● On` / `○ Off`, **default is off**. See "Curator" section below for what it does.

### Step 5: Save config

Click **💾 Save config**. Button changes to "Saving..." then "✓ Saved" for about a second and a half then reverts.

Write mode, four switches and Curator **only take effect after clicking Save**. The on/off button alone saves immediately.

### Step 6: Click Learn now to try one run

Click **▶ Learn now**. Thansa saves current config then runs one learning on the selected brain. Button shows "Learning..." for about 2.5 seconds then auto-reloads sections below.

Note: **Learn now still respects write mode**. In try run mode clicking Learn now also doesn't create files, just logs.

If no chat turn is queued, Thansa takes the newest conversation of that brain to learn from. Very short conversation it silently skips, no log entry created, so if Learn log shows nothing new it usually means that brain has no content long enough to learn from.

## When Thansa learns automatically (auto tick)

You don't click anything. After each chat turn ends, Thansa sorts that turn then adds it to a queue per brain:

- Very short turn or just greeting/"ok"/"thanks" gets dropped immediately, doesn't count.
- Turn with **special knowledge signals** (questions "what is", "how many steps", "formula", "principle", "procedure", "concept", "how to") gets marked separate.
- You say "remember", "remember this for me", "save this" → turn marked **urgent**.

Every 30 seconds Thansa checks the queue and fires one learning batch when one of these hits: **3 accumulated turns**, or urgent turn and 30 seconds passed, or special knowledge turn and **3 minutes silent**, or **10 minutes silent** with queued turns left.

Each learning batch reads at most 3 nearest conversations, takes 12 messages each, total content cut around 24,000 chars. Meaning it learns from the **just-happened** part, not digging back through all history.

Only one learning batch runs at a time. Self-learning, Curator and other writing processes share one lock on the brain so they don't step on each other.

## Filtering gate before writing (why Thansa learns less than you think)

This part tends to puzzle: you see log "learned" but no file appears. Reason is each type has its own gate.

**Memory (facts):**
- Confidence must be 2 or higher to write.
- **Add only, never overwrite.** If memory file exists it skips, unless new info is marked as replacing the old. Then old file gets tagged `superseded_by` and one history line added, not deleted.
- After writing, Thansa adds one line to `MEMORY.md` pointing to the new memory file.

**Knowledge Wiki:**
- Density (level of explanation structure) must be 2 or higher.
- Anything **Thansa said itself without a source** then **can't go in Wiki**. Gets pushed to `_open-questions.md` for you to verify. This blocks Thansa from poisoning its own memory with its own words.
- Duplicate concept with note already there means no new note, just log addition proposal.
- Contradiction with old note means **don't overwrite**, add section `## Contradiction` to old note with new view, and open one question needing check.
- After writing, Thansa adds line to `index.md` (section "## Self-learned") and one line to Wiki's `log.md`.

**Skill:**
- Before writing Thansa opens **one independent second check**, assuming proposed skills are wrong or extra, keeping only what passes.
- `description` longer than **150 chars** gets blocked (router cuts there so remainder vanishes silently), starts with empty cliché like "Trigger when..." also blocked.
- **Never overwrites existing skill**, and **never resurrects skill you turned off**.

**Tasks (Kanban), if you turn the switch:**
- Max 3 tasks per batch, confidence 2 or higher.
- One gate blocks straight any task headless worker can't do for sure: ones touching login / cookie / OTP / QR / password / 2FA, ones sending or posting outside (Zalo, Telegram, email, fanpage, comment), ones just waiting for someone else, and ones touching code outside brain. Blocking reason gets logged.

Everything blocked shows up in Learn log under **Blocked** section with specific reason. Reading that part tells you exactly why the file didn't come out.

## Token-saving caps

Self-learning runs on **background task model** not main model. You pick that model on **Models** page (under **Connections** group), block "◆ Background task model" says it serves "loop · Kanban task · reminder · self-learning · source digest". Pick cheap model there makes self-learning cheap too.

Besides Thansa sets three hard caps, counted per day and independent of turn batching:

| Cap | Default value | When hit |
| --- | --- | --- |
| Minimum gap between batches | 90 seconds | That batch doesn't write files |
| Learning batches per day | 40 | Downgrade to try run |
| Estimated tokens per day | 300,000 | Downgrade to try run |

When downgraded, Thansa still analyzes and still logs "will learn", just doesn't write files. Log status says exactly why, e.g. "dry-run (hit cap fork/day → downgrade dry-run (backpressure))".

Clicking **▶ Learn now** also hits exactly these caps: analysis always runs, but to make files you must be in Auto-write mode **and** not hit any cap.

## Curator: periodic maintenance, deletes nothing

**Curator (periodic maintenance)** button turns on a cleanup loop running every **24 hours**. Description on screen: "Clean index, LINT Wiki (suggest only), compress MEMORY.md. Deletes nothing."

Specifically it does three jobs:

1. **Rebuild memory index.** Scans `memory/facts/`, spots any memory file missing a line in `MEMORY.md` then adds it. Catches case where you create memory file by hand and forget to add to index.
2. **Warn when index swells.** `MEMORY.md` loads into **every chat turn**, so it being long makes everything cost more. Over around **150 lines**, Curator logs "⚠ past index cap (~150 lines) - think about compressing.". It **doesn't auto-compress**, merging old memories is your call.
3. **Check Wiki health (LINT).** Finds duplicate notes, orphan notes no one points to, broken wikilinks, unresolved contradictions, and gaps. Result is **suggestion list only** logged under "Wiki LINT (suggestions, not fixed)". Curator doesn't self-fix and doesn't delete any note.

The old "🩺 LINT Wiki" button on dashboard is gone. LINT now runs inside Curator.

Curator has three smart money-saving tips:

- **If Wiki unchanged skip that pass entirely**, don't call model.
- **If it changes only check recently-changed notes**, don't re-scan whole store. Except when noting note deleted or renamed then must scan all, since those break wikilinks everywhere.
- **Every 30 days scan everything once** to catch slow-building cross-note issues.
- **Brain silent over 14 days gets skipped.** Self-learning brain list only grows never shrinks, so without filter Curator would run on abandoned brains every 24 hours.

To run one pass right now, click **🧹 Curator now**. Button shows "Cleaning..." then auto-reloads.

## Quick button and status table

| Button / line | Where | What happens |
| --- | --- | --- |
| `● On` / `○ Off` | Turn on box | First time on git-inits brain then saves right away. Off also saves right away |
| `Try run` / `Suggest` / `Auto-write` | Write mode box | Pick write level. Only Auto-write makes files |
| `● Memory (Memory)` … `○ Tasks (Kanban)` | Learn what box | Four switches pick knowledge type to learn |
| `● On` / `○ Off` | Curator box | Turn on 24-hour maintenance loop |
| **💾 Save config** | Button row | Save mode + switches + Curator. Shows "Saving..." then "✓ Saved" |
| **▶ Learn now** | Button row | Save config then run one batch on chosen brain |
| **🧹 Curator now** | Button row | Run one maintenance pass right now |
| **■ Stop** | Button row | Cancel running batch and Curator pass |
| **↶ Undo last learning** | Button row (orange text) | Asks confirm "Undo (git revert) last learning?" then git revert the last learning commit |

## "Stats" line

Right below button row is one line summarizing brain health, like:

`Stats · Memory: 87 · Wiki: 174 · MEMORY.md: 18363B · Batch today: 3 · Token est: 41200 · Learn commit: 26`

Read this line how:

| Field | Meaning |
| --- | --- |
| **Memory** | Count of files in `memory/facts/` |
| **Wiki** | Count of notes in Wiki folder (not counting `index`, `log` and files starting with underscore) |
| **MEMORY.md** | Index file size in bytes. This loads every chat turn so smaller is cheaper |
| **Batch today** | Learning batches successfully written today, vs cap of 40 |
| **Token est** | Self-learning tokens burned today (rough estimate), vs cap of 300,000 |
| **Learn commit** | Learning commits found in brain's git history (count up to 50 newest commits) |

## Block "Thansa self-learned what (nearest commit)"

This block lists up to 12 newest learning commits of the brain, each line has commit title, short hash, time, and list of up to 6 changed files.

Commit titles look like `learn: +2 fact +1 wiki +0 skill (2026-07-29)` for a batch, and `curator: reindex memory (2026-07-29)` for maintenance. Only these two prefixes count as "learning commit", so init commit Thansa made at repo start won't show here and also won't be hit by the Undo button.

Nothing yet shows "No learning commit yet.". If brain is not git repo yet, block shows orange line "Brain not git repo - turn on Self-learning to git-init (will see/undo commits)."

**Undo:** click **↶ Undo last learning**, confirm, Thansa runs `git revert` on the last learning commit. Success shows dialog "Undone:" with commit title. Three common fail reasons:

- "Brain not git repo"
- "No learning commit to undo"
- "Learning files being edited, fix first: ..." (you're editing exactly these files from that commit. Save or undo your edits then try. Unrelated edit-in-progress won't block undo)

One reassurance: git here tracks only **curated knowledge** (memory, Wiki, skill, `MEMORY.md`). Raw log, learn log, loop log, conversation log, `attachments/` and `inbox/` all stay outside, so revert is always clean and never touches personal files.

## Block "Learn log"

Last block shows up to 10 newest entries, gathered from three newest log files in `Javis/learn-log/` of the brain (one file per day `YYYY-MM-DD.md`).

Each entry has timestamp, type (`learn` or `curator`), reason (`auto` when self-fired, `manual` when you clicked), status (`auto-write` or `dry-run` with reason downgraded), then list of what learned like `fact=[...] wiki=[...] skill=[...]`, and commit hash if any. Body is one Vietnamese summary line of the batch, with **Blocked** section listing each thing blocked gate blocked and why.

Nothing yet shows "No learn log yet.".

This is plain markdown file, open on **File** page (group **Brain**) if you want full text instead of 10 newest entries.

## Sync brain with GitHub

Midpage is one block **⇅ Sync brain with GitHub (2-way)**. Here because it uses git too, but it's a different feature: push whole `brains` folder to private repo and pull back from another machine. Full guide (create repo, make token, handle `.conflict-*`) at [Backup brain to GitHub](18-sao-luu-github.md).

## Machine has no git, what then

Self-learning **still runs and still writes files** normally. The write mode box will show extra line: "ℹ No `git` on machine: Self-learning STILL runs normally, just missing one-click undo/backup to GitHub. Install git to turn on undo + brain backup."

What you lose without git:

- **↶ Undo last learning** button won't work.
- Block "Thansa self-learned what" empty, can't see each learning's file changes.
- Can't sync brain to GitHub.

Other safety gates stay: learning process still read-only, still scans secrets and injection, memory still add-only-not-overwrite, and still can't write outside allowed folder list.

Install git then turn self-learning off and back on once so Thansa git-inits brain.

## Tips

- **Want to guarantee Thansa remembers one thing, say it straight "remember ..." in chat.** Turns with "remember", "remember for me", "save this", "remember that" get marked urgent and learn right after, not waiting for 3 turns.
- **Check if Thansa learns right by reading `MEMORY.md` itself.** Open **File** page, go `memory/MEMORY.md`. Each line is one memory. Line wrong then fix or delete there, faster than undoing a whole commit.
- **Keep `MEMORY.md` compact.** This file loads every chat turn. Over around 150 lines it's time to merge small memories into bigger ones.
- **For quality Wiki knowledge, state the source.** Anything only Thansa itself reasoned won't get in Wiki. You affirm or cite a named source then it writes.
- **Try run for a few days before Auto-write** if brain has lots of hand-written notes and you want to be sure Thansa won't mess up naming.
- **Switch background task model to cheap one** on **Models** page if self-learning eats lots of quota. Self-learning doesn't need strongest model.

## Common problems

**Turned on self-learning, chatted all day but learned nothing.**
Check in order: is write mode **Auto-write** (try-run and suggest don't make files); do turns have "substance" (hi, "ok", "thanks" get dropped); did you hit 3 turns or 10 minutes silent yet; did stats line **Batch today** hit 40. Learn log always has the exact answer.

**Log says "learned" but no new file.**
Read **Blocked** section in that exact log entry. Common reasons: memory duplicates existing file so no overwrite, Wiki note rejected because Thansa said it without source, note duplicates concept, skill duplicate name or `description` over 150 chars.

**Clicked Learn now but nothing changed.**
If a batch or Curator pass is already running, new click gets refused. Wait for running one (max 240 sec) or click **■ Stop** first.

**Clicked Undo got "files being edited".**
You're editing exactly these files from that commit. Save or undo your edits, then click undo again. Unrelated work-in-progress won't block.

**Self-learning went to wrong brain.**
This page works on selected brain at top. Switch to right brain, save config and Learn now again. The auto loop itself learns from the actual chat brain, not from which brain you have open here.

**Curator turned on but doesn't run.**
Runs every 24 hours, and skips brain silent over 14 days. Also when Wiki didn't change any notes it skips that part (log says "wiki unchanged"), because scanning costs and there's nothing to fix. To run one pass right now click **🧹 Curator now**.

**Scared self-learning will trash hand-written notes.**
Learning process has no write power. Write code doesn't overwrite existing memory, doesn't overwrite existing Wiki notes, doesn't overwrite existing skills, deletes nothing, and only touches `memory/`, `Wiki/`, `skills/`, `Javis/` folders. Any path escaping gets restored right away.

## Related

- [Second Brain: memory and Wiki](13-second-brain-bo-nho-wiki.md) - structure of `memory/facts/`, `MEMORY.md` and Wiki folder that self-learning writes
- [Skills](06-skills.md) - skills from self-learning sit with hand-written skills in same list, turn on/off same way
- [Tasks (Kanban)](21-viec-kanban.md) - where tasks from the Tasks switch end up to run
- [Backup brain to GitHub](18-sao-luu-github.md) - sync block lives in this page
- [Models & engine](10-models-va-engine.md) - pick background task model for self-learning
- [Manage files](05-quan-ly-tep-tin.md) - open `MEMORY.md`, Wiki notes and learn log files to read or hand-edit
- [Troubleshoot & FAQ](17-khac-phuc-su-co.md)
