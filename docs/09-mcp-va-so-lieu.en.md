# Connections & Business Metrics

The **Connections** page is where you "plug" Thansa into the tools you're using: Pancake POS, Zalo, Webcake Landing, Botcake, Meta/Google/TikTok ads, calendar, CRM... After connecting, Thansa reads REAL data and (if you grant permission) performs real actions on those tools. This page guides you through: connecting a service from the Library, linking multiple accounts, permission management, viewing logs, and how to read data.

## What is this feature

Underneath, each connection is an "MCP pipe" (Model Context Protocol) linking Thansa to an external service - but you don't need to know the details. New features from version 0.9:

- **Pre-built Connection Library**: choose a service, paste the API key (or scan QR for Zalo) and done. Thansa auto-checks the key and auto-names the account (e.g., pulling the exact store name from Pancake POS). No need to type URLs or headers.
- **One service, many accounts**: 3 Pancake stores = 3 accounts under one Pancake POS card. 2 Zalo numbers = 2 Zalo accounts running in parallel. Each account toggles on/off, permissions are set separately, defaults are customized.
- **All brains share one pool**: Claude Code, ChatGPT (Codex), OpenRouter, OpenAI API, Anthropic API and Google Gemini (API) all use this shared Connection library via Thansa's "hub" - connect once, switch models freely. Gemini has one quirk: the MCP underneath can already call tools via hub, but the Connections page still shows a yellow warning "⚠ Main Model is Google Gemini (API) - tool calling not supported yet. Change on the Models page." because the UI list hasn't updated. Just use it normally.
- **Hard permission enforcement**: each account has a permission level. Thansa BLOCKS (not just suggests in words) actions exceeding the level, e.g., creating an order when set to Read-only.

## Where to find it in Thansa

1. Open the dashboard (default port `7777`).
2. Left sidebar, open the **Connections** group, then click the **Connections** item (plug icon, subtitle "Data sources & tools").
3. The page has 3 sections:
   - **◆ Connected** - your linked accounts, with a checkbox "Only use Thansa connections (bypass device defaults)".
   - **◆ Connection Library** - 24 pre-built services ready to connect, with a "Search services…" box and filter buttons: **All**, Apps, Sales, Messaging, Marketing, Office, Ads, Social, Creative. Six Google services are grouped into ONE **Google** card labeled "6 services" - click **Choose service** on that card to see the sub-list.
   - **◆ Connections from Claude Code and Codex** - a FOLDED section at the bottom, subtitle "click to view". These are pre-logged sources in your Claude account (synced from claude.ai) and in the Codex CLI. The list only loads when you click to open, and is somewhat slow because Thansa checks the status of each source. View-only here, can't edit.

## How to use (step by step)

### 1. Connect Pancake POS (paste API key)

1. In the **Connection Library**, find the **Pancake POS** card, click **Connect**.
2. Follow the instructions in the dialog: open Pancake POS > Store Setup > Apps & API > create an API key, then paste it into the box.
3. Click **Connect**. Thansa auto-checks the key - if correct, shows "✓ Connected: <store name>" and the account appears in the Connected section. Invalid key shows an error right there.
4. Multiple stores? Click **+ Add account** on the Pancake POS card, paste the next store's key. Each store gets its own chip.

Pancake POS defaults to **Read-only** - Thansa can view revenue, orders, customers... but cannot create orders or touch money. To let Thansa act, see the Permission section below.

### 2. Connect Zalo (scan QR)

Requires Node.js 20+ on the machine running Thansa (download from nodejs.org, install once).

1. In Connection Library, click **Connect** on the **Zalo Agent MCP** card.
2. Read the risk warning: this is an UNOFFICIAL tool, your Zalo account may be restricted or locked - recommend using a secondary account. Click "I understand the risk, show QR code".
3. Open Zalo on your phone > QR icon top corner > scan the code on Thansa's screen.
4. After scanning, the account appears automatically. To link another Zalo number, use **+ Add account** - accounts run isolated, no interference.

Zalo defaults to Full access to use the send message tool. Can be downgraded to Draft or Read-only on the account chip. The new integration uses directly the seven tools of `zalo-agent-cli`, no separate listener/webhook or message forwarding to Telegram. See [Zalo Agent MCP guide](12-zalo.md).

### 3b. Connect Slack / Systeme.io

- **Slack** (official MCP, login via dashboard): Slack requires MCP to go through an app of your own, so a bit more setup once: go to api.slack.com/apps, create an app in your workspace, in "OAuth & Permissions" add Redirect URL `http://localhost:7777/connect/oauth/callback` (VPS: add your domain name) and add "User Token Scopes" (search, channels, users, chat:write, canvases...), then copy Client ID + Secret and paste into the connection dialog. If workspace requires app approval, get admin sign-off. Defaults to Read-only - sending messages needs Full access.
- **Systeme.io** (official MCP, paste key and done): go to systeme.io > Account Settings > "MCP & API keys" > create an MCP key (max 90 days), paste it in. Thansa manages contacts, tags, newsletters, funnels. Defaults to Read-only.
- **Lark** (official MCP, runs local, needs Node.js 18+): messaging, docs, Base tables, wiki, contacts in Lark. Create one Lark app at open.larksuite.com/app, grant permissions (im, docx, bitable, contact...), get App ID + App Secret and paste in. Thansa can only do what the app's permissions allow. Defaults to Read-only - sending messages and file permissions need Full access.

### 3. Connect Webcake Landing / Botcake

- **Webcake Landing**: get JWT from webcake.io > Settings > Access Code > Create API keys, paste in. Thansa can design/edit landing pages by voice. Needs Node.js 18+.
- **Botcake**: open Botcake > Settings > Integrations > Public API > Create API Key; paste Page ID + key. Thansa reads customers, tags, flows and (if Full access) sends flows to customers.

### 4. Connect Google suite (Sheets, Search Console, Calendar, Gmail, Workspace, Tasks, Keep)

Except Search Console, Google services live in one **Google** card in the Connection Library (labeled "6 services"). Click **Choose service** to open the list and select what to connect. If you've already created an OAuth client for one service, subsequent services can click **Reuse key** and skip Google Cloud.

- **Google Sheets**: dump revenue/inventory/debt reports into spreadsheets. Create a service account in Google Cloud (instructions in the connection dialog), share your Drive folder with the service account email, paste the JSON key file contents + folder ID - no extra login needed.
- **Google Search Console**: SEO data for your website (what keywords visitors search for, click-through rates). Also paste service account JSON, add that email as a user in Search Console.
- **Google Calendar** and **Gmail** (2 separate connections, Google's official MCP, remote so works on VPS): Calendar views schedules, finds free slots, creates/edits/deletes events, sets reminders; Gmail reads/searches mail, drafts messages, adds labels. Safety point: Gmail's official server has NO direct-send tool, so Thansa always stops at draft for you to click send yourself. Requires one-time OAuth client setup (console.cloud.google.com > Credentials > OAuth client ID type "Web application", add Redirect URI exactly as shown in the connection dialog, add your email to Test users). Paste Client ID + Secret, click Connect and your browser opens for you to sign in to Google. Use the SAME OAuth client for both Calendar and Gmail (just enable the APIs). Both default to Read-only; upgrade to Draft to create events/draft mail, Full access to delete events. **Must declare full scopes** on Google's Data Access page - the official MCP server won't accept just `calendar`, and finding free slots specifically needs `calendar.events.freebusy`; without it login shows green but checking availability says "permission missing", and deleting/reinstalling doesn't fix it (the connection dialog lists the full scope list to paste).
- **Google Workspace** (Gmail + Calendar + Drive + Docs + Sheets in 1 connection, runs local): needs one-time OAuth client in Google Cloud (~10 min, step-by-step in the dialog), type "Desktop application" so you DON'T declare Redirect URI. **Only works on a machine with a screen**: when Thansa first calls a tool, your machine's browser opens for you to approve - if on VPS, use the two separate connections above instead. Enable APIs for each service you'll use (Gmail, Calendar, Drive, Docs are the basics; add Sheets, Slides, Forms, People, Tasks if needed) - skipping one makes that tool group report an error, others still run. Should fill in the Google email field, leaving blank means each tool call asks which account - annoying. Defaults to Draft: Thansa can draft mail, create events, create docs but NOT auto-send or delete - turn on Full access to confirm the risk. Choose this if you want Drive/Docs/Sheets all together; if you only need Calendar + Gmail, the 2 separate connections above are cleaner (fewer tools, run remote, work on VPS).
- **Google Tasks** (to-do lists, runs local via `uvx`): view lists, add tasks, set deadlines, mark done. Only requests Tasks permission, can't read Gmail or Drive. Uses the same OAuth client as Google Workspace, just enable Google Tasks API for the project and create a "Desktop application" type client. Defaults to **Draft** - at this level Thansa can create, edit, mark done and delete individual tasks; Full access adds permission to create/rename/DELETE entire lists (deleting a list loses all its tasks, no undo). Runs on the same server as Google Workspace so **only works on a machine with a screen**: first time Thansa calls a tool, your machine's browser opens for approval.
- **Google Keep** (notes, runs local via `uvx`): find notes, create notes and task lists, add labels, pin, archive. **Read carefully before connecting**: Keep has no official API, so this connection must use **a master token with FULL ACCOUNT ACCESS** (Gmail, Drive, Photos) - not a limited-scope OAuth like Gmail or Calendar. Thansa only touches notes, but if that token leaks, your whole account is exposed. How to connect: enable 2-step verification, create an App Password (16 characters), paste email + that string in; Thansa exchanges it for a token and DOES NOT save the App Password. Leave `unsafe_mode` blank and Thansa can only edit notes it created; set to `true` and it can edit any note including ones you wrote by hand. Defaults to **Read-only**.

- **Google NotebookLM** (runs local via `uvx`): list notebooks, read sources inside, chat within a notebook, add sources, save notes, create summaries or audio in Studio. **Read carefully before connecting**: NotebookLM has no official API, so this connection borrows **your browser session cookie**, equivalent to being logged into your Google account, not a limited-scope OAuth like Gmail or Calendar. How to connect: on **a personal machine with a browser** (can't do on VPS), run `uvx --from "notebooklm-py[browser]" notebooklm login`, log into Google and open NotebookLM once; then open the `~/.notebooklm/profiles/default/storage_state.json` file that was just created, copy all contents and paste into the dialog box. When session expires, run that command again and paste the new string. Defaults to **Read-only** - Draft level lets chat and create summaries (uses NotebookLM quota), Full access lets delete notebooks and share externally. The library underneath (`notebooklm-py`) is unofficial so Google could change their protocol any time and break this connection.

Tip: if you only need Gmail/Calendar/Drive and you use the Claude Code engine, a faster path is to click Connect right in the Claude app (claude.ai > Settings > Connectors) - Thansa sees them in the **◆ Connections from Claude Code and Codex** section at the bottom.

Similarly with the ChatGPT engine (Codex): MCP you've registered directly in the Codex CLI (`codex mcp add <name> --url https://...` for HTTP servers, or `codex mcp add <name> -- <command>` for stdio servers) loads automatically when ChatGPT runs, and also appears in that same folded section (Codex list sits right below Claude Code list). OAuth-type servers: run `codex mcp login <name>` once in terminal. Adding an OAuth server via Thansa's "Add custom (advanced)" form also registers it in both CLIs (Claude Code and Codex) so switching engines won't lose tools.

### 5. Connect advertising (Meta Ads, Google Ads, TikTok Ads)

All 3 default to **Read-only** - Thansa views reports, analyzes spend/performance but cannot touch campaigns.

- **Meta Ads (Facebook & Instagram)** has TWO connections in the library, pick one:
  - **Meta Ads (official MCP)**: Meta's hosted MCP. Currently in LIMITED BETA: Meta only lets a few approved apps (ChatGPT/Claude/Perplexity assistants) connect and closed self-registration, so Thansa - and other tools - CAN'T self-serve yet. Not your machine's fault; wait for Meta to open more accounts. See details below.
  - **Meta Ads (custom app - Graph API)**: the WORKING path right now (same as Composio/byadsco use) - Thansa calls Meta's Marketing API directly via a Facebook App YOU create. READ-ONLY data, no money spent. Setup instructions in the section below.
- **Google Ads**: official Google MCP, pure read-only (query GAQL data: campaigns, spend, conversions, keywords). Most technical setup in the library - needs four things: developer token (get from your MCC manager account's Google Ads API Center, Explorer level is enough for reading), a Google Cloud project with Google Ads API enabled, one OAuth client ID type **"Web application"**, and add Redirect URI `http://localhost:7777/connect/oauth/callback` (VPS: also add `https://<your-domain>/connect/oauth/callback`). Fill in and click the login button on the UI - your browser opens to grant permission - **Thansa builds the login file itself, NO NEED to install Google Cloud CLI or run any commands**. If you ran `gcloud` before, you can paste the `application_default_credentials.json` file contents into the final box to skip the browser step. Running ads through an agency/MCC, fill in the MCC account ID. Hit "unverified app" warning > Advanced > Continue, because this is your own app.
- **TikTok Ads**: TikTok hasn't opened an official MCP yet (just announced at TikTok World 5/2026), so Thansa uses a community server running the official Marketing API - pure read-only (account, campaigns, reports). Create a Marketing API app at business-api.tiktok.com, get App ID + Secret + Access Token and paste in. When TikTok releases their own MCP it will replace this in the library.

Google Ads and TikTok Ads run locally via the `uv` tool - your Thansa machine needs to install once: `winget install astral-sh.uv` (Windows) or see docs.astral.sh/uv. Specifically **Google Ads also needs Git** on your Thansa machine because `uvx` fetches the server straight from GitHub. Missing Git = the connection dies instantly even if `uv` is there.

#### Connect Meta Ads via Graph API (custom Facebook App) - do once, ~10 min

This is the self-serve path that works right now, no dependency on Meta's MCP beta. You create your own Facebook App, Thansa uses it to read your ad account's data. Because you own the app and keep it in dev mode, you can grant read permission yourself without Meta's review.

**Before you start: check which UI you're using.** Meta is gradually moving app management to a new interface, so two people opening at the same time might see different menus. Look at the **left column** in the app page:

- See a **"Products"** section = **OLD interface**.
- See a **"Use cases"** section and NO "Products" = **NEW interface**.

Both paths do the same thing every step, only difference is exactly where the Facebook Login section opens (step 2). If you search and search and don't see "Products" or "Facebook Login for business" then you're almost certainly on the new interface, not a permissions issue or unverified Business Manager.

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps) > **Create App**. Choose type **Business** (or "Other"), name anything (e.g., "Thansa reads ads").
2. Open the **Facebook Login** section, depends on your interface:
   - **Old version**: **Products > Add Product** > add **Facebook Login** (regular version, NOT "for business"), then click **Set Up**.
   - **New version**: left column **Use cases** > open **"Authenticate and request data from people via Facebook Login"** > **Customize** > **Set Up**. This section usually exists already when you create the app, you don't have to add anything.
3. **Valid OAuth Redirect URIs** box - **different depending where you installed Thansa**:
   - **Installed on personal machine** (address `localhost`): **skip this box, don't fill it.** When the app is in Development mode, Meta **auto-allows** localhost redirects, so this box deliberately doesn't accept localhost. Meta has a note right there: "In development mode, the system will automatically allow http://localhost redirects and you don't need to add them here." Can't fill it = **correct**, not an error, just move on. Just remember Thansa must run at **localhost** not 127.0.0.1.
   - **Installed on VPS / custom domain**: **MUST fill it**, paste your https address and Save, e.g., `https://javis.yourdomain.com/connect/oauth/callback`. Outside localhost, Meta doesn't auto-allow and REQUIRES **https** - skip this and login fails.
   - **Don't type by hand**: the Connection dialog has a box with your machine's address and a **Copy** button - ready-made CORRECT address for your domain - click Copy and paste exactly. Facebook matches **every character** (including `/` at the end), one typo = **"URL blocked"** error.
   - **Also for VPS / custom domain**: go to **App Settings > Basic**, box **App Domains** (App Domains), enter bare domain name, e.g., `javis.yourdomain.com` (NO `https://`, NO `/`), scroll to bottom and click **Save Changes**. The Connection dialog also has a Copy button for this domain. Skip this step and Facebook says **"Can't load URL - the domain of this URL is not in the app's domain list"**.
   - Don't go to "App Settings > Advanced", that's a different place and not related.
4. Keep the app in **Development** mode (toggle top right stays "In development"). Make sure you are **Admin** of the app and of the ad account you want to read - then `ads_read` permission is self-granted, no App Review needed.
5. **Skip "Verify Business" and "App Review"** even if the app's task list suggests them. Those steps only matter if your app serves ANOTHER BUSINESS to access THEIR data; if you're using it yourself, not needed, just adds days of waiting for approval.
6. Go to **App settings > Basic**, copy **App ID** and **App Secret**.
7. Back in Thansa, page **Connections** > **Meta Ads (custom app - Graph API)** card > paste App ID + App Secret > **Connect**. Your browser opens a Facebook page for you to approve; come back to Thansa and hit refresh.

After connecting, ask Thansa in words: "how much did my Facebook ad account spend this week, how did it perform?". Thansa has ready tools to read: list of ad accounts, performance (spend/impressions/clicks/CTR/CPC/reach/conversions) by period, and list of campaigns. All READ-ONLY - Thansa doesn't create/edit campaigns or spend your money.

Token lifespan: Facebook tokens live about 60 days, Thansa auto-renews while in use. If unused for too long and token expires, just click Connect again to log into Facebook one more time.

### 5b. Connect Facebook Page and Monitor Facebook

Two separate connections in the **Social** group in the library, different purposes:

- **Facebook Page (custom app - Graph API)**: manage your own Pages/Fanpages. Read-only: see list of Pages, posts, comments; Full access: post text, photos, photo albums, video, edit posted content, reply and delete comments. Setup is identical to Meta Ads (Graph API) above and **reuses the same Facebook App** - just enable extra Page permissions. When Facebook asks for permissions, TICK the Pages you want. Defaults to **Read-only**; deleting posts is permanent (no trash) so only upgrade to Full access if you really want Thansa posting.
- **Monitor Facebook (Apify)**: monitor public Pages and Groups to find viral posts, returns shares/reactions/comments to filter hot content. Key point: it queries through Apify's service, NOT your personal Facebook account, so no risk of getting locked and runs well 24/7 on VPS. Setup: sign up apify.com, Console > Settings > API & Integrations copy "Personal API token", paste in. Cost is per-query, roughly 2.6 USD per 1000 posts. This connection is **read-only**, no write path. Private groups not supported yet (would need cookies).

### 5c. Other connections in the library

- **Composio** (Apps group): opens over 500 apps (Gmail, Notion, Sheets, GitHub, Linear, Slack...). Go to platform.composio.dev, create one MCP server, copy API key format `ck_...` and paste in. Then to use any app, just say in chat ("connect Notion via Composio"), Composio gives you a login link for that app. **Important note about permissions**: every action of every app runs through ONE shared Composio tool so Thansa can't separate read from write commands. Read-only (default) only finds and describes tools, can't run anything; to let Thansa act you must upgrade to **Full access**, and then Thansa can do EVERY action on all apps you connected, including sending messages and deleting data.
- **Higgsfield** (Creative group): create and edit images/video with AI - generate image, generate video, upscale, expand frame, remove background, cut character. One-tap login, no need to create an app or paste key: click **Connect** then log in to your Higgsfield account and grant permission. Each creation or edit **spends pre-paid credits** in your Higgsfield account. Defaults to Draft (create immediately, block delete and payment); to save credits by having Thansa just view history, downgrade to Read-only.
- **X (Twitter)** (Social group): find and read posts, view public profiles and metrics via X's official MCP. Go to developer.x.com > Developer Portal > Projects & Apps > tab "Keys and tokens" > Generate **Bearer Token**, paste in. This is an App-only token so **read-only** - can't post yet.
- **Substack** (Marketing group): write and publish articles / newsletters by voice. Thansa calls Substack API directly via internal Python so NO NODE NEEDED. Needs three things: your Substack publication address, session token (cookie `substack.sid` from DevTools), and User ID; the **Guide** button in the connection dialog opens a page with an assistant to quickly fetch User ID and publication address. Defaults to **Draft** - only create drafts, can't publish or send to subscribers. To let Thansa PUBLISH for real you must upgrade to Full access; even then, publishing defaults to web-only, only publishes to email subscribers if you explicitly say "email subscribers" - and once emails are sent, can't take back. Session token has full Substack account permission, keep it secret like a password.

### 6. Manage one account (chip)

Click an account chip in the Connected section to open a menu:

- **Test connection**: try it, report number of available tools.
- **Set as default**: when you have many accounts of one service, Thansa prioritizes the default when you don't say which store.
- **Rename** / **Suspend temporarily** / **Delete**.
- **Change permissions**: see Permission section below.
- **Block specific tools**: for power users - type a tool name you want to ban entirely.
- **Tool call log**: see what Thansa called, when, what got blocked.

### 7. Three-level permission (important)

Each account has one permission level, Thansa enforces it HARD:

- **Read-only**: view data only. Creating orders, editing data, sending messages... all blocked. Safest, default for POS.
- **Draft**: can write/edit regular data (notes, products...), STILL BLOCKS financial/order/sending actions.
- **Full access**: REAL actions - create orders, send messages, publish pages. Must tick "I understand the risk"; Zalo has an extra warning.

Smarter than the old version: Thansa understands even Pancake's "2-in-1" tools - same order tool, asking `list orders` passes, `create order` gets blocked if not enough permission.

Background loops are further restricted by loop mode: `suggest` loop only reads, `auto` loop never touches money/orders/sending - regardless of account permission.

### 8. Add custom services outside the library (advanced)

Service not in the library? Click the **Add custom (advanced)** card - technical form like the old version (URL/command + headers/env, supports HTTP, SSE, stdio). OAuth-standard MCP services: Thansa auto-opens the login page and keeps the token, works on VPS too.

### 9. "Only use Thansa connections" mode (strict)

Tick this box in the Connected section if you want Thansa to ONLY use connections listed here, ignoring MCP pre-installed in Claude Code on your machine - tight control, avoid accidentally calling a tool from your Claude account. Note: this box applies to Claude Code engine (strict flag of Claude CLI); Codex's native MCP pool is managed separately by the `codex` command - to remove an original server from ChatGPT, use `codex mcp remove <name>`.

## Reading data

No change from before: ask directly in chat ("how much did I sell today, compared to yesterday?"), Thansa calls the right source, replies following the formula data + comparison + cause + suggestion, and auto-pushes 3-6 metrics to the metrics panel on Thansa's left column. Closed periods cache in `05 - Data Cache/` of your brain. Multiple stores: say the store name clearly, no name = Thansa uses the default account.

## Tips

- Name accounts by store for easy reference in chat ("Kim Khí store" vs "store 2").
- Leave POS at Read-only if you just need reports - no risk of Thansa accidentally creating an order.
- First message after boot can be slow with local-run connections (Zalo, Webcake) because tools need startup - later calls are fast because Thansa keeps the connection alive.
- Tool call log is the first place to check if Thansa "does something odd".

## Common issues

- **Facebook says "URL blocked" at login**: redirect URI in your Facebook app doesn't match. Open Thansa's Connection dialog, click **Copy** on the redirect address box and paste EXACTLY into the "Valid OAuth Redirect URIs" box (Facebook Login > Settings), Save. Don't type - Facebook matches every character.
- **Facebook says "Can't load URL - the domain of this URL is not in the app's domain list"**: missing App Domains. Go to App Settings > Basic > "App Domains" box, paste bare domain (no https, no /) - Connection dialog has a Copy button - then click "Save Changes" at bottom.
- **Pasting key says "Key incorrect or missing permission"**: create a new API key in the service, paste again. For Pancake check the key belongs to the right store.
- **Zalo says "Need Node.js 20+"**: install Node.js from nodejs.org and try again.
- **Google Ads / TikTok Ads can't connect**: check machine has `uv` installed (`winget install astral-sh.uv`). **Google Ads also needs Git** because `uvx` pulls the server from GitHub - missing Git = connection dies even if `uv` is there. First connection takes time to download packages - click Test again after 1-2 minutes.
- **Meta Ads (official MCP) says "self-serve not enabled / DCR"**: correct - Meta's hosted MCP is in beta, only accepts apps pre-approved by Meta. To read data now, use **Meta Ads (custom app - Graph API)** above.
- **Meta Ads (Graph API) says "Facebook rejected / redirect_uri"**: check based on where you installed. On **personal machine**: (1) app is in Development mode - that's what makes localhost accepted, leaving Development breaks it immediately; (2) Thansa opened at `localhost` not 127.0.0.1; (3) App ID + App Secret pasted right. On **VPS/domain**: check Valid OAuth Redirect URIs filled with your **https** address, matches every character including `/connect/oauth/callback` path.
- **Can't fill localhost into "Valid OAuth Redirect URIs"**: correct, not an error. App in Development mode auto-allows localhost and blocks manual adding, note says so next to the box. Skip and move on; only VPS/domain need to fill.
- **Table shows "Invalid Scopes: pages_show_list, pages_read_engagement, ..." (or ads_read, business_management)**: **just click OK and move on.** This is Meta's developer-only warning and does NOT block login - the message itself says "This message is only shown to developers". While the app is in Development and you're its Admin, Facebook still grants full permission, so in most cases connecting works right away. Quick check: after connecting, ask Thansa "list my Pages"; if you see all Pages, you're good, nothing else needed. 

  **Only if** connecting works but Thansa sees no Pages (or no ad accounts) should you add permissions to the app. In the **new interface**, permissions lock by use case: an app created via the "Authenticate and request data from people" use case only gets `email` and `public_profile`. To add:
  - **Page permissions**: **Add use case** > pick **"Manage everything on your Pages"** > **Customize** > **Permissions** tab > click Add for `pages_read_engagement`, `pages_manage_posts`, `pages_manage_engagement`. Permissions `pages_show_list` and `business_management` usually already exist in this use case.
  - **Ad permissions**: **Add use case** > pick the relevant ad use case (Marketing API) > **Customize** > **Permissions** tab > Add `ads_read` and `business_management`.
  - **Old interface**: go to **Products > Add Product**, add **Marketing API** (for ads) or **Facebook Login** regular version (for Pages); in Development mode you self-grant these permissions without App Review.
  - Then come back to Thansa and click Connect again.
- **Want Thansa to manage ONE MORE Page (fanpage)**: click **Connect again** on the Facebook Page card. Facebook shows the **"Choose content you allow"** screen again - tick the new Page while KEEPING the old ones checked (unchecking a Page makes Thansa lose access to it), then Continue. No need to delete and re-connect from scratch. If Facebook skips straight to "Continue as [your name]" instead of showing the Page picker, check Thansa has updated to version 0.9.249+; older version missed a parameter forcing Facebook to ask again, so the Page selection screen got skipped.
- **Meta Ads (Graph API) says "no ad accounts found"**: token missing `ads_read` permission or the logged-in Facebook account isn't admin of any ad account - check your role in Business/Ads Manager.
- **In the app don't see "Products" menu, or don't see "Facebook Login for business"**: you're on the **NEW interface** where the Products menu is replaced by **Use cases**. Click left column **Use cases > Customize > Settings** to find the redirect URIs box. NOT because Business Manager is unverified or permissions missing - reread step 2 in the guide above.
- **Don't see "Facebook Login for business" even finding the right spot**: it only shows when the app type is **Business** ("Business" type), and once created the type can't change. But Thansa's flow uses the regular **Facebook Login** version, so you don't need the "for business" one.
- **QR code expired**: click again to get a fresh QR (Zalo QR ~3 min lifespan).
- **Tool blocked with "currently at restricted permission level"**: correct design - raise the account's permission in the chip menu if you want Thansa to do that task.
- **After updating from old version**: old MCP servers auto-convert to accounts in the Connections page (backup at `mcp_servers.v1.bak.json`), no need to set up again.
- **Want to go back to old system** (each server one entry, no hub): set `"mcp": {"hub": false}` in `server/settings.json` then restart.

## Related

- [Models & engine](10-models-va-engine.md) - which brain uses what, change model where.
- [Zalo Agent MCP](12-zalo.md) - QR login, seven tools and permission setup.
- [Chat & Voice](02-tro-chuyen-va-giong-noi.md) - ask metrics by voice.
- [Usage: tokens & cost](23-muc-dung-token.md) - see tool calling burn rate.
