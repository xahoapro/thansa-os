# Zalo Bot Channel

*[Tiếng Việt](26-kenh-zalo-bot.md) · **English***

Ask Thansa directly on Zalo - no need to open the dashboard and no need to install Telegram. You message a dedicated Zalo bot just like messaging a person, and Thansa replies using the brain and memory running on your machine or VPS.

This channel uses **Zalo's official API**, so there's no account-lock risk.

## Don't Confuse It With Two Other Zalo Things in Thansa

Thansa has three places that touch Zalo. Read this table once then you won't have to guess.

| | Page | Is Who | For What |
|---|---|---|---|
| **Zalo Bot Channel** (this page) | Channels | A separate bot | **You** ask Thansa |
| [Chatbot](25-chatbot.md) | Chatbot | A separate bot, speaks as an Agent | **Customers** ask Thansa |
| [Zalo Agent MCP](12-zalo.md) | Connections | Your actual Zalo account | Thansa **acts on your behalf** |

The first two use the official API, safe, but only see messages sent directly to the bot. The third logs into your real account, so it reads conversations and messages anyone, but your account risks restrictions or lock.

Using all three at once is fine - they don't interfere.

## Get a Bot Token

1. Open the Zalo app, find the Official Account **Zalo Bot Manager**.
2. In the chat, select **Create bot**.
3. Set a bot name. The name **must start with "Bot"**, for example "Bot Thansa Of Mine".
4. Zalo sends you the token via message, format `123456789:abc-xyz`.

This token **doesn't expire** until you reset it yourself in Zalo Bot Manager. Keep it secret - whoever has the token controls the bot.

## Turn On the Channel

1. Open the dashboard, **Connections** group, **Channels** item.
2. Scroll down to the **Zalo** card.
3. Check **Turn on Zalo bot**, paste the token into the Bot token field.
4. **Leave the "Allowed Chat ID" field empty.** Click **Save & Turn on**.
5. Open Zalo on your phone, find the bot you just created, send it any message.
6. The bot replies with a **pairing code** - four digits.
7. Go back to the Zalo card on the dashboard. You'll see a block **Waiting for your approval** with your Zalo name and that same code. Click **Allow**.
8. Send a message to the bot again. This time Thansa replies for real.

### Why Jump Through All These Hoops

Zalo has no tool for you to look up your own Zalo ID - it's a string like `6ede9afa66b88fe6d6a9`, not a easy-to-read number. So instead of asking you to find it, Thansa flips it around: whoever messages the bot appears on the dashboard with their **real Zalo name**, you click one button and done.

The pairing code lets you be sure you're approving the right person when two people have the same name. Ask them to read the code in the bot's message and check it matches.

### Empty Chat ID Field Means NO ONE Approved Yet

This is where Zalo **works different from Telegram**, don't be surprised.

On [Telegram](11-telegram.md), leaving the Chat ID field empty means anyone who finds the bot can use it, and the docs warn you not to. On Zalo, leaving it empty means **nobody is approved yet** - everyone who messages it goes to a waiting queue.

If we didn't do that, the on-boarding flow above would create a bot that anyone could reach your brain with, from the moment you turned it on until you hit Allow.

## What You Can Do Over Zalo

Almost everything Telegram can do: ask numbers through MCP, read and write files in your brain, call skills, assign background work, set reminders. Every engine works because tools go through Thansa's MCP Hub, not attached to any one brain.

Slash commands (`/status`, `/reset`, `/stop`, `/model`, `/brain`, `/notes`...) work too, but **Zalo doesn't show a command menu** like Telegram, so you have to type them.

Results from background work and reminders you set from Zalo **come right back to that Zalo chat**, not over to Telegram.

### Run Commands by Voice (Voice Message)

Press and hold the mic in Zalo, speak, release. Thansa hears what you said and acts like you typed it.

**Needs Groq's API key** - that's where Thansa borrows the tool to turn speech into text (Whisper model). Go to the dashboard, **Models** page, **Groq (API)**, paste a key from [console.groq.com](https://console.groq.com), save. Without it, sending a voice message makes Thansa tell you plainly it needs the key - it doesn't stay silent. Paste it and it works right away, no bot restart.

This is **the same key as the Telegram channel**: set it once and both channels hear.

A few things to know:

- **Actions that reach outside get Thansa to ask first.** Sending, posting, scheduling, spending money, editing files - Thansa starts with a line "I heard: ..." then waits for you to confirm. Asking info, looking things up, summarizing - it does straight.
- **Voice recordings don't save to the brain.** Convert to text and done.
- Can't hear the words, file too big, or Groq returns an error - the bot tells you why. No silent failure.
- **One Zalo-only risk:** Zalo hasn't published the data shape for voice messages, so Thansa might not find the file path in the message Zalo sends back. If that happens, the bot says it can't load the file, and the server logs a line `[zalo voice] couldn't find voice file path in payload` with the data sample. Send that line to the developer and it's fixed immediately. Telegram has no such risk because the data shape is published.

## Four Ways Zalo Falls Short of Telegram

Heads up so you know these are expected, not bugs.

**No status updates.** Zalo won't let you edit or delete sent messages, so Thansa can't show "calling a tool..." then update it like on Telegram. While you wait you just see "typing" dots. Instead, the reply has a trace at the end like `⚙ pos_statistics · Read · 8s` showing which tools it touched.

**Can't send file documents.** Zalo Bot doesn't have an API for sending documents, so PDF, spreadsheets, .docx won't go through this channel. Thansa will tell you straight that it couldn't send it and give you the path in your brain so you can open it yourself - not silent. Images are in beta.

**2000 character limit per message** (Telegram is 4096). Long answers auto-split into several messages in a row.

**No buttons.** When Thansa needs to ask for a parameter, it drops to plain text with a numbered list - you send back the number.

## Send Test Button

Click **Send test** to fire a test message to every approved ID. It proves the token and Chat ID are right, **not** that the bot is receiving messages. To see if the bot is getting them, read the status line - it should be **Bot is receiving messages**.

## Common Problems

**Pasted token and it says "Token invalid (Zalo rejected)".** Check you didn't paste a Telegram token by mistake. Two channels, two completely different tokens.

**Sent to bot, nothing shows.** Look at the status line under the Zalo card. If it says "Bot is receiving messages" and still nothing, check the **Waiting for your approval** block - odds are you haven't hit Allow yet for yourself.

**Bot keeps replying asking for pairing code.** Right - not approved yet. Go to the dashboard and hit Allow, then message again.

**Bot says it hit a rate limit.** Zalo hasn't published a rate limit number. Getting a 429 error makes Thansa wait a minute then retry, and shows the error on the status line.

**Zalo is green but replies to nobody.** Check the server log for the line `[zalo getUpdates] strange reply shape`. Zalo's docs don't specify the shape of `getUpdates` replies so Thansa sees many shapes and yells when it sees a new one. Send that line to the developer and it's fixed fast.

## Related

- [Telegram Channel](11-telegram.md) - the other channel, more features but less used in Vietnam.
- [Chatbot](25-chatbot.md) - bot for CUSTOMERS to message, also runs on Zalo.
- [Zalo Agent MCP](12-zalo.md) - log into your personal Zalo account so Thansa can act on your behalf.
- [Scheduled Work & Reminders](08-viec-dinh-ky.md) - where background reports come from when sent to this channel.
