# Getting Started & First Setup

*[Tiếng Việt](01-bat-dau-thiet-lap.md) · **English***

This page guides you from the first time you open Thansa until Thansa is ready to chat: creating an admin account, choosing an AI provider as the "brain," selecting a model, and checking system status on the Settings page.

## What is this feature

Thansa OS is an AI operating layer running on your machine or VPS. The brain is the AI provider you plug in: Claude Code, ChatGPT (via Codex), Antigravity CLI, OpenRouter, OpenAI API, Anthropic API, Google Gemini, Groq, or Ollama Cloud. The first-time setup wizard **pre-selects** Claude Code as it is the recommended choice, but Thansa is not locked into any single provider.

Before you can use Thansa, you need 3 things:

1. An admin account (to block strangers, required when running publicly on a VPS).
2. An AI provider logged in or with an API key pasted.
3. A main model to answer conversations.

When you open the app for the first time, a setup wizard will appear and guide you through exactly these 3 steps. Everything set here can be changed later in the management pages.

## Where to open it in Thansa

- On a personal machine, open a browser and go to `http://localhost:7777` (default port is 7777).
- On a VPS or Docker, use the address provided by your provider, for example `http://<ip-vps>:7777` or an HTTPS link like `https://<app>.<vps>.hstgr.cloud`.

After setup is complete, related items are on the navigation rail on the left. The rail has 7 groups, and **you must click to open each group to see its items**:

| Group | Item | Used for |
|---|---|---|
| Connections | **Models** | Switch main model, login/disconnect providers (see [Models & engine](10-models-va-engine.md)) |
| System | **Settings** | Four collapsible config groups: system status, interface & brain, voice/branding, startup with Windows |
| System | **Updates** | Running version, update button, progress and version history |
| System | **Account** | Change password, logout, disable login (see [Security & account](14-bao-mat-tai-khoan.md)) |

## How to use (step by step)

### Step 1: Open app and meet the setup wizard

Open `http://localhost:7777` (or your VPS address). If this is the first time and there is no account yet, Thansa shows a **Welcome to Thansa** window with 3 numbered items.

If you're running on a personal machine (localhost), the password and SETUP CODE fields are optional and can be left blank. If you're running publicly (VPS/Docker), Thansa requires you to set a password and enter a new SETUP CODE to proceed; the prompt line "Set account + password (≥8 characters) + SETUP CODE to protect Thansa on public server." appears right below the button.

### Step 2: Set Workspace name

In section **1. Workspace**, type a display name in the **Display name** field (for example, your store name or your name). If left blank, Thansa uses the default "Thansa OS". This is just a label, you can change it anytime.

### Step 3: Create admin account (and SETUP CODE if needed)

In section **2. Admin account**:

1. Type a username in the **Account** field (default suggestion is `admin`).
2. Type a password in the **Password** field. Password must be at least 8 characters.
3. If Thansa is running publicly, a **Setup code** field will appear. Paste the SETUP CODE here (see "When you need SETUP CODE" section below for how to get it).

On a personal machine, if you leave the password blank, Thansa does not create an account and anyone opening this machine's link can use it. Only do this if only you use the machine.

### Step 4: Choose an AI provider (brain)

In section **3. AI provider (brain)**, choose one of 3 cards:

| Option | Text on card | What you need to use it |
|---|---|---|
| **🧠 Claude Code** (pre-selected) | "Login subscription Claude → full MCP, skill, file read/write, self-improving loops. Most powerful & complete." | Login Claude subscription once (no API key needed) |
| **💬 ChatGPT (subscription plan)** | "Login ChatGPT Plus/Pro (via Codex) → still use Thansa's MCP." | Login ChatGPT on Models page |
| **🌐 OpenRouter** | "Many models one place cheap, still has Thansa MCP + skill + file read/write brain. Just API key - no login needed." | Paste OpenRouter API key (paste now or later on Models) |

Choosing any of them gives you a fully functional Thansa: all three can call the Connections hub (MCP), read/write files in brain, run skills, assign tasks, and create loops. The only difference is **running machine commands**, which only CLI engines (Claude Code, Codex, Antigravity CLI) can do. The wizard only shows 3 cards for simplicity; go to the **Models** page to find Antigravity CLI, OpenAI API, Google Gemini, Anthropic API, Groq, and Ollama, and switch anytime.

If you choose **OpenRouter**, an input field for **OpenRouter API key** will appear where you can paste the key now or leave it blank and paste it later on the Models page. Below the list is a suggestion line that changes based on which card you select, for example selecting ChatGPT then suggests "After entering: **Models** section → login ChatGPT".

Click **Start using Thansa →** to save and enter the app. The wizard also sets a default model for your chosen provider: `sonnet` for Claude Code, `gpt-4.5-turbo` for ChatGPT, `openai/gpt-4o-mini` for OpenRouter. Change it anytime on the Models page.

### Step 5: Login Claude as the brain

This is the most important step if you choose Claude Code. The wizard only saves your provider choice; Claude login happens on the **Models** page (in the **Connections** group):

1. Go to **Models** on the rail on the left.
2. Find the **Anthropic OAuth (Claude Code)** card. Initial status is "○ Not logged in".
3. Click the **Login Claude** button.
4. Thansa shows a link. Click to open that link (in a new tab) to login at claude.ai.
5. If after logging in the page shows a code, paste that code in the **paste code (if any)** field then click **Send code**. Some flows don't need a code—Thansa will check status every 3 seconds and update the card.
6. When done, the card status changes to "● Connected" (with email/plan if available).

This is a device-code flow: you don't need to enter an API key. This method works even on headless VPS. If you have terminal access to the server, you can also login once with the command `claude auth login --claudeai` instead of the above steps.

The **↻ Check again** button on the card reloads login status anytime. The **Disconnect** button logs out Claude from Thansa.

Thansa's Claude engine runs via **Claude Agent SDK**, but the SDK still calls the `claude` CLI on the machine, so the machine running Thansa must have `claude` installed for login and native MCP to work.

### Step 6: Select main model and background task model

After logging in, check and select model on the **Models** page:

- **◆ Main Model** section shows the model currently used for chat. Click **Change model ▾** to pick another.
- **◆ Providers** section lists **ten** providers: Anthropic OAuth (Claude Code), OpenAI OAuth (ChatGPT), Google Antigravity CLI, Google Gemini CLI, OpenRouter, Anthropic (API), OpenAI (ChatGPT API), Google Gemini (API), Groq (API), Ollama Cloud. Cards that need a key have a key input field and **Connect** / **Change key** / **Disconnect** buttons.
- **◆ Background task model** (subtitle "loop · Kanban task · reminder · self-learn · ingest source") lets you pick a cheap model for background tasks to save quota. If not changed, the status line says "Default of Claude Code". Click **Change model ▾** to pick, or **Back to default** to reset. If you pick a provider not yet connected, a warning card says "⚠ This provider not connected - background tasks will fall back to Claude".
- **◆ Reasoning** (thinking depth) sets how deep Thansa thinks when answering: **Off**, **Low**, **Medium**, **High**. Default is Off (quick answer).

Background tasks can run with any API provider, not just Claude. The real difference is elsewhere: Claude Code and Codex read/write files directly in brain and can run machine commands, while API models read/write via Thansa's vault tool and cannot run machine commands, so they're good for reading, summarizing, and writing notes.

See [Models & engine](10-models-va-engine.md) for full details on each provider and model.

## Settings page: four config groups

Open **Settings** (**System** group on the rail). The page splits into four collapsible groups—click the group title to close or open.

### Group 1: System

Subtitle: "Current status and shortcuts to specialized groups." Has four status boxes:

| Box | Shows |
|---|---|
| **Engine** | Label of provider running the main model, e.g. "Anthropic OAuth (Claude Code)", "OpenRouter", "Google Gemini (API)" |
| **Model** | Main model in use, or "Default" |
| **Workspace** | Workspace name you set in the wizard |
| **Telegram** | "On" or "Off" (see [Telegram channel](11-telegram.md)) |

Below are four shortcuts you click to jump directly to the corresponding page: **Models**, **Channels**, **Account**, **Updates**.

### Group 2: Interface & Brain

Subtitle: "Graph performance and data structure." Has three cards.

**Brain graph card** shows if the knowledge graph is on or off.

- Click **Turn off graph** to reduce load to maximum; when off, the button becomes **Turn on graph**.
- If screen is narrow (under 860px, i.e. mobile), Thansa automatically goes into light mode: the graph stops running even if the toggle is on. The app still opens on the Thansa screen like on desktop—it already has the chat box, just no brain visualization.

See [Knowledge graph](03-do-thi-tri-thuc.md) for details on the graph.

**Brain normalization card** consolidates the `agents`, `workflows`, `memory`, `skills` directories of the selected brain into a uniform flat structure. Click **Normalize selected brain** to run.

This operation is safe: it only moves when the destination directory doesn't exist yet, doesn't overwrite, and running multiple times is harmless (e.g., moving `Javis/agents` to `agents`, `Memory` to `memory`). After running, Thansa reports what it moved or "Nothing to move (already normalized)".

**AI-generated image source marking card** decides whether images Thansa creates carry a source origin mark (Content Credentials, C2PA standard) or not. The label on the right is "Keeping" or "Removing".

- Default is **Keep mark**: images carry a mark saying they were AI-generated. Facebook reads this mark to label "AI-generated content" on posts.
- Click **Remove mark** and newly created images won't have the mark; the label on platforms usually won't show then. Images created before the change don't change.
- Whether on or off, the author mark `javisos.com` is still kept, and you still must take responsibility for disclosing AI content per the law and terms of the platform where you post.

### Group 3: Voice, branding & access

Subtitle: "TTS, avatar and custom domain". This is home to the **⚙ QUICK SETTINGS** block:

- Toggle **🔊 Read answers aloud**.
- Block **TEXT-TO-SPEECH PROVIDER**: choose "Edge TTS - free (default)", "OpenAI - smooth, multilingual" or "ElevenLabs - most natural", paste the key, then click **Save provider**. Paid providers error out will fall back to Edge.
- **LISTEN LANGUAGE** (Vietnamese `vi-VN` or English `en-US`), **VOICE (Edge)** (Hoài My or Nam Minh), **SPEED** and button **▶ Hear sample**. The Edge voice block only shows when the provider is Edge.
- **AVATAR**: **Upload image** or **Restore default**.
- **DOMAIN & SSL**: enter domain, click **Save & check**, see two labels `DNS:` and `SSL:`, then **Enable SSL** or **Check again**.

See [Chat & voice](02-tro-chuyen-va-giong-noi.md) and [Branding & domain](15-thuong-hieu-ten-mien.md) for details.

### Group 4: Startup with Windows

This group **only appears on Windows builds**; Docker/Linux versions hide it completely. The **Auto-start Thansa** card shows status ("On" or "Off") and has one button: **Enable auto-start** or **Disable auto-start**. When on, Thansa runs in the background when you log in to Windows; opening `localhost:7777` is ready to use.

#### When the card says "On but not running"

Opening the machine and seeing **ERR_CONNECTION_REFUSED** at `localhost:7777`—open this page again. Thansa automatically checks three causes and writes the cause directly under the card, because **all three leave no error logs**:

- **Windows is blocking this startup item.** Task Manager, **Startup** tab, when you hit Disable it doesn't delete anything, just sets a flag for Windows to skip. Many "PC cleanup, speed up" apps also turn things off using the same flag without asking. Click **Enable auto-start** again and Thansa removes the flag.
- **Installation directory has moved**, but the startup command still points to the old path. Click enable again to update.
- **Missing `start-javis.vbs` or `.venv\Scripts\python.exe`.** Run `setup.bat` again to rebuild the missing part.

If the card says **On** without any warning but the machine still doesn't start it, open `server\javis.log` in the installation directory: that's where the server logs errors if it did run but died mid-execution.

For Second Brain (memory, Wiki, vault structure), see [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).

## Version updates

This section is in the **Updates** item (**System** group). The Thansa OS frame at the top shows the running version and tells if there's a new version on GitHub.

- New version available: "🆕 New version **v...** (running v...)" with environment label (`Windows`, `Linux`, `macOS` or `Docker / VPS`), and a "What's new in this version" block listing the latest 2 versions.
- Already on latest: "✅ Running latest version (v...)".
- Click **Check again** to compare with latest anytime.

### When the "⬆ Update now" button shows

The **⬆ Update now** button only shows when Thansa can update in place. Thansa doesn't guess by provider name: it **checks for real** to see if a Watchtower container is listening.

| Run type | One-tap update? |
|---|---|
| Windows | Yes |
| Linux / macOS running directly | Yes |
| Docker with Watchtower running | Yes |
| Docker without Watchtower | No, frame explains why and how to enable |

**Why one machine has the button and another doesn't.** Almost always because Watchtower is in the `profiles: ["update"]` of `docker-compose.yml`, so the habit `docker compose up -d` **doesn't turn it on**. Enable it once, in the directory with the compose file:

```bash
docker compose --profile update up -d
```

Reload the page and the button appears. If you don't want to enable it, you can still update manually: `docker compose up -d --pull always`.

The **Hostinger stack** (`docker-compose.hostinger.yml`) deliberately doesn't include Watchtower—on that platform it can't access Docker socket so running causes a deadlock. Hostinger machines update via **Redeploy** in Docker Manager, nothing extra to enable.

The Updates frame auto-detects these two cases and writes the correct solution for your machine.

### 6-step progress bar

Click **⬆ Update now**, Thansa asks confirmation ("Update Thansa to latest version? The app will restart; if there's a system error it will try to roll back."). After you agree, a progress bar appears and lights up through 6 steps:

**Prep → Fetch code → Install libraries → Restart → Health check → Done**

The running step shows ⏳, completed steps show ✅. While running, the status line says "⏳ Updating… don't close this page." If the source on your machine has local edits, Thansa reports "📦 Local edits have been stashed in git." (saved, not deleted). When done it shows "✅ Update complete. Reloading page…" and the app reloads itself after about 1.5 seconds.

### When new version breaks: roll back

Thansa has a built-in escape route, it doesn't leave you stuck at a broken version:

- **Auto roll back:** if the new version fails the Health check step, Thansa rolls back to the old one. The progress bar shows "↩ New version broken, rolling back…", then "↩ New version broken, **rolled back**."
- **Manual Docker roll back:** if after a while the version still hasn't changed, Thansa says "⚠ New version not up after a while - may be broken." then shows a **How to roll back Docker** block with the command `docker compose pull && docker compose up -d`, with a tip to pin image `ghcr.io/blogminhquy/javis-os:<old-version>` then Redeploy.
- **Other error:** frame reports the specific error and reminds you to check the `update.log` file. If the server doesn't come back up after about 3 minutes, the frame says "Server not back after about 3 minutes - try reloading the page."

Below the update frame is a version history: what's new in each version, paged, the currently installed version is marked.

## When you need SETUP CODE and where to get it

**SETUP CODE (setup token)** only shows when Thansa is running publicly (listening on `0.0.0.0`, i.e. VPS/Docker/Hostinger) and has no admin account yet. Because at this point the brain runs with full machine privileges, Thansa won't let just anyone with the link create an admin account. SETUP CODE is a secret string printed only to server log/terminal, so only someone with server access can get it.

On a personal machine (localhost), Thansa doesn't ask for this code.

How to get the code:

| Scenario | Command to run |
|---|---|
| Hostinger, go to App terminal (inside `javis` container) | `cat /data/state/.setup_token` |
| SSH to the host running Docker | `docker compose logs javis` then find the line with `SETUP TOKEN` |

Once you have the code, paste it into the **Setup code** field in the wizard then click **Start using Thansa →**. The code is one-time use; after account creation succeeds, Thansa deletes it.

**To avoid needing the code:** when deploying, pre-set two environment variables `JAVIS_ADMIN_USER` and `JAVIS_ADMIN_PASSWORD`. Thansa creates the admin account at startup, opening the app goes straight to login, no SETUP CODE asked. See [.env config](16-cau-hinh-env.md) for details on environment variables.

## Quick reference table of buttons and status

| Button / text | Where | What it does |
|---|---|---|
| **Start using Thansa →** | Wizard | Save workspace, account, provider then enter app |
| **Login Claude** | Models, Anthropic OAuth (Claude Code) card | Start device-code flow, show claude.ai link |
| **Send code** | Models, after clicking Login Claude | Send the code obtained from the claude.ai page |
| **↻ Check again** | Models, Claude Code card | Reload login status |
| **Disconnect** | Models | Logout provider from Thansa |
| **Change model ▾** | Models, Main Model and Background task model sections | Open model selection table |
| **Back to default** | Models, Background task model section | Reset background task to Claude Code default |
| "○ Not logged in" / "● Connected" | Models | Provider status |
| **Turn on graph** / **Turn off graph** | Settings, Brain graph card | Turn on or off the knowledge graph |
| **Normalize selected brain** | Settings, Brain normalization card | Consolidate brain directories to flat structure |
| **Keep mark** / **Remove mark** | Settings, AI-generated image source mark card | Turn on/off C2PA mark on Thansa-created images |
| **Enable auto-start** / **Disable auto-start** | Settings, Startup with Windows group | Let Thansa run in background when Windows logs in |
| **Check again** | Updates | Compare version with GitHub |
| **⬆ Update now** | Updates (only shows when in-place update is possible) | Run 6-step update then auto reload page |

## Tips

- If you only run a personal machine and don't mind strangers, leave the password blank in the wizard for quick access. You can set a password later on the **Account** page.
- After entering the app, if you see "Claude not logged in", go back to **Models** and click **Login Claude** once—done.
- Avatar, domain, voice and speed changes are in **Settings → Voice, branding & access**, not in the first-time wizard.
- After updating the version, if the interface doesn't change, press Ctrl+Shift+R to reload the page clean.
- Pick a cheap model in **Background task model** from the start: loops, Kanban tasks, reminders, self-learning, and ingesting sources run quite a lot, and running them on an expensive model exhausts quota fast. Track actual numbers on the [Token usage](23-muc-dung-token.md) page.

## Common issues

- **App asks for SETUP CODE but you don't know where to get it:** go to App terminal (Hostinger) and run `cat /data/state/.setup_token`, or on the host running Docker run `docker compose logs javis` and find the line with `SETUP TOKEN`. Or pre-set env `JAVIS_ADMIN_PASSWORD` to skip needing the code.
- **Says "Setup code wrong or missing":** code was pasted wrong or incomplete. Get the right code from server log again and re-paste, being careful not to pick up extra spaces.
- **Says "Password minimum 8 characters":** set password 8 characters or longer.
- **Says "Account exists - please login":** admin was created before (e.g. via env). Use the login screen with the account/password you set.
- **Claude says not logged in:** go to **Models**, click **Login Claude**, open the link, paste code if asked. Or run `claude auth login --claudeai` in server terminal.
- **Forgot admin password:** on the login screen click "Forgot password?" to see instructions. The fix is to open `server/settings.json`, delete the `"auth"` block (or set it empty), restart the server; reopening the app goes back to the wizard to create a new account. See also [Security & account](14-bao-mat-tai-khoan.md).
- **Too many wrong login attempts, gets "Too many tries":** Thansa locks temporarily to prevent password guessing. Wait a moment then try again.
- **Clicked update but says "Already updating, wait.":** another update is running. Wait for that to finish then try again.
- **Don't see the "⬆ Update now" button:** you're running Docker and Watchtower isn't running. The Updates frame tells exactly what your machine needs. On a self-managed VPS, run `docker compose --profile update up -d` once then reload the page—routine `docker compose up -d` usually DOESN'T enable Watchtower since it's in a separate profile. On Hostinger you can't enable it, use Redeploy.
- **Opened correct port but don't see the app:** check the address is exactly `http://localhost:7777` (or VPS IP with port 7777). If you just edited code, restart the server then try again.

For more troubleshooting, see [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Related

- [Chat & voice](02-tro-chuyen-va-giong-noi.md) - first thing to do after setup is complete.
- [Models & engine](10-models-va-engine.md) - details on each provider and how to switch models.
- [Connections & business metrics](09-mcp-va-so-lieu.md) - wire data sources into the **Connections** page.
- [Plugins](20-plugins.md) - add native tools for every engine.
- [Tasks / Kanban](21-viec-kanban.md) - assign one-time background tasks.
- [Scheduled tasks & reminders](08-viec-dinh-ky.md) - recurring tasks by cycle and reminders by time.
- [Self-learning](22-tu-hoc.md) - consolidate memory and check Wiki health.
- [Usage: tokens & cost](23-muc-dung-token.md) - see tokens consumed by day and provider.
- [Security & account](14-bao-mat-tai-khoan.md) - tighten access before going on a VPS.
