# Security & Account

*[Tiếng Việt](14-bao-mat-tai-khoan.md) · **English***

This page explains how Thansa OS protects itself when you put it on the network, and how to use the **Account** page in the dashboard to set passwords, log out, disable login, and rename your workspace.

## What This Feature Is

Thansa runs an AI brain with **full permissions on your machine/VPS**: it reads files, runs commands, calls tools. So if you leave the dashboard open on the Internet without a password, anyone who knows the address can control your machine.

Thansa handles this with 6 layers:

1. **Forces login when running public.** When the server listens outward (not just this machine), Thansa blocks all features until you log in. Running on a personal machine (localhost) doesn't force it, use directly as before.
2. **Prevents account takeover on first login.** The first person who wants to create an admin must have a **SETUP CODE** (printed in server log) or admin already set via environment variable. Someone who only knows the URL can't create an account.
3. **Stops password guessing.** Wrong attempts lock out temporarily by IP address; each wrong try is slowed down.
4. **Blocks spoofed web pages that trick Thansa (CSRF) and blocks foreign domain names pointing to your machine (DNS-rebinding).** See separate section below.
5. **Encrypts secret keys stored in `settings.json`.** API keys, Telegram tokens, GitHub tokens... are not stored as plain text on disk.
6. **API tokens for CLI and scripts default to NONE.** Login cookies only work with browsers; to call Thansa from terminal you must manually create a token, choose scope, and can revoke it anytime. See separate section below.

## Where to Access in Thansa

All account operations are in the **Account** section in the **System** group on the left nav bar (subtitle "Login, workspace, API tokens"). The **Settings** page has a condensed block to do three common things (change password, logout, disable login) and a line showing 2-factor auth status; the rest like enabling 2FA or API tokens only appear on the **Account** page.

The **Account** page has 3 sections:

- **Workspace**: rename the workspace display name.
- **Login Account**: set password, logout, disable login.
- **API Tokens (for CLI)**: create and revoke tokens so [Thansa CLI](24-cli-terminal.md) or scripts can call Thansa. On same page because tokens are another login method, just for machines instead of browsers.

## When Thansa Forces Login

Thansa decides whether to force login based on how the server is running:

| Situation | Force Login? |
|---|---|
| Running on personal machine, listening to `127.0.0.1` / `localhost` (or `::1`) | No (unless you set a password yourself) |
| Running public (Docker/VPS/Hostinger), listening to `0.0.0.0`, `::` or LAN IP | Yes, auto-enable |
| Password already set in Account page | Yes, in all modes |

Can force with environment variable `JAVIS_REQUIRE_LOGIN`:

- `JAVIS_REQUIRE_LOGIN=1` : always force login, even localhost. Use when exposing Thansa over tunnel (Cloudflare Tunnel, ngrok...) on personal machine.
- `JAVIS_REQUIRE_LOGIN=0` : disable forced login.

Safety principle (fail-closed): if server listens to an address **that is not** pure localhost, Thansa treats it as public by default and enables login. Environment variable details see [Environment Configuration](16-cau-hinh-env.md).

## How to Use (Step by Step)

### A. Create Admin Account First Time on VPS/Public

When opening dashboard for the first time on a public server, Thansa shows an **account creation** screen and asks for **SETUP CODE**. Two ways:

**Method 1 - Set admin via environment variable (recommended):**

1. In deployment config (e.g., Hostinger compose), add 2 variables:
   - `JAVIS_ADMIN_PASSWORD` : your chosen admin password.
   - `JAVIS_ADMIN_USER` : login name (optional, default is `admin`).
2. Start Thansa. At boot, Thansa auto-creates admin from these 2 variables and **closes** the account creation screen. You open the app and go straight to login.
3. Login with the user/password you just set.

**Method 2 - Use SETUP CODE from log:**

1. Open server log/terminal. At startup, if running public but no admin yet, Thansa generates a setup code and saves to `.setup_token` file in state directory.
   - On Hostinger, go inside container (App terminal) run: `cat /data/state/.setup_token`.
   - On VPS running Docker: see `docker compose logs javis` and find the line with `SETUP TOKEN`.
2. Open dashboard, on account creation screen enter: username, password (**minimum 8 characters**), and paste the **SETUP CODE**.
3. Click create account button. If code is correct, Thansa creates admin, logs you in, and the setup code self-destructs (one use only).

If you enter wrong/missing code, Thansa says: "Wrong or missing SETUP CODE - see code in server log/terminal."

Setup code only generates **at server startup**. If you used it already (code deleted) and later need to create another account, you must restart the server for Thansa to generate a new code.

### B. Set Password (When Running Personal Machine, No Password Yet)

If you run Thansa at home and want to lock it before putting on VPS:

1. Go to **Account** on left nav.
2. In the **Login Account** section, enter **Account** (leave blank to use `admin`).
3. Enter **Password**.
4. Click **Set Password**.
5. Thansa saves the account and gives you a login session right away (doesn't lock you out).

Password minimum **8 characters**, and the interface enforces this before sending, so you don't discover it too short after clicking Save.

### C. Change Password / Login Name

Once you have a password, the **Login Account** section shows "🔒 Password set · account: <your name>", adds a **Current Password** field, and the button changes to **Change Password**.

1. Go to **Account** on left nav (or **Login Account** section in **Settings** page, both work the same).
2. Enter **Current Password**. Required, even if already logged in: a browser left with dashboard open should not be able to change password and lock the owner out.
3. Enter **New Password** (8+ characters). To change only login name, leave this blank and only edit the **Account** field.
4. Click **Change Password**.

After changing, **all other login sessions are revoked** (other machines, other browsers, phone) but your machine gets a new session right away so you don't get kicked off. Two-factor auth and recovery codes stay the same, no need to scan QR again.

Changing only login name keeps other sessions alive, because password didn't change.

**Forgot current password** - no workaround in dashboard, must fix from server:

1. Stop container (or stop Thansa).
2. Delete (or empty) the `"auth"` block in `settings.json` in state directory (Docker: `/data/state/settings.json`).
3. Set `JAVIS_ADMIN_PASSWORD` (and `JAVIS_ADMIN_USER` if desired) then restart. Thansa recreates admin from environment variables at boot.

### D. Logout

1. Go to **Account**.
2. Click **Logout**.
3. Thansa deletes current session and reloads the page. Next time you visit you must login again.

Logout only ends the session on this browser, does not delete password.

### E. Disable Login (Delete Password)

Only do this on personal machine, never on VPS.

1. Go to **Account**.
2. Click **Disable Login**.
3. Confirm in dialog "Disable login? Anyone opening dashboard can use it."
4. Thansa deletes password and **logs out all open sessions**.

Note: if server still running public (or you set `JAVIS_REQUIRE_LOGIN=1`), disabling password does **not** make dashboard wide open, but returns to the forced account creation screen. Login only truly disables when server listens to pure localhost and doesn't force login.

### F. Rename Workspace

1. Go to **Account**.
2. In the **Workspace** section, edit **Workspace Name**.
3. Click **Save**. New name shows immediately at top of dashboard.

## Block CSRF and DNS-rebinding

This is a protection layer running silently, you don't need to enable anything, but should know it exists because sometimes it's the culprit of mysterious 403 errors.

The problem it solves: dashboard listens at `localhost:7777`. When you **haven't** set a password, any web page open in your browser can still send a POST request to `http://localhost:7777/...`. The browser blocks that page from READING the response, but doesn't block the request from running, so the action still happens. An attacker could also point a domain of theirs to `127.0.0.1` to bypass origin checks.

Thansa blocks both paths with a gate running before even the login gate:

| Case | Handling |
|---|---|
| WRITE request (POST/PUT/DELETE/PATCH) with `Origin` different from Host and not in allowlist | Block, return 403 with `"cross-origin request blocked"` |
| Request arrives with a foreign hostname (Host), while **not yet** enabled login gate | Block, return 403 with `"host not allowed"` |
| Same origin (Origin matches Host) | Allow |
| Client not a browser (no `Origin` sent, e.g., CLI, curl, MCP) | Allow |
| Host is an IP address | Skip Host check |

Allowlist includes: `localhost`, `127.0.0.1`, `::1`, `0.0.0.0`, plus custom domain you set in **Settings → Domain & SSL**, plus any names in `JAVIS_ALLOWED_HOSTS` environment variable (multiple names separated by comma).

When you need to touch this: running Thansa behind a reverse proxy with a domain not declared in the app, but **no password set yet**. Then Thansa thinks that domain is foreign and returns 403. Fix: set password (enables login gate which then skips Host check), or add domain to `JAVIS_ALLOWED_HOSTS`.

## API Tokens - Gateway for CLI and Scripts

Login cookies only work with browsers. When you want [Thansa CLI](24-cli-terminal.md) or a script to call Thansa, you need different credentials: **API token**, created at **Account > API Tokens (for CLI)** (System group, same page as login password).

Most important point: **no tokens exist by default**. Until you manually click create, no token exists, and no door opens outside the browser. Opening another gateway to the Internet must be a conscious action.

How Thansa keeps tokens:

| Rule | Why |
|---|---|
| Two scope levels: **chat only** and **full permission** | Chat-only uses a WHITELIST (`/chat`, `/version`, `/health`, `/sessions`). Whitelist wins over blacklist, because blacklist means every new endpoint added to Thansa auto-exposes to narrow token. |
| On disk only SHA-256 hash | Anyone reading server config file can't get the token. Raw string shows exactly once when created. |
| Compare using `compare_digest` | Normal string comparison exits early at first different character, and that time difference is enough to brute-force one character at a time. |
| Token goes in `Authorization` header, never in query string | Query string ends up in logs of every proxy along the way. |
| **Don't use token to create token** | Creating token requires browser session. Without this barrier, one leaked token lets its holder self-issue more tokens permanently, making revocation of the leaked one pointless. |
| But token **can self-revoke** | Lose laptop without access to browser and still need to kill that credential immediately. |
| Wrong 10+ times in 5 minutes, IP blocked for 15 minutes | Logs to `auth_audit.jsonl`, only first 12 characters (log files often sent with error reports). A token brute-force becomes visible instead of running silently for months. |

Token list shows **last used time** of each. See a token you don't remember getting used regularly, revoke it immediately - revocation takes effect right now, cannot be undone.

## Secrets in settings.json Encrypted

Sensitive fields in `settings.json` not stored as plain text. Thansa encrypts them using Fernet (AES-128-CBC + HMAC) before writing to disk, and auto-decrypts when reading. Encrypted value has `enc:` prefix.

Fields that are encrypted:

| Field | Is |
|---|---|
| `model.openrouter_key` | OpenRouter API key |
| `model.anthropic_api_key` | Anthropic API key |
| `model.openai_api_key` | OpenAI API key |
| `model.gemini_api_key` | Google Gemini API key |
| `model.openai_oauth.access_token` / `refresh_token` / `id_token` | ChatGPT login token |
| `telegram.token` | Telegram bot token |
| `backup.token` | GitHub PAT for brain backup |
| `voice.elevenlabs_key` | ElevenLabs API key |

Key used for encryption lives in file **`.secret_key`** in state directory (`JAVIS_STATE_DIR`, Docker: `/data/state/.secret_key`). File generates once, never goes to git.

Operational consequences to remember:

- **Copy `settings.json` to another machine but forget `.secret_key` and you lose all keys.** Thansa reads `enc:` but can't decrypt so returns empty string, you must re-enter every key. Intentional trade-off: better to ask for re-entry than leave keys exposed.
- **Backup both `settings.json` + `.secret_key` together**, and keep them as secure as each other.
- If machine missing `cryptography` library, Thansa can't encrypt: secret falls back to `plain:` prefix and server prints warning to log. Install via `pip install cryptography` then restart and encryption re-enables.
- Old values without prefix (saved before encryption existed) still read normally, and auto-wrap with `enc:` on next write.

## How Security Works (For People Who Want Deep Understanding)

| Mechanism | Implementation |
|---|---|
| Password storage | No plain password. Thansa hashes with PBKDF2-HMAC-SHA256 (120,000 rounds) plus random salt. |
| Login session | Issued via `javis_session` cookie, `httponly` style cookie (JavaScript can't read), `samesite=lax`. |
| Session timeout | Each session lives maximum **30 days** then auto-expires, must login again. |
| Session across restart | Sessions saved to file, so **restarting server doesn't log you out**. |
| Prevent password guessing | Count wrong attempts by IP. Enough consecutive wrong attempts (8) lock temporarily ~5 minutes; each wrong try slowed by half a second. When locked, Thansa says "Too many wrong attempts - try again in a few minutes." |
| Safe cookies over HTTPS | When accessing via **custom domain** with HTTPS enabled (Caddy On-Demand TLS), cookie marked `secure` (only sent over HTTPS). |
| CORS | Only open to `localhost` / `127.0.0.1` / `::1` (convenient during dev). Other web pages can't read API via browser. |
| CSRF gate | Block write requests from cross-origin, and block foreign Host when login not yet enabled (see separate section above). |
| Secrets on disk | API keys and tokens in `settings.json` encrypted with Fernet using `.secret_key` in state directory. |

About `secure` cookie: by default Thansa **does not** force `secure` cookie to work on both HTTP and HTTPS (avoid getting stuck in login loop after HTTP proxy like path-style `http://host/PORT/`). If you're certain running HTTPS end-to-end, enable `JAVIS_SECURE_COOKIE=1` in environment variable (see [Environment Configuration](16-cau-hinh-env.md)). Accessing via correct custom domain returns Thansa auto-enables `secure` without this variable (based on Host matching domain, not inferred from `X-Forwarded-Proto`).

## Quick Reference of Buttons and Status

| Button / text | Where | What happens |
|---|---|---|
| **Set Password** | Account → Login Account (when no password yet) | Create admin account and issue session right away for you |
| **Change Password** | Same place, when password exists | Change password and/or login name. Must enter current password; after change all other sessions log out |
| **Logout** | Account → Login Account | Delete this browser's session, reload page |
| **Disable Login** | Account → Login Account | Delete password + logout all sessions (ask confirmation first) |
| **Save** | Account → Workspace | Change workspace display name |
| 🔒 Password set · account: ... | Login Account | Have admin, login name shows right after colon |
| No password set - anyone opening dashboard can use it. Set password if putting on VPS. | Login Account | No admin yet |
| ✅ Account saved. | Login Account | Set password succeeded |
| ⚠ Minimum 8 characters. | Login Account | Interface blocks before sending to server, same limit as server |
| ⚠ Wrong current password. | Login Account | **Current Password** field wrong, nothing changed |
| **Forgot Password?** | Login screen | Click to show instructions for deleting `"auth"` block in `server/settings.json` then restart |

## Tips

- **Always set admin before going public.** Safest is to set `JAVIS_ADMIN_USER` + `JAVIS_ADMIN_PASSWORD` at deploy, no need to hunt for SETUP CODE.
- **Set password long enough.** Minimum 8 characters; use long phrases, hard to guess.
- **Run over HTTPS when accessing from afar.** Use custom domain (e.g., Hostinger `*.hstgr.cloud`) or Cloudflare Tunnel instead of exposing port 7777 raw to the Internet. How to point domain and enable HTTPS see [Brand & Custom Domain](15-thuong-hieu-ten-mien.md).
- **Localhost + tunnel then enable `JAVIS_REQUIRE_LOGIN=1`.** When machine only listens to localhost but you expose it outside via tunnel, Thansa doesn't auto-know it's public, so force login manually.
- **SETUP CODE one use only.** After creating admin, code self-destructs. Need new code then restart server.
- **Backup `.secret_key` with `settings.json`.** Missing either one means re-entering all API keys.

## Common Issues

**App asks for SETUP CODE.**
You're running public and have no admin yet. Get code from state: App terminal (inside container) run `cat /data/state/.setup_token`; on host run `docker compose logs javis` then find line with `SETUP TOKEN`. Or set `JAVIS_ADMIN_PASSWORD` to skip needing code.

**Click Change Password says "Account exists - please login."**
Bug in versions before 0.28.3, fixed. Page still holds old version in browser cache then reload with Ctrl+F5 (Mac: Cmd+Shift+R) then follow step C again.

**After changing password, phone (or other machine) asks to login again.**
Designed that way. Change password revokes old sessions so someone borrowing your machine stops working; login again with new password and done.

**Enter correct user/password but keeps returning to login screen (login loop).**
Usually `secure` cookie enabled while you're accessing via HTTP (many proxies serve HTTP like `http://host/PORT/`). Don't enable `JAVIS_SECURE_COOKIE` unless certain HTTPS end-to-end. If already enabled, remove this variable then restart server.

**Says "Too many wrong attempts - try again in a few minutes."**
You (or someone on same IP) entered wrong password too many times. Wait ~5 minutes then try again. Restarting server also clears this counter.

**All operations return 403 "host not allowed".**
You're visiting Thansa with a domain that Thansa doesn't know, while no password set. Add that domain to `JAVIS_ALLOWED_HOSTS`, or enter it in **Settings → Domain & SSL**, or simply set password.

**Any operation says 403 "cross-origin request blocked".**
You're calling Thansa API from another page (script, extension, iframe from third party). This is the CSRF gate doing its job. If it's your own tool, add its hostname to `JAVIS_ALLOWED_HOSTS`.

**Forgot password.**
Windows repo has **`reset-auth.bat`** script in project root: run it to delete account/password in `server/settings.json` and return app to setup state (prints "OK - password deleted." then shows restart instructions). Can't use script: edit/delete the `auth` block in `settings.json` in state directory (Docker: `/data/state`) then restart; or reset admin via `JAVIS_ADMIN_PASSWORD` after deleting old `auth` block.

**Switch machine / restore backup then all API keys empty.**
You copied `settings.json` but not `.secret_key` with it. No way to recover: re-enter keys on Models, Channels, and Settings pages. Next time remember both files.

**Disabled login but still asked for account.**
Server still running public (or `JAVIS_REQUIRE_LOGIN=1`). In this mode Thansa won't fully disable login but forces account creation again. To run without password you must make server listen to pure localhost.

## Related

- [Start & First Setup](01-bat-dau-thiet-lap.md) - set up Thansa and create admin first time.
- [Brand & Custom Domain](15-thuong-hieu-ten-mien.md) - point domain and enable HTTPS auto.
- [Environment Configuration](16-cau-hinh-env.md) - list security environment variables (`JAVIS_HOST`, `JAVIS_REQUIRE_LOGIN`, `JAVIS_ADMIN_USER/PASSWORD`, `JAVIS_SECURE_COOKIE`, `JAVIS_ALLOWED_HOSTS`, `JAVIS_STATE_DIR`).
- [Plugins](20-plugins.md) - why plugins you install must enable separately via environment variable.
- [Thansa CLI (terminal)](24-cli-terminal.md) - use API tokens to call Thansa from other machines.
- [Troubleshoot & FAQ](17-khac-phuc-su-co.md) - other common errors.
