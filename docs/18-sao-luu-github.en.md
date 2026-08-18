# Sync brain with GitHub (2-way)

This feature syncs **ALL brains in the brains folder** (all your minds: notes, Wiki, memory, agents/workflows) with a **private** GitHub repo of yours - in BOTH directions: push changes from this machine up, while pulling changes from other machines down. Purpose: never lose data when a machine breaks or VPS is lost, and **use multiple machines at once** (home machine + VPS) - they auto-sync data via the repo.

> Should keep **all brains inside the brains folder** (creating new brain via button puts it there). Sync uses the entire brains folder as one unit, so brains outside (selected with folder picker) will NOT sync together - move them into brains.

Open at: **Self-learning** page (under **Brain** on left nav), scroll down to **⇅ Sync brain with GitHub (2-way)**.

## Why enable it

Brain is all the knowledge Thansa has accumulated about you and your work. It lives on your disk/VPS. With only one copy, a single disaster loses everything. Sync with GitHub gives you:

- Backup copy, safe if the machine fails.
- History of each change (review, revert to old points).
- Work across multiple machines: edit on home machine, VPS auto-receives it at next sync, and vice versa.
- New machine only needs to paste repo + token then sync and you have full brain back.

## Requirements

- Machine/VPS must have **git** installed (the Sync section will say "git not installed on this machine" if missing). Official Docker image already has git.
- One GitHub account.

## Setup in 3 steps

### Step 1 - Create a private GitHub repo

1. Go to https://github.com/new
2. Name it, for example `javis-brain-backup`.
3. Select **Private** (REQUIRED - brain contains personal/business data, must never be Public).
4. **DON'T** check "Add a README file" (keep repo empty to avoid push conflicts on first sync).
5. Click **Create repository**. Copy the URL like `https://github.com/<your-name>/javis-brain-backup`.

### Step 2 - Create a token (fine-grained)

1. Go to https://github.com/settings/tokens?type=beta (Settings → Developer settings → **Fine-grained tokens** → Generate new token).
2. Name the token, choose expiry.
3. **Repository access** → Only select repositories → select your `javis-brain-backup` repo exactly.
4. **Permissions** → Repository permissions → **Contents** → select **Read and write**.
5. Click Generate, **copy the token** (format `github_pat_...`). Token only shows once - copy now.

### Step 3 - Paste into Thansa

1. Open **Self-learning** page → **⇅ Sync brain with GitHub (2-way)** section.
2. Paste **repo URL (https)** and **GitHub token (fine-grained, Contents permission)** into the matching fields.
3. Check the **Branch** field: default is `main`. If your repo uses a different default branch (e.g., `master`), edit here, otherwise pushing will land on the wrong branch.
4. Click **🔌 Check connection** - must show "Connection OK".
5. Click **⇅ Sync now** for the first sync.
6. Want automation: toggle **Auto**, set **Auto sync every (hours)** (default 6), then **💾 Save config**.

Using multiple machines: do these 3 steps on EVERY machine (same repo, same branch, same or different tokens both work). Enable Auto on both - machines will auto-sync with each other at the interval.

## Quick reference of fields and buttons

| Field / Button | What it does |
|---|---|
| **Repo URL (https)** | Private GitHub repo receiving backup, format `https://github.com/<you>/<repo>`. |
| **GitHub token (fine-grained, Contents permission)** | Token for pushing/pulling. Stored internally in `settings.json` encrypted, never goes to repo. |
| **Branch** | Which branch to push to, default `main`. Matches key `backup.branch` in `settings.json`. |
| **Auto sync every (hours)** | Interval for auto-run, default 6. |
| **Auto** | Toggle for scheduled runs, shows **○ Off** when off. |
| **🔌 Check connection** | Test repo + token connection, no push. |
| **⇅ Sync now** | Run one full sync immediately. |
| **💾 Save config** | Record all fields above (including Auto toggle and hours). |

## How it works

Each sync does 4 things in order:

1. **Snapshot** the brains folder into a clean copy (strip sensitive files + stray git from each brain) and record this machine's changes.
2. **Pull** the latest from GitHub and **merge**: different files auto-combine; two machines both editing ONE file means **newer edit wins**, loser saved as `.conflict-<local|remote>-<timestamp>` right next to the file for you to decide; one side edits, other deletes means edit wins (no silent data loss).
3. **Apply result** back to the brains folder (files edited by hand right during sync won't be overwritten - machine keeps yours, next sync continues merging).
4. **Push** to GitHub (normal push, NOT force). If another machine just pushed in the middle, Thansa auto-pulls and re-merges then pushes again.

Safety notes of the mechanism:

- Token is **never** stored in brain or pushed to repo. It lives in `settings.json` internally (git-ignored). Error messages auto-hide the token too.
- **Only text files sync.** Images, videos, audio, PDF and all binary files don't go to the repo - see [Sync TEXT only, not media](#sync-text-only-not-media) section right below.
- Sensitive files also excluded from sync even if text: original chats (`memory/conversations`), loop/learn logs (`Javis/loop-log`, `Javis/learn-log`, `Javis/learn-staging`), skill usage stats (`Javis/skill-usage.json`), lock files, `.tmp`, and each brain's `.git`. These only exist on the machine that created them.
- Brain trash (`brain-trash` in state folder) lives OUTSIDE sync scope so doesn't go to repo.
- A machine with **empty brains folder** (new machine, fresh volume) is treated as RECOVERING: only receives data, never pushes "empty state" up to overwrite backup.
- Deleting a file/brain on one machine means all other machines delete it at the next sync (that's what sync means). Thanks to git being the store, everything stays in history - recover when needed.

## Sync TEXT only, not media

This is the most surprising part, read once then remember.

**Only text files go to GitHub.** Notes, Wiki, memory, skills, scheduled task config, scripts: `.md`, `.txt`, `.html`, `.csv`, `.json`, `.yaml`, `.canvas`, `.py`, `.svg` and few more text types. Full list is `TEXT_EXTS` in `server/git_brain.py`.

**Images, videos, audio, PDF and all binary files DON'T go.** They stay on the machine and work normally, just don't enter git history and don't reach other machines this way.

### Why block instead of just push everything

Git is designed to **remember forever**, and that's fundamentally different from a disk or Google Drive.

Each commit, git takes file contents, hashes them, then stores the contents compressed in `.git/objects` (called a *blob*). Deleting a file at the next commit just adds a line "file gone from here" - the blob itself must stay, because without it you can't revert to that old commit. `git gc` can't clean it because it still has an owner. In other words: **deleting a file from git doesn't reclaim storage.**

With text, that trait is an advantage. Git compresses very well and only stores diffs between versions, so a `.md` edited a hundred times bundled together weighs less than you'd think.

With media the opposite. A `.mp4` or `.jpg` is already codec-compressed, git can't compress more, and two renders of the same clip look completely different to git, not like one edited slightly. Each re-export adds a whole chunk to the store, permanently. A brain with hundreds of MB of media plus habit of tweaking clips a few times each will push the repo to many GB in months, and new machines cloning must download all those renders you threw away years ago.

Then to clean you'd need to **rewrite all history** (`git filter-repo` or BFG). That changes the hash of every commit, so all copies on other machines become incompatible and must re-clone from scratch. With Thansa syncing two-way across multiple machines, that's a disaster not maintenance. So the right way is to never put media in from the start.

### So where do I back up media

Use something that stores by **current state**: Google Drive, OneDrive, external drive, NAS. There deleting is real loss and reclaiming storage is real - the right tool for photos and videos. Two tools divide the labor: git keeps knowledge and all its history, Drive keeps heavy files at current state.

After each **⇅ Sync now**, if media was skipped, Thansa logs it right below the status line: how many files, total how many MB. Silent skipping would trick you one day into thinking your photos were backed up, only to find out when you lose the machine.

### Media in brain still expires as usual

Thansa treats `attachments/` and `inbox/` as cache: every 6 hours, files older than **30 days** get deleted, and if total exceeds **300 MB** old files are deleted until under cap. This rule is separate from sync, but you should know because it's why old images vanish from your machine. To keep long-term, extract content to a `.md` note, move file to another brain folder, or store elsewhere. To adjust/disable the rule see `media` key in `settings.json`. Details at [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Recover brain on a new machine

No need for manual git: install Thansa, open **Self-learning → ⇅ Sync brain with GitHub (2-way)**, paste repo + token + correct branch, click **⇅ Sync now** - your full brain comes back. (The old way `git clone` directly into brains folder still works.)

## Handle .conflict-* files

When two machines edit the same file between syncs, you'll see extra files like `file-name.conflict-local-20260702-101530.md` next to the original:

- Original file = WINNING version (the edit with newer timestamp).
- `.conflict-*` file = LOSING version, kept as-is so you can compare and merge by hand if needed.
- After reviewing, delete the `.conflict-*` file (it syncs between machines like normal files).

## Safety notes

- **Always use Private repos.** Brain may contain business data, customer names, sometimes even keys you pasted in chat - and as above, both images/files you sent to chat go along too.
- Set token expiry and only grant **Contents** permission for exactly that repo - don't grant broader.
- One repo for ONE set of brains. Don't point 2 different Thansa systems (completely different data) to the same repo - they'll mix data into each other exactly as designed by sync.

## Common issues

| Symptom | Cause / Fix |
|---|---|
| "git not installed on this machine" | Install git on machine/VPS. Official Docker image has it. |
| Check connection reports 403 error | Token missing Contents: Read and write permission, or repo not selected correctly. |
| Push works but files don't appear on GitHub in expected branch | The **Branch** field is different from your repo's default (Thansa defaults to `main`). Fix Branch field to match then Save config and sync again. |
| "push constantly rejected / exceeded" | Multiple machines syncing at exact same time repeatedly. Click again after a minute - the auto-merge logic will sync them. |
| "Apply sync result to machine failed for N files" | Some files are locked/unwritable on this machine (e.g., open in another app). This sync NO files pushed up (safe), close the app holding the files then sync again. |
| Lots of `.conflict-*` files showing | Two machines often edit the same file between syncs. Shorten auto interval, or divide labor per machine; handle conflicts per the section above. |
| Backup repo growing very fast | Images in `attachments/`/`inbox/` are also being pushed. See "Only sync TEXT, not media" above; consider letting media cleanup run instead of disabling it. |
| Old images vanished from repo | By design: media over 30 days gets cleaned on machine then propagates to repo. Recover from history or relax `media.max_age_days` in `settings.json`. |
| Want to stop automating | Turn off the Auto toggle then Save config. You can still click "Sync now" manually. |

---

Related: [08 - Scheduled Tasks & Reminders](08-viec-dinh-ky.md) · [13 - Second Brain: memory, Wiki](13-second-brain-bo-nho-wiki.md) · [22 - Self-learning](22-tu-hoc.md) · [17 - Troubleshooting & FAQ](17-khac-phuc-su-co.md)
