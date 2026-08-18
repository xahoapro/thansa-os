# Environment Configuration

*[Tiếng Việt](16-cau-hinh-env.md) · **English***

This page lists environment variables that Thansa OS reads at startup, including their meaning, defaults, and when to change them. Content based on `env.example` file and how server actually reads `os.getenv(...)` in source code (`server/config.py`, `server/main.py`, `server/web_security.py`, `server/claude_cli.py`, `server/sessions.py`, `server/plugins_host.py`...).

Most important thing to remember: **every blank line still works**. On personal machine, you almost never need to touch `.env` file. Editing `.env` mainly for when you put Thansa on VPS/public server or want to change voice, port, data path.

Only when installing via **Hostinger Docker Manager**, you won't see the full advanced list below. Hostinger compose only puts 3 user fields in Environment box: `DOMAIN_NAME`, `JAVIS_ADMIN_USER`, `JAVIS_ADMIN_PASSWORD`. Internal variables about port, state, brain, and work directory are already in the Docker image.

## What This Feature Is

`.env` is a text file at **project root** (where `env.example`, `docker-compose.yml`, `server/` folder are). Each line is a variable like `VARIABLE_NAME=value`. When Thansa starts, it reads these to know: what port to listen, force login or not, where Second Brain lives, what voice to read.

Must distinguish 3 config places to avoid confusion:

- **`.env` file**: system-level settings, read once at startup. After changing must restart Thansa to take effect.
- **⚙ Settings table in app** (Account page, Models, Channels...): hot-swap settings via interface, saved to `settings.json`, no restart needed. Examples: change model, revoke OpenRouter key, Telegram token, custom domain, logo. See more in [Models & Engine](10-models-va-engine.md), [Security & Account](14-bao-mat-tai-khoan.md), [Brand & Domain](15-thuong-hieu-ten-mien.md).
- **A few keys in `settings.json` without UI yet**: currently has `media` block (rules for cleaning images/temp files). To change, must edit file by hand. See separate section below.

Short: `.env` handles "run where, who enters, data where". Settings table in app handles "use which model, disable what keys, what voice". `settings.json` is where both meet, plus a few rare keys you can only edit there.

## Where to Access in Thansa

`.env` has no button in dashboard. This is a file you create and edit yourself with a text editor (Notepad, VS Code...).

Steps to create `.env` for first time:

1. Open project root folder (where you downloaded/unzipped Thansa; Docker version means `/app` inside image, but `.env` goes next to `docker-compose.yml` on host).
2. Find template file `env.example` (name intentionally has NO leading dot - so Hostinger's Docker Manager doesn't auto-scan `.env*` files then import comment lines into Environment box).
3. Copy it and rename the copy to `.env` (copy HAS leading dot, no `.txt` suffix).
4. Open `.env` in text editor, uncomment (remove `#` at line start) any variables you want to enable, then enter values.
5. Save file. Restart Thansa.

Quick copy via command (run in project folder):

- Windows PowerShell: `Copy-Item env.example .env`
- Git Bash / Linux / macOS: `cp env.example .env`

Note about `#`: lines starting with `#` are comments, Thansa skips them. To enable a variable that's commented, delete the `#` at line start. Example: change from `# JAVIS_PORT=7777` to `JAVIS_PORT=8080`.

## List of Variables

Grouped by function. "Default" column shows value used when you leave blank or don't declare. Groups 1 to 5 are common user variables; groups 6 to 7 are advanced, almost never need changes.

### Group 1: Workspace Display

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `WORKSPACE_NAME` | Workspace name shown on dashboard | `Thansa OS` | Want custom name for workspace. Note: if you set name in app, app wins over this variable, which is fallback only. |
| `USER_NAME` | User name displayed | `Bạn` | Want Thansa use your name instead of "Bạn". |

### Group 2: Network (Port and Listen Address)

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `JAVIS_HOST` | Address server listens on. `127.0.0.1` = only this machine connects. `0.0.0.0` = listen everywhere (public, anyone with address enters) | `127.0.0.1` (Docker image pre-sets `0.0.0.0`) | Change to `0.0.0.0` only when running on VPS/server and want access from other machines. Then must enable login (see group 3). |
| `JAVIS_PORT` | Port for dashboard | `7777` | Port `7777` occupied or want different port. After changing remember to use right port in browser. |

Detail about `JAVIS_HOST`: Thansa uses "secure by default" logic. If you set listen address NOT loopback (i.e., not `127.0.0.1`, `localhost`, `::1`), server auto-treats as public and **auto-enables forced login** so nobody enters without account. Reason: AI brain runs with full machine permissions, leaving it open is dangerous.

### Group 3: Login and Security

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `JAVIS_REQUIRE_LOGIN` | Force enable/disable forced login. `1`/`true`/`yes`/`on` = enable. `0`/`false`/`no`/`off` = disable | Auto (enable when public) | Running localhost then expose via tunnel (Cloudflare, ngrok...): set `JAVIS_REQUIRE_LOGIN=1` to block strangers. |
| `JAVIS_ADMIN_USER` | Admin login name pre-created at deploy | `admin` | Set together with `JAVIS_ADMIN_PASSWORD` to pre-create account, no need to fetch SETUP CODE from log. |
| `JAVIS_ADMIN_PASSWORD` | Admin password pre-created at deploy | (blank) | Deploy public: set a strong password here. With this variable and no existing admin, Thansa creates admin at boot and closes account creation screen (safest for public). |
| `JAVIS_SECURE_COOKIE` | Enable cookie only sent over HTTPS. `1`/`true`/`yes`/`on` = enable | Disable | Enable only when CERTAIN running HTTPS end-to-end (custom domain with SSL). Enabling by mistake when proxy runs HTTP will jam login loop (correct password still gets rejected from login screen). |
| `JAVIS_ALLOWED_HOSTS` | Add hostname allowed to call Thansa (blocks CSRF and DNS-rebinding). Multiple names separated by comma | (blank) | Running behind reverse proxy with undeclared domain but no password yet, got 403 "host not allowed". By default already allows `localhost`, `127.0.0.1`, `::1` and domain you set in Settings. |
| `JAVIS_ENABLE_USER_PLUGINS` | Hard gate for user-installed plugins. `true` only loads them | Disable | You installed plugins (folder `plugins/` globally or in brain) and want them to run. User plugins run ACTUAL PYTHON CODE in server process so blocked by default. Old alias: `JAVIS_ENABLE_VAULT_PLUGINS`. Bundled plugins aren't gated. See [Plugins](20-plugins.md). |
| `JAVIS_TERMINAL` | Switch to disable Terminal completely in Code group. `0`/`off`/`false`/`no` = disable | Enable | Don't want any terminal opened from browser. Terminal already restricted to ALREADY-LOGGED-IN browser (API tokens can't open), but many still want server-level lockdown. See [Code Tab: Terminal](27-tab-code-terminal.md). |
| `JAVIS_TERMINAL_SHELL` | Shell that Terminal runs | `$SHELL`, fallback `bash`/`sh`. Windows: `powershell.exe` then `cmd.exe` | Want to force a different shell (`zsh`, `fish`, `cmd.exe`). |
| `JAVIS_TERMINAL_CWD` | Directory terminal opens in | HOME of user running Thansa | Want shell to open in brain root or another project folder. |

About SETUP CODE: when running public with no admin, opening app first time asks for setup code. Code only prints to server log at startup, so only log viewers can create account, URL-only visitors can't do anything. If you pre-set `JAVIS_ADMIN_USER` + `JAVIS_ADMIN_PASSWORD` then skip code, just login with set account. See more in [Security & Account](14-bao-mat-tai-khoan.md).

About custom domain and HTTPS: VPS using Caddy enters domain right in **Settings → Voice, Brand & Access → Domain & SSL** then click **Enable SSL**. Hostinger wizard pre-creates `DOMAIN_NAME` variable to copy to Docker Manager then Redeploy. When accessing via correct domain over HTTPS, server auto-enables cookie Secure so no need to set `JAVIS_SECURE_COOKIE` manually. Detail in [Brand & Domain](15-thuong-hieu-ten-mien.md).

### Group 4: Data Paths (Second Brain and State)

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `CLAUDE_CWD` | Working directory of CLI engine (where it reads `CLAUDE.md` and inherits MCP) | Project root folder (Docker: `/app`) | Want engine work in different directory. |
| `BRAINS_DIR` | Parent folder holding all brains, each subfolder is one Second Brain. Default brain is `<BRAINS_DIR>/Brain Default` | `brains/` in project (Docker: `/brains`) | Want multiple brains elsewhere (e.g., separate data drive, git-backup mount). |
| `OBSIDIAN_VAULT_PATH` | Path to main Second Brain vault | `vault/` in project (Docker: `/data/vault`) | Server already has real Obsidian vault then point this here. Blank uses sample vault in repo (new machine runs immediately). |
| `BRAIN_PATH` | Old-style brain folder, time of one-brain. Only for migrating old data | `brain/` in project (Docker: `/data/brain`) | Almost never need touch. Don't use for new install. |
| `SOURCES_PATH` | Where to save file attachments from chat (source for Second Brain) | `brain/01 - Sources/` in project | Want source folder elsewhere. |
| `JAVIS_STATE_DIR` | Where Thansa writes its own state: `settings.json`, login sessions, schedule config, encryption key `.secret_key`, conversation database | `server/` (Docker: `/data/state`) | Docker/VPS must point to writable volume (source tree in container is read-only). Personal machine blank is fine. |
| `JAVIS_SESSIONS_DB` | Path to conversation history database file (`conversations.db`) | Inside `JAVIS_STATE_DIR` | Want history file elsewhere. See [Conversation Sessions](04-phien-hoi-thoai.md). |
| `JAVIS_FILES_ROOT` | Ceiling of file browser on Files page (can't go up past here). `brain`/`vault` = locked in brain; `drive`/`root` = whole drive with brain; `<path>` = specific folder (must contain brain) | localhost: whole drive; public: locked in brain | Running public but still want broader browse, set `drive` or a parent folder. Want tight lock on personal machine, set `brain`. |

Note on Second Brain: `BRAINS_DIR` is the folder actually containing your brains (not `brain/` at repo root, that's old-style path). Blank works immediately with sample data in repo. See more on how memory works at [Second Brain: Memory, Wiki, Ingest](13-second-brain-bo-nho-wiki.md) and [Knowledge Graph](03-do-thi-tri-thuc.md).

**Warning on `.secret_key`:** inside `JAVIS_STATE_DIR` there's a small file `.secret_key`. It's the key encrypting sensitive fields in `settings.json` (OpenRouter/Anthropic/OpenAI/Gemini API keys, ChatGPT login tokens, Telegram token, GitHub backup token, ElevenLabs key). Copy `settings.json` to another machine but forget `.secret_key` and **all keys lost**: Thansa reads `enc:` but can't decrypt so returns empty string and you must re-enter everything. Backup both together. If machine missing `cryptography` library, Thansa can't encrypt: secret falls to `plain:` prefix plus warning line in log; install via `pip install cryptography` then restart and encryption re-enables. See detail in [Security & Account](14-bao-mat-tai-khoan.md).

### Group 5: Voice (TTS)

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `TTS_VOICE` | Default voice for reading (uses free Edge TTS) | `vi-VN-HoaiMyNeural` | Want different voice. E.g., male voice in Vietnamese or foreign language voice. |
| `TTS_RATE` | Reading speed, as percentage offset | `+5%` | Voice too fast, reduce (e.g., `+0%` or `-10%`), want faster increase (e.g., `+15%`). |

Note: these two TTS variables apply to default free Edge TTS voice. If you pick different voice provider (OpenAI TTS or ElevenLabs), configure that in app Settings instead, not `.env`. How to chat and enable voice see [Chat & Voice](02-tro-chuyen-va-giong-noi.md).

### Group 6: Deploy, Domain and Updates

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `DOMAIN_NAME` | Domain that reverse proxy (Traefik of Hostinger) routes to Thansa. Thansa reads to compare with domain you entered in app and know if Redeploy needed | (blank; Hostinger compose sets `localhost`) | Hostinger deploy: set to your domain in Docker Manager then Redeploy. Wizard in app has **Copy Variable** button to copy this line. |
| `JAVIS_DEPLOY_TARGET` | Clarify which environment running: `hostinger`, `vps`, `native`, `windows` | Auto-guess (hostname `.hstgr.cloud` = hostinger; Docker = vps) | Almost never set by hand. Hostinger compose pre-sets `hostinger`. Set when Thansa guesses wrong and domain wizard shows wrong instructions. |
| `WATCHTOWER_TOKEN` | Token for "Update Now" button (page **Updates**) to call Watchtower when running Docker | In `docker-compose.yml`: `javis-update`. Outside Docker: blank (no variable means Watchtower not running) | Want tighter security: change to random string, set same value for both app and watchtower service. |

### Group 7: Advanced Variables (Rarely Need Touching)

| Variable | Meaning | Default | When to Change |
|---|---|---|---|
| `JAVIS_CLAUDE_IDLE_TIMEOUT` | Ceiling wait when engine answered but silent without tool running, in seconds. `0` = no limit | `0` | Default skips ceiling: engine silent doesn't mean stuck (model thinking hard, or composing long file to write, both silent for minutes). Only set positive number if really need auto-cut. |
| `JAVIS_CLAUDE_FIRST_TIMEOUT` | Ceiling wait for FIRST LETTER of a turn, in seconds. `0` = no limit | `0` | Same reason as above: long conversation needs to reload all context so first turn slow. |
| `JAVIS_CLAUDE_TOOL_TIMEOUT` | Ceiling wait when TOOL running (render video, background remove, build...), in seconds. `0` = no limit | `3600` | This ceiling stays because it measures REAL child process alive, not silence. Task running over 1 hour (encode long video, train model...) increase it. |
| `JAVIS_CODEX_SANDBOX` | Use Codex's own sandbox for background jobs or not. `auto` = yes, matches job's permission level (suggest becomes read-only, auto becomes workspace-write). `off` = no separate sandbox | `auto`, but **Docker image pre-sets `off`** | Codex wraps file read/write in bubblewrap, but bubblewrap can't start in container (regular user, no CAP_SYS_ADMIN, Ubuntu 24.04 even blocks user namespace via AppArmor) so that sandbox doesn't tighten but breaks - all jobs running via ChatGPT can't read any file. Outside Docker leave `auto`. Trade-off when `off`: Codex has no per-call allowlist like Claude so level `suggest` loses the barrier that blocks file write; but barriers on money/orders/posting/messaging are NOT affected because they live in MCP Hub. |
| `JAVIS_AGY_PROMPT_DAI` | Force how Thansa passes prompt to Antigravity CLI when longer than command-line ceiling: `stdin` (pipe through), `file` (write to file, model reads), `argv` (put straight in command) | (blank, Thansa picks: stdin first, if breaks auto-fallback to file) | Only when your machine hits rare case. Windows caps total command line at 32767 chars while Thansa system prompt already over 36,000, so `argv` there certain to break. See [Models & Engine](10-models-va-engine.md). |
| `JAVIS_AGY_TIMEOUT` | Ceiling duration of one Antigravity CLI turn, in seconds. Thansa passes this down to `--print-timeout` of the CLI itself | `900` | Background job cut off mid-way increase it. No variable then `agy` auto-cuts at 5 minutes and returns partial answer without error. |
| `JAVIS_MAX_TOOL_ROUNDS` | Max tool-call rounds for ONE turn of API-key engines (OpenRouter, OpenAI, Anthropic, Gemini, Groq, Ollama). Clamped between 1 to 40 | `8` | Multi-step job (read few files, check few sources then write result) or stops halfway with "ran N tool rounds" message then increase to 15-20. Must restart Thansa after change. Claude Code and Codex NOT subject to this - they manage their own loops. |
| `JAVIS_KANBAN_MAX_WORKERS` | Number of Kanban jobs running parallel. Clamped between 1 to 8 | `2` | Strong VPS and long job queue increase it; weak machine or often congested then set `1`. See [Jobs / Kanban](21-viec-kanban.md). |
| `JAVIS_MEMORY_INDEX_MAX` | Ceiling characters of memory index (`MEMORY.md`) loaded in every chat turn. Over ceiling Thansa shortens description instead of dropping memory | `20000` | Memory too thick burns tokens each turn; want tighter set this lower. See [Second Brain](13-second-brain-bo-nho-wiki.md). |
| `JAVIS_CLAUDE_ENGINE` | (Legacy) Since 0.9.37 Claude engine always runs via main Agent SDK - this variable no longer works, setting `cli`/`sdk-loops` gets ignored with warning log | `sdk` | No need to touch. Claude engine error then report with server logs. |
| `JAVIS_CODEX_BIN` | Absolute path to `codex` executable | Auto-find in PATH and usual install spots | Codex CLI installed somewhere unusual and Thansa can't find it. |
| `CLAUDE_CONFIG_DIR` | Config directory of Claude Code (where `.credentials.json` is). Setting this variable is an escape hatch, same as Claude Code's behavior | `~/.claude` | You changed Claude Code's config folder. |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token of Claude Code, for asking real model list from Anthropic | (blank, read from credentials file) | Environment has no credentials file (CI, minimal container) but want dynamic model list. |
| `JAVIS_CLAUDE_PROJECTS_DIR` | Where Thansa reads Claude Code session logs to compute **Usage** | `~/.claude/projects` | Claude Code log elsewhere. See [Usage: Tokens & Cost](23-muc-dung-token.md). |
| `JAVIS_CODEX_SESSIONS_DIR` | Where Thansa reads Codex session logs to compute **Usage** | `~/.codex/sessions` | Codex log elsewhere. |
| `JAVIS_IMAGE_HOST_MODEL` | "Host" chat model for calling image creation tool via ChatGPT package | `gpt-5.5` | Provider renamed model breaking image function. |
| `JAVIS_IMAGE_MODEL` | Actual image generation model | `gpt-image-2` | Like above. |

Note: `JAVIS_ENABLE_USER_PLUGINS` is also advanced but security gate so listed in group 3.

## `media` Block in settings.json (No UI Yet)

Folders `attachments/` and `inbox/` in each brain are **cache zone**, not knowledge repo: images are raw materials, after reading extract to `.md` is enough. So Thansa auto-cleans by age and size, sweeps every 6 hours. Stage folder (where files you paste in chat land) has its own shorter limit.

This cleanup rule **has no Settings box yet**. To change, open `settings.json` in state directory (personal machine: `server/settings.json`; Docker: `/data/state/settings.json`) and edit `media` block:

```json
"media": {
  "enabled": true,
  "max_age_days": 30,
  "max_mb": 300,
  "staging_days": 3
}
```

| Key | Meaning | Default |
|---|---|---|
| `enabled` | `false` = don't clean anything | `true` |
| `max_age_days` | Delete media older than this many days. Set `0` or negative = turn off age rule | `30` |
| `max_mb` | Ceiling capacity of each brain's media zone in MB. Set `0` or negative = turn off size rule | `300` |
| `staging_days` | Separate ceiling for temp stage folder in state directory | `3` |

After editing must restart Thansa. Image deleted but still mentioned in old chat will show gray box saying image expired, not broken-image icon. To keep images long-term connect external storage (e.g., Drive) via **Connections** page, don't let Thansa hold them.

## Note About ANTHROPIC_API_KEY

Thansa uses your **subscription package** as the brain (Claude Code for Claude tier, Codex for ChatGPT tier), so **no need** for `ANTHROPIC_API_KEY` variable in `.env`. Any MCP you install in Claude Code, Thansa auto-inherits. To use model via API provider (OpenRouter, OpenAI API, Anthropic API, Google Gemini API, Groq API), you enter key in app at **Models** page, not in `.env`. Keys entered there get encrypted before saving to `settings.json`. See [Models & Engine](10-models-va-engine.md).

## Example Minimal .env File

Personal machine, only want to change name and reading speed, leave rest default:

```
WORKSPACE_NAME=My Thansa
USER_NAME=John
TTS_RATE=+0%
```

Public deploy on VPS, pre-create admin and open for outside access:

```
JAVIS_HOST=0.0.0.0
JAVIS_ADMIN_USER=admin
JAVIS_ADMIN_PASSWORD=put-strong-password-here
OBSIDIAN_VAULT_PATH=/data/vault
JAVIS_STATE_DIR=/data/state
JAVIS_ALLOWED_HOSTS=javis.yourname.com
```

In the second example, since `JAVIS_HOST=0.0.0.0` (public) Thansa auto-enables forced login, and since have `JAVIS_ADMIN_PASSWORD` you login right away with that account, no need for SETUP CODE.

## Tips

1. Always keep `env.example` as reference copy. Only edit `.env`.
2. After changing `.env` must restart Thansa. Different from Settings table in app (change is immediate).
3. Unsure what a variable does, leave it commented for safety. Default already works well.
4. For on/off variables (`JAVIS_REQUIRE_LOGIN`, `JAVIS_SECURE_COOKIE`, `JAVIS_ENABLE_USER_PLUGINS`), true values accept `1`, `true`, `yes`, `on`. False values accept `0`, `false`, `no`, `off`.
5. `.env` contains passwords and sensitive config. Don't put anywhere public. On shared machine set read permission tight. File `.secret_key` in state folder same way, even more important: losing it loses all stored API keys.
6. Enabling `JAVIS_ENABLE_USER_PLUGINS=true` is a big decision: plugins you install run real Python code in server. Enable only when you know exactly where each plugin in `plugins/` folder comes from.

## Common Issues

**Changed .env but nothing changed.**
You didn't restart Thansa. `.env` reads only at startup. Stop server then start again.

**Changed port then can't reach app.**
You're opening browser at old port. E.g., changed to `JAVIS_PORT=8080` must open `http://localhost:8080`, not `7777` anymore.

**Login with correct password but keeps returning to login screen.**
Likely you enabled `JAVIS_SECURE_COOKIE=1` but actually accessing via HTTP (not HTTPS). Secure cookie only sends over HTTPS so browser can't keep session. Remove that line or set to off, restart.

**All operations return 403 "host not allowed".**
You visiting Thansa via domain not in allowlist, no password set. Add domain to `JAVIS_ALLOWED_HOSTS` (or enter in Settings → Domain & SSL), or simply set password.

**Enabled plugin in app but still not running.**
User plugins need `JAVIS_ENABLE_USER_PLUGINS=true` in `.env` then restart. App also clearly says when blocking a plugin.

**App asks for SETUP CODE, don't know where to get.**
Code prints in server log at startup. Docker: check container logs for "SETUP TOKEN", or read `.setup_token` file in state folder. Simpler: set `JAVIS_ADMIN_PASSWORD` to skip needing code.

**Set workspace name in .env but app shows different name.**
App prioritizes name already saved in Settings over `WORKSPACE_NAME`. Edit name in app Settings, or delete saved name so app uses `.env` value again.

**Point OBSIDIAN_VAULT_PATH to real vault but Thansa doesn't see data.**
Check path correct and Thansa has read permission. Docker must mount right volume to that path. After fixing restart and rebuild graph (see [Knowledge Graph](03-do-thi-tri-thuc.md)).

**Restore backup then all API keys empty.**
You copied `settings.json` but not `.secret_key` alongside. Can't recover: re-enter keys in Models and Channels pages. Next time bring both files.

See more at [Troubleshoot & FAQ](17-khac-phuc-su-co.md) if still stuck.

## Related

- [Start & First Setup](01-bat-dau-thiet-lap.md)
- [Security & Account](14-bao-mat-tai-khoan.md)
- [Brand & Domain](15-thuong-hieu-ten-mien.md)
- [Models & Engine](10-models-va-engine.md)
- [Plugins](20-plugins.md)
- [Usage: Tokens & Cost](23-muc-dung-token.md)
