# Zalo Agent MCP

*[Tiếng Việt](12-zalo.md) · **English***

> **Thansa connects to Zalo in THREE different ways, don't mix them up.** This page covers the first one: logging in with **your personal Zalo account** so Thansa can act on your behalf. The other two use official, secure APIs, but only see what people send directly to the bot.
>
> | | Zalo Agent MCP (this page) | [Zalo Bot Channel](26-kenh-zalo-bot.md) | [Chatbot](25-chatbot.md) |
> |---|---|---|---|
> | Who it is | Your personal account | A separate bot | A separate bot under Agent name |
> | API | Unofficial (zca-js) | Official | Official |
> | Risk of account lock | Yes | No | No |
> | Can read old conversations | Yes | Only messages sent to bot | Only messages sent to bot |
> | Can message people unfamiliar with bot | Yes | No | No |
> | Used for | Thansa acts on your behalf | **You** message Thansa | **Customers** message Thansa |
>
> You can use all three at the same time; they don't interfere with each other.

Thansa connects your personal Zalo via an MCP standard of the
[`zalo-agent-cli`](https://github.com/PhucMPham/zalo-agent-cli) project. The new flow has just one MCP process: QR login, read or search conversations, and send messages via tools provided by the upstream project.

> `zalo-agent-cli` uses Zalo's unofficial API through `zca-js`. Zalo does not support this connection method and your account may be restricted or locked. Use a secondary account, avoid sending messages in bulk automatically, and take full responsibility when using this.

## Prerequisites

- Node.js 20 or later on the machine or VPS running Thansa.
- A phone with the Zalo account you want to connect already logged in.
- Thansa is running and you are logged into the dashboard.

Thansa pins `zalo-agent-cli` to version `1.6.2`, which has been tested with the seven MCP tools below.

## Connect via QR

1. Open **Connections** → find **Zalo Agent MCP** → click **Connect**.
2. Read the risk warning, enter a nickname if desired, then click **Show QR Code**.
3. In the Zalo app on your phone, open the QR scanner and scan the code on the dashboard.
4. When your account card appears in the **Connected** section, the connection is ready.
5. To add another account, click **＋ Add Account**. Each account uses its own session directory so they don't overwrite each other.

The **GitHub Guide** button in the Zalo card always opens the documentation page at:

<https://github.com/blogminhquy/thansa-os/blob/main/docs/12-zalo.md>

## MCP Tools

| Tool | Purpose | Action Level |
|---|---|---|
| `zalo_get_messages` | Read new messages in buffer, supports cursor | Read |
| `zalo_get_history` | Get chat history, has pagination | Read |
| `zalo_list_threads` | List current conversations in buffer | Read |
| `zalo_search_threads` | Search for groups or people by name | Read |
| `zalo_view_media` | Download/open images, audio or video from messages | Read |
| `zalo_mark_read` | Mark as processed up to a cursor | Write |
| `zalo_send_message` | Send message to individual or group | Dangerous |

List above follows `zalo-agent-cli` version 1.6.2 source code. MCP documentation of the upstream project:

<https://github.com/PhucMPham/zalo-agent-cli/blob/main/skill/references/mcp-guide.md>

## Sending Images and Files

`zalo_send_message` above **only sends text**. To send images (e.g., images Thansa just created) or files (PDF reports, spreadsheets), use the `zalo_send_image` tool provided by the bundled `zalo-image` plugin. The plugin is enabled by default, no additional installation needed, and uses the same Zalo account you scanned the QR with.

| Tool | Purpose | Action Level |
|---|---|---|
| `zalo_send_image` | Send image or file with a message | Dangerous (Full Permission level) |

Speak in chat as usual, for example "send this image to Business group" or "send July report to Nam via Zalo".

Three important things to know:

- **Can only send files in the current brain.** This is an intentional safety barrier: otherwise, a clever chat message could trick Thansa into sending any file from the server, and Zalo messages can't be recalled.
- **Send one type at a time**, either all images or all files, maximum 10 files per send. Mixing them confuses Zalo's display so Thansa will report back instead of guessing.
- **Multiple Zalo accounts means Thansa asks which one to use** before sending. Sending from the wrong account means sending under someone else's identity, so this is a decision that can't be guessed.

Requires Node.js 20+ on the machine running Thansa, same as the Zalo connection part.

## How to Use in Chat

You can speak naturally:

- "Find Business group on Zalo."
- "Read the 20 most recent messages from Business group."
- "Any new Zalo messages?"
- "Send Business group: let's meet tomorrow at 9am."

When sending a message, clearly state the name or `threadId`, content, and whether it's a personal or group chat. If the search results have multiple conversations with the same name, Thansa must ask instead of guessing.
If there's only one exact match, Thansa sends right away using `zalo_send_message`; no need to enable listener, no need for the recipient to message first, and it doesn't depend on any watch list.

## Permissions

New connections default to **Full Permission** level to use `zalo_send_message`.

- **Read Only**: only use the five read tools.
- **Draft Write**: add `zalo_mark_read`, still block sending.
- **Full Permission**: allow sending (both `zalo_send_message` and `zalo_send_image`).

You change permissions in the account chip menu on the **Connections** page. Even if running in restricted mode, MCP Hub still blocks sending regardless of the account's Full Permission setting.

## Difference from Old Zalo Integration

The new flow dropped the sidecar `listen --webhook`, endpoint `/hook/zalo`, panel "Listen for messages", chat-specific rule files, and two plugins `javis_zalo_rule`/`javis_zalo_send`.
No more listener process turning itself on and off while MCP connector runs.

So Thansa no longer forwards Zalo messages to Telegram in the background. When you need to check messages, ask Thansa; MCP can use `zalo_get_messages` for buffered messages or `zalo_get_history` for history.

## Troubleshooting

- **QR doesn't show**: check `node --version` must be 20 or later and machine can reach npm.
- **QR expired**: close the connection window then click **Connect** to make a new code.
- **Can't see the conversation**: try `zalo_search_threads`; if you need old messages, use `zalo_get_history` instead of just `zalo_get_messages`.
- **Send tool blocked**: open account chip menu and change permission to **Full Permission**.
- **Session in use elsewhere**: close Zalo Web or other `zalo-agent-cli` processes using the same account, then try again.
- **Want to re-login from scratch**: delete the connection on dashboard, then reconnect and scan QR again. Other connections' session directories are unaffected.

## References

- [Repository `zalo-agent-cli`](https://github.com/PhucMPham/zalo-agent-cli)
- [Upstream MCP Guide](https://github.com/PhucMPham/zalo-agent-cli/blob/main/skill/references/mcp-guide.md)
- [MCP Connection and Permissions in Thansa](09-mcp-va-so-lieu.md)
