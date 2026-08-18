# Telegram Channel

*[Tiếng Việt](11-telegram.md) · **English***

Turn on Telegram bot to ask Thansa straight from phone, no need to open dashboard. You text the bot like texting a person, Thansa answers with the same brain and memory running on your machine/VPS.

## What is this feature

- You create one Telegram bot of your own (free), paste token into Thansa, limit to only your account.
- After turning on, any regular text you send to bot Thansa will answer. Bot freshly on shows Telegram's "typing" indicator, sends one status message that auto-updates text as it progresses then self-deletes when reply comes.
- Has ready quick commands (start with `/`) to see status, switch model, stop running query, start new chat, save note to brain.
- Over Telegram Thansa still has full MCP and skills: ask sales numbers, ads, read and write vault files all work. This is true for EVERY engine (Claude, ChatGPT/Codex, OpenRouter, Claude API, OpenAI API) since Thansa's tools go via MCP Hub not tied to one engine.
- Send files two ways: you send image/document to bot for Thansa to read, and files Thansa creates in the turn self-send back to you.
- **Voice command**: press and hold mic say one sentence, Thansa hears to text then does like you typed. Need Groq API key on Models page once.
- Answer runs in background: while answering this message you can still send `/stop` to cut it off.

See more engine and model at [Models & engine](10-models-va-engine.md), MCP tools at [Connect & business numbers](09-mcp-va-so-lieu.md).

## Where to open in Thansa

1. Open Thansa dashboard (default `http://localhost:7777`).
2. On left navigation, open **Connect** group then click **Channel**.
3. You'll see **Telegram** card with fields: enable/disable bot, Bot token, Chat IDs allowed, and 2 buttons **Save & turn on** / **Send test**.

## Prep: get Bot token and Chat ID

These 2 are required. Do in Telegram app (phone or computer).

### Get Bot token (from BotFather)

1. In Telegram find account named **@BotFather** (has blue checkmark) and open chat.
2. Type `/newbot` then follow instructions: set display name for bot, then set username ending with `bot` (ex `my_thansa_bot`).
3. BotFather returns string like `123456789:ABCdef...`. This is **Bot token**. Keep secret, whoever has this token controls bot.

### Get your Chat ID (and anyone else sharing)

Chat ID is the account number in Telegram. Thansa uses it as an allow list: only IDs on list can text bot.

1. In Telegram find bot named **@userinfobot** and open chat, click Start.
2. It returns line `Id: 123456789`. That number is **your Chat ID**.
3. Write down this number to paste to Thansa in next step.

Want others (wife/husband, staff...) to share bot: have each person do steps 1-2 above to get their Chat ID, and remember each person must open your bot and click **Start** once (Telegram only lets bot text people who started).

## How to use (step by step)

### Step 1: Set up and turn on bot

1. Go to **Channel** (in **Connect** group) on dashboard, to **Telegram** card.
2. Tick **Turn on Telegram bot**.
3. Paste token string to **Bot token** field. (If you set token before, field shows "(already set)"; leave blank if you don't want to change token.)
4. Paste Chat IDs to **Chat IDs allowed** field. Multiple people sharing then paste multiple IDs separated by comma, like `123456789, 987654321`.
5. Click **Save & turn on**.

Thansa saves config and auto-restarts bot right after clicking Save (you don't click separate restart). Status line below card will show "✅ Saved, starting bot…" then auto-update after ~2 seconds.

### Step 2: Check bot is receiving

Small text right under 2 buttons is real bot status. Each line means:

| Status line | Meaning |
|---|---|
| 🟢 Bot receiving messages | Bot working, text bot and Thansa answers. Line has number of allowed Chat IDs, or warning "EVERYONE can text (ID not limited)" |
| ⚪ Bot NOT on | Haven't ticked "Turn on Telegram bot" and saved |
| ⚪ Bot token missing | Already on but no token |
| ⏳ Starting bot | Bot just turned on, wait a few seconds |
| 🔴 409 | Same token running somewhere else (other Thansa, other machine, or old webhook). Only one place per token. See Trouble section |
| ⚠ Bot error | Other error, line shows details |
| ⚪ Bot off | Bot stopped (not turned back on) |

Important: sending test successfully DOESN'T mean bot is receiving. Test only proves token and Chat ID valid. To know bot receiving, status line must be 🟢 **Bot receiving messages**.

### Step 3: Send test (optional)

1. Click **Send test** button.
2. If token and Chat ID valid, Thansa sends to your Telegram chat one message: "✅ Thansa Telegram connected. Ask any question." Status line shows "✅ Sent test." (multiple IDs show "✅ Sent test to 2/3 IDs." with errors for bad IDs).
3. If token or Chat ID missing, test button says config incomplete. Save & turn on first then try test again.

### Step 4: Ask Thansa via Telegram

1. Open chat with your bot on Telegram.
2. Type any question like normal chat, ex "What tasks today?" or "Summarize vault for me".
3. Bot shows "typing" indicator with one temp status message, then sends reply. Long answer auto-splits to multiple messages.
4. While bot answering, if you send new message, bot says "⏳ Processing prior. Send /stop to stop then ask again." Only one turn per person at a time.

## Status message auto-updates then stays as a trace

Right when receiving your question, bot sends you one real message: **🤔 Thansa processing…**. This message does NOT send repeatedly, it gets **edited in place** as it progresses, always starting with ⏳:

| Text you see | Thansa doing |
|---|---|
| 🤔 Thansa processing… | Just got question, starting turn |
| ⏳ ⚙ Calling: `<tool name>` | Claude engine calling one tool (Read, Write, MCP tool...) |
| ⏳ ⚙ Calling tool: `<tool name>` | API engine (OpenRouter, OpenAI, Claude API) calling tool via MCP Hub |
| ⏳ ✓ Got result - analyzing… | Tool returned data, engine reading |
| ⏳ ✍ Drafting answer… | Started generating text |

Few notes:

- Status message updates max **once per 2.5 seconds**, don't watch it jump constantly. Limit because Telegram rate-limits bot if too many edits.
- Message sends **silent, no phone vibrate**. Just for you glancing when waiting in chat. Only one sound in whole turn: when real reply arrives and bell notification shows the reply.
- When done, bot **no longer deletes status message**. Last edit becomes one short trace line, real answer is new message below. From **0.26.4** it's this way; before it would delete so many thought bot broke.
- Trace line shows which tools called and time taken, like `⚙ pos_statistics · Read · 8s`. No tools used shows `✓ Direct reply · 3s`. This stays in history so later you can see a number just pulled from POS real data vs. guessed, and it's proof Thansa touched MCP.
- Typing `/stop` mid-turn: status message changes to **⏹ Stopped.** and bot sends no reply for that turn.
- Line "⚙ Calling..." is proof Thansa really touched MCP (POS, ads, calendar, files...) not fake answer.
- These status messages only on **your Thansa bot**. [Chatbot for customers](25-chatbot.md) talking to guests hides them clean, just shows "typing" dot like real person.

## Send files to bot, get files from bot

Bot runs files both directions. This is fastest way to get a photo or document into brain when away from desk.

### You send image/file to bot

1. Send image or document file straight to bot chat, add caption if you want to explain.
2. Gateway downloads file to `inbox/telegram/` **of the brain set for your Telegram session** (switch via `/brain`), then puts that path in message for engine to read.
3. Thansa reads file right there and replies same way. Same-name file doesn't overwrite: Thansa adds suffix `_1`, `_2`.

Limits to remember:

- **Download limit 20MB** (Telegram bot API cap, not Thansa). File over that, bot says it can't download and suggests other ways.
- **Voice record Thansa can hear** - see section below.
- **Video and video note: Thansa can't watch yet.** Bot will politely ask you type, send voice, or send as document file.
- Caption can be command too. Ex take photo of receipt then caption `/notes today steel box receipt` so Thansa runs `/notes` command with that image, not as plain text.
- `inbox/` is **cache zone**, not knowledge store: file over **30 days old** or cache over **300MB** auto-cleans. Need to keep long-term, ask Thansa to extract to `.md` note or move to other folder in brain. See [File management](05-quan-ly-tep-tin.md).

### Voice command (voice record)

Press and hold mic button in Telegram, say one sentence, let go. Thansa hears it to text and acts like you typed - handy when driving or hands full.

**Need one thing: Groq API key.** Groq is who Thansa borrows from to turn voice to text (model Whisper). No key yet, send voice record and Thansa says it needs key with instructions - not silent.

How to set up, do once:

1. Go to [console.groq.com](https://console.groq.com), log in, create one API key.
2. Open Thansa dashboard, go to **Models** page, find **Groq (API)** provider, paste key then save.
3. Done. Next voice record goes straight, **no need restart bot**.

Few things to know:

- **This key shared with chat.** Already using Groq as brain then voice record goes, don't need setup. Or hook key just for voice - no need to switch main model to Groq.
- **Thansa hears Vietnamese** (gives Whisper a language hint so short sentence doesn't misidentify as other language then translate).
- **Jobs affecting outside ask first.** Send message, post, schedule, spend money, edit file: Thansa starts with line "I heard: ..." then waits for OK. Machine can mishear, and those jobs no undo once done. Query data, look up, summarize goes straight, no ask.
- **Voice record not saved to brain.** Thansa hears and takes text, no `.ogg` file stays in `inbox/`.
- Send voice with caption `/notes` still runs command with that voice content.
- Hear nothing (silent, too loud) or Groq errors then bot says why and ask type instead. No dead silent.

Zalo channel also hears voice record, uses **same Groq key** - set once both channels work. See [Zalo channel](26-kenh-zalo-bot.md).

### Bot send files back

Files Thansa made in turn **auto-attach right after reply**, no need ask. Three sources get sent:

- File Thansa wrote via Write tool in that turn.
- File with absolute path mentioned in final answer.
- Image/file in vault with relative markdown link, like `![](attachments/anh.png)` - exact way Thansa-made image comes back.

Limit and behavior:

- Max **10 files one turn**, each under **50MB** (Telegram doc limit).
- Only file **just made or edited this turn** sent back. Mentioning old file won't make bot resend to avoid spam.
- Image `.jpg .jpeg .png .webp .gif` under **10MB** sends as image (preview in chat); rest as doc. Telegram rejects image then auto-falls back to doc.
- If image already sent alone, markdown line `![...](...)` gets ripped out of reply so you don't see junk text next to real photo.
- Send fails then bot says straight: "⚠ Can't send file `<name>`: `<reason>`".
- Text first, files after, so reading flows natural.

## When Thansa asks back with numbered choice

On dashboard, when need to ask parameter again (date range, pick store...), Thansa draws buttons. Telegram is text-only, can't draw buttons, so Thansa drops choice down as **question + numbered list** (max 4):

```
What revenue period you want?
1. This week
2. This month
3. vs last month
```

Reply by typing exact number, like `2`, or type what you want. Thansa reads number in context of question just asked so knows right away, no special syntax.

## Quick commands in Telegram

Type `/` in chat (or tap Menu of bot) shows command list. Ready commands:

| Command | What it does |
|---|---|
| `/help` | See guide and command list |
| `/status` | See provider, model, brain in use and if bot busy answering |
| `/skills` | List skills in vault (type `/skill-name` to call) |
| `/notes` | Save text (with image) to vault Sources. Type `/notes <content>`, or send image with caption `/notes ...` |
| `/agents` | List agents, say if any turn running |
| `/workflows` | List workflows |
| `/model` | See or switch model. Type `/model` blank to open button table; or type straight like `/model sonnet` |
| `/brain` | See or switch brain (vault) FOR THIS SESSION ONLY. Type `/brain` to open button table; or type straight like `/brain Kim Khi`. Switching resets chat to load new brain memory; others and dashboard unaffected. Files you send also land in that brain's inbox |
| `/retry` | Re-send last question |
| `/stop` | Stop answer running now |
| `/reset` | Start new chat (forget old context) |
| `/cli` | Switch to Claude engine (Claude) |
| `/or` | Switch to OpenRouter engine (chat + multi-model MCP) |

`/notes` has no separate handler in bot: runs via skill, so also needs engine other than OpenRouter (see section below). Details at [Skills](06-skills.md).

About `/model`:

- Button table when typing `/model`: pick **ALREADY CONNECTED** provider (provider in use has ✓ with model count), then grid 2 col 8 models per page, buttons ◀ ▶ flip page. Model list **straight from provider** (OpenRouter shows hundreds, Antigravity shows exact row of Antigravity IDE), not hard-coded list.
- Type name straight works too: name with `/` (like `openai/gpt-4o`) is OpenRouter model; `gpt-...` or `...-codex` is ChatGPT model (need logged in OAuth); rest (like `opus`, `sonnet`, `fable`) is Claude.
- From 0.33.7, button table shows **all 10 providers** like Models page on dashboard, including **Antigravity CLI** - before it was 5-line cheat sheet so new providers couldn't switch from phone. Provider with no model yet (like CLI installed no login) hides for clean, except provider in use.
- Type `/model <name>` straight then Thansa hunts name in real lists of hooked providers then switches to right one. Name on many but none in use then it asks instead of guess, because guessing wrong auto-flips payment (subscription vs pay-per-call).

## MCP and skill via Telegram

- **Every engine can use Thansa's MCP via Telegram**, since tools go via MCP Hub not tied to one engine. Bot's own `/help` text says "ChatGPT/Codex and OpenRouter can both use Thansa MCP". You see it real when status line shows "⚙ Calling tool: ...".
- Call skill via `/skill-name`. One gate: at OpenRouter engine typing `/skill-name` bot reminds "⚠ Skill needs Claude engine. Send /cli to switch, then /skill-name again."
- Switch engine right in Telegram: type `/cli` for Claude (bot says "✅ Provider: Anthropic (Claude) - full MCP, ask POS/Ads/vault."), `/or` for OpenRouter (bot says "✅ Provider: OpenRouter (`<model>`) - chat + multi-model MCP."). Switching here also switches whole Thansa (dashboard and bot share one model config).
- To use `/or` need already set OpenRouter key in [Models & engine](10-models-va-engine.md); no key yet bot says "⚠ No OpenRouter key - set in Models on dashboard first."

## Permission limit: only you use bot

- **Chat IDs allowed** field is the whitelist. Only Telegram accounts with ID on list can text bot. Stranger texts in gets: "You don't have permission to use this Thansa bot."
- Leave Chat IDs blank: anyone finding bot can use. Not recommended, since bot can touch your vault and data. Always set at least 1 Chat ID.
- Add more people to 1 bot: add their Chat ID to field, comma-separated, then **Save & turn on**. **Send test** button will send to ALL IDs and say which ones failed (usually person hasn't clicked Start bot yet).
- Each person has **own chat thread**: context separate per Chat ID, no leaking to other people, two can text at same time no waiting. `/reset` and `/stop` only affect the person typing. But all **share one vault and same permission** (everyone can read/write your data, numbers, brain) - only add Chat ID of people you trust. Need complete data split then run Thansa + bot separate for each person.

## Who gets notifications from background

Using bot with multiple people, must know each alert type goes to who. Not everything broadcasts to all.

| Alert type | Goes to |
|---|---|
| Result from each loop in [Scheduled Tasks](08-viec-dinh-ky.md) done | Exact person who asked for loop, if that Chat ID in allow list. Unknown person (like loop made on web) sends to **first ID** on list |
| Kanban job done, see [Tasks / Kanban](21-viec-kanban.md) | Same: exact person who asked, or first ID if unknown |
| Reminder time arrives | To chat_id set for schedule. If reminder no chat_id or old chat_id gone from list, sends to ALL IDs |
| Loop self-pauses | ALL IDs in allow list |
| Engine down alert | ALL IDs in allow list, each crash only one alert |
| Zalo message hits rule, see [Zalo](12-zalo.md) | Per listener config; no config then first ID |

Short: **job result goes to person who asked**, **system alert goes to everyone**.

## Telegram chat lives in shared history

Every turn via Telegram saves same as chat on dashboard: goes to history, goes to brain's memory log, goes to self-teach loop. In sidebar 🕘 History, bot chats labeled **TG** so you don't mix with web chats. See more at [Chat session](04-phien-hoi-thoai.md).

Chat linked to **brain set for your Telegram session** (switch via `/brain`), so only shows when dashboard viewing that brain.

### Why Telegram chat split into chunks

On dashboard you click "＋ New chat" yourself so one never endless. On Telegram almost nobody types `/reset`, so if left as one Chat ID stuck on one endless chat, open to read very heavy. Thansa auto **starts new chat** when:

- you stop texting more than **12 hours**, or
- chat now **long enough** (roughly **100 turn**s), or
- you type `/reset`, switch brain via `/brain`, or server restarts.

Important: this split only for **history to read back**, totally **doesn't touch Thansa's memory while chatting**. You keep texting and Thansa remembers chain exactly; only dashboard history splits for easy reading.

Telegram old chats over **30 days** auto-archive to storage so list doesn't flood. Archived not deleted: search still finds them.

## Check bot status

Two ways:

1. Dashboard: go to **Channel** (**Connect** group), read status line under Telegram card (described in Step 2). Fastest and clearest.
2. In Telegram: type `/status`. Bot returns provider, model, brain in use, your session, busy or free.

**Settings** page top **System** group also quick-shows Telegram "On" or "Off" with button linking to **Channel** page; full config stays on **Channel**.

## Quick reference: buttons and status

| Button / field | Where | What |
|---|---|---|
| Turn on Telegram bot | Telegram card, Channels page | Enable/disable bot. Need Save & turn on to apply |
| Bot token | Telegram card | Token from BotFather. Set once, leave blank if no change |
| Chat IDs allowed | Telegram card | Whitelist. Multiple IDs comma-separated |
| Save & turn on | Telegram card | Save config then auto-restart bot |
| Send test | Telegram card | Shoot test message to all IDs in list. NOT proof bot receiving |

## Tips

- Change token or Chat IDs then always click **Save & turn on** again; Thansa auto-restarts bot with new config, no other step.
- Long reply auto-splits to multiple messages by Telegram, reads normal.
- Ask new topic clean, type `/reset` first.
- Bot messed up or you mis-asked, type `/stop` to cut, then `/retry` to ask last question again.
- Snap photo of receipt, bill, price sheet then caption `/notes ...` is fastest way to jam something to brain when standing at shop door.
- Before sending image/file, check `/brain` right - file lands in that brain's inbox, not default.
- Telegram can't show markdown table, so Thansa told to answer on this channel as text like messages, use bold/italic/`code` instead of table.
- On VPS, secure dashboard with password on [Security & account](14-bao-mat-tai-khoan.md) page at same time as setting Chat ID for Telegram.

## Common trouble

**Status line shows 🔴 409.** Same bot token running elsewhere (other Thansa, other machine, or old webhook). One token one place only. Bot Thansa auto-removes webhook on startup; if still 409 kill other Thansa or make new token via BotFather. After fix, click **Save & turn on** again.

**Send test says token or Chat ID missing.** You didn't save full. Fill token and Chat ID both, click **Save & turn on** then test.

**Send test works but bot no reply when texting.** Test and receiving are different. Check status line is 🟢 **Bot receiving messages**. If ⚪ or 🔴, fix per that line (turn on, or fix 409).

**Bot replies "You don't have permission for this Thansa bot".** Chat ID you set in Thansa doesn't match account texting. Get right Chat ID from @userinfobot, paste to Chat IDs field, Save & turn on.

**"🤔 Thansa processing…" stuck not changing.** That turn hasn't called tool yet, or engine waiting. When done it'll change to trace (`⚙ ...` or `✓ Direct`). If stuck forever on 🤔 with no reply after then turn broke, check status line on **Channel** page.

**Typing `/skill-name` says need Claude engine.** You at OpenRouter. Type `/cli` switch to Claude then call skill again.

**Send image/file, bot says can't read.** Check 2: file over 20MB (Telegram limit, not Thansa), or is video/video note (Thansa can't watch, send as file or type).

**Send voice record, Thansa says need Groq key.** Right: voice-to-text runs on Groq Whisper. Go to **Models** page, find **Groq (API)**, paste key from console.groq.com then save. Don't need restart bot.

**Thansa misheard voice.** Closer to mic, slower talking, less noise. Sentence too short (one two words) mishears easy - say full sentence more accurate. Jobs with outside action: Thansa reads back what heard then acts, you catch mistake before.

**Thansa says made file but you don't get it.** Only file just made/edited this turn, under 50MB, max 10 per turn auto-attach. Old file ask bot resend by name.

**Old image in chat shows gray "Image expired".** Cache media (`attachments/` and `inbox/`) cleaned file over 30 days or space over 300MB. Content already pulled to `.md` note stays.

**Changed config, bot still old.** Wait few seconds reload **Channel** page so status line updates. If still not 🟢, see more [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Token save level applies to Telegram too

From **0.24.0**, your setting on Settings page (**Optimal** / **Super save**) also applies to Telegram channel, not just dashboard chat.

Before, both levels only wired to dashboard, so click on then each Telegram turn still sent full `CLAUDE.md` + `MEMORY.md`. No error shows - just token bill doesn't drop on your most-used channel.

Two levels do:

- **Optimal**: swap `CLAUDE.md` + `MEMORY.md` with memory and skill cherry-picked right for your question.
- **Super save**: question needing no lookup (regular chat, short math) calls model **one round** with one small capsule, no tool table. When question needs data, need to call source, or has file then goes full like before - shortcut just for safe queries. Shortcut fail (quota hit) auto-backs to full path, you get reply.

Scheduler command (cancel schedule...) always handled by schedule gateway, shortcut never eats that turn.

## Related

- [Models & engine](10-models-va-engine.md) - pick provider and model for both dashboard and bot.
- [Connect & business numbers](09-mcp-va-so-lieu.md) - hook data source so you ask real numbers via Telegram.
- [Scheduled Tasks & Reminders](08-viec-dinh-ky.md) and [Tasks / Kanban](21-viec-kanban.md) - source of background alerts to bot.
- [Zalo channel](12-zalo.md) - other channel, read and report Zalo messages to this Telegram bot.
- [File management](05-quan-ly-tep-tin.md) - see where files you send land in brain.
- [Env settings](16-cau-hinh-env.md) - advanced config via file.
