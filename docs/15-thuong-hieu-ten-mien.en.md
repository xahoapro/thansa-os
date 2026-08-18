# Brand & Custom Domain

*[Tiếng Việt](15-thuong-hieu-ten-mien.md) · **English***

This page guides two things: change Thansa's logo/avatar to your own image, and point a custom domain (e.g., `javis.yourname.com`) to Thansa to run over HTTPS. These operations are in **Settings → Voice, Brand & Access**.

## What This Feature Is

- **Avatar (logo/avatar):** replace the default THANSA OS image with your own. New image shows right away at top-left corner, in sidebar, on login screen, in welcome window, and becomes the browser tab icon (favicon).
- **Custom Domain (HTTPS):** instead of opening Thansa with an IP address and port (like `http://12.34.56.78:7777`), you use an easy-to-remember domain with HTTPS security. Thansa auto-issues HTTPS certificates (On-Demand TLS via Caddy), and has a **Enable SSL** button to proactively request certificates now instead of waiting.

Important note right from the start: the **Custom Domain** section only works when you deploy Thansa via Docker on a VPS and opened ports 80/443. If you run Thansa on personal machine, the **Change Logo** part still works normally, but the custom domain part won't get HTTPS. See deployment details in [Environment Configuration](16-cau-hinh-env.md) and `DEPLOY.md` in the project folder.

## Where to Access in Thansa

Both features are in **Settings → Voice, Brand & Access**. If the group is collapsed, click title to open. Inside has two cards:

- **AVATAR** field: has preview image, **Upload Image** button and **Restore Default** button.
- **DOMAIN & SSL** field: has input field (blank shows "e.g.: javis.yourname.com"), **Save & Check** button, two badges showing DNS and SSL status, two buttons **Enable SSL** and **Check Again**, plus a three-step wizard that changes content based on right VPS/Hostinger environment.

Each time you open Settings, Thansa auto-reloads current values, checks DNS/HTTPS, and shows correct next steps.

## Change Logo/Avatar (Step by Step)

1. Open **Settings → Voice, Brand & Access**, find the **AVATAR** field.
2. Click **Upload Image** button. File picker from your machine appears.
3. Pick an image file. Formats accepted: PNG, JPG, WEBP, GIF. Maximum 5MB.
4. After picking, Thansa shows **Uploading…** then **Image updated ✓** when done. New image replaces everywhere (top corner, sidebar, login, preview area) without reloading page.

Browser tab icon (favicon) changes slower by one beat: Thansa serves it with 5-minute cache, and browser caches favicon heavily. To see it immediately, open tab again or reload page clearing cache.

### Restore Default Image

1. In the **AVATAR** field, click **Restore Default** button.
2. Thansa shows **Restoring…** then **Back to default image.** Logo returns to system's original image.

### Image Status Messages You Might See

| Message | Meaning |
|---|---|
| Using custom image. | You uploaded your own image and Thansa is using it. |
| Using default image. | Haven't uploaded custom, or restored to default. |
| Uploading… | Sending image to server. |
| Image updated ✓ | New image received and applied. |
| Restoring… | Removing custom image. |
| Back to default image. | Removed, using original again. |
| Upload failed | Server rejected file (wrong format, too large, or empty). Specific reason shown instead of this line when server provides it. |
| Network error uploading | Lost connection mid-transfer, try again. |
| Can't restore | Failed to remove custom image, try again. |

## Point Custom Domain and Enable HTTPS (Step by Step)

This section assumes you deployed Thansa via Docker on VPS, enabled Caddy (On-Demand TLS), and opened ports 80/443. If not, do the deploy part first per `DEPLOY.md`.

### Step A: Enter and Save Domain

1. Open **Settings → Voice, Brand & Access**, find the **DOMAIN & SSL** field.
2. Enter the domain (or subdomain) you want into the field, e.g., `javis.yourname.com`. No need to type `https://`; if you do, Thansa strips it.
3. Click **Save & Check** button (or press Enter in field). Thansa shows **Saving and checking…**, saves domain, then auto-runs DNS/SSL check and draws a three-step wizard right on UI.
4. If domain format is wrong, Thansa says: **Invalid domain (e.g.: javis.yourname.com)**. Fix and save again.

To **delete** domain: clear the field then click **Save & Check**. Thansa says **Domain deleted.** and hides the instruction section.

### Step B: Create DNS Record Per Instructions

After saving (or clicking **Check Again**), wizard shows step **2. Point DNS to VPS** with the record to create and **Copy Record** button. Record shown as one compact line `A · <domain> · <server IP>`:

1. Go to your domain provider's management page (where you bought the domain) and create a record:

   | Field | Value |
   |---|---|
   | Type | A |
   | Name/Host | domain you just entered, e.g., `javis.yourname.com` |
   | Value/Points to | your VPS server's IP address (Thansa auto-found and filled this in the wizard) |

2. Wait for DNS to propagate (few minutes to few hours), click **Check Again**. When DNS is correct, step 2 turns to checkmark and description changes to "A record correctly points to server IP."

### Step C: Click Enable SSL to Request Certificate

When step 2 is checkmarked, wizard shows step **3. Enable HTTPS** with line "Once DNS is correct, click Enable SSL for Thansa to request certificate."

1. Click **Enable SSL** button. Thansa shows **Enabling SSL and requesting certificate… (may take ~10 seconds)**.
2. Server logs the intent to enable SSL then opens `https://<domain>/health` from itself. This request forces Caddy to go request certificate on first run, instead of you manually opening a browser.
3. Done, Thansa re-checks and updates badge. When certificate is live, status line says **HTTPS running for `<domain>`.**, button changes to **Re-activate**, and wizard shows extra **Open https://`<domain>` ↗** link.
4. If not yet, Thansa clearly states reason and adds sentence **"Running on VPS: docker compose -f docker-compose.yml -f docker-compose.https.yml up -d"** when you're running Docker version but haven't enabled HTTPS layer.

**Check Again** button usable anytime: it just reads status (shows **Checking…** then redraws badge), doesn't touch certificates.

On Hostinger, **Enable SSL** button is hidden, because Traefik of hPanel is the one issuing certificates. See Hostinger section below.

## Quick Reference of Buttons and Status

Two badges sit right under domain field:

| DNS Badge | Means |
|---|---|
| DNS: checking | No result yet (just opened page) |
| DNS: correct | A record matches server IP |
| DNS: wrong IP (`<ip>`) | Has a record but points to different IP, actual IP shown in parentheses |
| DNS: not pointing | No record found for domain |

| SSL Badge | Means |
|---|---|
| SSL: checking | No result yet |
| SSL: enabled | HTTPS running for real on domain |
| SSL: via Hostinger | Deployed on Hostinger, certificate managed by hPanel's Traefik |
| SSL: waiting | You enabled SSL but certificate not yet live |
| SSL: disabled | Haven't enabled SSL for this domain |

| Button | What happens |
|---|---|
| **Save & Check** | Save domain into Thansa then auto-run DNS/SSL check |
| **Enable SSL** | Log intent to enable SSL and pro-actively force Caddy to request cert now |
| **Re-activate** | Same button as above, name changes when HTTPS already running; click to request cert again |
| **Check Again** | Just read DNS/SSL status, don't touch certificates |
| **Copy Record** | Copy line `A · <domain> · <IP>` to clipboard (changes to "Copied ✓" for ~1 second) |
| **Copy Variable** | Only in Hostinger wizard: copy line `DOMAIN_NAME=<domain>` |

Status line at bottom of card can be:

| Status Line | Meaning | What to do |
|---|---|---|
| No domain set. | Haven't saved any domain. | Enter domain then click Save & Check. |
| Saving and checking… / Checking… | Running, wait. | Nothing to do. |
| Saved. Checking DNS/SSL… | Recorded domain, checking DNS. | Wait for result. |
| Domain deleted. | You just saved empty field. | Nothing to do. |
| HTTPS running for `<domain>`. | All done. | Nothing more needed. |
| You're accessing via HTTPS | You're visiting this exact domain via HTTPS. | Done. |
| Certificate not valid - DNS not correct yet or certificate not issued | Connected but certificate not usable. | Check DNS badge; if DNS correct wait more then click Enable SSL again. |
| Can't reach port 443 - Caddy/HTTPS not running, or ports 80/443 occupied by other proxy | Nobody answers on port 443. | Enable HTTPS layer per Thansa's suggestion, and check if ports 80/443 already taken by other service. |
| Saved in Thansa; still need to set DOMAIN_NAME and Redeploy on Hostinger. | Hostinger: Traefik route doesn't match domain. | Do step 3 of Hostinger wizard. |
| Please enter and save domain first. | Clicked Enable SSL with empty domain field. | Enter domain then save. |
| Invalid domain (e.g.: javis.yourname.com) | Input doesn't match domain format. | Remove spaces, remove path after domain, type as `name.yourname.com`. |
| Enable SSL failed | Server rejected enabling. | Read extra reason line that came with it. |
| Can't check (network error). | Browser can't reach server. | Try again in a few minutes. |
| Network error saving / Network error enabling SSL | Lost connection mid-operation. | Try again. |

## About Caddy and On-Demand TLS (Good to Know)

- Thansa uses Caddy to auto-request and auto-renew HTTPS certificates (Let's Encrypt) via On-Demand TLS. You don't install certificates yourself.
- To prevent abuse, before issuing a certificate Caddy asks Thansa (via internal gate `/tls-check`) and only issues for domains you entered in the app. Strangers pointing DNS anywhere to your IP can't force server to request certs for random domains.
- When changing or deleting domain on VPS using Caddy, you just edit **DOMAIN & SSL** field then click **Save & Check**, then **Enable SSL** for new domain. Hostinger needs Redeploy when changing Traefik route.
- Enabling Caddy (running `docker compose ... up -d` with HTTPS config) and opening ports 80/443 is infrastructure deploy, outside this interface. See detailed deploy guide in project's `DEPLOY.md`.
- When visiting Thansa via correct custom domain over HTTPS, server auto-marks login cookie as `secure`, no need to set `JAVIS_SECURE_COOKIE` manually. See [Security & Account](14-bao-mat-tai-khoan.md).

## If You Deploy on Hostinger (Different Process)

Hostinger VPS pre-installed reverse proxy Traefik managing SSL, and ports 80/443 already occupied by Traefik. Thansa still lets you enter domain, check DNS and pre-create variables needed right on UI, but container can't edit Traefik's routes in hPanel. So **Enable SSL** button is hidden, SSL badge says **SSL: via Hostinger**, and step 3 of wizard becomes **3. Activate HTTPS route on Hostinger**:

1. Point DNS: `A  <your domain> → <Hostinger VPS IP>`.
2. Deploy using compose with Hostinger's Traefik tag: `docker-compose.hostinger.yml` (Docker Manager → Compose → URL).
3. Click **Copy Variable** in wizard, set `DOMAIN_NAME=<your domain>` in Docker Manager then click **Redeploy**. Wizard always shows current Traefik route so you can compare.
4. Open `https://<domain>`; Traefik auto-requests certificate on first access. No more accessing via `:7777`.

If you try clicking Enable SSL on Hostinger (e.g., via API), Thansa refuses and says clearly: Hostinger manages HTTPS via Traefik, set `DOMAIN_NAME` in Docker Manager then Redeploy.

After Redeploy, go back to Settings and click **Check Again**. Detailed steps and troubleshooting see "Domain + HTTPS on Hostinger" section in `DEPLOY.md`; both doc links also sit right under domain card.

## Tips

- Logo should be square (1:1 ratio) so it doesn't get warped, since Thansa displays logo in a square rounded box.
- After uploading new image and some places still show old one, wait ~1 minute or reload page; system has short image cache (favicon longer, ~5 minutes).
- If you don't have custom domain but still want access from afar with HTTPS, can use alternative (e.g., Cloudflare Tunnel) described in `DEPLOY.md`.
- Use **A** record type (point via IPv4). Don't use CNAME for this domain unless you fully understand consequences.
- Don't click **Enable SSL** repeatedly when DNS not yet correct. Each click makes Thansa force Caddy to request cert, requesting too many times will hit Let's Encrypt's rate limits.

## Common Issues

- **Click Save says "Invalid domain":** check spelling, no spaces, no path after domain. Correct format is `name.yourname.com`.
- **Created A record but badge still says "DNS: not pointing":** DNS takes time to propagate. Wait more minutes to hours then click **Check Again**.
- **Badge says "DNS: wrong IP (...)":** IP in A record differs from your server's IP. Copy the correct IP Thansa shows in step 2 of wizard and update the A record.
- **DNS correct but click Enable SSL says "Can't reach port 443":** HTTPS layer not running. On Docker VPS, run the exact command Thansa suggests (`docker compose -f docker-compose.yml -f docker-compose.https.yml up -d`) then try again, and verify ports 80/443 open and not taken by other proxy.
- **Click Enable SSL says "Certificate not valid":** usually DNS just became correct, Caddy not finished issuing yet. Wait a minute or two then try again.
- **Don't see Enable SSL button:** you're on Hostinger. Thansa hides button because Traefik of hPanel issues certs; follow Hostinger wizard above.
- **Upload image says format or size error:** only use PNG, JPG, WEBP or GIF, under 5MB.
- **Domain field not working as expected on personal machine:** this is a feature for Docker deploy on VPS with ports 80/443. On personal machine, domain/HTTPS part won't activate.

## Related

- [Start & First Setup](01-bat-dau-thiet-lap.md)
- [Security & Account](14-bao-mat-tai-khoan.md)
- [Environment Configuration](16-cau-hinh-env.md)
- [Troubleshoot & FAQ](17-khac-phuc-su-co.md)
