# Thansa CLI - ask Thansa from terminal

*[Tiếng Việt](24-cli-terminal.md) · **English**

Install a small package on your machine then type `thansa "revenue this week how is it"` straight in terminal, no need to open browser. Answer still comes from your own Thansa: same brain, same memory, same MCP you plugged, same conversation history.

> **Read this first:** Thansa CLI **doesn't contain Thansa inside**. It's the microphone - the other end must be a Thansa server running, on this machine or on VPS. No server means CLI can't do anything, and it will say so straight not vague network error.

## What is this feature

- **Third channel**, beside web dashboard and Telegram. Same Thansa, just where you stand.
- Ask one question then exit (`thansa "..."`), or open ongoing Q&A session (`thansa chat`).
- Connect multiple Thansa: one profile for home machine, one for VPS, switch by `--profile`.
- Delegate Kanban task, browse brain, see loops, check server status - all from terminal.
- **Pipe into script**: answer goes to stdout, everything else goes stderr. So `thansa "summarize this week" > report.md` gives clean content, no status line noise.
- Thansa knows it's talking to terminal so answers differently: no markdown table, no image embed, file path printed absolute so you copy-run instant.

## Install

Needs Python 3.9 or newer. Package brings only **one** library (`httpx`), installs on machine never had Thansa.

```bash
pip install javis-cli
```

Install from source (when you cloned Thansa repo):

```bash
pip install ./cli
```

Then you have command `javis`. Check: `javis --help`.

## Step 1: create token in dashboard

Thansa server doesn't take outside commands without token. **No pre-made token** - until you create one the door stays closed.

1. Open Thansa dashboard, go **Account** (group **System** at nav bottom left) then scroll to **API Token (for CLI)**. Same page as login password, because token is another login method.
2. Set memorable name, e.g. "my laptop" - later when you revoke you know which one.
3. Pick scope:
   - **Chat only** - access `/chat`, `/version`, `/health`, `/sessions`. Enough for Q&A and history. Pick this if just asking questions.
   - **Full** - like logged-in browser. Needed for `javis task add`, `javis brain`, `javis loops`.
4. Click **Create token**. String appears **one time only**: server hashes it on save, no way to see again. Copy right away.

Lost token? Can't look it up, only create new one then revoke the old. On purpose.

## Step 2: hook CLI to your Thansa

```bash
javis login https://your-thansa.com
```

It will ask token, paste in. Or give straight:

```bash
javis login https://your-thansa.com --token jvs_xxxxx
```

CLI **tries real connection** before saving, so wrong address or token you know right here, not when asking first question.

Settings saved at `~/.javis/config.json`, permission `600` (only you read). File has token so don't put in repo or public backup.

### Many Thansa at once

```bash
javis login http://localhost:7777 --name home
javis login https://thansa.company.com --name work --brain work-brain
javis --profile work "how's this week at work"
javis profiles          # list saved, * is default
```

### Set by env var (for CI, Docker, server)

Three vars override config file, handy when you don't want token on disk:

| Var | Means |
|---|---|
| `JAVIS_URL` | Thansa server address |
| `JAVIS_TOKEN` | API token |
| `JAVIS_BRAIN` | default brain |
| `JAVIS_PROFILE` | default profile name |

## Daily use

### Ask one question

```bash
javis "revenue this week how"
javis "summarize notes this week"
```

No subcommand needed - type question straight and run. Sitting at terminal you see progress line running (Thansa calling which MCP, reading which file), then answer shows up.

### Ongoing Q&A session

```bash
javis chat
```

Type question, Enter, read answer, type next. Whole session shares one conversation code so Thansa tracks context: ask "and last month?" it understands you mean previous number. `Ctrl+D` or `/exit` to stop.

Want to continue same chat next time:

```bash
javis chat --session sales-august
```

### Pipe into script

This is the killer feature. Answer goes stdout, progress goes stderr, so redirect is clean:

```bash
javis "write sales summary this week" > report.md
javis -q "status today" | mail -s "Thansa" you@work.com
```

Flag `-q` turns off progress line. Fail means CLI exits non-zero and **prints nothing to stdout**, so `&&` in script works right.

### Check status

```bash
javis status
```

Shows Thansa version, is there new version, which brain running, token saving setting now, and percent saved last 24 hours.

### Delegate task, browse brain, see loop

Commands need **full** token.

```bash
javis task add "write post about new product"     # delegate Kanban task
javis task add "run monthly report" --mode auto     # suggest (default) | auto | full
javis tasks                                          # list tasks and status

javis brain ls                                       # list brain root
javis brain ls "05 - Data Cache"
javis brain cat "Memory/MEMORY.md"

javis loops                                          # which loop on, what permission
```

Task delegated runs in background on server. Result comes back to where you delegated, check progress on **Tasks** page on dashboard or type `javis tasks` again.

### Start Thansa on this machine

If machine already has Thansa installed (cloned repo):

```bash
javis up
```

It finds install (via `JAVIS_HOME` var, current folder, or `~/thansa-os`), starts it, and saves profile `local` for next time `javis "..."` runs. Thansa already running, it notices and doesn't start second copy.

Can't find install it says straight: **`javis up` doesn't have server inside**, and gives three fixes (set `JAVIS_HOME`, run from inside Thansa folder, or `javis login` to Thansa somewhere else).

## Manage token

Go **Account > API Token** on dashboard. List shows name, first 12 chars, scope, and **last used time** - if you see a token you don't remember using regularly that's time to revoke.

Click **Revoke** and token dies immediately, any machine using it loses connection right then and can't undo.

Few things to know how Thansa keeps token:

- **On disk only hash** (SHA-256). Even if someone reads server config file they can't get token out.
- **Token can't make token.** To create new token must be logged in by browser. If token leaks, whoever has it can't make more - revoke and done.
- **But revoke works with token itself.** Lose laptop and can't open browser, still revoke credential from terminal with the token.
- **Fail token 10+ times in 5 min then that IP blocked 15 min**, and each try logs to `auth_audit.jsonl` (only logs first 12 chars, since log often sent with errors). Token guessing becomes visible instead of running silent for months.

## When problem hits

**"Haven't connected to any Thansa"** - run `javis login <address>` first.

**Reports 401 or "token invalid"** - token wrong, or revoked. Create new one at Account > API Token then `javis login` again.

**Reports 403 when typing `javis task add` or `javis brain ls`** - your token is **chat only**. Create **full** token for those commands.

**Temporarily blocked** - tried wrong token too many times. Wait 15 min, or restart Thansa server.

**Can't connect** - check Thansa server still running (`javis status`, or open dashboard in browser). Thansa on VPS, check port and domain.

**Vietnamese chars show wrong on Windows** - run `chcp 65001` in terminal first, or use Windows Terminal instead of old cmd.exe.

See more at [Troubleshoot & FAQ](17-khac-phuc-su-co.md).

## Why CLI can't run standalone

Fair question: why not make a full agent that runs alone in terminal, no server?

Because nearly everything making Thansa work needs a **long-living process**: loop runs on cycle, reminders wait for trigger time, MCP Hub holds connection to POS and ads, capability registry keeps rules, runtime learns token saving through turns. CLI that exits when done doesn't fit.

Building second copy means copying everything then watching two versions drift - whichever gets less use has bugs sitting silent. So CLI talks through **exactly what the dashboard and Telegram use**. Trade-off: new feature in Thansa lands in CLI instantly, instead of two code paths to fix.

Design detail at [CLI spec](dev/2026-08-cli-spec.md).

## Related

- [02 - Conversation & voice](02-tro-chuyen-va-giong-noi.md) - web channel.
- [11 - Telegram Channel](11-telegram.md) - phone channel.
- [14 - Security & account](14-bao-mat-tai-khoan.md) - password, login, secret encryption.
- [21 - Tasks (Kanban)](21-viec-kanban.md) - where `javis task add` tasks land to run.
