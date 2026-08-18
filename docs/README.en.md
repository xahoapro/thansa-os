# 📚 Thansa OS Documentation

***English** · [Tiếng Việt](README.md)*

Detailed guides for every feature in Thansa OS. Each page is a standalone how-to: where to find it, what to click, how to use it.

> Starting out? Read [Installation in README](../README.md#-installation) first, then go to [01 - Getting Started & First Setup](01-bat-dau-thiet-lap.md).

The dashboard's left navigation combines **19 pages** into **7 groups**: Assistant · Brain · Code · Capabilities · Work · Connections · System. The table of contents below follows the same structure.

## Contents

### Getting Started
- [01 - Getting Started & First Setup](01-bat-dau-thiet-lap.md) - create admin, log into brain, choose engine/model, Settings page.

### Daily Use (Assistant & Brain groups)
- [02 - Chat & Voice](02-tro-chuyen-va-giong-noi.md) - chat, voice-to-text, slash commands, quick-reply buttons, send files, generate images.
- [03 - Knowledge Graph](03-do-thi-tri-thuc.md) - wikilinks, category colors, timelapse and graph toggles.
- [04 - Chat Sessions](04-phien-hoi-thoai.md) - save, reopen, rename, delete, full-text search, compress long sessions.
- [05 - File Management](05-quan-ly-tep-tin.md) - browse brain, search files by name/content, edit .md/.txt inline, upload/download.

### Code (Code group)
- [27 - Code Group: Terminal](27-tab-code-terminal.md) - real command line from the machine running Thansa, open in the dashboard, no SSH needed.

### Expand Capabilities (Capabilities group)
- [06 - Skills](06-skills.md) - organize, search, toggle on/off, add/edit/delete, import/export skills.
- [07 - Agents & Workflows](07-agents-va-workflows.md) - build specialized assistants + multi-step automated chains.
- [20 - Plugins](20-plugins.md) - add native tools/hooks for every engine via one Python folder.
- [25 - Chatbot (Specialist Agent)](25-chatbot.md) - put an Agent in front of customers via a separate Telegram or Zalo bot, separate brain, hand off to staff when stuck.

### Background Work (Work & Brain groups)
- [08 - Scheduled Work & Reminders](08-viec-dinh-ky.md) - multiple background loops + time-based or cron reminders.
- [21 - Tasks (Kanban)](21-viec-kanban.md) - assign goals by voice, AI writes specs and runs background tasks.
- [22 - Self-Learning](22-tu-hoc.md) - Thansa auto-captures memory, distills knowledge into Wiki and skills after each chat, fully reversible.

### Connections & Channels (Connections group)
- [09 - Connections & Business Data](09-mcp-va-so-lieu.md) - outside service hub, multi-account, permissions, real-world metrics.
- [10 - Models & Engines](10-models-va-engine.md) - swap brains between Claude Code, ChatGPT/Codex, Antigravity CLI, OpenRouter, OpenAI, Gemini, Anthropic, Groq, Ollama with no feature loss; thinking levels, background job model.
- [11 - Telegram Channel](11-telegram.md) - ask Thansa on your phone, send and receive files.
- [26 - Zalo Bot Channel](26-kenh-zalo-bot.md) - ask Thansa on Zalo using the official API, one-click pairing.
- [12 - Zalo Agent MCP](12-zalo.md) - log in by QR, read/search history and send messages via standard MCP.
- [24 - Thansa CLI (terminal)](24-cli-terminal.md) - type `thansa "..."` from your terminal, API tokens, embed in scripts.

### Brain & Data
- [13 - Second Brain: Memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) - multiple brains, live memory, knowledge digestion.
- [18 - Backup Brain to GitHub](18-sao-luu-github.md) - two-way sync to a private repo, restore if machine/VPS dies.
- [19 - Tasks & Dataview in Notes](19-task-va-dataview.md) - checkbox auto-save Obsidian-style, dataview blocks run for real.

### Account, Branding, Setup (System group)
- [14 - Security & Account](14-bao-mat-tai-khoan.md) - login required, passwords, rate limits, secret key encryption.
- [15 - Branding & Custom Domain](15-thuong-hieu-ten-mien.md) - change logo/avatar, point domain, turn on HTTPS.
- [16 - .env Configuration](16-cau-hinh-env.md) - reference for every environment variable.
- [23 - Usage: Tokens & Costs](23-muc-dung-token.md) - Thansa measures tokens in/out by day, provider, source.

### When Things Break
- [17 - Troubleshooting & FAQ](17-khac-phuc-su-co.md) - common errors and fixes.

---

## English Docs

Documentation is being translated page by page, not all at once. [docs/en/](en/README.md) shows which pages have English and which are still Vietnamese only - check there instead of guessing. To add another language to Thansa itself (not the docs), see [language addition guide](dev/them-mot-ngon-ngu.md).

---

> Documentation writing rules: Vietnamese, practical, concise. Never use em dash (U+2014), always replace with hyphen "-". See [CLAUDE.md](../CLAUDE.md) for system conventions for AI agents.
