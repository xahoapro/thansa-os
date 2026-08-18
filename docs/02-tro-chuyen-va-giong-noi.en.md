# Chat & Voice

*[Tiếng Việt](02-tro-chuyen-va-giong-noi.md) · **English***

This is where you interact with Thansa the most: type or speak, Thansa replies in text and reads it aloud. This page describes the entire chat interface, from keyboard shortcuts to slash commands, buttons under each message, how to select a voice, and how to ask Thansa to generate images.

If you haven't finished the initial setup yet, see [Getting Started & Setup](01-bat-dau-thiet-lap.md) first.

## What is this feature

A single place to work with Thansa:

- Type messages like a normal chat.
- Speak using your voice; Thansa listens and sends automatically when you stop talking.
- Thansa replies in text and simultaneously reads it aloud in Vietnamese.
- Attach files or images to a message for Thansa to read.
- Thansa embeds images, files, diagrams, and HTML pages directly into replies for you to view in place.
- Watch the knowledge sphere react to sound (brightens when listening / when reading).

Replies are processed by **the engine you have selected**, not Claude by default: Claude Code, ChatGPT (Codex), OpenRouter, OpenAI API, Anthropic API, or Google Gemini API. A small badge next to the CONVERSATION text shows the actual engine + model that just ran. All engines can call Thansa's tools and data sources via MCP Hub, not just Claude. See [Models & Engines](10-models-va-engine.md) for details.

While Thansa thinks, a chip appears at the end of the chat frame with bouncing dots, status line ("Thansa thinking...", "✓ Received data - analyzing...", "✍ Composing reply..."), and a timer counting seconds (only shown from the third second onwards).

## Where to find it in Thansa

There are **two** chat places that share the same conversation, so you can switch back and forth without losing anything.

### Main "Thansa" screen

Left navigation rail, **Assistants** group → **Thansa** section. This is also the default screen when you open the dashboard (default port 7777).

| Area | Position | Content |
|---|---|---|
| VAULT | Left column | File tree of the selected brain, **Find note...** box, two filter modes **Name** / **Content**, three buttons **+** (create file), **📁** (create folder), **⟳** (refresh tree) |
| Knowledge graph + status | Center | Note network, status line (READY, LISTENING...), stats bar **AGENTS** / **SKILLS** / **WORKFLOWS** at bottom |
| CONVERSATION | Right column | Chat history, engine badge, **⛶** button to Chat page |
| Model bar | Above input bar | Model + Effort chip, **SYSTEM** and **MCP** rows in use |
| Input bar | Bottom | Mic button, clip button for files, speaker button, text input, send button (becomes stop button when running) |

The left column no longer has business metric cards; it's now the Vault explorer. Click a note to open it for editing directly on screen (see [File Management](05-quan-ly-tep-tin.md)). Click the AGENTS / SKILLS / WORKFLOWS numbers to jump to the corresponding page.

### Dedicated "Chat" page

Navigation rail, **Assistants** group → **Chat**. This is a full-screen chat page without the knowledge sphere and vault tree:

- Left column is **conversation history** (reopen, find, rename, delete old sessions).
- Top bar shows **Chat with Thansa**, engine badge on the right.
- Chat area, attached file chips, model bar, and input bar are **the exact same** as on the Thansa screen borrowed to this page, so messages, attached files, and running requests stay intact.

Use this page when you want a wide screen dedicated to chat. To see the knowledge sphere and file tree, go back to the **Thansa** section.

## How to use (step by step)

### Step 1 - Type to ask

1. Click the input box at the bottom (where it says "Talk to Thansa, type here, or drag/drop files...").
2. Type your question.
3. Press **Enter** to send. To create a new line within the same message, press **Shift + Enter**.
4. Or click the send button (arrow icon) on the right side of the input bar.

Thansa's reply appears gradually in the right CONVERSATION column, text flowing in real time.

### Step 2 - Speak using voice: hold Space

The fastest way to say a sentence:

1. Make sure the cursor is **not** inside the text box or any input field (if you're typing, Space will produce a space character instead of activating the mic).
2. **Hold the Space bar**. The middle line changes to **LISTENING**, the mic button lights up.
3. Speak your sentence. Your words appear immediately below the status so you can verify Thansa understood correctly.
4. **Release Space**. Thansa automatically sends your entire sentence and starts replying.

When you press the mic for the first time, your browser will ask for permission to use the microphone. Grant it. If you refuse, Thansa won't hear you and will report "You need to grant microphone permission to this page."

### Step 3 - Speak using voice: press mic button (hands-free mode)

The mic button (large microphone icon, left of input bar) turns on **always-listening mode**, useful if you don't want to hold the key:

1. Press the mic button once. Status changes to **LISTENING • ALWAYS** and the mic button lights up.
2. Just speak naturally. When you pause for a moment (about 1.5 seconds of silence), Thansa automatically closes the message and sends it.
3. After replying, Thansa turns the mic back on automatically; you don't need to press again.
4. To turn off this mode: press the mic button again, or press **Esc**.

In hands-free mode, when you start speaking, Thansa automatically stops reading so it can listen, so you can interrupt anytime. This mechanism measures voice volume through echo-cancelled mic stream (speaking continuously for about 0.3 seconds, much louder than background), so Thansa's own voice doesn't trigger it to cut off.

### Step 4 - Hear Thansa reply with voice

By default, Thansa **reads aloud** every reply in Vietnamese (Edge TTS running on server). The knowledge graph glows with the rhythm of the voice.

You can turn voice reading on/off in **3 places**, all staying in sync and remembering your choice after reload:

- The **speaker** button in the top right corner (tooltip when hovering: "Turn Thansa voice on/off"). When muted, the button dims significantly.
- The **speaker** button just above the chat input bar (tooltip "Turn off voice reading" / "Turn on voice reading"). When muted, the button turns red with a slash through it. This button is hidden on phones.
- Go to **Settings → Voice, Brand & Access**, toggle the **"🔊 Read replies aloud"** switch.

### Step 5 - Stop when Thansa is replying

When Thansa is thinking or reading, the send button on the input bar becomes a **stop button** (square icon). Click it to interrupt the running request and stop reading immediately, status returns to READY. Typing `/stop` and pressing Enter gives the same result.

**Pressing Esc does NOT stop replies or voice reading anymore.** Esc only exits hands-free mode, turns off mic, and closes open popups. The tooltip on the stop button still says "(Esc)" as legacy text from the old version.

The stop button only stops **the session you're viewing**; other sessions running in the background continue. See [Conversation Sessions](04-phien-hoi-thoai.md).

## Slash "/" commands in chat

Type a **`/`** to open a command menu right above the input box - **at the start of the box or in the middle, both work**.

Three session commands lead the list:

| Command | Name in menu | What it does |
|---|---|---|
| `/new` | New conversation | Start a new chat |
| `/reset` | Reset session | Clear context, start fresh |
| `/stop` | Stop | Stop the current reply |

On the web version, `/new` and `/reset` both open a new conversation.

Below these three are **all skills of the selected brain**, each line showing `/slug`, skill name, and a description.

How to navigate:

- Type a few more characters to filter. Prioritizes slug matches first, then skill names.
- **Arrow up/down** to choose, **Enter** or **Tab** to confirm, **Esc** to close. Clicking a line also works.
- Selecting a **session command** runs it immediately, no Enter needed.
- Selecting a **skill** inserts `/slug ` **at your cursor position**, text on both sides stays; type the rest and press Enter to send.

When sending a skill command, Thansa translates it: "Use skill `<slug>` with request: ... If this skill doesn't exist, just handle my request normally."

### Calling skills mid-sentence

You don't always have to think of the skill first. Just write your request, and when you need it, type `/` there: *"test using skill mid-chat `/notes`"* runs skill `notes` with the request being **the rest of the text**. Text before and after the command both get included in the request, so *"write me `/notes` about the meeting"* becomes "write me about the meeting".

A few rules to avoid mistakes:

- The `/` must come **at the start of a line or right after a space**. This way `https://example.com/notes` and `3/4 of the cake` aren't interpreted as commands.
- Mid-sentence, the command name must be a **real skill** in the selected brain. `/home/user/notes` or `/doesnt-exist` just go into chat as plain text.
- Multiple commands in one message take the **last one** (latest intent). Session commands at the very start of the input box always get priority.
- **The three session commands (`/new`, `/reset`, `/stop`) only run when at the start of the input box**, and the menu won't suggest them mid-sentence - typing halfway through a sentence and accidentally pressing `/reset` would be more harmful than helpful.

For more about skills, see [Skills](06-skills.md).

## When Thansa asks back with buttons

When a parameter must be guessed and guessing wrong would cause harm (time period, which store, which channel), Thansa asks and attaches a row of buttons right below the reply bubble:

- One question line, may have a short topic label at the start.
- Up to **4 option buttons**, plus one **"Something else…"** button.
- Clicking a button sends **the exact text on the button** as your message. Clicking "Something else…" doesn't send anything, just puts the cursor back in the input box for you to type.
- Labels longer than 40 characters get cut off with "…" at the end; the button shows what it sends, never different.

Only the **latest** row of buttons is clickable. When you reply (press a button or type), all old button rows freeze and become unresponsive. Thansa always writes the question into the reply, so you can type an answer without needing the button.

## Sending files in chat

You can put files or images into messages for Thansa to read. Three ways:

1. Click the **paper clip** button (next to the mic button) and select a file. You can choose multiple files.
2. **Drag and drop** files from your computer into the Thansa window (an overlay appears showing where to drop).
3. **Paste** directly using Ctrl + V.

Pasting has a special trick: pasting an **image** works as a normal attachment, but pasting **very long text** (over 1500 characters or over 25 lines) into the chat box makes Thansa automatically package it as a `.txt` file instead of filling the input box. Thansa still reads the entire content, the screen just shows a compact card. This only applies to the chat box; pasting into other input fields works normally.

Files appear as small cards above the input bar. Wait for the card to say it's uploaded, then type or speak your request and send normally. Click the ✕ on the card to remove it from the message.

Important about how Thansa handles files:

- **Default: read-only.** Thansa reads the file content (views images and describes them) then replies, it **does not** save it anywhere. The overlay text saying "Drop files here → save to Sources" is old text; the actual behavior is read-only.
- **Only save when you ask clearly.** To put a file into memory (Second Brain), say so explicitly in your message, like "save to source", "ingest this", or "write to second brain". Then Thansa converts the file into a note and saves it to the Sources folder of your vault. See [Second Brain: Memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) and [File Management](05-quan-ly-tep-tin.md).

## "Open" tag: files you're editing become chat input

Besides attachments, there's another type of card: when you open a text file in the editor (see [File Management](05-quan-ly-tep-tin.md)), Thansa automatically pins it to the chat as an orange card saying "open - click to keep editing".

Different from attachment cards: there's **only one** pinned card (opening a different file changes it), and it **doesn't disappear after sending** - that file is input to the entire conversation, not data for one message. So you can say "clean up the overdue section" or "write the conclusion" without mentioning the filename; Thansa still knows which file you mean and writes directly to it.

The pin card is also a **way back**: click it to reopen the file in the editor at the exact spot you left off (if already open, just brings your view back without reloading, so unsaved text stays). Click the **✕** on the card to unpin.

## Thansa shows images, files, and artifacts in replies

The reverse also works: Thansa can put images and files from the brain directly into replies.

- **Images**: Thansa writes `![description](attachments/image-name.png)` and the dashboard renders the actual image in the chat bubble. Click the image to open it in the **Files** page.
- **Other files** (pdf, docx, xlsx...): Thansa writes markdown links, click to open in the Files page.
- **Paths in backticks** like `Thansa/loops/report-monday.md` also become clickable links.
- **Wikilink** `[[Note Name]]` becomes a Wikipedia-style link; click to jump to that note in your vault.
- **Broken images** (cache expired, deleted, or renamed) show as a gray box saying **"Image expired"** instead of a broken icon. The `attachments/` and `inbox/` folders are cache: expire after 30 days or when exceeding 300MB.

### Artifact block

Long content or visual content doesn't flood the chat but gets packaged into a compact **artifact card**:

| Type | Card label | Becomes artifact when |
|---|---|---|
| HTML page | HTML Page | Block ``` ```html ``` or starts with `<!doctype html>` / `<html>` |
| SVG image | SVG Image | Block ``` ```svg ``` or starts with `<svg` |
| Mermaid diagram | Diagram | Block ``` ```mermaid ``` |
| Long source code | Code + language | 24+ lines or 800+ characters |

The card shows line count and "click to view", right side has **Open ▸** button. Click the card and a panel opens on the right with:

- Two tabs **Preview** and **Source** (long code has only the source tab).
- **⧉** button to copy source, **⇩** button to download as file, **✕** button to close.
- Press **Esc** also closes the panel.

Mermaid diagrams need to load the drawing library from the internet; offline mode shows the library couldn't load and displays the source. Blocks ``` ```dataview ``` and ``` ```tasks ``` don't become artifacts but run as result tables, see [Tasks & Dataview in notes](19-task-va-dataview.md).

## Ask Thansa to create images

Thansa can create images right in chat using your **ChatGPT account** (OAuth, no API key needed). Just describe it, for example "create an image of a fish sauce bottle on a wooden table, dark background, landscape".

Below, Thansa calls tool `javis_generate_image` (bundled plugin `image-chatgpt`) with three parameters:

| Parameter | Value | Default |
|---|---|---|
| `prompt` | Image description, as detailed as possible (required) | none |
| `aspect_ratio` | `square` (1024x1024), `landscape` (1536x1024), `portrait` (1024x1536) | `square` |
| `quality` | `low`, `medium`, `high` | `medium` |

Generated images are saved to the `attachments/` folder of the selected brain, then Thansa embeds `![...](attachments/...)` into the reply for you to see. Since `attachments/` is cache that expires after 30 days, save important images to another folder.

A few things to know:

- **You must connect ChatGPT first.** If not connected, the tool replies "ChatGPT not connected (OAuth)." with instructions to the **Models** page to sign in. See [Models & Engines](10-models-va-engine.md).
- Creating images is a `safe` operation (writes file + uses quota), so read-only background mode won't auto-generate images.
- AI-generated images carry provenance markers (Content Credentials). In **Settings → Interface & Brain → AI image provenance** there are two buttons **Keep mark** / **Remove mark**; default is keep.
- Besides chat, you can call directly via `POST /image/generate` with fields `prompt`, `aspect_ratio`, `quality`, `brain`.

## Button row under each message

Hover over a message (yours or Thansa's) and a small button row appears below. On phone, **tap** the message to show it.

| Button | Tooltip when hovering | What it does |
|---|---|---|
| Sent time | Full date, e.g. "Wednesday, 07/29/2026 14:05" | Display only |
| ↻ | "Resend this message" (your message) or "Reply to the question above" (Thansa message) | Send the original text again as a NEW request at the end of the chat, don't delete the old one |
| ✎ | "Edit and resend" | Only on your messages. Puts the original text in the input box for you to edit; **does not** auto-send |
| ⧉ | "Copy message" | Copy the entire message, button changes to "✓ Copied" for a moment |

A few notes:

- While running a request, ↻ button fades and becomes unclickable, preventing overlap.
- Messages with only images no text have no ↻ and ✎ buttons (nothing to resend).
- Messages saved from before a certain version have the time hidden, not replaced.
- **Long** messages of yours (over 10 lines or 900 characters) get collapsed, with **Show more** / **Collapse** buttons to expand/close.
- Each code block has its own **⧉ Copy** button in the corner.
- When you scroll up to read old messages while Thansa keeps replying, the chat does NOT jump down; a **↓ New message** button appears at the bottom to jump when ready.

## Choose model, Effort, and engine badge

Right above the input bar is a dedicated area:

- **Model chip**: shows abbreviated provider and model name, with **Effort: Off / Low / Medium / High** (thinking depth). Click the chip to open selection: **Find model...** box, provider list, each expands to show models. Unconfigured providers show 🔒 with "+ Add API key on Models page to unlock". Effort row is at the bottom.
- **SYSTEM bar**: two status lights "⬤ Claude Code CLI" and "⬌ Voice (Edge TTS)".
- **MCP bar**: data sources / tools Thansa called in this session. Nothing called yet shows "No activity". See [Connections & Business Data](09-mcp-va-so-lieu.md).

Engine badge next to **CONVERSATION** (and top right of Chat page) shows the actual engine + model from the server, not what you assume. If the badge differs from what you thought, trust the badge.

On phone, the model chip moves to the header and selection opens centered on screen.

## How Thansa formats replies

From version 0.26.9, chat replies on the web are written for **eye-reading**, not ear-listening:

- Short paragraphs of 2-4 sentences then line break, instead of long prose blocks.
- Lists of 3+ items use bullet points.
- **Bold** numbers, names, and conclusions - things your eyes scan for.
- Long replies with distinct sections get section headings.
- Tables when comparing the same fields across multiple items, like revenue across three channels per week.

Previously Thansa was told to write flowing prose because Thansa was mainly used by **voice**. Now there's no tradeoff: the speaker button **auto-parses markdown** (headings, bold, bullets, links, code blocks) before reading aloud, so visual formatting doesn't hurt audio.

Short questions still get single-sentence answers. Formatting is for readability, not making every answer look like a report.

Text-only channels apply tighter rules because they can't render: **Telegram** and **Zalo** don't support markdown tables, **terminal** doesn't support tables or embedded images and links. All three still use normal bullet points. See [Telegram](11-telegram.md) and [CLI in terminal](24-cli-terminal.md).

> If Thansa still replies with long prose: your brain's long-term memory likely has an old memory like "doesn't like markdown tables, prefers spoken brevity" from when you used voice, and that memory gets loaded into **every** chat turn. Open `memory/MEMORY.md` in the **Files** page, find the line about reply style and delete it along with the matching file in `memory/facts/`. See [Second Brain, Memory & Wiki](13-second-brain-bo-nho-wiki.md).

## Voice: provider, voice, speed

Everything about voice is in **Settings → Voice, Brand & Access**.

### Choose voice provider

The **VOICE PROVIDER** block has three options:

| Option in list | What you need |
|---|---|
| Edge TTS - free (default) | Nothing |
| OpenAI - smooth, multilingual | OpenAI API key (same as chat) + pick one of 11 voices: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer, verse |
| ElevenLabs - most natural | ElevenLabs API key + **Voice ID** (get from ElevenLabs → Voices) |

After choosing, click **Save provider**. The status line below shows which one is in use. If a paid provider errors (limit exceeded, bad key, network lost), Thansa **automatically falls back to Edge TTS** so voice never cuts out.

When you pick OpenAI or ElevenLabs, the Edge voice block (two Vietnamese voices) auto-hides because voice selection moves to the provider's block.

### Choose Edge voice and speed

| Setting | Value | Notes |
|---|---|---|
| Voice | **Ngoc Thu** | Female, warm and natural (default; Edge code: `vi-VN-HoaiMyNeural`) |
| Voice | **Nam Minh** | Male, deep (Edge code: `vi-VN-NamMinhNeural`) |
| Speed | Slider 0.70× to 1.80× | Default 1.10× |
| Listening language | **Vietnamese** (vi-VN) | Default |
| Listening language | **English** (en-US) | Use when you speak English |

Steps:

1. Choose Ngoc Thu or Nam Minh.
2. Drag the **SPEED** slider for faster/slower; number beside shows current speed (e.g. 1.10×).
3. Click **▶ Test listen** to hear a sample greeting in the chosen voice.
4. "Listening language" is the language Thansa uses to recognize what you say, different from reply voice. Keep default Vietnamese unless you usually speak English.

All voice, speed, and listening language choices are remembered for next time.

## Expand chat window

While working in chat on the **Thansa** screen, click the **⛶** button in the CONVERSATION area to go full-screen to the **Chat** page - conversation history on the left (**reopen/find/rename/delete old sessions** - see [Conversation Sessions](04-phien-hoi-thoai.md)), chat content centered on the right for easy reading, taller input box for longer typing.

Back to Thansa screen: click **‹ Collapse** on the Chat page title bar.

This is still **one single conversation**: chatting on the Thansa screen or the Chat page is the same stream, same model bar, same file attachments. From version 0.12.4, the expand button no longer opens a separate floating layer - previously there were two chat windows that looked similar but behaved differently, easy to mix up.

## Ask about business data

The fixed metric card row on the left is gone (from version 0.9.166). Before, every time you opened the dashboard, Thansa would auto-run a scan of connected sources to fill that row, wasting your quota while you weren't even looking at it.

Now just ask in chat ("how's revenue today", "vs last week"). Thansa calls the right source that's connected (POS, channel, ads...) and replies with words, so it only runs when you actually need it. More on data sources at [Connections & Business Data](09-mcp-va-so-lieu.md).

## On phone

Below 860px width, the interface changes to fit the screen:

- Navigation collapses into a drawer: click **☰** to open, click the overlay or press Esc to close. Selecting an item closes the drawer.
- **Model chip** and **+** (new conversation) button move to the header.
- **System** group (choose brain, light/dark toggle, speaker, SYSTEM and MCP bars) moves to the bottom of the drawer.
- Input box shortens its placeholder to "Talk or type for Thansa…".
- Speaker button on input bar and **🕘 History** button on header are hidden (speaker is in the drawer already, and the **Chat** page has history built-in).
- No mouse to hover, so **tap a message** to show its buttons; tap elsewhere to hide.
- In the **Chat** page, the **🕘** button on the title bar opens/closes the history drawer sliding from the left.

## Meaning of the status line in the middle

The line under the knowledge sphere shows what Thansa is doing:

| Text shown | Meaning |
|---|---|
| READY | Idle, waiting for you |
| LISTENING | Listening to you (holding Space) |
| LISTENING • ALWAYS | Hands-free mode is on |
| THINKING | Brain is processing your question |
| SPEAKING | Thansa is reading the reply |

## Quick reference table for buttons and shortcuts

Buttons around the chat:

| Button | Location | What it does |
|---|---|---|
| Large mic | Left input bar | Toggle hands-free mode (always listening) |
| Paper clip | Next to mic | Select attachment file(s) |
| Speaker | Next to clip | Toggle reply voice reading (hidden on phone) |
| Arrow | Right input bar | Send message |
| Square | Replaces send when running | Stop current reply + stop reading |
| ⛶ | CONVERSATION area corner | Expand chat window |
| 🕘 History | Top right corner | Open chat with history sidebar |
| Engine badge | Next to CONVERSATION | Actual engine + model from server |
| Model chip · Effort | Above input bar | Change provider, model, thinking depth |

Shortcuts:

| Action | Result |
|---|---|
| Hold **Space** (not in input box) | Mic on, listen until you release |
| Release **Space** | Send your spoken sentence |
| **Enter** | Send typed message |
| **Shift + Enter** | New line in message |
| **Ctrl + V** | Paste image as attachment, or long text as `.txt` file |
| **/** (start of input) | Open command menu; ↑ ↓ to choose, Enter/Tab to confirm |
| **Esc** | Exit hands-free + turn off mic; close command menu; close artifact panel. **Does NOT** stop reply |

## Tips

- Want to speak many sentences without Thansa sending early, use hands-free mode (mic button) and speak continuously; only pause when truly done.
- Hearing Thansa read for a while and want to read silently: toggle off "🔊 Read replies aloud", reply still shows fully in text.
- Paste many screenshots at once by drag-drop them all into the window, Thansa processes each one.
- If you usually speak English, change "Listening language" to English for better recognition.
- Paste long text freely into chat: Thansa auto-converts to `.txt` file attachment, chat stays compact.
- Resend a question you asked before but want to change a few words: click **✎** on the old message, edit in the input box, send again - no need to type from scratch.
- The **⛶** button on CONVERSATION and the **Chat** item in the Assistants group both lead to the same place; use whichever is handier.

## Common issues

- **Holding Space doesn't start mic.** Cursor is in a text box or input field. Click an empty area then hold Space again.
- **Browser doesn't support voice.** Thansa reports "Your browser doesn't support voice. Use Chrome/Edge." Open the dashboard with Chrome or Edge.
- **Microphone not working.** Browser blocked the permission. Go to the page permissions in your browser settings and allow microphone, then reload the page.
- **Pressing Esc but Thansa keeps speaking.** That's how it's designed now: Esc doesn't stop replies anymore. Click the stop button (square) on the input bar, or click the speaker to mute.
- **Can't hear Thansa reading.** Check the speaker button (top right is dim, or input bar button is crossed-out red) - is it muted? Check system volume. Click "▶ Test listen" to test voice separately. If using OpenAI or ElevenLabs and voice sounds odd, likely the provider errored and Thansa fell back to Edge.
- **Typing "/" but no menu appears.** Menu only opens when "/" is at the box start and no space follows. If no skill lines appear, the selected brain has no skills enabled.
- **Clicking Thansa's choice button doesn't work.** That's a button from an old request, frozen when you sent a new message. Just type your answer by hand.
- **Image in conversation shows gray "Image expired" box.** File is in cache `attachments/` past 30 days or got cleaned when exceeding 300MB. Ask Thansa to recreate it, or next time copy important images to another folder.
- **Diagram won't render, only see code.** Diagram library loads from the internet; you're offline or blocked. Content is safe in the source code tab.
- **Asking for image creation shows "ChatGPT not connected."** Go to the **Models** page and sign into ChatGPT (OAuth), no API key needed, then try again.
- **Reply box empty.** If it shows a retry hint or model switch suggestion, your current model may have an issue. See [Models & Engines](10-models-va-engine.md) to switch.
- **File keeps uploading.** Large file or slow network; the file card will show the specific error (timeout, server error). Try again with a smaller file or check your connection.

## Related

- [Conversation Sessions](04-phien-hoi-thoai.md) - save, reopen, rename, delete old conversations.
- [Skills](06-skills.md) - write and call skills using `/slug` command.
- [Models & Engines](10-models-va-engine.md) - seven model providers and how to switch engines.
- [Connections & Business Data](09-mcp-va-so-lieu.md) - connect data sources to ask real numbers.
- [File Management](05-quan-ly-tep-tin.md) - left VAULT column and Files page.
- [Tasks & Dataview in notes](19-task-va-dataview.md) - `dataview` and `tasks` blocks in replies.
- [Telegram Channel](11-telegram.md) and [Zalo Channel](12-zalo.md) - chat with Thansa outside the dashboard.

Still stuck? See [Troubleshooting & FAQ](17-khac-phuc-su-co.md).
