# Chatbot (Specialist Agent)

*[Tiếng Việt](25-chatbot.md) · **English***

Deploy an **Agent** you've created to serve outside users: they message a dedicated bot on **Telegram** or **Zalo**, and the Agent answers according to rules you've written. When it's out of scope, transfer to a real person.

Useful for any repetitive back-and-forth conversations: answering questions about a product or service, explaining internal policies to colleagues, responding to student inquiries, guiding community members, or pre-screening questions before they reach you.

Differs from [Telegram Channel](11-telegram.md) in one critical way: the Telegram bot on the **Channels** page is **Your Thansa** (full control, reads your main brain, can call any data source, only you can message it). The bot on the **Chatbot** page is **a specialist Agent on duty** (read-only by default, sees only its own brain, anyone can message it). Don't use one instead of the other.

A specialist bot **actually works** if you grant it elevated permissions - writing files, calling data sources, even acting outside. But whoever sends it messages controls it, not you, so read the [Three Permission Levels](#three-permission-levels---what-the-bot-can-do) section carefully before raising permissions.

## What This Feature Is

- Each bot = one **Agent** in one brain + one **dedicated token** on Telegram or Zalo. The bot reads documents from that same brain.
- **Choose your channel**: Telegram or Zalo. For Vietnam customers, Zalo is almost always the right choice because they already have the app. See [Choose Telegram or Zalo](#choose-telegram-or-zalo).
- The Chatbot page **belongs to the brain you have open**: switch brains at the top and you see that brain's bot, just like the Agents and Skills pages.
- People message the bot privately, or you add the bot to a group.
- **The bot follows your Agent file exactly.** Thansa doesn't inject any rules of its own.
- **Three permission levels**, chosen when creating and changeable later: Read-only (default), Write, Full control. Raising levels requires checking a box after reading the risk section.
- Two barriers that **don't change with level** and are locked in source code, not by instructions: **the bot only sees its own brain**, and **cannot run shell commands**.
- When a question is out of scope, the bot transfers to a human operator you designate.
- The Chatbot page was built for **multiple bots** from the start: card grid, search box, add/edit/delete, toggle on/off inline. Running one or ten bots uses the same interface.

## Where to Find It in Thansa

Left sidebar, **Capabilities** group, **Chatbot** item.

## Before You Create a Bot

Three things, in this order, so you don't have to come back and fix them.

### 1. Stand in the Right Brain

The bot belongs to **the brain you have open**. The Agent it uses and documents it reads both come from that brain, so before creating a bot, switch to the correct brain first.

**The bot only knows what's in this brain.** This is the most important consideration: if the bot will answer outsiders, don't create it in your main brain, because that contains internal notes, private numbers, unpublished plans - and the bot can't tell which information should stay private.

The clean way: create a separate brain just for answering outsiders (on the **Second Brain** page), put only documents that outsiders should see, then switch to that brain and create the bot.

Principle for choosing documents: **if a sentence in this file would bother you if it leaked, the file doesn't belong in the bot's brain.**

### 2. An Agent in That Same Brain

Go to the **Agents** page and create an Agent for exactly what the bot will do. Write the role and instructions as if you're briefing a new hire: how they should speak, what to prioritize, when to transfer to a real person.

If you're on the Chatbot page and the brain has no Agent yet, click **Create Agent** to jump to the Agents page, finish creating, then come back.

The bot **reads the Agent at runtime**, doesn't copy it. If you edit the Agent later on the Agents page, the bot changes immediately - no need to edit both places. See [Agents & Workflows](07-agents-va-workflows.md) for how to write an Agent.

### 3. A Dedicated Token, from the Right Place by Channel

For a **Telegram** bot: go to **@BotFather**, type `/newbot`, set a name and username, get a token string like `123456789:ABCdef...`.

For a **Zalo** bot: open the Zalo app, find the Official Account **Zalo Bot Manager**, select **Create bot**. The bot name must start with the word "Bot" (example "Bot Kim Khí Hà Lộc"). The token is sent to you via Zalo message, format `123456789:abc-xyz`, and it **doesn't expire** until you reset it yourself.

**Each bot needs its own token, never reuse your personal Thansa bot token.** A single token can only run one process; sharing kills both and the server returns error 409. Thansa blocks this when you hit Check, but knowing first is better.

Paste the wrong channel's token into this channel and Thansa tells you plainly instead of letting you guess: the **Check** button asks the exact platform you just selected.

## Choose Telegram or Zalo

The first field in the bot creation form is channel selection, and it's first because it determines everything below: where to get the token, whether the bot can join groups, whether it can send files.

| | Telegram | Zalo |
|---|---|---|
| Vietnam customers have the app pre-installed | Rarely | Almost always |
| Can join groups | Yes | **No** in the basic bot tier |
| Bot sends images to customers | Yes | In beta |
| Bot sends file documents (PDF, spreadsheets) | Yes | **Not yet** (Zalo hasn't opened the API) |
| Customers send images to bot for reading | Yes | Yes |
| Customers send file documents to bot for reading | Yes | Not yet |
| Character limit per message | 4096 | 2000 |
| Bot displays `/` command menu | Yes | No, must type manually |

Short version: **to chat with Vietnam customers, choose Zalo**, accept that it only works private-chat and can't send documents yet. **For in-house groups or needing file transfers, choose Telegram.**

**You cannot change the channel after creating a bot.** Changing channels means switching to a completely different bot: different token, different identity, different customers, and all stored group IDs instantly become invalid. Need a different channel? Create a new bot; the Edit form will show the channel as locked with this explanation.

On the card grid, each bot carries a **channel indicator** in two places: a small badge on the icon (quick glance to tell them apart), and a chip with the logo in the info section (for reading). When you have bots on both channels, the page automatically adds a filter row of buttons: **All / Telegram / Zalo**.

### How Zalo Bot Differs from Zalo Agent MCP

Thansa has two paths to Zalo, and they don't replace each other:

- **Zalo Bot** (this page) is a **separate identity**, using the official API. No account-lock risk, but it only sees messages sent directly to it.
- **[Zalo Agent MCP](12-zalo.md)** logs into **your actual Zalo account** via unofficial API. Reads real conversations, messages anyone, but your account risks restrictions or lock.

The first is for **others to chat with Thansa**. The second is for **Thansa to act on your behalf**. Using both is fine.

## How to Use (Step by Step)

### Step 1: Create a Bot

Click **New Bot**, fill in:

| Field | What to Enter |
|---|---|
| Where does this bot chat | **Telegram** or **Zalo**. First field because it changes the rest of the form. See [Choose Telegram or Zalo](#choose-telegram-or-zalo) |
| Bot name | Name you see to tell bots apart |
| Agent for the brain | Pick an Agent in the open brain, or click **Create Agent** |
| Bot's answer source | See the two modes section below |
| What the bot can do | Permission level. Leave at **Read-only** for first time; see [Three Permission Levels](#three-permission-levels---what-the-bot-can-do) before raising |
| Token | Paste the token from the channel you just chose, then click **Check** |
| Operator's Chat ID | Telegram ID of the person who receives transfers (see below) |
| Allowed groups | Telegram only. Leave blank if you prefer - add the bot to a group then approve with one click later (see Step 4) |
| When bot speaks in groups | Telegram only. By default only when @mentioned or replied to |

Choose Zalo and the last two fields **disappear** instead of appearing and doing nothing: Zalo's basic bot tier doesn't allow groups, so entering group IDs there is just a broken promise in your data.

**No "choose brain" field**, intentionally: the bot belongs to the brain you have open. For a bot in another brain, switch brains at the top, then create again - one place to look, no two layers to sync.

Click **Check** before saving: Thansa asks the exact platform you chose whether the token is real, returns the correct bot name, and warns immediately if another bot in Thansa is already using that token. For a Zalo bot, if your tier doesn't allow groups, it tells you right here.

**Bots start in OFF state.** By design: turning one on means the bot talks to real people immediately, so flipping that switch should be a conscious act, not a side effect of creation.

### Step 2: Test Message Before Turning On

Turn the bot on with the **On** button on its card, then open Telegram and message the bot privately like a real customer. Ask a few questions in scope, then ask one you know for certain isn't in the documents. Check the tone, whether it makes things up, whether it admits "I don't have that information".

If it looks off, turn it off, edit the Agent or add documents to the brain, test again. Turning off takes effect immediately, no Thansa restart needed.

### Step 3: Hand Off to a Real Person

Fill in **Operator's Chat ID** so the bot has someone to transfer to when stuck. Get that number by asking the person to open **@userinfobot** on Telegram; it returns a line `Id: 123456789`.

The operator must click **Start** in a chat with this bot once, or Telegram blocks the bot from messaging them.

Then the bot has two transfer paths: it calls the operator automatically when **stuck on two questions in a row** with the same person, and if the person types `/nhanvien` it reports immediately. Both send the operator a message with the bot's name, conversation ID, and reason. When the bot hits a **technical error**, it reports right away starting from the first time, but only once until the bot runs again.

Leaving this blank means **the bot still answers normally** per its Agent - it just has no one to hand off to. Anyone typing `/nhanvien` is told that no operator can be reached and invited to ask more.

If you want the bot to stay silent when no documents match, that's the **Documents only** mode above, not this field.

### Step 4: Add Bot to a Group

1. Invite the bot to a group like inviting any member.
2. In the group, type **`/id`**. The bot returns the group id **and tells you the status**: whether this group is enabled, whether Telegram's privacy mode is on, and what to do next.
3. That group **shows up as a card on the Chatbot page**. Click **Allow this group**. Done.

Use `/id`, not the bot's name - intentional: **`/...` commands always reach the bot** even if Telegram privacy mode is on, but mentioning the name isn't guaranteed (see below). If step 2 and the bot **says nothing at all**, the problem isn't the group - the bot is either off or the token is bad; check the status dot on the card.

You can also do it manually: get the ID from step 2 (a **negative** number, format `-1001234567890`), paste it into the **Allowed groups** field in the create or edit form, one ID per line.

**Without approval, the bot won't reply in that group.** By design: a bot added to a random group that starts replying on its own interrupts other people's conversation. But refusal doesn't mean disappearing - the bot sends one message to the person who called it explaining what to do, and the group sits on the bot's card waiting for you to decide.

If you don't want a group, click **Skip** and it leaves the queue. If someone tries the bot there again, it comes back - this page doesn't hide a place where people are actually trying to use the bot.

In an approved group, by default the bot replies only when someone **mentions its name** (type `@bot_name`, or click its name from the member list) or **replies directly to one of its messages**. With many bots in a group it knows the difference: if you mention a different bot or reply to a different bot, it doesn't take the message.

To make it reply to **every message in the group**, change the "When bot speaks in the group" field. Think carefully: large groups are very noisy and burn through model quota fast. And it only works when privacy mode is off - read the section below.

### Telegram's Privacy Mode (Read This If the Bot Is Silent in Groups)

All new bots have privacy mode **turned on by default**. When on, Telegram **doesn't forward** most group messages to the bot - it's blocked on Telegram's end, so Thansa never even sees those messages, regardless of your dashboard settings.

Messages that **definitely** reach the bot when privacy mode is on:

- **Commands** `/...` (why `/id` always works).
- **Replies straight to a bot message** (click Reply on something the bot said).
- Service messages (member added/removed).

Messages that **only mention** the bot's name are **not guaranteed**, depending on version and group type. If you @mention the bot and it stays silent while private messages work fine, this is almost always the cause.

Fix it **one of two ways**:

1. Open **@BotFather**, type `/setprivacy`, choose this bot, select **Disable**.
2. Or make the bot a **group admin**. A bot with admin rights gets all messages, privacy mode doesn't matter.

Then **turn the bot off and back on** on the Chatbot page so it reads the new status. The bot card shows this status for any bot using groups, and `/id` in the group also reports it.

There's a third, rarer cause with the exact same symptom: **the bot couldn't ask Telegram for its own identity** (network hiccup at startup). Then it doesn't know its own `@username` and can't recognize being called by name, even though private messages work perfectly. The bot card reports it with a red line, and Thansa re-asks every minute; toggling the bot off and back on fixes it immediately.

**When a regular group is upgraded to a supergroup, Telegram changes its ID** (adds prefix `-100`). Thansa hears it and updates the list automatically - you don't have to re-enter IDs. This used to be a mystery why the bot went silent with zero clues.

## Reading a Bot Card

Each card has a color dot and a status line. **Four** states, not two:

| Dot | Meaning |
|---|---|
| Green - Running | Bot is listening and replying normally |
| Yellow - Starting up | Just turned on, handshaking with Telegram |
| Red - Error | Bot is dead. Token revoked, network down, or token duplicated elsewhere. Reason shows right below the card |
| Gray - Off | You turned it off |

The **Error** state must be visible - a bot dying silently is something you'd only find out about when someone complains.

The card **auto-refreshes every few seconds** while you have the page open. Necessary because status changes without anyone clicking: you click On and the card says "Starting up" (bot is shaking hands with Telegram), then a few seconds later it's "Running". Without auto-refresh the card would stay stuck on "Starting up" until you leave and come back - while the bot has been replying for a while.

The card also warns when the **bot's Agent is gone** (you deleted it or changed its slug on the Agents page). The bot still runs but without role instructions, so fix it immediately.

**Permission level shows right on the card**, all three levels, not just the two with power: gray for Read-only, yellow for Write, red for Full. No need to open the Edit form to tell which bot is at which level, and an unlabeled card can't be read two opposite ways anymore.

## How Many Tokens Does a Bot Use

The bot **doesn't go through** the Optimize and Extreme savings modes on the Usage page. Intentional, not an oversight: those two modes exist to trim CLAUDE.md, MEMORY.md, and tool spec tables - **three things the bot never has**.

Measured on a sample brain, fixed overhead per turn:

| Route | Fixed Tokens |
|---|---|
| Dashboard chat, Full mode | ~8,900 |
| Dashboard chat, Extreme savings | ~460 |
| **Specialist bot** | **~20** |

The rest of a bot turn is the documents it looks up - that's the answer itself, not waste. In other words the bot is already lighter than the deepest savings mode, so pushing it through two extra layers only makes it **heavier**.

Below the answer and on the measurement table, a bot turn shows as **"Specialist bot"**. Before 0.23.1 it was lumped into "Full" - the exact opposite of the truth, because this is the cheapest route in the system.

The bot still counts toward **Usage** like any other turn, per the provider and model actually running.

Don't confuse the bot with **your personal Telegram channel**: that channel *does* go through the two savings modes (from 0.24.0), because your Thansa really does have CLAUDE.md and MEMORY.md to trim. The bot has nothing to trim.

## What the Bot Bases Its Answers On

Each time someone asks, Thansa **searches the brain's documents first**, pulls the best-matching excerpts, then feeds them straight into the start of that turn.

This is different from "the bot can read the brain". Being able to read doesn't mean it will: a model can perfectly well answer straight from its general knowledge, the words flow just as confidently, and you **can't tell from the outside**. So Thansa searches first and doesn't leave it up to the model.

### Two Modes, Choose When Creating the Bot

The only difference is **when no matching documents are found**. Find something and both modes act exactly the same.

| Mode | When no docs match, bot does | Good for |
|---|---|---|
| **Agent's specialty** (default) | Thansa says nothing extra; Agent handles it per your instructions | Coaching, training, expertise advice, answering questions |
| **Documents only** | Add a rule: "no information available", don't use general knowledge | Reading numbers and policies where one wrong answer costs real money |

Pick wrong and you see it right away: an Agent set to "documents only" that's written as a coach will reply "I don't have that information" to exactly the questions in its specialty, even though you wrote detailed instructions. Switch modes in the **Edit** button, takes effect immediately.

### Thansa DOESN'T Write Rules for the Bot

This is the most important thing to know about this page.

The bot runs on **exactly the contents of your Agent file**, nothing more. Thansa doesn't layer on extra rules: it doesn't tell the bot how to speak, doesn't ban topics, doesn't force short answers. The only rules the bot has are what you wrote in the Agent.

The only exception is the "documents only" mode above, and that's a rule **you actively turn on**, not a Thansa default.

So **the Agent file decides bot quality, almost entirely**. Write like you're briefing a new hire: how they should speak, their scope, what not to promise, when to transfer to a real person. If the bot acts wrong, edit the Agent - don't look for another button.

### Two Barriers Thansa Locks at EVERY Level

Both things below are true even when you give the bot full control. They're in source code, not in instructions, so no clever wording gets around them:

- The bot **doesn't see other brains**, including your main brain. Every read and write path is trapped in that brain's directory; trying to escape with `../` or absolute paths is rejected immediately.
- The bot **can't run shell commands**, can't open random web pages, can't spawn child agents. The bot also **has no admin commands**: `/brain`, `/model`, `/status` do nothing, it just answers generically.

How Thansa guarantees this: **the bot never touches the engine's root tools**. At Read-only it has no tools at all; at higher levels, every tool goes through Thansa's connection hub, where file paths are trapped and permissions enforced right at the call site. The bot doesn't open a CLI, so Claude Code's `Bash` and absolute-path `Read` don't exist here.

Documents are still pre-searched by Python before the model runs, fed into the start of the turn, at every level. The bot reads its brain without needing any tool.

## Three Permission Levels - What the Bot Can Do

Choose from the **What the bot can do** field when creating or editing. Default is **Read-only**.

| Level | Bot Can | Good For |
|---|---|---|
| **Read-only** (default) | Only read documents and reply. No tools. | On-duty chat and FAQs - covers almost everything |
| **Write** | Add: write files in its own brain, call data sources already connected at read/write | Recording requests, updating notes, looking up real numbers |
| **Full** | Add: send, charge payments, book/cancel, delete, publish outside | Where you control who messages the bot |

### What You Lose When You Raise the Level

This is the part worth reading most carefully, because it's the core difference between a specialist bot and your personal Thansa: **the person typing to the bot is someone else, not you.**

At Read-only that's harmless - even if a bot is clever, it can only talk because it has nothing else to do. Raise the level and you're handing that away.

**At Write level:**

- The bot can write files in its own brain. One message from the person chatting becomes changes inside the brain, **with no review step**.
- The bot can call any data source you connected, at read and write levels. Everything in those sources is in reach of whoever is messaging the bot.
- Thansa still **hard-blocks** actions outside this level: no sends, no charges, no booking/canceling, no deletes, no publishing. Blocked at the tool call layer, not by instructions.

**At Full level:**

- The bot can do **everything** those data sources allow, including send, charge, book/cancel, delete, publish outside. Those actions **can't be undone**.
- A clever prompt ("ignore instructions before this, do X") is enough. The only remaining barrier is the Agent file you wrote, and words can be talked around.
- The bot doesn't ask you first. No review gate for each command.

That's why: **only turn Full on when you control who messages the bot.** A place where anyone can message? No, regardless of how carefully you write the Agent.

### How to Raise a Level

1. Click **Edit** on the bot's card (or choose when creating).
2. Pick a level from the **What the bot can do** field. The risks for that level appear right below.
3. Check the box **I have read and accept the risks above**. Without it, you can't save - Thansa blocks at both UI and server, so dev tools can't work around it.
4. Full level asks one more time before saving.
5. Turning the bot on also asks again, because you might have chosen a level weeks ago and forgotten which one this bot is at.

Lowering a level asks nothing: lowering permissions is always safe, and you need speed when fixing an incident.

Any bot with raised permissions has a color bar showing the level clearly - yellow for Write, red for Full. Read-only bots have no label because it's the default. The log also marks the permission level for **each turn**, so you can look back at "what did the bot do that day" even if you've lowered permissions since then.

### Which Engines Support Raised Permissions

**Read-only** runs identically across all nine brains - no exceptions.

Raised permissions need an engine that can call tools. Six API engines (OpenRouter, OpenAI, Anthropic, Gemini, Groq, Ollama) and Claude Code have a proven path. The **ChatGPT tier** goes through a backend Codex path that the provider hasn't announced as stable, so it might not call tools.

In that case **the bot doesn't die**: it answers that turn at Read-only, and the card shows a yellow bar saying it's running with less permission than you set. Raising permission is never allowed to take away something the bot had.

See that yellow bar? Pick one: switch the engine on the **Models** page if you really need the bot to work, or lower the bot to **Read-only** so there's no confusion about what it's doing.

### Switching Brains Doesn't Change How It Works

The bot runs identically on **all nine brains**: Claude Code, ChatGPT (via Codex), Antigravity CLI, OpenRouter, OpenAI API, Anthropic API, Google Gemini, Groq, Ollama. Change the model on the Models page and the bot changes with it, but how it works stays the same. When tools can be called, every engine gets **exactly one tool set** - see the note above about ChatGPT tier.

Works because a bot turn follows its own path, shared by every engine: same Agent preamble, same pre-searched documents, same conversation history, and tools (if any) from the same place. Any remaining difference is just the difference between models themselves, not between pathways.

This path also doesn't open a CLI, so the bot replies faster than your personal chat path.

### Getting Documents to Match Well

- **Use clear headings in your files.** Thansa cuts documents by markdown heading (`##`), and each section is taken separately. A long file with no headings means the bot might read only the first condition and answer as if that's the whole rule. Breaking into "Retail Price", "Wholesale Price", "Returns", "Shipping"... matches much better.
- **Files uploaded by customers do NOT count as documents.** They live in `inbox/khach/` and are excluded entirely from search. Otherwise anyone uploads a file overwriting your policy, asks again, and the bot cites it as official.
- **Thansa's internal policy files are also excluded.** `CLAUDE.md`, `AGENTS.md`, `wiki/index.md`, `wiki/log.md` and a few navigation files exist in every brain but are system internals, not customer-facing content. Your actual Wiki notes still work normally.
- **Tone marks and no-tone searches both work**, but exact tone marks are more precise: "bán" doesn't match "bản", "cà" doesn't match "cả". Documents should be spelled correctly and with proper tone marks.

## Log and Where Documents Are Lacking

Click **Log** on the bot's card. Two tabs, and the open one is more important.

**Bot stumped** lists questions the bot couldn't answer, deduplicated and sorted by **how many times asked**. This is the most valuable tab: each line points to exactly one gap in your documents, in the customer's own words. Add content to the brain and the bot answers next time.

Deduplication drops tone marks, so "Giá bao nhiêu?" and "gia bao nhieu" count as one question. Otherwise the same question gets split across many lines and you'd miss how often it's actually asked.

"Stumped" is measured by **the exact words the bot just said**: it said it has no information, or it transferred to a human. For bots in "documents only" mode, not finding documents counts too.

Most valuable is the kind of stumped where the bot **still found documents**: documents exist but lack exactly what the person needs. Points to under-written documents, more subtle than finding no file at all.

**Recent conversation** shows each turn with **the exact file the bot used** to answer. That source line is what makes the question "was the bot right?" verifiable instead of guesswork.

### When the Operator Gets Called

With an operator's Chat ID set, the bot calls the operator in two cases: the person typing `/nhanvien`, or the bot **got stuck on two questions in a row** with the same person. Answering one question resets the count to zero.

Getting stuck on one lone question doesn't call. Reporting every vague message means the operator turns off notifications, and when a real person needs help nobody reads anymore. Two in a row is the signal someone is actually stuck.

The third case is the bot **breaks** (can't reach the model). Reports immediately from the first time, not waiting for two, because every silent minute makes the person think they're ignored. But only **once** until a turn succeeds - otherwise the operator's inbox becomes an error log.

Before declaring a break, Thansa retried up to three times if the error was **temporary** (provider returned 429 for rate-limit, 5xx for overload, network blinked). A single passing 429 doesn't wake the operator anymore. "Broke" messages include *(retried 3 times)* meaning every option was tried, so go check the **Models** page or your account limit. Details in [Troubleshooting](17-khac-phuc-su-co.md#nh%C3%A0-cung-c%E1%BA%A5p-b%C3%A1o-v%C6%B0%E1%A3t-h%C1%BA%A1n-m%E1%BB%A9c).

The log keeps 2000 most recent turns per bot - older than that auto-trim. Delete the bot and the log goes with it.

## What the Bot Can and Can't Do

**At every level, the bot can:** read documents in its brain, reply per its Agent rules, remember each person's chat history, transfer to an operator.

**At every level, the bot cannot:** read or write other brains, run shell commands, open random websites, spawn child agents, use admin commands (`/brain`, `/model`, `/status`... do nothing, it just answers generically).

**The rest depends on permission level** - writing files, calling data sources, acting outside. See the table under [Three Permission Levels](#three-permission-levels---what-the-bot-can-do). Default is Read-only, meaning it can't do any of those.

Telegram's command menu on the bot only has three items (`/help`, `/nhanvien`, `/id`), not the admin menu of a personal Thansa bot. Listing commands there that the bot refuses to run teaches people to go hunt another command set.

Meanwhile, **how it speaks, what scope it accepts, what it refuses** - all that is decided by your Agent file, not Thansa. Want the bot to avoid a topic, not promise things on your behalf, not get fooled by clever prompts? Write that into the Agent.

Important to understand correctly: those limits above are **permission levels in source code**, not instructions in the prompt. Instructions can be talked around; permission levels can't, because the tool simply isn't given to that turn. The flip side of the same fact: when you **do** grant a tool to a turn, the instructions in the Agent can't hold it back anymore.

## The Bot Talks Like a Person, Doesn't Leak System Status

A specialist bot **shows zero Thansa status lines** to the person messaging it. This is very different from your personal Thansa bot (it shows everything - see [Telegram](11-telegram.md), because the machine owner needs to see where Thansa is in its work).

Specifically, someone messaging the bot will NEVER see:

- "🤔 Thansa is thinking…" and updates like "⏳ ⚙ Calling a tool…"
- "⏳ Processing the previous message. Send /stop to cancel and ask again."
- Error lines like "⚠ Error: TimeoutError: ..."
- "(no content)" when a turn returns empty

Instead, while the bot thinks, Telegram shows typing dots **"typing…"** at the top of the conversation, just like a real person typing. If a turn breaks, the bot apologizes in plain language and asks them to try again; the reason is still logged in full in the bot's log and still alerted to the operator if you set one.

**Sending more while the bot is replying doesn't get blocked.** The bot collects those messages, finishes the previous answer, then answers the new batch as a single turn - like a person reading more messages before replying. Collected up to 5 messages per conversation to keep strangers from spamming and bloating memory.

One place still intentionally speaks plainly: when someone calls the bot in **a group you haven't approved**, the bot says in one message one time that it's not enabled for this group. Going silent there would make the bot look broken and you'd have no way to know to click **Allow this group**.

## Rate Limits

Each person hits a turn limit per hour (default 20, changeable in Edit). Over that, the bot politely asks to try again later.

Necessary because an idle person in a group can burn through your model quota in an afternoon, and you only find out when you see the bill.

## Delete the Bot

Click **Delete** on the card. The bot stops replying immediately.

**Its brain and Agent are NOT deleted.** The brain might hold a month of documents you wrote, the Agent might be used by another bot or workflow. Delete them on their own pages if you want them gone.

## Frequently Asked Questions

**What model does the bot use?** Whichever model you picked on the Models page. Change the model and the bot changes with it, and how it works doesn't change - all nine brains use the same path.

**Can the bot call the data sources I connected?** Not by default - Read-only just has documents in its own brain. Raise to **Write** and yes, and **Full** adds actions outside too. Keep in mind that whoever messages the bot controls it; if it's something only you need, ask Thansa on your personal dashboard or Telegram channel instead - much safer.

**Is Full permission dangerous?** Yes, which is why Thansa makes you check a box and asks a second time. The danger isn't the model acting up, it's **anyone being able to message the bot**: one clever sentence and the bot calls a real tool, no undo, no asking you first. Only use it when you control the message list.

**Bot is at Full and I see a problem now - what do I do?** Click **Off** on the card - takes effect in seconds, no Thansa restart. Then click Edit and drop the level to Read-only; lowering permission asks nothing. Check the **Log** tab to see what the bot did.

**Can I run many bots at once?** Yes. Each bot has its own token, runs its own process. The Chatbot page was built for that.

**Can two bots share an Agent?** Yes, sometimes it makes sense: same role but two brains for two different groups of customers. Two bots using the same token? No - Thansa blocks that.

**When customers send images to the bot?** Files land in `inbox/khach/` in the bot's brain, separate from your files, and don't count as documents for answering.

**Bot gave a wrong answer - where do I check?** Click Log, Recent conversation tab. The source line under each turn tells you which file it pulled the answer from, so fix the right place.

**Bot says "no information" but the document clearly says?** Usually long files with no headings, or the document uses different words than the person asked (document says "refund", person says "return"). Add headings to files, or write alternate phrasings into that exact section.

**Does the bot remember people?** Yes, each person gets their own conversation thread in the bot's brain.

**I added the bot to a group, @mentioned it, and it doesn't reply, but private messages work?** Type **`/id`** in that group - the bot will answer and say why. Three causes for exactly this symptom: group not enabled (click **Allow this group** on the card), Telegram privacy mode still on (see [Privacy Mode](#telerams-privacy-mode-read-this-if-the-bot-is-silent-in-groups) section), or the bot couldn't learn its own username yet (toggle off/on). If `/id` itself gets no reply, the bot isn't running - check the status dot on the card.

**Bot set to "reply to everything" but still only replies when @mentioned?** Telegram privacy mode is still on - it blocks from Telegram's side so Thansa never sees those messages. Disable it in @BotFather (`/setprivacy` → Disable) or make the bot a group admin, then toggle the bot off and on again. The card tips you off when this happens.

**If I turn off Thansa, does the bot keep running?** No. The bot runs in Thansa's process, so the machine/VPS must stay on. Turn Thansa back on and any bot that was on auto-restarts.

## See Also

- [Agents & Workflows](07-agents-va-workflows.md) - writing an Agent to be the bot's brain.
- [Telegram Channel](11-telegram.md) - your personal Telegram bot, very different from this one.
- [Second Brain](13-second-brain-bo-nho-wiki.md) - create a brain and load documents for the bot to read.
- [Security & Account](14-bao-mat-tai-khoan.md) - how tokens are encrypted.
