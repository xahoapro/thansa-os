# File Management

The "Files" page is a file manager integrated into the Thansa dashboard. You can find files, browse folders, open and edit text files (.md, .txt...) directly in your browser and save them, upload files, download files (all types), download entire folders as .zip, create folders, rename, and delete. The entry point is always the "brain" (memory) you've selected - no need to open File Explorer or use command line.

## What is this feature

Each brain in Thansa is essentially a folder on your machine/VPS containing all your knowledge: source notes, Wiki, memory, agents, workflows... The "Files" page lets you view and edit those files visually:

- Find files in your entire brain by **name** or by **content**.
- Browse the folder tree (click a folder to go deeper, use breadcrumbs to go back).
- Open files to read: the editor opens **right on the page**, replacing the file list (not a popup). It's the same editor you use in chat, so .md has visual editing, formatting toolbar, Undo/Redo between notes; images and PDFs show inline.
- Edit text files (.md, .txt, .json...) then click save.
- Upload files from your machine to brain, or download files from brain to your machine (all file types, not just .md).
- Download an entire folder to your machine: Thansa compresses it to .zip first.
- Create new folders, create new files, rename, delete.

## Browse range: where does it end

The default entry point is always the root folder of your selected brain. But the **browse ceiling** (where the "↑ Up" button no longer works) depends on how you're running Thansa:

| How you run it | Browse ceiling | Meaning |
|---|---|---|
| Local, no login required (localhost) | **Disk containing brain** | You can browse and edit files outside brain too, since it's your machine |
| Listen public / login required (Docker, VPS) | Brain folder | Locked within brain, doesn't expose the disk to the web |
| Set `JAVIS_FILES_ROOT=brain` (or `vault`) | Brain folder | Locked within brain even when running locally |
| Set `JAVIS_FILES_ROOT=drive` (or `root`) | Disk containing brain | Force expand to the full disk |
| Set `JAVIS_FILES_ROOT=<path>` | That exact folder | Ceiling can be anything you want, must be a folder containing the brain |

So on your personal machine, pressing **↑ Up** multiple times might take you outside brain all the way to the disk root. The **🏠 Brain** button takes you back home instantly. When you reach the ceiling, **↑ Up** hides itself. Thansa always blocks paths trying to exceed the ceiling (like `../../`), and brain always stays within the ceiling.

How to set environment variables see [Environment Config](16-cau-hinh-env.md).

## Where to open it in Thansa

1. Open the Thansa dashboard (default at port 7777).
2. On the left navigation rail, open the **Memory** group and click the **Files** item.
3. The page shows a search box at the top, toolbar below it, and below that a file/folder list. First time you enter, Thansa shows the root folder of your selected brain.

If the list shows an error like "Thansa server doesn't have the Files feature yet", restart the server (run `stop-javis.bat` then `start-javis.vbs`) and reload the page. See also [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Choose which brain to work with

The file manager always operates on the selected brain. You change brain using the dropdown at the top-left corner of the dashboard:

1. Find the brain dropdown on the top toolbar (default is "Brain Default").
2. Click it and choose the brain you want. Each brain shows as "🧠 brain name" (with note count if any).
3. The Files page **auto-reloads** to the new brain as soon as you change it, no refresh or F5 needed. The vault tree on the left also updates.

Next to the brain dropdown there are three small buttons:

| Button | Meaning |
|---|---|
| ➕ | Create a new brain in the brains folder |
| 🗑 | Delete the selected brain (must type the name to confirm) |
| 📁 | Pick a brain from any outside folder |

About the 🗑 button, three things to remember:

- With a real brain (🧠): delete the **entire** brain, not just one file. The confirmation box states clearly the brain will move to **TRASH (kept 30 days then auto-deleted)**, and the deletion will **SYNC to all other machines**. You must type the exact brain name to delete it.
- With an outside folder link (📁): this button only **removes from the dropdown**, doesn't touch your disk. The confirmation says "Remove from brain menu only, DO NOT delete data on disk."
- Default brain cannot be deleted; Thansa says "Cannot delete Default Brain (starting brain)."

Don't confuse this button with the "Delete" button for individual files in the Files page. See more about brains and memory in [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).

## The Files page layout

**Top row - search**, includes:

- Search box with 🔍 icon, placeholder text **Find file in entire brain...**. When you type, a **✕** button appears (tooltip: "Clear search").
- Two chips to pick scope: **Name** (tooltip: "Search by filename") and **Content** (tooltip: "Search inside text file content"). Default is **Name**.
- Status line on the right shows state: when idle "Search in entire brain" (or "Scanning text file content" if on Content chip), when results come back "12 results · filename".

**Second row - toolbar**, includes:

- **Breadcrumb** on the left: starts with "🏠 root folder name", then each subfolder you're in. Click any link to jump straight to that level.
- **↑ Up** button: go up one level to parent folder. Hides itself when you're at the ceiling.
- **🏠 Brain** button (tooltip: "Go to brain root"): jump straight back to brain root, no matter where you are.
- **+ Folder** button: create a new folder.
- **+ File** button: create an empty file.
- **⤒ Upload** button: choose files from your machine to upload (can select multiple at once).
- **⤓ Download folder** button: compress the current open folder to .zip and download to your machine.
- **↻** button: reload the current list.

Below is the file list. Each row shows file type icon, name, size (for files), and an action button group. This group always shows (slightly faded) and becomes prominent on hover; on phones and tablets it's always prominent since touch has no hover.

## How to use (step by step)

### Find files in entire brain

1. Click the **Find file in entire brain...** box at the top of the page.
2. Choose scope: **Name** chip to match filenames, **Content** chip to scan inside files.
3. Type a keyword. Thansa finds automatically after you pause; press **Enter** to find right now.
4. The list below becomes search results. Each row shows: filename, its path, an excerpt (if searching by content), and a match label - **Filename** or **In content · line 42**.
5. Click **Open** button (or click the filename) to open that file.
6. Click **⤓ Download** button to download just that file, no need to go into its folder.
7. Click **Location** to jump to the folder containing the file; Thansa scrolls to it and highlights the row.
8. Clear the search box (or click **✕**, or press **Esc**) to go back to the folder list.

A few things to know about search:

- Search scope is always **brain root**, even if your browse ceiling opens up to the full disk. Thansa deliberately doesn't scan the entire disk because it would be very slow.
- **Name** search ignores Vietnamese tone marks: typing `bao cao` still finds `báo-cáo.md`. Works for all file types.
- **Content** search only scans text files (.md, .txt, .json, .yaml, .csv, .py, .js...), skips files bigger than 1MB, and skips technical folders `.git`, `node_modules`, `__pycache__`, `.obsidian`, `.trash`, `.venv` and any hidden folders.
- **Content** mode needs at least 2 characters. Typing 1 character shows "Type at least 2 characters to search content."
- No matches shows `No files match "<keyword>".`

### Browse folders

1. Click a **folder name** (row with 📁 icon) to go into it.
2. Use breadcrumb at top, **↑ Up** button, or **🏠 Brain** button to go back.
3. Click a **filename** (or its icon) also opens it right away: text files, images, and PDFs open in the editor on this page; other types open in a new tab.
4. Empty folder shows "This folder is empty."

### Open and edit text files

1. Hover over a file row, click **Edit**. (Or click the filename directly.)
2. The editor opens **right on the page**, replacing the file list - not a popup. This is the same editor you use in chat, so everything is identical: text files (.md, .txt, .json, .yaml, .yml, .csv, .js, .ts, .py, .html, .css, .toml, .ini, .log, .sh, .bat, .xml, .svg, .env) have an editing box, and .md specifically has two modes **Edit** (visual like Word) / **Source** (raw markdown) plus a formatting toolbar.
3. When done editing, click **💾 Save** (or press `Ctrl` + `S`). On success, the button becomes **✓ Saved** then goes back to normal.
4. Click **✕** (or press `Esc`) to close and return to the file list. The list auto-reloads, so any file you just renamed or deleted in the editor shows its new state.
5. The toolbar also has: rename, delete, **↗** open in new tab, **⤓ Download** to machine, and fullscreen button.

**The "Properties" block at the top of .md notes.** If a file starts with a `---` block (frontmatter: `type`, `status`, `created`...), Thansa shows it as a separate block, **locked from editing** in Edit mode. That's metadata, not text, and the lock keeps it exact byte-by-byte after each save. To edit metadata, switch to **Source** mode.

### Back and forward between notes

Reading a wiki note means following a chain of links: click a `[[wikilink]]` and you go to another note. Two arrow buttons **‹ ›** in the **top-left corner**, just before the filename, let you move back and forth along that trail - just like browser Back/Forward.

- **Click left arrow** to go back to the note you just read, **right arrow** to go forward again.
- **Hover over the button to see where you'll go.** The tooltip says the filename directly, e.g. "Back to: Special Offer.md". If you've gone four levels deep into links, remembering where you came from isn't easy, so the button tells you.
- **No more to go? The button fades out, not disappear.** Hiding/showing would make the title bar jump, and you'd never know the button exists.
- **Keyboard shortcut: `Alt` + `←` and `Alt` + `→`.** Mouse back/forward buttons also work.
- The trail **stays the same when you close the editor** and reopen it (closing to chat about this same note is normal), and **clears when you switch to a different brain** - since every step in the trail belongs to the old brain.
- If you're in the middle of a trail and open a new note, the forward part gets cut off, just like a browser.

**If you leave a file while editing, Thansa auto-saves first.** Click an arrow, click a wikilink, or click another file in the tree - if you made changes but didn't click Save, Thansa saves then goes. If save fails (no network, file is locked), **Thansa doesn't go anywhere** and the Save button shows an error, so your draft never gets silently thrown away. Files you just opened to read then left don't get written to at all.

**Open file means Thansa works on it.** The moment you open a text file to edit, Thansa **pins** it to chat: an orange tag appears above the input area with the filename and text "open - click to edit again". From then on, whatever you ask, Thansa already has this file as input, no need to paste the path or describe it again. Say "tidy up the outdated section" or "add a conclusion" without naming the file and Thansa writes straight into this open file.

The pin tag differs from file attachment in three ways:
- **Only one.** Open another file and the tag switches to the new one, not added.
- **Doesn't disappear after sending.** File attachments vanish after send; the pin stays all through the conversation because it's the file you're working on. Closing the editor doesn't unpin either - closing to chat about this same file is normal.
- **Click the tag to edit the file again.** Closed the editor and chatted a few turns, want to keep editing? Click the tag (or Tab to it then Enter) - the file opens in the editor, the vault tree on the left auto-expands to the right branch, no need to find it again. If the file is already open, Thansa just brings you back there, so unsaved text doesn't disappear. On mobile, the tag opens the file in the edit panel in the middle of the screen. Click **✕** on the tag to unpin, not open the file.

Unpin by clicking **✕** on the tag. The pin also auto-clears when you switch to a different brain or delete the pinned file itself, and survives F5 so reloading doesn't break your workflow.

Notes:
- **Edit** button only shows for the text file types listed above.
- Files bigger than 2MB won't open in the browser to view. Thansa suggests downloading instead.
- If the file is binary (not text), the editor suggests **⤓ Download** instead of showing an edit box.

### Fix corrupted .md files from old versions

Versions of Thansa **before 0.33.4** had a silent bug: open a .md note in the visual editor then click Save, and the `---` block at the top (frontmatter: `type`, `status`, `created`...) would turn into `* * *`, and every time you edit again it adds a layer of backslashes to the text (`1.` → `1\.` → `1\\.`). The file still opens, but metadata is gone - Thansa, dataview and Obsidian all read past it.

This version plugs that hole. For files that got corrupted:

1. Go to the **Files** page. Thansa scans your entire brain on entry. **If no files are corrupted, it says nothing** - silence is good news.
2. If there are broken files, a yellow panel appears at the top with a list of files and where they're broken.
3. Click **Fix all N files**. Thansa rebuilds the metadata block and removes extra backslashes, then reports how many files it fixed.

Thansa only fixes what **only that bug could have created**: a `* * *` block at the very start of the file that looks like metadata, and backslash sequences of two or more. Horizontal lines in the middle of text, files with intact frontmatter, or a single backslash you typed on purpose - none of those get touched.

### When links point wrong: Thansa finds it for you

Paths in chat sometimes drift from the actual filename on disk - most common is chat having tone marks ("Plan...") but the file is saved without ("Ke Hoach..."). Before, clicking would land on a blank page saying "Not a folder". Now:

- If a path points to **a single file** (even if it looks like a folder name), Thansa opens it straight up to edit.
- If a path **has nothing there**, Thansa opens the closest parent folder that still exists, says what it was looking for, then **scans the entire brain by name** (ignoring Vietnamese tone marks) and shows a list of similar-named files - click one to open it.
- Open a file directly in the editor but can't see it either? The editor suggests similar filenames right away instead of just erroring.

### View images and PDFs right in the dashboard

1. Hover over an image file row (.png, .jpg, .jpeg, .gif, .webp, .bmp, .ico) or .pdf file, click **View** (tooltip: "Preview"). Click the filename also works the same way.
2. Images show in the editor; PDFs embed in a viewer right there.
3. The toolbar also has **↗** to open in its own tab and **⤓ Download** to your machine. Click **✕** (or press `Esc`) to go back to the file list.

Other file types (video, archive, data file...) don't have Edit or View buttons, they have **Open** (tooltip: "Open in new tab"). In short, each file row always has exactly one view/open button, just different names by type.

### Create a new file

1. Click **+ File** on the toolbar.
2. Type the filename, remember to include the extension. Example: `my-note.md`.
3. Thansa creates an empty file in the current folder. You can click **Edit** to add content.

### Create a new folder

1. Click **+ Folder**.
2. Type the folder name.
3. The new folder appears in the current folder.

### Upload files

1. Click **⤒ Upload**.
2. Choose one or more files from your machine.
3. Thansa uploads them to the current folder then reloads the list.

If the folder already has a file with the same name, Thansa auto-adds a number suffix to the new filename (e.g. `report_1.pdf`) so it doesn't overwrite the old one.

### Download files to machine

1. Click the **⤓ Download** button on a file row.
2. The file downloads via your browser's download mechanism, keeping the original name including Vietnamese tone marks.

This button is on **every file type**, not just .md: images, PDFs, videos, archives, spreadsheets, data files all download. Search results also have **⤓ Download** right next to Open, so you can find and download without going into the folder.

The file view/edit window also always has **⤓ Download** at the top, even when the file is open in edit mode (before, edit-mode files only had Save).

### Download an entire folder as .zip

Two ways, both give the same result:

- Click **⤓ Zip** on a folder row in the list.
- Go into the folder and click **⤓ Download folder** on the toolbar.

Thansa measures the folder first, then compresses everything inside (keeping the subfolder tree) into one .zip file named after the folder, e.g. `attachments.zip`. A few things to know:

- Folders bigger than 200MB prompt you first, showing file count and estimated size, so you don't sit waiting for nothing.
- Safety cap is 20,000 files or 2GB. Going over that and Thansa says so, suggesting you download subfolders instead - this cap prevents one misclick at disk root from pulling the whole disk into a zip.
- Empty folder shows "Nothing to download" instead of an empty .zip.
- Empty subfolders still get included in the .zip.

The file tree on the note panel also has **⤓** the same way: standing on a file downloads it, standing on a folder downloads the entire folder as .zip.

### Rename

1. Hover over a file or folder row, click **Rename**.
2. Type the new name and confirm. Leave blank or keep the old name and nothing changes.

Strange characters in the name get replaced by underscores by Thansa for safety, so the actual filename might differ slightly from what you typed. Vietnamese tone marks, dots, hyphens, underscores, spaces, and parentheses stay as-is.

### Delete

1. Hover over the row you want to delete, click **Delete** (warning color button).
2. Thansa asks to confirm: `Delete "<name>"? Cannot undo.` Click OK to delete.
3. For folders, deleting also removes everything inside.

Warning: the delete action has no trash, can't be undone. Make sure before you confirm. Thansa won't let you delete a brain's root folder or the browse ceiling, saying "Cannot delete root folder / brain".

## Two folders are cache zones, don't store valuables there

`attachments/` and `inbox/` of each brain are treated by Thansa as **cache zones**, not storage:

- Files in both folders older than **30 days** auto-clean, and if total size exceeds **300MB** Thansa cleans oldest-to-newest until under the cap.
- Except .md notes that land in these folders don't get cleaned, those are spared.
- To turn off auto-cleaning entirely, set `enabled: false` under the `media` key in `settings.json`. Days and size thresholds also set there.
- Old images hitting the cutoff time will show a gray box with **"Image expired"** instead of a broken icon when they reappear in chat.

Practical takeaway: documents you want to keep long-term, move to Sources or Wiki of your brain. Don't leave them in `attachments/` or `inbox/`.

## Quick reference of buttons and states

| You want | Click | Notes |
|---|---|---|
| Search files by name | Search box + `Name` chip | Ignores Vietnamese tone marks |
| Search text inside files | Search box + `Content` chip | Text files only, skip >1MB, need ≥2 characters |
| Open a search result | `Open` | Or click the filename |
| Jump to folder containing a file | `Location` | Scroll to and highlight that row |
| Exit search | `✕` or press `Esc` | Back to folder list |
| Go into a folder | Folder name (📁) | Breadcrumb to go back |
| Go up one level | ↑ Up | Hides when at the ceiling |
| Go to brain root | 🏠 Brain | Useful when you've wandered outside |
| Reload list | ↻ | Brain changes auto-reload anyway |
| Read/edit text file | Edit → 💾 Save | Text files only, under 2MB |
| View image / PDF | View | Comes with ↗ New tab and ⤓ Download |
| Open other file type | Open | Opens in new tab |
| Create empty file | + File | Remember to type extension, e.g. `.md` |
| Create folder | + Folder | |
| Bring files from machine | ⤒ Upload | Can select multiple |
| Get file to machine | ⤓ Download | On EVERY file type, plus in search results |
| Get entire folder to machine | ⤓ Zip (on folder row) or ⤓ Download folder (toolbar) | Compress to .zip; cap 20,000 files / 2GB |
| Rename | Rename | Strange characters turn to `_` |
| Delete | Delete | Asks for confirmation, no undo |

## Tips

- Can't remember where a file lives? Don't browse by hand: type in the search box - it's fastest. Fuzzy on the content? Switch to the **Content** chip, it reads inside files too.
- Wiki and notes in vault are both .md, so you can edit quick here instead of opening another app. But for just tweaking knowledge content, usually easier to let Thansa do it through chat. See [Chat & Voice](02-tro-chuyen-va-giong-noi.md) and [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).
- Filename should describe the main idea; avoid vague names. Helps you and Thansa find it again faster.
- Want to bring an article, screenshot, or research material in for Thansa to digest? Upload to the brain's Sources folder then ask Thansa in chat to process it.
- On your personal machine you can browse all the way to disk root, so watch the breadcrumb before deleting. If 🏠 isn't your brain name, you're outside your brain.
- Before bulk operations, double-check you're on the right brain via the brain dropdown at the top. Editing the wrong brain is the most common slip-up.

## Common issues

**List says "Thansa server doesn't have the Files feature yet".** Server is running an old version without this feature. Restart the server (`stop-javis.bat` then `start-javis.vbs`) and reload the page.

**Says "Session expired" or error 401.** Reload the page and log in again. See [Security & Accounts](14-bao-mat-tai-khoan.md).

**Hit ↑ Up and the button is gone.** You're at the ceiling already, button hides. Click **🏠 Brain** to go back to brain root.

**Browsed outside brain, can't find the way back.** Click **🏠 Brain**. This is by design when running locally: the ceiling is the disk, not the brain folder. To lock inside brain, set `JAVIS_FILES_ROOT=brain` then restart the server.

**Search found nothing but you know the file exists.** Three common reasons: file is outside brain root (search only covers brain); file is in a skipped folder like `.git`, `node_modules`, `.trash`; or you're on **Content** chip and the file isn't text or is bigger than 1MB. Try switching to **Name** chip.

**Search says "Need at least 2 characters".** **Content** mode needs a minimum of 2 characters. Add one more character, or switch to **Name** chip.

**Opening file says "File too large to view (>2MB) - please download".** File exceeds the inline view limit. Use **Download** to save to your machine, then open with appropriate software.

**Opening file says "Binary file - cannot view as text".** File isn't text (e.g. archive, data file). Can't edit in browser, only download.

**Download folder says "Folder too large to compress".** Folder exceeds the safety cap of 20,000 files or 2GB. Go inside and download subfolders instead. Most common when you're at disk root instead of inside brain - check the breadcrumb.

**Download folder says "No files to download".** Folder is empty. Thansa doesn't make empty .zip files.

**Clicked Download but file doesn't show up.** Check your browser's Downloads folder, and see if the browser blocked auto-download. Large folders take a few seconds to compress before the browser starts receiving.

**Clicked Save but button shows "⚠ Error".** Save failed. Try again; if still fails, check brain folder write permissions and disk status, or see [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

**Don't see the file I just uploaded or created.** Click **↻** to reload the list. If still not there, check you're in the right folder and on the right brain.

**Images in attachments disappeared.** Likely older than 30 days or folder hit the 300MB cap, so they auto-cleaned. See "Two folders are cache zones" above.

**Accidentally deleted a file.** No trash in this file manager; delete can't be undone. If brain is in a git-backed folder you might recover from there; otherwise the file is gone. See [Backup brain to GitHub](18-sao-luu-github.md).

**Accidentally deleted an entire brain.** That one you can rescue: deleted brain goes to trash and stays 30 days before final deletion.

## Related

- [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) - structure inside a brain.
- [Backup brain to GitHub](18-sao-luu-github.md) - keep change history and recover deleted files.
- [Task & Dataview in notes](19-task-va-dataview.md) - write tasks and query tables in .md files.
- [Environment Config](16-cau-hinh-env.md) - `JAVIS_FILES_ROOT` variable and others.
- [Troubleshooting & FAQ](17-khac-phuc-su-co.md)
