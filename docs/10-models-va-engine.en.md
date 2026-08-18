# Models & Engine

*[Tiếng Việt](10-models-va-engine.md) · **English***

The **Models** page is where you choose the "brain" for Thansa: which engine to use, which model to answer with, log in to AI providers, pick a cheap model for background jobs, and turn on deep thinking level. This is the page that decides how smart Thansa gets and which plan's credits you're consuming.

If you're just starting, see [Start & setup first](01-bat-dau-thiet-lap.md) first. When you need to hook up more tools for Thansa, see [Connect & business numbers](09-mcp-va-so-lieu.md).

## What is this feature

Thansa can run on many different "engines" (AI providers). You pick 1 as **Main Model** (main model for chat), and optionally add:

- **Background job model**: cheaper model for tasks Thansa runs when you're not around - loop, Kanban job, reminder, self-teach, source ingest.
- **Thinking (reasoning)**: how much the model thinks before answering.

Most important thing to understand: **changing model does NOT break Thansa's features.** Every provider gets the same toolkit via Thansa's connection hub (MCP Hub): call hooked sources, read/write brain files, run skills, assign Kanban tasks (tool `javis_task`), create agent/workflow/loop/reminder (tool `javis_schedule`).

| How to call | Provider | MCP Thansa · tool file brain · skill | Run machine commands (Bash) |
|---|---|---|---|
| Via **Claude** | Anthropic OAuth (Claude) | Yes - MCP native + skill native | **Yes** |
| Via **Codex** | OpenAI OAuth (ChatGPT) | Yes - MCP via hub (includes local connectors like Zalo/Webcake) + Codex's native MCP stock (server you register via `codex mcp add`) + skill via router (`javis_use_skill` / read file `skills/`) | **Yes** |
| Via **Antigravity CLI** | Google Antigravity CLI (`agy`) | Yes - MCP via hub (write to `.antigravity/` in the brain you're in) + skill via router | **Yes** |
| Via **Gemini CLI** ⛔ | Google Gemini CLI (personal accounts cut off by Google 18/06/2026) | Yes - MCP via hub (write to `.gemini/settings.json` in the brain you're in) + skill via router | **Yes** |
| **Call API direct** | OpenRouter | Yes - MCP via hub + tool file vault + skill via router | No |
| **Call API direct** | OpenAI (API) | Yes - like above | No |
| **Call API direct** | Anthropic (API) | Yes - like above | No |
| **Call API direct** | Google Gemini (API) | Yes - like above (from 0.9.270 connection page also stopped false warning) | No |
| **Call API direct** | Groq (API) | Yes - like above | No |
| **Call API direct** | Ollama Cloud | Yes - like above | No |

### Four things API engine doesn't have

Before 0.17.1 this page said "only difference is running machine commands or not". True but short. Real list:

- **Machine commands (Bash)** - run commands on the server.
- **WebFetch and WebSearch** - self-open a random URL to read, self-search web. API engine wanting outside data must go through hooked MCP.
- **Task** - spawn child agent to run in parallel within one turn.
- **Resume prior CLI session** - API engine rebuilds context each turn.

Plus two practical API engine limits: each turn max **8 tool call rounds** (more it stops and reports), and when turn **has tool calls** the answer shows as one chunk at end instead of flowing word by word (each round is one request).

Besides those, everything else is identical. Specifically: call any hooked MCP, read and write brain files, run skills, assign Kanban tasks, create loop and reminders, create agent/workflow/skill (they're just `.md` files in vault), make images, use plugin tools.

> **Assigning Kanban task from API engine since 0.17.1.** Before then only way was `POST /kanban/task`, which needed Bash and curl - only Claude and Codex could do, though docs promised all brains could. Now with tool `javis_task` going via hub that promise is real.

Short: **features lie in Thansa, not the model.** Three CLI engines (**Claude** with Claude plan, **Codex** with ChatGPT plan, **Antigravity CLI** with Google plan) use your own subscription and run extra machine commands; six API providers only need one API key and do everything else - even orchestrate jobs, create loops, run skills. Agent in Workflow also picks model per provider - see [Agents & Workflows](07-agents-va-workflows.md).

## Where to open in Thansa

1. Open Thansa dashboard (default at port `7777`).
2. On left sidebar, open **Connect** group, then click **Models**.
3. Models page shows 4 blocks in order: **◆ Main Model** ("main model for chat"), **◆ Providers** ("log in / connect to provider"), **◆ Background job model** ("loop · Kanban job · reminder · self-teach · source ingest"), **◆ Thinking** ("reasoning depth when answering").

## Ten providers ready to use

**Providers** block lists 10 providers. **Already connected ones ranked up top**, not connected pushed down; within each group keeps original order below. This way if machine already hooked a few providers, opening page shows them right away, no scrolling.

| Provider (label on screen) | Connection type | Note |
|---|---|---|
| **Anthropic OAuth (Claude)** | Log in Claude, no key needed | Full MCP/skill/machine tool. Default Main Model |
| **OpenAI OAuth (ChatGPT)** | Device code (log in ChatGPT plan) | Runs via Codex, hook connection storage via hub + use skill via router |
| **Google Antigravity CLI** | Type `agy` **once in terminal**, no key | Google's only pick to replace Gemini CLI. Runs via binary `agy`. Full MCP/skill/machine tool, and pick **exact model row of Antigravity IDE** (includes non-Google models) |
| **Google Gemini CLI** | Log in Google, or `GEMINI_API_KEY` | ⛔ Google **cut all personal accounts** since 18/06/2026 (free, AI Pro, Ultra). Only runs with business Code Assist license or API key - see [B2](#b2-gemini-cli---google-cut-personal-accounts-18062026) |
| **OpenRouter** | Paste API key | Many models one place, MCP + file tool + skill via hub |
| **Anthropic (API)** | Paste API key | MCP + file tool + skill via hub (from 0.9) |
| **OpenAI (ChatGPT API)** | Paste API key | MCP + file tool + skill via hub |
| **Google Gemini (API)** | Paste API key | MCP + file tool + skill via hub |
| **Groq (API)** | Paste API key | MCP + file tool + skill via hub. Fast reasoning, good for background job model. This key also is what lets you **voice command via recording on Telegram and Zalo** (Whisper hears voice to text) - see [Telegram](11-telegram.md) and [Zalo channel](26-kenh-zalo-bot.md); hooking key enough, no need to switch main model |
| **Ollama Cloud** | Paste API key from ollama.com | MCP + file tool + skill via hub. Large open-source models (gpt-oss, qwen3-coder, deepseek) run on Ollama's server |

Each provider card shows status **● Connected** or **○ Not connected**, with number of available models, and a label type beside name: **MCP/skill** (Claude), **Device code** (ChatGPT), **MCP Thansa** (API providers). Whichever card is Main Model gets label **MAIN**.

> Before 0.9.270 API provider labels said **chat**, making many think they only chat plain. Wrong: they call connection storage, read/write brain and run skills exactly like two CLI engines. Label now is **MCP Thansa** for correctness.

## How to use (step by step)

### A. Connect Claude (default)

This is the default engine. It uses every tool, skill and memory, plus run machine commands. Optional: if you don't have a Claude plan, skip this and go straight to B (ChatGPT) or C (API key) - Thansa runs full features either way, just missing machine commands when using API key.

1. Go to **Models**, find card **Anthropic OAuth (Claude)**.
2. If not logged in, card says **○ Not logged in** with two buttons: **Log in Claude** and **↻ Check again**.
3. Click **Log in Claude**. Thansa shows line "**1)** Open this link to log in claude.ai" with link.
4. Open that link to log in your claude.ai account.
5. If page shows **one code**, paste code to "paste code (if any)" field then click **Send code**. Some flows don't need code paste - Thansa just waits and auto-checks every 3 seconds, connection done the card auto-changes. Over 5 minutes it times out with "Timed out, try again.".
6. When done, card changes to **● Connected** with email and plan.

Button **↻ Check again** only shows when not logged in, use when you just logged in via terminal and want Thansa to see it. When connected, card has only one button **Disconnect**.

This works even on VPS with no screen. If you prefer command line, you can run `claude auth login --claudeai` in terminal.

### B. Connect ChatGPT with your subscription

Use your ChatGPT Plus/Pro plan instead of a separate API key. This runs via Codex and Thansa auto-pushes your connections (e.g. POS sales) to Codex so ChatGPT can also call those tools.

Card **OpenAI OAuth (ChatGPT)** when not connected has **two** buttons, for two login paths:

**Path 1 - button "Log in ChatGPT" (device code, for most people):**

1. Click **Log in ChatGPT**. Thansa opens OpenAI's auth page and shows line like "Open <link> · enter code **XXXX-XXXX** - waiting…".
2. On the page just opened, enter that code exactly.
3. Thansa auto-waits and checks. Done then shows **✓ Connected!** and card changes to **● Connected** with account plan.
4. Thansa waits roughly 16 minutes then gives up with "Timed out, try again." - at that point click **Log in ChatGPT** again for new code.

**Path 2 - button "Via browser" (when your workspace BLOCKS device code):**

Some ChatGPT workspaces turn off device code, clicking first button gives error. Don't think it's broken, use this button:

1. Click **Via browser**. Thansa opens ChatGPT login page in new tab.
2. After logging in, browser jumps to **localhost** and very likely **shows can't load page - that's normal**, since Thansa doesn't really open that port.
3. **Copy the entire address bar URL** (like `http://localhost:1455/auth/callback?code=…`) and paste into Thansa field, click **Confirm**.
4. Thansa extracts code from that URL and trades for token. Done then shows **✓ Connected!**.

Since just need to paste URL back, this path also works when Thansa is on VPS while browser on your machine.

To disconnect: click **Disconnect** on this card. If ChatGPT is Main Model when you disconnect, Thansa auto-switches Main to Claude so chat doesn't break.

Note: this is experimental path (runs Codex backend). For max stability, use Claude or OpenRouter.

### B1b. Connect Antigravity CLI (use your Google plan)

This is the **Google's pick** after they cut Gemini CLI for personal accounts. Biggest plus: you pick **exactly the model row in Antigravian IDE**, including non-Google models.

1. Install CLI once on machine running Thansa:
   - Linux/macOS: `curl -fsSL https://antigravity.google/cli/install.sh | bash`
   - Windows PowerShell: `irm https://antigravity.google/cli/install.ps1 | iex`
2. Type `agy` once **in terminal of machine running Thansa**. If machine has display it auto-opens browser; via SSH it prints a link - open that link on your machine then log in Google. Session saves in OS keyring so only need once.
3. Back to **Models**, card **Google Antigravity CLI**, click **Check again** (it test-runs one real chat). Card changes to **● Logged in**.
4. Click **Switch model ▾** in Main Model block, pick this provider then pick model.

Model list **asks `agy models` directly**, not Thansa keeping a cheat sheet, so whatever models your account gets you see exactly, and Google renaming models won't make picker stale.

A few things different from Gemini CLI, forewarning to avoid confusion:

- **Log in is in terminal, dashboard has no button** (from 0.32.2). Version 0.30.0 used to build a login flow right on page: Thansa opened `agy` in a fake terminal then relayed between it and your browser. Worked on Linux, but the UI field on page was click-dead so you ended up opening real terminal anyway, and Windows has no pseudo-terminal so never worked. `agy` users all have terminals already, so one command is cleaner than half-baked UI. So Thansa doesn't hold anyone's token - it sits in OS keyring.
- **Read-only level here is lighter.** On Gemini CLI, `suggest` mode goes straight to CLI's `--approval-mode plan` so CLI blocks it. `agy` has no equivalent, so Thansa tightens via `--sandbox` plus system prompt hinting. Money/order/post block still lives in MCP Hub like every engine.
- **Doesn't resume prior CLI chat.** Opens new chat each turn then primes with saved history, so **no context loss** but burns more tokens.
- Thansa doesn't auto-install `agy` at setup (different from three npm engines): Google's installer is a script download-and-run, so you run it when you want.
- **On Windows, prompt no longer goes via command line** (from 0.33.1, fixed again 0.33.2). Windows caps command line at 32767 chars, but Thansa's system prompt on blank brain alone is over 36.000 - so this brain used to die outright on Windows, and error message blamed "chat too long" so restarting with fresh chat never helped. Workaround was going via file; now works.
- **Thansa MEASURES how this `agy` copy takes prompt, doesn't guess.** Learned lesson paid twice: 0.33.1 inferred syntax from official CHANGELOG (says `agy` reads stdin when prompt uncapped) so it sent `--print ""`, and real `agy` errored because it checks flag value before looking at stdin. Docs were right on principle, wrong on syntax. Now first run Thansa tries three ways to pump stdin with tiny prompt containing unique marker, whichever way marker comes back wins and Thansa remembers for later. No way works, it writes context to file and tells model to read it; model can't read then it says straight, no silent wrong reply. Hinting on prompt style, it doesn't guess poorly.

- **Vietnamese diacritics don't break mid-line** (from 0.33.6). Old symptom: word "gồm" becomes `g<?><?>m`, each Vietnamese char 3 bytes turns into 3 `<?>`. That's the signature of something reading in mouthfuls, cutting mid-char then decoding piecemeal. Measured and ruled out Thansa (its reader uses incremental decode, cuts mid-char still joins back right), so break lives in `agy`'s reader. Thansa can't patch CLI, but fixes where Thansa sets break: now pumps prompt by chunks ending exactly on char boundary, so whatever `agy` reads won't break. Mangled char comes back, Thansa switches to file route and asks again; still mangled means error is in CLI. Tell us with CLI's error message.

**If still error on Windows**, set env var `JAVIS_AGY_PROMPT_DAI=file` to force file route, then report back with `agy` error line.

### B2. Gemini CLI - Google cut personal accounts (18/06/2026)

> ⛔ **Read before doing this.** June 18 2026 Google stopped serving Gemini CLI for **every personal account** - free tier, Google AI Pro and Google AI Ultra all cut. Log in still works, but when you chat CLI returns `IneligibleTierError` plus `reasonCode: UNSUPPORTED_CLIENT`. This is server-side block by Google, **not config error and Thansa can't patch it**.
>
> Still works if you have **business Gemini Code Assist license**, or run CLI with **API key** (`GEMINI_API_KEY`) - but if you're paying per call, **Google Gemini (API)** card in section C is cleaner.
>
> **Want Gemini model, or want model picker as full as Antigravity:** use **Antigravity CLI** (binary `agy`, install via `curl -fsSL https://antigravity.google/cli/install.sh | bash`). Thansa **hasn't** hooked this engine yet.

> **From 0.29.1 this card SELF-HIDES** on Models page when machine has no binary `gemini` - meaning almost everyone won't see it, won't trip on a dead choice. Machine with `gemini` installed (usually business license or API key) shows card back, and anyone SETTING it as Main also still sees it to switch to other engine. Thansa also stopped auto-installing `@google/gemini-cli` at setup; install it yourself if needed.

Below kept for anyone still eligible (business / API key).

1. Check CLI already there. Installs via Docker and `install.sh` **already have** `@google/gemini-cli` pre-installed, so usually skip this. Only when card says *"Gemini CLI not installed"* install by hand on machine running Thansa: `npm install -g @google/gemini-cli`
2. Go to **Models**, card **Google Gemini CLI (log in Google)**, click **Log in Google**.
3. Thansa opens Google's consent page (shows app name **Gemini CLI** exactly). Log in your Google account, OK then Google shows **one code**.
4. Copy that code paste to field in Thansa, click **Done**. Card changes to **● Logged in Google** with email.
5. Click **Switch model ▾** in Main Model block, pick this provider and one model (default `gemini-2.5-pro`).

No localhost in the middle so this works **even when Thansa on VPS while browser on your machine** - same as Claude login flow. Thansa uses Gemini CLI's public OAuth client, so Google's consent page shows **Gemini CLI** name, right app gets token.

Logged in, Thansa keeps refresh token (encrypted in `settings.json`) and **rebuilds CLI credential file before each run** - needed since new Gemini CLI loads file into keychain then deletes it.

Click **Disconnect** to drop Google account from Thansa. This button only shows when logged in via dashboard; anyone logged in via terminal `gemini` command then token is CLI's, Thansa doesn't drop it.

Still can log in via terminal if you like: run `gemini` then pick **Login with Google**. Thansa recognizes that account type too.

If you install elsewhere and Thansa can't find binary, set env var `JAVIS_GEMINI_BIN` pointing to it then restart.

**Why not hook direct to Antigravity:** that app is pure Electron, no command-line port to call silently, and token lives in encrypted Keychain. Even if pried out, that's Google's internal API not promised to third parties, can break anytime. Gemini CLI gives the exact package via Google's public path.

### C. Connect provider with API key (OpenRouter / Anthropic API / OpenAI API / Gemini / Groq)

1. Go to **Models**, find card for provider.
2. Paste API key to input field (field says "paste API key to connect").
3. Click **Connect**.
4. Card changes to **● Connected** with model count.

Want to switch key later: type new key then click **Switch key** (field now says "switch key" with last 4 chars of old key). Want disconnect: click **Disconnect** (this deletes key). If provider is Main Model when disconnected, Thansa auto-switches to Claude.

Where to get key:

- **OpenRouter**: site openrouter.ai (one key calls many models from many makers).
- **Anthropic (API)**: console.anthropic.com.
- **OpenAI (ChatGPT API)**: platform.openai.com.
- **Google Gemini (API)**: Gemini API key, get at aistudio.google.com.

### D. Set Main Model (pick main model)

1. In **◆ Main Model** block top of page, you see current model and provider name.
2. Click **Switch model ▾** button.
3. Window **SET MAIN MODEL** opens, sub-line says "current: <model> · <provider>":
   - Left column: provider list. Not-connected providers show **⚠ needs connecting**; provider in use shows **IN USE**.
   - Right column: model list for picked provider.
   - **Filter provider / model…** field at top to type and find fast (filters both columns at once).
4. Click provider on left, then click model on right. Current model has label **IN USE**.
5. Click **Switch** to apply, or **Cancel** (or ✕ button) to close.

Model list loaded live from provider (label **· live**). If can't get from network, Thansa uses fallback list (label **· catalog**); loading shows **· loading…**. Your chosen model saves and applies to new chat.

Main Model block also shows one line about engine in use, clear on path and real limits: "Via Claude - MCP Thansa + skill + loop + run machine commands", "Via Codex - MCP Thansa + skill + loop + run machine commands", or "Call API direct - MCP Thansa + skill + loop (no machine commands)". Before 0.9.270 last line said "plain chat (no MCP)" - wrong and removed.

### E. Pick background job model

Block **◆ Background job model** picks which model runs tasks Thansa does when you're not around: **loop · Kanban job · reminder · self-teach · source ingest**. Usually pick a cheap model here to shave credit silently.

1. Scroll to **◆ Background job model** block. Big line shows current: unchanged then says **Default per Claude** with small line "don't switch model, use default".
2. Click **Switch model ▾**. Window opens same as Main Model table but title is **BACKGROUND JOB MODEL**, footer says "Background job: loop · Kanban job · reminder · self-teach · source ingest", apply button name is **Pick**.
3. Pick provider on left, model on right, then click **Pick**.
4. Want to go back: click **To default** (button only shows when you set one).

Few things to know:

- **Can pick ANY provider you hooked**, not just Claude: Claude, ChatGPT/Codex, OpenRouter, OpenAI, Gemini, Anthropic API. Pick different provider then background jobs run on that provider's plan or key, stops eating Claude quota.
- If you pick one not-yet-connected provider, this block shows warning "⚠ provider not connected - background job will fall back to Claude". Job doesn't die, just no savings.
- **Tools differ between routes.** Claude and Codex read/write files direct in brain. API models (OpenRouter, OpenAI, Gemini, Anthropic API) read/write via Thansa's vault tool and **can't run machine commands**, so fit read-summarize-write jobs; background job needing machine commands just stays Claude.
- With API route, file write tool auto-locks when loop at `suggest` level, exact as Claude mode.

### F. Set Thinking level (reasoning)

Turn on to make model think harder before answering: more accurate, but slower and burns more tokens.

1. Scroll to **◆ Thinking** block.
2. Click one of 4 levels: **Off**, **Low**, **Medium**, **High**.

This level applies different by engine:

- **Claude API / OpenRouter**: use adaptive thinking + effort level matching.
- **OpenAI**: only applies to o-series models (o1/o3/o4) and gpt-5; normal models ignore it.
- **Gemini**: only applies to 2.5+ models (and models with "thinking" in name). Older models don't get this param to avoid error.
- **Claude**: insert thinking hint into query (from think level to ultrathink as depth ramps).

## What Claude engine runs under the hood

From 0.9.37, Thansa's Claude engine runs **only via Claude Agent SDK** (Anthropic's official library). Old branch that called `claude` command as separate process got removed. Two things users need to know:

- **Machine MUST still HAVE `claude` CLI.** SDK calls that CLI under the hood, and all login and native MCP go via it. No CLI means Claude Code card errors and engine won't run - see [Start & setup first](01-bat-dau-thiet-lap.md).
- **Tool permission in background phase gets checked PER CALL.** When loop or workflow runs in safe background mode, each time Thansa is about to call a tool outside the allow list it gets rejected right there and logged, not just announced at startup. Rejection message says this is background session tool gate, **not** MCP connection broken - see that line means don't re-login connector.

## Claude (full tools) and calling API direct differ how

This is the trickiest spot, must get it clear:

- **Main Model = Claude**: strongest - native file read/write, run machine commands, call MCP, native skill, auto loop, session resume. Peak Thansa OS exploitation mode.
- **Main Model = ChatGPT OAuth (Codex)**: call all connection storage (hub auto-pushes to Codex, including local connectors like Zalo), have Codex file tool, and use skill via router (Thansa lists skill in system prompt + tool `javis_use_skill`; Codex runs cwd=brain so reads `skills/<slug>/SKILL.md` straight). Plus Codex loads its own native MCP stock (server you register via `codex mcp add`, see collapsed "◆ Native connections of Claude and Codex" block on Connect page) - like how Claude engine uses Claude's native MCP.
- **Main Model = OpenRouter / OpenAI (API) / Anthropic (API) / Gemini**: from 0.9 all four can call connection storage via tool round-trips, plus brain file tool and skill activation (`javis_use_skill`). **Background job also runs on these providers** (see section E). Remaining difference vs Claude: no machine command tool (Bash), no WebFetch, can't resume CLI session.

Practical upshot: keep Main at **Claude** for **most complete** Thansa. Switch to API provider when you want to try one specific model from another maker, or want to push background jobs to cheaper plan.

## Save tokens across subscription plan

Block **Token save mode** on **Usage** page (System group) makes Thansa send fewer words each turn: only load related memory part, only load skill when needed instead of listing all.

From 0.12.4, this works for **all three brain types**, not just API key:

| Brain type | Why still worth turning on |
|---|---|
| API key (OpenRouter, OpenAI, Anthropic, Gemini, Groq) | Fewer token = less money, and avoid hitting per-minute quota |
| Claude plan (Claude) | Fewer token = each 5-hour window do more turns |
| ChatGPT plan (Codex) | Same as above |

Open page and right away see **Brain now in use** block: it says brain category, which save modes apply, and which ones don't plus why. Some modes only run on API-key brains - e.g. chat history resend, since Claude and Codex remember their own chat session, sending again means sending twice.

**Hit plan quota** then Thansa says in Vietnamese: which plan ran out, how much time left, which other brain pre-set to run temp. Thansa **doesn't auto-switch brain** - switching costs another account's cap, maybe real money, so that's your call (switch here, chat stays). Note: quota type is **usage count per hour**, not length, so shortening question doesn't help.

## Quick model switch

Don't have to leave Models page to switch: click **Switch model ▾** on Main Model block to open **SET MAIN MODEL** right there, pick provider + model then **Switch**. This saves and applies to next chat. **◆ Background job model** block has its own **Switch model ▾** button (opens **BACKGROUND JOB MODEL** table), and level buttons in **◆ Thinking** apply right when you click.

## Quick reference: buttons and status

| Button / line | Where | What it does |
|---|---|---|
| **MAIN** | Provider card corner | This provider is Main Model |
| **● Connected** / **○ Not connected** | Provider card | Status with available model count |
| **○ Not logged in** | Claude card | Not logged in to Claude |
| **Log in Claude** | Claude card | Start login flow via link |
| **↻ Check again** | Claude card (when not logged in) | Re-check login status |
| **Log in ChatGPT** | OpenAI OAuth card | Log in via device code |
| **Via browser** | OpenAI OAuth card | Fallback path when workspace blocks device code |
| **Connect** / **Switch key** / **Disconnect** | API provider card | Save new key / switch key / drop key |
| **Switch model ▾** | Main Model and background job model | Open model picker table |
| **To default** | Background job model | Return job model to Claude default |
| **USED** | Model picker table | Provider or model now set |
| **⚠ needs connecting** | Model picker table, left | That provider not keyed / not logged in |
| **· live** / **· catalog** | Model picker table | List from network / fallback list |
| **Switch** / **Pick** | Model picker table foot | Apply for Main / background job |

## Tips

- If just want Thansa remembering and working smooth, leave Main on **Claude**. Other providers for special needs.
- Set **Background job model** to cheap to keep loop, Kanban, reminder, self-teach and ingest from eating Main plan. Want to see what burns most, check [Usage: tokens & cost](23-muc-dung-token.md).
- Flip **Thinking** to Medium or High when asking hard things (analyze, strategy); off for quick asks to save wait.
- OpenRouter handy if wanting to try lots of makers' models on one key.
- Want ChatGPT calling your sales tools: hook connection in [Connect & business numbers](09-mcp-va-so-lieu.md) first, Thansa auto-pushes to Codex.

## Common trouble

- **Claude card says "Claude CLI not installed"**: machine missing Claude CLI. SDK needs it (CLI runs under the hood). Install then click **↻ Check again**. See [Start & setup first](01-bat-dau-thiet-lap.md).
- **Chat GPT log in gives no code, or instant error**: your workspace might block device code. Use **Via browser** button in section B.
- **ChatGPT log in says "Timed out, try again."**: Thansa waits ~16 min then gives up. Click **Log in ChatGPT** again for new code.
- **Can pick provider but model column empty**: provider not connected, or no models. Connect it again in Providers block, or add models to `settings.json` (key `model.catalog`). See [Env settings](16-cau-hinh-env.md).
- **Model returns nothing**: retry or switch model in **SET MAIN MODEL** table. On Anthropic API, message has reason too (e.g. out of max_tokens: send "continue" for model to write more).
- **Connection page shows yellow line "⚠ Main Model is ... - doesn't support calling tools. Switch on Models page."**: from 0.9.270 **no built-in provider** throws this anymore. Before that Google Gemini got snagged out of list so it warned wrong though MCP hub was running normally underneath. Yellow line now only blocks unknown provider. Six providers Claude, OpenRouter, OpenAI, Anthropic API, Gemini and Groq show GREEN; ChatGPT OAuth alone has GREEN with separate line saying it runs via Codex CLI.

- **Red banner "⚠ Brain claude lost login" on machine never had Claude**: fixed 0.9.270. Brain light stays ON in RAM and no cleanup, so red stayed lit from when Claude was Main then you switched to OpenRouter. Now light only counts brains you REALLY pick (Main + background job when explicitly set), and kills automatically when you switch provider - not waiting 10-min scan.
- **Click Disconnect provider that's Main**: Thansa auto-switches Main to Claude so chat keeps working. Intentional, not bug.
- **ChatGPT OAuth says Codex CLI not installed**: this path needs Codex CLI on machine. From 0.28.8 all three CLIs (Claude, Codex, Gemini) pre-install at Thansa setup - Docker, `install.sh` and `setup.bat` - so message usually means old install, **update Thansa** once and you have it. Can install by hand too: `npm i -g @openai/codex`.

## Related

- [Connect & business numbers](09-mcp-va-so-lieu.md) - hook data sources and tools all engines share.
- [Usage: tokens & cost](23-muc-dung-token.md) - see which model, which job burns most.
- [Agents & Workflows](07-agents-va-workflows.md) - pick model per agent.
- [Start & setup first](01-bat-dau-thiet-lap.md) - install Claude CLI and Codex CLI.

Still stuck, see [Troubleshooting & FAQ](17-khac-phuc-su-co.md).
