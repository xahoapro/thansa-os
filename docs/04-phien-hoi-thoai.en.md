# Conversation Sessions

*[Tiếng Việt](04-phien-hoi-thoai.md) · **English***

Every conversation you have with Thansa is automatically saved. This page shows how to view, search, rename, delete, and resume old conversations, even ones from days ago.

If you're new to the chat interface, read [Chat & Voice](02-tro-chuyen-va-giong-noi.md) first.

## What is this feature

Thansa automatically saves every question and answer into a database on your machine. So you don't lose content when closing the browser or restarting the server. Specifically you can:

- View a list of old conversations, newest at the top.
- Search full text: type a keyword and Thansa searches across all conversations.
- Reopen an old one and continue the same thread.
- Rename for easy memory.
- **Pin** important ones to the top.
- **Group** multiple conversations into a **Project** (collection).
- **Set icon for each Project** to categorize groups visually.
- Delete conversations you don't need anymore.

## Pin, Project, and icon

The list is sorted by time, so a conversation used repeatedly drifts down. Three tools below let you reorganize; all are in the **History** sidebar on the left of the chat.

**Pin.** Hover a conversation and click the pin icon. It moves to a **Pinned** group at the top and stays there. Pinning doesn't mark the conversation as "just talked to", so the order of other conversations stays the same. Click again to unpin.

**Project.** The bar right below "New conversation" is where you pick a group. Click to see the list, create new groups, rename, change icon, or delete. When a project is open:

- The list shows only conversations in that project.
- **New conversations you start will automatically go into that project**, no manual assignment needed.

Select "All conversations" to see everything, or "Uncategorized" to find leftovers. To move a conversation to another group, hover it and click the folder icon.

**Deleting a project DOESN'T delete conversations.** They're just removed from the group and return to "Uncategorized". The confirmation dialog also spells this out with the count of conversations being removed.

**Project icon.** Open the group selector, hover a project, and click the palette icon. A picker shows all icons Thansa uses, with a filter box (type `star`, `folder`, `brain`...). Projects without an icon temporarily borrow a folder icon, so every row has one and your eyes scan by the icon column.

Icons only exist on **Projects**, not individual conversations. Reason: every row in the list is a conversation, so an icon there wouldn't categorize anything, just add a button to click. But each project really is a different thing, so an icon serves a purpose.

These are **Thansa's own icons**, not emoji, and intentionally so: Thansa icons auto-adjust color for light/dark theme and render identically on all machines. Emoji render differently per OS, plus have hard colors that look jarring on dark backgrounds.

Projects are tied to each brain, so switching brains changes your project list. Only "which project is currently open" is remembered per machine (browser), not synced across devices.

One important point: conversations are tied to the "brain" (vault) you have selected. When you switch brains in the vault selector, the history list changes to show only conversations for that brain, **and the chat window switches too**. See "Switch brain mid-session" below, and how to pick a brain in [Getting Started & Setup](01-bat-dau-thiet-lap.md).

## Where data is stored

All history lives in a single file called `conversations.db`.

| Item | Default value | Notes |
|---|---|---|
| Filename | `conversations.db` | SQLite format |
| Folder | Thansa's `server/` folder | Same place as `settings.json` |
| Env variable to move file | `JAVIS_SESSIONS_DB` | Point to a different `.db` file |
| Env variable to move entire state folder | `JAVIS_STATE_DIR` | Move the entire state folder |

If you want to move history elsewhere (like a separate data drive), set the `JAVIS_SESSIONS_DB` variable. See [Configuring .env](16-cau-hinh-env.md) for how to set environment variables.

Each conversation saves: name (title), brain, engine in use, model, channel (where it originated), message count, creation time, and last update time. Each question and answer is saved separately for precise searching and resuming.

## Conversations from Telegram

This list isn't just for the web. What you send to Thansa over **Telegram** also gets saved here with a **TG** label, so you can read and search those conversations from your computer even while moving around.

Since Telegram rarely has a "start new conversation" button, Thansa auto-splits when you've been quiet for over 12 hours or the conversation reaches about 100 turns. This is just for archive readability and doesn't erase the thread while you're chatting on Telegram. Telegram conversations older than 30 days go into archive storage and don't show by default, but you can still find them with the search box. See [Telegram Channel](11-telegram.md) for more.

## Where to find it in Thansa

The history sidebar is on the **Chat** page. Three ways to get there, all lead to the same place:

- **Navigation rail.** Open **Assistants** group on the left, click **Chat**.
- **⛶ button** on the **CONVERSATION** box on the main Thansa screen.
- **🕘 History** button in the top right corner.

The page has two columns: left is the **History sidebar** with **+ New conversation** at top, search box, and conversation list grouped by time (**Today / Yesterday / Past week / Older**); right is the chat window titled "Chat with Thansa". The open conversation is highlighted in the list so you know where you are.

The **🕘** button on the title bar (tooltip "Show/hide history") toggles the left column. The **‹ Collapse** button takes you back to the Thansa screen. On narrow screens (under 860px), the sidebar hides and opens as a floating drawer; selecting a conversation auto-closes the drawer.

## How to use (step by step)

### View conversation list

1. Open the history sidebar using one of the three ways above.
2. The list shows conversations for the selected brain, grouped by time, most recent at top.
3. Each line shows: conversation name, time (or date), channel label if not web (e.g. **TG**), engine used, and message count (e.g. `12 messages`).
4. The list shows **20 conversations** at first. For more, scroll to the bottom and click **Load 20 more**. No limit, keep loading.
5. If you have no conversations, the sidebar shows "No conversations." and "Click + to start."

Unnamed conversations temporarily show your first question as the name. Thansa also auto-names a shortened version from your first question (about 48 characters) right after the first reply.

### Recognize conversations still replying

Any conversation with a running background request will have a **⏳** icon before the name (tooltip "Replying") and the entire row is highlighted. Go do other work; the reply keeps running on the server and auto-saves to that conversation.

If you try sending another message to that exact conversation, Thansa refuses: "This session is replying - wait for the current turn to finish." To ask something else immediately, click **+ New conversation** and ask there.

### Full-text search

1. Open History sidebar.
2. Click the box with faded text **Search all conversations…** at the top.
3. Type a keyword. Thansa searches automatically after you pause, no Enter needed.
4. While searching, the list shows "Searching…".
5. Results show matching lines: conversation name, a short excerpt around the keyword (matching part in bold), and when that message was sent.
6. Click a result to open that conversation straight to that message.
7. Clear the search box to return to the full list.

If nothing matches, the sidebar shows "Not found." Search only covers conversations in the selected brain. To search another brain, switch brains first then search again.

### Reopen and continue an old conversation

1. In the list (or search results), click the conversation you want.
2. The chat window immediately loads all old questions and answers, that row is highlighted in the list.
3. Type a new question normally. Thansa continues the exact same thread, doesn't start over.

How Thansa keeps the thread varies by engine; see "How Thansa remembers the thread" below and [Models & Engines](10-models-va-engine.md).

### Start a new conversation

1. Open History sidebar.
2. Click **+ New conversation** at the top.
3. The chat window clears and you start fresh. The new conversation only gets saved to history after you send the first message.

### Rename a conversation

1. In the list, hover a conversation line. Two small icons appear on the right.
2. Click the pen icon **✎** (tooltip "Rename").
3. An input box appears saying "New name for conversation:". Type the new name and click OK.
4. The list updates with the new name.

Names are capped at about 120 characters; excess gets cut off. Clicking Cancel keeps the old name.

### Delete a conversation

1. In the list, hover the conversation to delete.
2. Click the trash icon **🗑** (tooltip "Delete").
3. A confirmation box appears with the name: `Delete conversation "<name>"`? Click OK to delete, Cancel to keep.
4. The conversation and all its messages are removed from the database; the list updates.
5. If you were viewing that conversation, the chat window switches to a blank new conversation.

Note: deletion is permanent, no trash bin recovery. Think carefully before deleting important conversations. (Different from deleting an entire brain - that has a trash that keeps it 30 days, see [File Management](05-quan-ly-tep-tin.md).)

## How Thansa remembers the thread

Three engines keep context in three ways, so resuming an old conversation behaves differently.

**Claude engine (Agent SDK).** Each conversation on the dashboard saves the original Claude session ID. Reopening the old conversation reconnects to that exact session, so both context and previously-used tools stay intact.

**Codex engine (ChatGPT package).** Each conversation saves a native Codex thread ID to resume the thread. If the thread is lost (machine upgraded, old rollout cleaned up), Thansa doesn't break the thread: it rebuilds context from the history in `conversations.db` and opens a new thread, reporting one line in the chat "Old Codex session no longer on machine - Thansa is restoring context from saved history." The history fed in has about a 60,000 character budget, prioritizing the most recent section.

If you switch to another engine then keep asking in the same conversation, the old Codex thread link is dropped (since it doesn't have the new turn). Switching back to Codex later, Thansa builds a new thread from the saved history.

**API engines (OpenRouter, OpenAI, Anthropic API, Google Gemini).** Each turn, Thansa rebuilds history from the database and sends it along. For long conversations, old content is **compressed not cut**: Thansa auto-summarizes the early part of the conversation, saves the summary, then on later turns includes it as a note "[Summary of early chat - compressed to save context...]". The model still remembers the topic, decisions, numbers, and in-progress work, while the payload doesn't balloon infinitely.

Compression usually runs in the background after each turn so you don't see slowdown. Only when uncompressed history gets very long (common on the first API turn right after a Claude conversation thread) does Thansa compress during the turn, adding a slight delay. If the provider errors during summarization, Thansa falls back to the old method of trimming very old content.

## Switch brain mid-session

Switching brains in the selector on the top bar doesn't just change the history list; it switches the chat window:

- The old brain's content immediately clears from the chat so you don't mix up what brain you're in.
- Any brain you've viewed in this page load, Thansa reopens to the exact conversation you were on there.
- Any brain you haven't opened in this session shows a blank chat, as if starting fresh.
- This memory only lasts one page load. Reload the page (F5) and the rule resets: each page load is a new conversation. Old conversations still sit in the history list; click them to resume.

## Quick reference

| Action | Button / key | Location |
|---|---|---|
| Open Chat page (with history sidebar) | `Chat` item | Navigation rail, Assistants group |
| Open Chat page from Thansa screen | `⛶` or `🕘 History` | CONVERSATION box / top right buttons |
| Toggle sidebar | `🕘` | "Chat with Thansa" title bar |
| Back to Thansa screen | `‹ Collapse` | Title bar |
| Search full text | `Search all conversations…` box | Sidebar top |
| New conversation | `+ New conversation` | Sidebar top |
| Resume conversation | Click the line | List (current one is highlighted) |
| Load older | `Load 20 more` | List bottom |
| Rename | `✎` | Appears when hovering |
| Delete | `🗑` | Appears when hovering |
| Conversation replying | `⏳` before name | Indicator, not clickable |

## Tips

- Give important conversations clear names right after finishing, so you find them later without reading through everything.
- To keep context for a long topic, reopen the exact old conversation instead of clicking **+ New conversation**. Thansa remembers the earlier context.
- Starting a completely different topic, click **+ New conversation** so Thansa doesn't mix old context into the reply.
- Search scans the full message content, so you can search by a number, customer name, or phrase you discussed - not just conversation names.
- List and search always match the selected brain. If you can't find a conversation, check you're on the right brain.
- Very long conversations still work, but if you switch to a completely different subject, starting a new conversation gives sharper replies: the old part when compressed is just a summary, not the full text.

## Sync when changing machines

Conversation history lives in `conversations.db` on the server running Thansa. This file doesn't auto-sync to the cloud and doesn't transfer to another machine.

- If you move Thansa to a new machine or VPS but want to keep history, copy `conversations.db` (in the `server/` folder) to the same location on the new machine. Do this while the server is stopped to avoid the file being open.
- If you don't copy it, the new machine starts with empty history. This is normal, not an error.
- Don't open the same `conversations.db` from two running servers in parallel, as it can cause write conflicts.
- For regular backups, just backing up `conversations.db` is enough to preserve all conversation history.

## Common issues

**History sidebar empty even though there were conversations before.**
Likely you're on a different brain. The list only shows conversations for the selected brain. Switch to the right brain and open the sidebar again.

**Click to open sidebar but see "Error loading list."**
The Thansa server may not be running or just restarted. Check the server is running on the default port (7777) then try again. See [Troubleshooting & FAQ](17-khac-phuc-su-co.md) for more.

**Don't see conversations from last week at the end of the list.**
The list loads 20 conversations at a time. Scroll to the bottom and click **Load 20 more** several times, or faster: type a keyword in the search box.

**Search says "Not found" but you're sure you said that.**
Check you're on the right brain that has that conversation. If still nothing, try a shorter keyword or a simpler word instead of the whole sentence.

**Send a new message but get "This session is replying - wait for the current turn to finish."**
That conversation has a running request (its row shows ⏳). Wait for it to finish, or click **+ New conversation** to ask something else in parallel.

**Reopen an old conversation but Thansa doesn't remember context.**
With Claude engine, full memory depends on whether the original session is still saved. With Codex, the native thread may have been cleaned off - Thansa will restore from history and report a line. With API engines, very old content might be compressed summary instead of full text, so minor details fade; just remind Thansa of key info in your new question.

**Switch brain and the chat window goes blank.**
Exactly by design: a brain you haven't opened in this page load shows a blank chat. That brain's old conversations are in the sidebar; click one to resume.

**Accidentally deleted a conversation.**
Deletion is permanent, no recovery from the interface. Only backup: save `conversations.db` regularly (see "Sync when changing machines").

**Renamed a conversation but the name got cut off.**
Conversation names are capped at 120 characters. Anything over gets trimmed. Keep names short and clear.

## Related

- [Chat & Voice](02-tro-chuyen-va-giong-noi.md) - how to send, attach files, turn on voice.
- [Models & Engines](10-models-va-engine.md) - pick Claude, Codex, or an API provider engine.
- [Telegram Channel](11-telegram.md) - conversations from Telegram and the TG label.
- [File Management](05-quan-ly-tep-tin.md) - choose and manage brains.
- [Troubleshooting & FAQ](17-khac-phuc-su-co.md)
