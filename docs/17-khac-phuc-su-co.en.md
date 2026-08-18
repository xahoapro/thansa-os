# Troubleshooting & FAQ

This page collects common issues when using Thansa OS and step-by-step solutions. Most issues can be resolved with one of two actions: restarting the server or reloading the browser with Ctrl+Shift+R. At the end is a brief FAQ section.

If you're setting up Thansa for the first time, see [Getting Started & Initial Setup](01-bat-dau-thiet-lap.md) first. If you're configuring environment variables, see [.env Configuration](16-cau-hinh-env.md).

## Before Reading: Two Most Common Quick Fixes

Many errors disappear after one of these, so try them before worrying:

1. **Restart the server (when you or an update just changed Python `.py` code).**
   - On **Windows**: run `stop-javis.bat` to shut down, then run `start-javis.vbs` (background) or `setup.bat` (show window) to restart.
   - On **Docker / VPS**: `docker compose restart`.
   - On **Linux (systemd)**: `sudo systemctl restart javis`.
2. **Hard refresh the interface to clear cache (when the screen shows wrong content, missing buttons, or you just changed the interface).** Press **Ctrl+Shift+R** in your browser (Mac: Cmd+Shift+R). This forces the browser to reload all interface files instead of using the old cached version.

> Simple rule to remember: changed core files (`.py` files) → **restart server**; interface displaying wrong → **Ctrl+Shift+R**.

## Common Issues Table

| Issue | Solution |
|---|---|
| Changed code (or just updated) but **don't see the change** | If you changed `.py` files: **restart the server** (Windows: `stop-javis.bat` then `start-javis.vbs`; Docker: `docker compose restart`). If only interface changed: press **Ctrl+Shift+R**. |
| **Port 7777 is held**, new version won't start | Shut down the old process FIRST before starting again. Windows: run `stop-javis.bat`, or `taskkill /F /PID <pid>` with the PID holding the port. Docker: `docker compose down` then `docker compose up -d`. |
| **Hostinger can't pull the image** | Set the package GHCR to **Public** (GitHub, repo, Packages section, select `javis-os`, Package settings, Visibility = Public). Then wait for GitHub Action build to complete (check repo Actions tab) then Deploy again. |
| App **asks for SETUP CODE** | Get the code from the container's App terminal: `cat /data/state/.setup_token`. If running on host: `docker compose logs javis` and look for the line with `SETUP TOKEN`. To skip the code: set `JAVIS_ADMIN_USER` and `JAVIS_ADMIN_PASSWORD` env vars at deploy time to auto-login. |
| **Claude reports not logged in** (Thansa can't respond) | Log in "the brain" Claude Code once. In the app: open **Models**, on the Claude Code tab click **Login Claude**, open the link, paste the code if requested. Via command: `claude auth login --claudeai` (Docker: run in App terminal). |
| **Files page reports error at "Loading..."** | Server doesn't have the Files endpoint yet (404 error). **Restart the server** to load the new endpoint, then press **Ctrl+Shift+R**. |
| Old chat images show gray square **Image Expired** | By design: `attachments/` and `inbox/` are cache zones, files older than 30 days (or exceeding 300MB) are cleaned. See "Images and old files disappear" below to learn how to keep them or disable cleanup. |
| Voice / microphone won't enable | Browsers only grant microphone access over **HTTPS** (or localhost). Opening via `http://<ip>:7777` will always be blocked. Use `https://` URL (Hostinger `*.hstgr.cloud`, Cloudflare Tunnel, or custom domain with SSL). See [Branding & Custom Domain](15-thuong-hieu-ten-mien.md). |
| Finished updating in app but **version didn't change** | Wait longer; if it still shows old version, check update log: `update.log` in state folder (`server/update.log` locally, `/data/state/update.log` on Docker), or `docker compose logs`. |
| **`javis` reports 401** or "token invalid" | Token is wrong or revoked. Create a new one in **Account > API Tokens** then `javis login <address>` again. See [Javis CLI](24-cli-terminal.md). |
| **`javis task add` / `javis brain ls` report 403** | Your token is **chat-only** type. These commands need **full-access** token - create another one in Account > API Tokens. |
| **`javis up` reports can't find Thansa installation** | That's correct: the CLI package doesn't include the server inside. Set `JAVIS_HOME` pointing to the Thansa folder, run commands from inside that folder, or `javis login <address>` to connect to a running Thansa elsewhere. |

Details for each row are explained below.

## Edited code but don't see the change

Thansa has two separate running parts, so refreshing them is different:

1. **Changed core files (Python `.py` in `server/`)**: the running server keeps the old version in memory. You must **stop and restart the server**:
   - Windows: run `stop-javis.bat`, wait a few seconds, then run `start-javis.vbs`.
   - Docker / VPS: `docker compose restart`.
   - Linux systemd: `sudo systemctl restart javis`.
2. **Changed interface (HTML/CSS/JS in `dashboard/`)**: server doesn't need restart, but the browser often caches the old version. Press **Ctrl+Shift+R** to reload cleanly.

If both still don't work, check you're opening the right port and the right brain.

## Port 7777 is held, new version won't start

Thansa's default port is **7777**. When an old process hasn't fully shut down and you start a new one, it will report an error because the port is busy. Handle in this order:

1. Shut down the old process first. Windows: run `stop-javis.bat`. If it still exists, find the PID holding the port then `taskkill /F /PID <pid>`. Docker: `docker compose down`.
2. Start again. Windows: `start-javis.vbs`. Docker: `docker compose up -d`.

To use a different port (when 7777 conflicts with other software), set the `JAVIS_PORT` variable in `.env` file; see [.env Configuration](16-cau-hinh-env.md).

## Hostinger can't pull the image

When deploying via Hostinger Docker Manager and it can't fetch the image, usually two reasons:

1. **Image is set to Private.** Go to GitHub, open repo, select **Packages**, select `javis-os`, go to **Package settings**, set **Visibility = Public**. Then Hostinger can pull it without needing to log into the registry.
2. **Image hasn't finished building.** Each time you push new code to the `main` branch, GitHub Action starts building. Open the repo's **Actions** tab, wait for the latest build to finish (green checkmark), then click Deploy again on Hostinger.

## App asks for SETUP CODE

When Thansa runs public (Docker/VPS/Hostinger), first time you open the app it creates an admin account and may ask for **SETUP CODE**. This is a security measure - the engine runs with full permissions on the machine, so we prevent strangers from creating accounts with just the URL. Get the code like this:

1. **From the container's App terminal** (this terminal is INSIDE the container so no `docker` commands): run `cat /data/state/.setup_token`, copy the string, paste it into the SETUP CODE field.
2. **From the host (outside container)**: run `docker compose logs javis` and look for the line with `SETUP TOKEN`.
3. **Skip the code**: set admin at deploy time using two env vars `JAVIS_ADMIN_USER` and `JAVIS_ADMIN_PASSWORD` in compose. Then opening the app auto-logs in, no code asked.

For full security and password setup details see [Security & Accounts](14-bao-mat-tai-khoan.md).

## Claude reports not logged in

When you run the Claude Code engine, Thansa uses the exact login session of the `claude` CLI on your machine: log in once and it persists through every restart/update. If Thansa can't respond or reports not logged in:

1. **Via the interface:** open **Models** (under **Connections** on left nav). On the Claude Code tab, the status line shows **○ Not logged in**. Click **Login Claude**, the app shows a link; open it to log in to claude.ai; if the page shows a code paste it into the field then click **Submit code**. When done, status changes to **● Connected**. There's a **↻ Check again** button to refresh status.
2. **Via command:** run `claude auth login --claudeai` once (on Docker run in **App terminal**), open the link, paste the code.

Login token lives in `~/.claude` (Docker: `claude-auth` volume) so it doesn't get lost on update. If already logged in on another machine, you can copy the `~/.claude` folder over. See more at [Models & Engine](10-models-va-engine.md).

## Files page reports error at "Loading..."

If you go to **Files** (under **Brain** on left nav) and the file list shows an error instead of appearing, usually the server is running an old version that doesn't have the Files endpoint yet (404 error). The interface itself will hint: **restart the server** (Windows: `stop-javis.bat` then `start-javis.vbs`) then **reload the page** with Ctrl+Shift+R.

If you see a session expired message (401 error), just reload the page and log in again. Full Files usage guide is at [File Management](05-quan-ly-tep-tin.md).

## Images and old files disappear (gray square "Image Expired")

Scrolling back in an old chat and seeing just a gray square saying **Image Expired**, or files you uploaded no longer work: this is intentional, not a bug.

Two folders `attachments/` and `inbox/` of a brain (images Thansa created, files you sent via chat or Telegram) are treated as **cache zones**, not knowledge. Knowledge is `.md` files. Thansa cleans them by two rules:

| Rule | Default | Meaning |
|---|---|---|
| File age | 30 days | Files in `attachments/` + `inbox/` older than this are deleted. |
| Storage cap | 300 MB | If total cache exceeds this, delete from oldest to newest until under the cap. |
| Staging folder | 3 days | Where files you paste/upload to the chat drop before the engine reads (`.staging` in state folder). Here even `.md` files are cleaned. |

Cleanup runs in background **once every 6 hours**. `.md` files lost in `attachments/` and `inbox/` are **never deleted** (only the staging folder cleans even `.md`).

**To keep long-term:** don't leave images in cache. After reading, extract content to a `.md` note in your brain, or move the file to another brain folder (only `attachments/`, variants, and `inbox/` get cleaned), or save elsewhere.

**To disable cleanup entirely:** open `settings.json` in state folder (`server/settings.json` locally, `/data/state/settings.json` on Docker) and add the `media` block:

```json
"media": { "enabled": false }
```

Set `"enabled": false` to clean nothing. To relax instead of disable, adjust the numbers: `"max_age_days": 90`, `"max_mb": 2000`, `"staging_days": 7`; set `max_age_days` or `max_mb` to 0 to disable just that rule. After editing, **restart the server**.

Note: if you have GitHub sync enabled: `attachments/` and `inbox/` STILL fall within sync scope, so cleanup also affects the backup repo and other machines at the next sync. See [Backing up brain to GitHub](18-sao-luu-github.md).

## Provider reports quota exceeded

Free tiers of API providers (Groq especially) apply **four limits in parallel**, requiring four different fixes. Thansa reads the error message and self-categorizes, so read the notification in chat to know which one you hit:

- **Tokens per minute, this request too big.** Thansa auto-shortens context then resends. If still too big, toggle **Optimize** mode at the top of the Usage page, or ask a shorter question.
- **Tokens per minute, window currently full.** Previous requests haven't drained yet. Thansa waits the exact seconds the provider says then resends. Shortening the question doesn't help.
- **Requests per minute.** Calling too frequently. Wait a bit then ask again.
- **Daily limit** (tokens or requests). Out of today's quota. Shortening helps zero. Must wait until tomorrow, temporarily switch to another brain on the **Models** page, or upgrade with the provider.

If Thansa doesn't recognize the type, it **shows the provider's original error** instead of guessing. Send that original text when reporting - much easier to diagnose.

Tip to reduce frequency: pick **Optimize** or **Ultra-save** mode at the top of the **Usage** page (since 0.24.7 new installs default to Ultra-save). After the first rejection, Thansa remembers the real quota of that account (the provider told it) and self-regulates context below the threshold for following requests, no extra config needed.

### Provider hiccups - Thansa auto-retries

Starting version 0.24.4, a model call that breaks due to **temporary** error (429 too many requests, 5xx overloaded, network flipped) auto-retries up to three times with pauses. If the provider sent `Retry-After` headers, Thansa obeys that exact duration. You usually see nothing, just a delayed response by a few seconds.

Two cases Thansa **intentionally won't** retry:

- **Response already started appearing.** Retry would make you read the answer twice.
- **That call already ran a tool** (sent message, wrote file, scheduled task). Retrying the whole loop would do those things again. Better to report error.

After three attempts still broken, Thansa shows the provider's exact error, tagged with *(retried 3 times)* so you know it's not a fluke. Non-temporary errors (wrong key, wrong model name, day quota out, context oversized) are reported immediately on first attempt, because retrying would just use another quota hit for the same error.

## Where to see logs

Several places depending on log type:

1. **Thansa background task logs**: open **Tasks** on the left nav, select **Scheduled Tasks**, scroll down to **Recent Logs**. This records when Thansa self-runs tasks, filterable per loop. See [Scheduled Tasks & Reminders](08-viec-dinh-ky.md).
2. **Self-learning logs**: **Self-learning** page (under **Brain**) has two boxes: **What Thansa learned (latest commit)** and **Learning log**. See [Self-learning](22-tu-hoc.md).
3. **Updates page** (under **System**, page title is **Update Log**): view current version and feature history by version. No separate "Logs" or "Activity" page anymore; the `logs` entry on left rail is this page.
4. **Server technical logs** (for deep debugging):
   - Windows running backgrounded via `start-javis.vbs`: log in `server\javis.log`.
   - Docker / VPS: `docker compose logs javis` (add `-f` to watch live: `docker compose logs -f`).
   - Linux systemd: `journalctl -u javis -f`.
5. **Update log** when clicking update button in app: file `update.log` in state folder, meaning `server/update.log` locally and `/data/state/update.log` on Docker (path per `JAVIS_STATE_DIR` var). Usually you don't open it: if update fails, the interface already shows notification and app reads the last 50 lines of this file to report status.

## FAQ (Frequently Asked Questions)

### Does data get lost when updating?

No, if running Docker. All notes, brains, settings and Claude login tokens live in **Docker volumes** (`javis-data`, `claude-auth`), separate from the image. When you update (click **⬆ Update now** in Updates, Redeploy on Hostinger, or run `./update.sh` on VPS), the image gets replaced but volumes stay, so data is **safe**. With native install, data lives in the repo's `brains/` folder, also not affected by `git pull`.

### How does in-app updating work?

Open **Updates** (under **System**); the **Thansa OS** tab shows your current version and auto-checks for newer ones on GitHub. If newer exists, status line shows **🆕 New version available** with a **What's new** box, and an **⬆ Update now** button appears when the environment supports it. Click the button, confirm, the app runs 6 stages on a progress bar (Preparing, Downloading code, Installing packages, Restarting, Health check, Done) then auto-reloads the page. If the new version breaks, Thansa **auto-reverts to old version** and reports **↩ New version broke, auto-reverted**. Below the tab is a timeline of update history.

Native installs (Windows, Linux, macOS) always auto-update. Docker only auto-updates when the **Watchtower** container is running.

Watchtower is in `profiles: ["update"]`, so `docker compose up -d` does NOT start it - this is the most common reason one machine has the button but another doesn't. Start it once with `docker compose --profile update up -d` then reload the page. Hostinger stacks intentionally don't include Watchtower (can't access Docker socket), those update via **Redeploy**. The Updates box auto-tells which category your machine falls into.

**Gettting "not found" when typing compose commands** - three types, three different causes:

| Error | Cause | Fix |
|---|---|---|
| `no configuration file provided: not found` | Wrong directory. Folder name varies on clone: `javis` if following DEPLOY.md exactly, `javis-os` if cloning without renaming | `cd` into the folder with `docker-compose.yml`. Don't remember? Ask Docker: `docker ps --format '{{.Names}}\t{{.Label "com.docker.compose.project.working_dir"}}'` |
| `docker: command not found` | You're typing INSIDE the Thansa container (the app's terminal), not on the server machine | SSH into VPS then type |
| `docker: 'compose' is not a docker command` | Old Compose version (v1) | Write with hyphen: `docker-compose --profile update up -d` |

### Can I run multiple brains (second brain)?

Yes. Thansa manages multiple brains in the `brains/` folder. From the brain selector dropdown on the interface, you can:

1. Create new brain: click the add button, enter name when prompted.
2. Switch brain: select another brain in dropdown; all Files, graph, and memory operations follow the selected brain.
3. Delete brain: select the brain to delete then click the delete button, interface asks you to **type the exact brain name** to confirm (prevents accidental deletes). Can't delete the **Default Brain**.

See details at [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).

### Can I recover a deleted brain?

Yes, within 30 days. Deleting a brain isn't permanent: Thansa moves the entire brain folder to **local trash** `brain-trash` in state folder (`server/brain-trash` locally, `/data/state/brain-trash` on Docker), named like `<brain-name>__<date-time>`. This copy is kept 30 days then cleaned, and it does NOT go to the sync repo. To recover, copy the folder back to `brains/` then reload the page.

Conversely, the deletion DOES propagate to other machines syncing the same repo (Thansa writes a "death certificate" so the other machine doesn't resurrect a deleted brain). So if recovering, do it soon and on the machine still holding the trash copy.

### Are uploaded images and files kept forever?

No. `attachments/` and `inbox/` are cache zones: by default files older than **30 days** or excess over **300 MB** total are cleaned, staging folder is **3 days**. Old images show as gray **Image Expired** in old chats. How to keep them or disable cleanup entirely is in "Images and old files disappear" above.

### How do I change Thansa's voice?

Default voice is `vi-VN-HoaiMyNeural` (Edge TTS Vietnamese), speed `+5%`. To change voice or speed, set two variables in `.env` then restart the server:

| Variable | Meaning | Default |
|---|---|---|
| `TTS_VOICE` | Voice name | `vi-VN-HoaiMyNeural` |
| `TTS_RATE` | Reading speed | `+5%` |

How to set variables is at [.env Configuration](16-cau-hinh-env.md). Note: the speaker icon on the interface only **toggles** whether to read the response aloud, not to change voice. How to use voice in chat is at [Chat & Voice](02-tro-chuyen-va-giong-noi.md).

### Can't enable microphone when accessing remotely?

Browsers require **HTTPS** to grant microphone access (except localhost). Opening via plain IP `http://<ip>:7777` always blocks it with no manual override. Solution: use `https://` URL via Hostinger (`*.hstgr.cloud`), Cloudflare Tunnel (for `https://...trycloudflare.com`), or custom domain with SSL. See [Branding & Custom Domain](15-thuong-hieu-ten-mien.md).

## Still can't fix it?

1. Collect server logs (see "Where to see logs" above) to know the exact error.
2. Try in order: restart the server, then Ctrl+Shift+R.
3. Check environment variables in `.env` are set correctly, see [.env Configuration](16-cau-hinh-env.md).
4. Check the "brain" is still logged in (go to **Models**, your engine tab must show **● Connected**).
