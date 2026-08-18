# Usage: token & cost

*[Tiếng Việt](23-muc-dung-token.md) · **English**

The **Usage** page answers two linked questions: *how many tokens have you burned* and *how do you burn fewer*. Thansa measures this from real logs on your machine, not asking the provider, so you see something that Claude or ChatGPT never shows: the part that Thansa itself running in background burns.

Top of page is **Token saving mode** block with three buttons. From version 0.24.7 it lives here; before was separate page "Saving" in sidebar. Merged because people would read the bill but never see the switch.

This page guides picking savings level, then reading each card, graph, table and how to use them finding where you're burning quota.

## What is this feature

Thansa sees token in/out on **every** answer turn, no matter which engine (Claude Code, ChatGPT/Codex, OpenRouter, OpenAI, Anthropic). So the number here is unified, **not dependent on whether the provider shows quota or not**.

Two things to remember before reading any number:

- **This is HOW MUCH YOU BURNED, not your remaining quota.** Most providers don't give out remaining quota through API. This page counts what went through, not how much your plan has left. Only OpenRouter is exception (see below).
- **Cost shown is CONVERTED, not real money.** With Claude or ChatGPT subscription, the dollar number only answers "if priced by API, this would cost". Only OpenRouter is real money.

Page gives you: 8 period buttons and 4 provider filters, stat cards with period comparison, token graph per day, three breakout column charts (source burn / activity type / provider), two ranking tables (model and project), and one auto-suggested saving list.

## Where to open in Thansa

Open dashboard (default port 7777). On left nav bar, open **System** group (pinned at nav bottom), then click **Usage** (icon 📊).

Page top shows title **Usage** with subtitle "Token & cost by day, by provider".

## Token saving mode (top block)

Every time you chat, Thansa must send along lots of background info: who it is, what tools it has, what it remembers about you, what was said before. That pile takes money and burns quota. Three buttons here decide how big that pile is.

- **Off** - Full mode. Send everything, every time. Safest, most expensive.
- **Optimize** - Send only part relevant to current question: selective memory, skills loaded when needed.
- **Ultra-save** - Like Optimize, plus shortcuts for simple questions needing no lookup. **This is default from 0.24.7.**

Each button says right there how much percent it saves and tokens per turn left. The number is **measured on your actual brain and memory**, not marketing, so two different machines see different numbers.

If your brain can't run one level, that level's button says straight out *"not compatible with brain you're using"*. Example: ultra-save shortcut only works on API-key brains, so with subscription it equals Optimize level.

Once you have enough runs in both modes in 24 hours, a **real measurement** block shows under three buttons: tokens per turn in full mode, tokens per turn when saving, and percentage cut. This is real number, not estimate.

**Mode change works immediately**, no restart. If Thansa answers worse try **Off** to go back as before.

### Why ultra-save is default

Before 0.24.7 default was **Off**, and almost no one turned it on - meaning most people paid for the most expensive mode without knowing. Measure on sample brain: Off costs around 8,900 fixed tokens per turn, Ultra-save around 460.

This is safe default, not dangerous: all paths in this level **fail-closed**. Missing condition means that turn auto-falls back to full mode, doesn't answer wrong.

If you **ever manually picked a level**, Thansa pins that choice and no update changes it again - even if you click **Off** on purpose. Line below three buttons tells you if you're on default or your own pick.

## How to use (step by step)

### Step 1: Open page and wait for first scan

Just opened, page shows "Building token index...". First time Thansa **rescans log** before drawing, might be slow few seconds if you used for many months. Later mode changes scan-free, just re-index, very fast.

If page says "Couldn't load token data." server isn't giving data yet; see Common problems.

### Step 2: Pick period

Top row is 8 period buttons: **Today**, **Yesterday**, **This week**, **Last week**, **This month**, **Last month**, **3 months**, **This year**. Picked period highlighted. Default when opening is **This month**.

Each period self-compares to matching previous period, comparison shows right under "Total tokens" card.

### Step 3: Filter by provider

Right next to period buttons is one cluster of 4 buttons: **All** (default), **Claude Code**, **ChatGPT**, **API**. Click to view one source only.

This filter affects stat cards, graph and split tables. Only the **Suggest** section at page bottom always calculates across all providers, ignoring this filter.

### Step 4: Read stat cards

Row of cards right under filter:

| Card | Number | Line below |
|---|---|---|
| **Total tokens** | Total tokens in period (includes read-cache) | "▲ x%" or "▼ x%" with "vs last period"; no last period data shows "last period no data" |
| **Token/day** | Average per day in period | "average in period" |
| **Cache hit** | Percent of input tokens that are read-cache reuse | "context reuse (high = cheap)" |
| **Session** | Sessions that burned tokens in period | "avg ... /session" - average tokens per session |
| **Cost converted** | Money value per API pricing table | "if calculated by API rate" |
| **OpenRouter left** | Actual remaining balance (only when OpenRouter key plugged) | "real money spent $..." |

Note arrow colors: **▲ (up) is red, ▼ (down) is green**. Here up is bad news, not good.

About **Cache hit**: "Total tokens" includes read-cache so looks huge. High cache hit means most of huge number is just re-reading old context (very cheap), not fresh load. So read both cards together.

### Step 5: See token graph by day

**Token by day** block draws each day as one column. Columns stack 3 colors by provider:

- **Claude** - interface highlight color
- **ChatGPT** - lime green
- **API** - navy blue

Horizontal axis marks day of month. Hover mouse over column shows tooltip like "2026-07-29: 12.3M token". Long period (3 months, this year) scrolls horizontally.

### Step 6: Find what's eating tokens

Below graph are three side-by-side horizontal bar charts, this is most important part of page:

- **Source burn (you vs Thansa)** - two lines: "You typed" and "Thansa (auto-run)".
- **Activity** - four lines: "Chat", "Background (loop/schedule)", "Subagent", "Manual".
- **Provider** - "Claude Code", "ChatGPT/Codex", "API (OpenRouter...)".

Meaning of each label lives in [Source burn and activity type](#source-burn-and-activity-type) below.

After charts are two ranking tables, each showing up to 8 rows:

- **Model eating most**: columns Model, Token, Converted. Model name shortened to fit (drops `claude-` / `gpt-` prefix, cuts long suffix). Converted shows "-" when model not in pricing table.
- **Project eating most**: columns Project, Token, Session. "Project" is brain name if Thansa figures which brain, otherwise working folder name.

### Step 7: Read Suggest section

If metrics hit threshold, Thansa creates suggestion cards at page bottom. Orange-bordered ⚠️ is action item, blue-bordered 💡 is tip. See [Saving suggestions](#saving-suggestions) for exact thresholds.

No cards means all metrics normal, not an error.

## Table of 8 periods

All dates by Vietnam time (UTC+7).

| Button | Period viewing | Compared to |
|---|---|---|
| **Today** | Today | Yesterday |
| **Yesterday** | Yesterday | Day before |
| **This week** | Monday to today | Same span of last week |
| **Last week** | Monday to Sunday last week | Two weeks ago same span |
| **This month** | 1st to today | Same days of last month |
| **Last month** | Full last month | Full month before that |
| **3 months** | 90 newest days | 90 days before those |
| **This year** | 1/1 to today | 1/1 year ago to same day |

The "This week" and "This month" comparison is on purpose: running periods only compare to **exact matching span** of prior period, not full prior period. Else day 3 of any month would report 90% drop.

## Source burn and activity type

This is where to learn **what's eating your quota**, and it's what provider stats pages never show.

**Source burn** splits two:

| Label | Means what |
|---|---|
| **You typed** | Session you opened `claude` in terminal yourself, not going through Thansa |
| **Thansa (auto-run)** | Session Thansa started via Agent SDK: dashboard chat, Telegram chat, background task, workflow |

**Activity** splits four:

| Label | Means what |
|---|---|
| **Chat** | Turn attached to real conversation session in your history |
| **Background (loop/schedule)** | Turn Thansa ran solo with no conversation tied to it: recurring task, reminder, Kanban task, source digest, self-learn |
| **Subagent** | Turn spawned by engine as child agent to help |
| **Manual** | Turn from session you typed by hand outside Thansa |

Column **Background (loop/schedule)** bloating big is clearest sign you have loop running too often. Review them on **Recurring Tasks** page ([Recurring Tasks & Reminders](08-viec-dinh-ky.md)) or **Tasks** page ([Tasks / Kanban](21-viec-kanban.md)).

One limitation to know: **this split only accurate with Claude Code.** With ChatGPT/Codex Thansa can't split background from chat yet so all turns land in "Thansa (auto-run)" + "Chat". API branch same.

## Converted cost and real money

**Converted cost** column and **Converted** in model table calculated from fixed price table (USD per million tokens) bundled with app, at `server/usage_pricing.json`. Table has pricing for `claude-opus`, `claude-sonnet`, `claude-haiku`, `claude-fable`, `gpt-5`, `gpt-4o`. Model matched by longest prefix; **model not in table costs 0** and shows "-".

So converted number always estimate, always lower than real if you use model not yet in pricing. Want accuracy then edit that file by hand and restart server.

**OpenRouter real balance** only thing on this page that's real money. Card "OpenRouter left" only shows when you saved OpenRouter key on **Models** page (under Connections group). Thansa asks OpenRouter directly for deposited and spent credit, shows balance left with line "real money spent $...". No key no card, no other provider gives this out.

## Saving suggestions

List self-generates from metrics of viewing period. Thresholds set in `server/usage_index.py`:

| Suggest | Appears when | Level |
|---|---|---|
| **Cache hit low (x%)** | Cache hit under 50%, and period big enough (200K+ input token) | ⚠️ |
| **Background activity eating x% token** | "Background (loop/schedule)" part takes 25%+ total | ⚠️ |
| **Opus eating x% token** | `claude-opus` models take 50%+ total | 💡 |
| **One session bloated (x input token)** | One session loaded 1M+ input token | ⚠️ |
| **Token/day up x% vs last** | This period's average per-day is 1.5x+ last period | ⚠️ |

Each card adds one action line, e.g. low-cache suggests using `/compact` or splitting session, opus suggests downgrading model for light work. The 200K token threshold for cache warning is to not yell when you're only 15 minutes in.

## Where this data comes from

Thansa doesn't call provider API for stats. It **re-reads raw log on your machine** then builds own index:

| Source | Where | Gives |
|---|---|---|
| Claude Code log | `~/.claude/projects/**/*.jsonl` | Claude column, full cache data, chat/background/subagent split |
| Codex log | `~/.codex/sessions/**/rollout-*.jsonl` | ChatGPT column, one file per session |
| Internal log | `usage-events.jsonl` in state folder | API column, and fallback for Claude/ChatGPT |
| Session store | `conversations.db` in state folder | Tells which turn is real chat, which is background run |

Results merge into SQLite database `usage_index.db` also in state folder (set by `JAVIS_STATE_DIR` var, see [Configure .env](16-cau-hinh-env.md)).

Scan is **incremental**: files unchanged size and mtime get skipped. So first scan slow, later rescans fast, even with thousands of log files.

API branch has no raw log to read, so only counts **since you upgraded to version with this feature**. Claude and Codex have history back to when you started using them, because their logs already sat on machine.

If install can't read raw logs (typical: Docker on VPS where your `~/.claude` doesn't sit in container), Thansa builds numbers from internal log instead, so page still has numbers not zeroes. Same day with both sources, raw log wins, no double-count. Sign of using internal log: "Project eating most" table has row named `(events)` for internal-log builds, `(api)` for API provider turn.

## Button and status quick table

| You see | Means / action |
|---|---|
| 8 period buttons (**Today** ... **This year**) | Switch period; bright button is picked |
| **All / Claude Code / ChatGPT / API** cluster | Filter by provider |
| **↻ Refresh** | Rescan log then redraw; while running button changes to "Scanning..." |
| "Building token index..." | First load happening |
| "Couldn't load token data." | Server can't return data |
| "No data." | That field empty for picked period |
| "last period no data" | Last period was zero so can't calculate percent change |
| ▲ red / ▼ green | Up / down vs last |
| ⚠️ orange card | Suggestion level warning |
| 💡 blue card | Suggestion level tip |

## Tips

- Open **This month** first to see trend, then click **Today** to look at one day. Read backward is shocking because one day alone always looks weird.
- Suspect loop running too heavy then filter **Claude Code** and look at "Background (loop/schedule)" column in Activity. This is only number telling straight how much Thansa burns when you're away.
- Low cache hit but high total token means problem is session length not turn count. Split session apart is cheapest way to drop.
- "Project eating most" table quick way to spot which brain costs most, when you use many.
- Only click **↻ Refresh** when you just finished big work and want to see it now. Default page load already rescans.

## Common problems

- **Page shows all zeros.** Usually install can't read raw log, most common on Docker/VPS because your `~/.claude` and `~/.codex` don't sit in container. New version uses internal log fallback so still gets numbers, but only from when you upgraded up. Already upgraded but still zero then you haven't had any chat turn logged since, try chatting then click **↻ Refresh**.
- **Number much lower than you expected.** Check you didn't filter one provider, and check picked period. Also "You typed" only counts when you run Claude Code on **same machine** as Thansa.
- **Gemini key plugged but API column doesn't move.** Gemini turns do log in internal log, but index builder currently only recognizes OpenRouter, OpenAI and Anthropic into API column, so Gemini part missing from this graph. Already on roadmap.
- **Don't see "OpenRouter left" card.** Card only shows when you have OpenRouter key in Model settings and OpenRouter replies. Go **Models** page (Connections group) and check key, see [Models & engine](10-models-va-engine.md).
- **Page shows simple table like "Today / Total stacked" instead of period filter.** That's fallback UI, shown when new UI file didn't load. Reload page, clear browser cache if needed.
- **Converted cost shows "-" for model you're using.** That model not in `server/usage_pricing.json` price table. That table is hand-edited, add row for your model then restart server.
- **Just upgraded Thansa but page no changes.** Page has backend part, restart server then reload page.

## Related

- [Models & engine](10-models-va-engine.md) - switch model, plug OpenRouter key, understand how each engine logs.
- [Recurring Tasks & Reminders](08-viec-dinh-ky.md) - where to turn off loop when "Background (loop/schedule)" column swells.
- [Tasks / Kanban](21-viec-kanban.md) - background task also counts in "Thansa (auto-run)".
- [Configure .env](16-cau-hinh-env.md) - `JAVIS_STATE_DIR` var picks where index sits.
- [Troubleshoot & FAQ](17-khac-phuc-su-co.md) - general dashboard errors.
