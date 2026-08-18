# Tasks & Dataview in notes

Since version 0.9.216, notes in Thansa's brain are more alive in Obsidian style: checkboxes `- [ ]` in notes **are clickable and auto-save**, and ` ```dataview ` blocks **run live** in the dashboard - showing task lists, note lists, summary tables pulled from your entire brain. These two features draw inspiration from two famous Obsidian plugins: **Tasks** and **Dataview**, reimplemented by Thansa in lightweight form without needing Obsidian or any plugin installs.

## 1. Clickable task checkboxes

### What it does

In markdown, a task line written in standard format:

```markdown
- [ ] Call customer A back
- [x] Locked in bulk quote for steel shipment
```

Before, Thansa only displayed these pretty boxes; to check one you had to switch to Source mode and manually change `[ ]` to `[x]`. Now you just click the box: checkmark appears, text strikes through, and **the file saves instantly** - no need to hit a 💾 Save button.

### Where to check

- **Files page** (under **Brain** on left nav): open a `.md` file, stay in **Edit** mode (render view, default). Click checkbox to check and auto-save.
- **File edit popup from chat** (when you click a file link in Thansa's answer): same, check and it saves.
- **Inside chat messages**: checkboxes display only for reading, not clickable. Reason: chat content isn't tied to a file to record the change.
- **In dataview query results**: clickable, writes straight to the source file that has that task (see section 2).

### Quick-type tasks with autocomplete menu (Obsidian style, lite)

In **Edit** mode of a note, Thansa has an autocomplete menu like Obsidian's Tasks plugin but simplified to avoid overwhelm:

1. Type `- [ ]` at line start then **press spacebar** - that line becomes a real task with checkbox. If you're in a bullet list already, just type `[ ]` then spacebar.
2. Stand at **end of the task line**, press spacebar - menu pops with 6 items: 📅 due date, ⏳ scheduled, 🛫 start date, and 3 priority levels ⏫🔼🔽.
3. Pick a date option - another menu: **Today / Tomorrow / This weekend / Next week / Pick date…** (opens calendar). Pick and Thansa inserts `📅 2026-07-28` right on the line, standard obsidian-tasks format so all queries understand it.

Navigate with arrow keys + Enter, or click. Esc closes, keep typing and the menu auto-hides, won't interfere.

### Date and priority symbols (Tasks plugin style)

Thansa understands emoji symbols the obsidian-tasks plugin uses, written right in the task line:

| Symbol | Meaning | Example |
|---|---|---|
| 📅 | Due date | `- [ ] Submit report 📅 2026-08-01` |
| ⏳ | Scheduled to do | `- [ ] Make slides ⏳ 2026-07-30` |
| 🛫 | Start date | `- [ ] New Year campaign 🛫 2026-12-01` |
| ✅ | Completion date | auto-added when you check it |
| 🔺 ⏫ 🔼 🔽 ⏬ | Priority from highest to lowest | `- [ ] Handle complaint ⏫` |

Two auto behaviors like Tasks plugin:

- Tasks **with date symbols** (📅/⏳/🛫/🔁) when checked auto-add `✅ 2026-07-28` (that day's date); uncheck removes it.
- Regular checkbox (no symbol) just flips `[ ]` to `[x]`, **doesn't add** anything to your text.

Tasks with 📅 past due show a red badge in dataview results to catch your eye.

## 2. Dataview blocks - query notes like a database

### What it does

Insert a code block with `dataview` language in any note:

````markdown
```dataview
TASK WHERE !completed
```
````

When you open that note in Thansa (or when Thansa pastes this block into a chat answer), the block doesn't display as code but **runs a real query** across all `.md` notes in your selected brain and renders the result: task lists, grouped by file, checkboxes work per task.

Three query types:

- `TASK` - lists task lines `- [ ]` / `- [x]`, grouped by file, with working checkboxes.
- `LIST` - lists notes (each line a link, click to open).
- `TABLE` - table: each row a note, columns from frontmatter or file info.

### Supported clauses

Write in the familiar Dataview order: first line is query type, then optionally `FROM`, `WHERE`, `SORT`, `LIMIT`.

**FROM - narrow your data:**

````markdown
```dataview
TASK FROM "01 - Daily"
```
````

- `"folder"` - only notes in that folder (including subfolders).
- `#tag` - only notes with that tag (tag in frontmatter or `#tag` written in note).
- Combine: `FROM "05 - Work" OR #project`, `FROM "notes" AND -#archive` (dash or `!` means exclude).
- No `FROM` means scan entire brain.

**WHERE - filter by condition:**

````markdown
```dataview
TASK WHERE !completed AND due <= date(today)
```
````

- For `TASK`, built-in fields: `completed` (checked or not), `text` (task content), `due`, `scheduled`, `start`, `done` (dates format `2026-08-01`), `priority` (0 highest, 3 default, 5 lowest), `tags`, `file.name`, `file.folder`.
- For `LIST` / `TABLE`, use note frontmatter field names directly (`status`, `type`...), plus `tags`, `file.name`, `file.folder`, `file.mtime`.
- Comparisons: `=`, `!=`, `>`, `<`, `>=`, `<=`. Dates compare because same format `YYYY-MM-DD`.
- `date(today)`, `date(tomorrow)`, `date(yesterday)`, `date("2026-12-31")`.
- `contains(text, "word")` - string contains string; `contains(tags, "#sales")` - array contains element.
- Combine with `AND` / `OR` / `!` / parens `( )` freely.

**SORT and LIMIT:**

````markdown
```dataview
TASK WHERE !completed SORT due ASC LIMIT 10
```
````

- `SORT field ASC` (ascending, default) or `DESC`.
- `LIMIT n` - return at most n results.

**Columns in TABLE:**

````markdown
```dataview
TABLE status AS "Status", file.folder AS "Folder"
FROM #project
SORT file.mtime DESC
```
````

- List columns separated by commas, `AS "Name"` to set header.
- First column is always a link to the file; write `TABLE WITHOUT ID ...` to hide it.

### Check tasks right in results

`TASK` query results have checkboxes just like in notes. Check one and Thansa writes straight to the **source file** containing that task, even if you're on a different summarizing note. Safety: if the source file changed meanwhile (the task line isn't exactly where it was), Thansa hunts for the right line by content; if unsure, reports "File changed" and **doesn't blindly write** - reload then check again.

### Practical examples

Overdue tasks, most urgent first:

````markdown
```dataview
TASK WHERE !completed AND due < date(today) SORT priority ASC
```
````

Running projects table, recently edited first:

````markdown
```dataview
TABLE status AS "Status", deadline AS "Due"
FROM "03 - Projects"
WHERE status != "done"
SORT file.mtime DESC
```
````

Notes mentioning a customer:

````markdown
```dataview
LIST WHERE contains(file.name, "Ms. Nga") OR contains(tags, "#ms-nga")
```
````

Weekly tasks, just this week:

````markdown
```dataview
TASK FROM "01 - Daily" WHERE !completed LIMIT 20
```
````

### ` ```tasks` block - plugin Tasks syntax

If you know obsidian-tasks plugin syntax, use it directly, Thansa reads ` ```tasks ` blocks:

````markdown
```tasks
not done
due before today
sort by due
limit 20
```
````

Each line is one condition, lines AND together (same as plugin). Supported lines:

- `done` / `not done`
- `due|scheduled|starts|done|created before|after|on <today|tomorrow|yesterday|YYYY-MM-DD>` (write `due today` too; `happens` ≈ `due`)
- `has due date` / `no due date` (similar for scheduled/start/done/created)
- `description includes <text>` / `description does not include <text>`
- `path includes <text>` / `path does not include <text>`
- `tag includes #x` / `tags do not include #x`
- `priority is [above|below] high|medium|low|none|highest|lowest`
- `sort by due|priority|description|path|... [reverse]`, `limit N` / `limit to N tasks`
- `group by ...`, `hide ...`, `show ...`, `short mode`, `explain` - silently ignored (no effect)

Unsupported lines (e.g., `filter by function`) show a warning naming the line, other lines still run.

### "+ Task" button - add tasks directly

Every task-listing block (` ```tasks ` or `TASK`) has a **+ Task** button in the top-right corner. Click to show an input box + optional date field, Enter or click Add to confirm. New task gets written to **`Task Inbox.md`** in the brain's dashboard folder, with `📅 due date` if you picked one, and all blocks on the page auto-refresh immediately. Task Inbox is a task inbox: quickly add here, organize to proper Daily/Weekly when you have time.

Thansa hunts for the dashboard folder by name, not hardcoded: any top-level folder with name `dashboard` (case-insensitive, optional number prefix like `00 - Dashboard`, `01 - dashboard`, `02_Dashboard`) becomes the one. Brain without a matching folder, Thansa creates one named `00 - Dashboard`.

### Default Dashboard page

The dashboard folder is part of brain standard structure: new brains come with `00 - Dashboard` pre-made with two seed files: `Dashboard.md` (task blocks: overdue, today, upcoming, no date) and `Task Inbox.md`. Old brains missing it get a banner with a button to add. Seed files only create if not present - changes you make stay unchanged.

### Not yet supported

This is a "lite" version, intentionally covering the most-used subset. Missing:

- `dataviewjs` (blocks running JavaScript code) - block will show clear notice instead of silent failure.
- `FLATTEN`, `GROUP BY` arbitrary (TASK already auto-groups by file), `dur(...)` time math functions.
- `[[link]]` in `FROM`.

Hitting unsupported syntax, the block shows an error with the original query so you can fix it, never crashes the page.

### Performance and technical limits

Dataview is built for large vaults to stay smooth, multiple saving tiers auto-kick in:

- **Warm up on boot**: server builds indexes for all brains right after startup (background), so opening dashboard the first time doesn't sit waiting to parse the entire vault.

- **Server-side incremental cache**: note indexes live in RAM, each call only re-parses files that changed (by edit time + size), reuses unchanged parts. Vault with thousands of notes: first opening after server restart is slower, second opening is just tens of ms.
- **ETag / 304**: if no notes changed, server sends empty packet instead of whole index, browser reuses old one.
- **Scope by FROM**: queries with `FROM "folder"` scan only that branch not whole brain. **So write specific FROM when possible**, e.g., interested only in Daily logs then `FROM "01 - Daily Log" OR "02 - Weekly Log" OR "03 - Monthly Log" OR "04 - Future Log"` much faster than scanning all. Tags-only `FROM` still scans all brain (tags scattered everywhere).

Remaining limits:

- Max **20,000 notes** indexed per brain, skips `.md` files larger than 1MB and hidden folders (`.git`, `.obsidian`, `.trash`...).
- Browser holds results ~**15 seconds** then asks server again: just finished editing a note but the block didn't update, wait a few then reopen the note with the block. Checking a task updates immediately, no wait.
- Tasks inside code blocks of other notes aren't picked up (e.g., sample code with `- [ ]` in it).

## Troubleshooting

- **Checkbox click doesn't work**: check you're in **Edit** mode (render), not **Source**; in chat checkboxes display-only. If still stuck, server probably running old version before 0.9.216 - update Thansa then reload page (Ctrl+Shift+R).
- **Dataview block stuck at "Running query..."**: server missing `/files/mdindex` API (old version). Update Thansa and restart server.
- **Results empty even though you're sure there are tasks**: check `FROM` - folder name must match exactly (capitals, order number, e.g., `"05 - Work"` not `"Work"`); tags need `#`.
- **Reports "File changed - reload and check again"**: source file just edited elsewhere (by you or Thansa). Reload to run block with new data then check again.

See more: [File Management](05-quan-ly-tep-tin.md) (open and edit notes), [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) (brain structure), [Troubleshooting & FAQ](17-khac-phuc-su-co.md).
