# Recommendation: put usjunkcars.si behind a CDN (owner decision)

Status: recommendation only. Nothing in DNS, nameservers or Cloudflare has been changed. Prepared 2026-10-18.

## Why

Every visitor today fetches every byte from one Hostinger VPS (69.62.69.84) through Nginx and the Node server. A visitor in California waits for each request to travel there and back, and the VPS also serves 13 other websites. A CDN keeps copies of the site's static files (CSS, scripts, fonts, images, the poster) on servers close to each visitor, so pages start faster and the VPS does less work. Cloudflare's free plan is the usual choice for a site this size.

What it would improve: time to first byte for visitors far from the VPS, and repeat-visit speed for static files. It does not fix render-blocking CSS, image weight or script cost; that work is done in the app.

## Recommended setup

1. **Cloudflare free plan for the website** (HTML passes through to the VPS; static files are cached at the edge).
2. **The launch video files are not cached by the Cloudflare CDN.** Cloudflare's terms limit using the CDN to serve video unless the video is hosted on a Cloudflare product such as Stream or R2 ([Cloudflare, May 2023](https://blog.cloudflare.com/updated-tos/)). Choose one of these:
   - **A. Keep video on the VPS (simplest).** Add a Cache Rule "bypass cache" for `/video/*`. The files still pass through Cloudflare but are served from the VPS. Read the live Service-Specific Terms (CDN section) before choosing this, because proxied but uncached video may still count as CDN use.
   - **B. Move the video files to Cloudflare R2 (cleanest).** Upload them to an R2 bucket on a subdomain such as `media.usjunkcars.si`. The free tier includes 10 GB of storage and has no egress fees, and the video files total about 20 MB. The app then points at that subdomain (a small code change, reviewed like any other).

## Exact steps (when you decide to go ahead)

Do these at a quiet time; allow about an hour, plus up to 24 hours for the nameserver change to spread.

1. **Back up the current DNS.** In Hostinger hPanel → Domains → usjunkcars.si → DNS / Nameservers, take a screenshot or export of every record (A, CNAME, MX, TXT including SPF/DKIM/DMARC, and any Google verification records).
2. **Create the Cloudflare account and add the site.** Go to dash.cloudflare.com, choose Add a domain, enter `usjunkcars.si` and pick the Free plan. Cloudflare scans the existing records.
3. **Check every record against your backup.** Fix anything missing, especially MX and TXT (email and Google Search Console verification). Set:
   - `usjunkcars.si` A `69.62.69.84`: **Proxied** (orange cloud)
   - `www` CNAME `usjunkcars.si`: Proxied
   - `dev` CNAME `usjunkcars.si`: Proxied. Dev keeps its password prompt and `no-store`, so Cloudflare will not cache it.
   - MX and mail-related records: **DNS only** (grey cloud)
4. **SSL/TLS → Overview: set "Full (strict)".** Never "Flexible": it causes redirect loops with our Nginx HTTPS redirect.
5. **Certificate renewal (important).** Certbot renews over plain HTTP at `/.well-known/acme-challenge/`. With Cloudflare in front, this still works as long as **"Always Use HTTPS" stays off** (Nginx already redirects to HTTPS, and it exempts the challenge path). If you would rather not depend on that, install a free Cloudflare Origin Certificate (15-year validity) on the VPS instead of Let's Encrypt; that is a server change to plan separately.
6. **Speed settings:** turn on Brotli, HTTP/3 and Early Hints. Leave **Rocket Loader off** (it rewrites scripts and can break Google Tag Manager and the Peddle offer form). Do not enable "Cache Everything" for HTML: lead pages and the future dashboard must never be cached at the edge.
7. **Cache Rules:** cache `/_next/static/*`, `/frontend/fonts/*`, `/css/*` and `/images/*` by honouring the origin's Cache-Control (the default). Add the `/video/*` bypass rule (option A), or skip it if the video has moved to R2 (option B).
8. **Change nameservers.** In Hostinger, replace `aster.dns-parking.com` / `helios.dns-parking.com` with the two nameservers Cloudflare shows you. Wait for Cloudflare to report the site **Active**.
9. **Verify:** `https://usjunkcars.si` loads with a valid certificate; `www` redirects to the apex; `dev.usjunkcars.si` still asks for the password; response headers show `cf-cache-status: HIT` for CSS/fonts on a second load; email still arrives; Google Search Console is still verified.
10. **Real visitor IPs:** after the switch, Nginx sees Cloudflare's addresses, not visitors'. Ask the developer to add Nginx `set_real_ip_from` for Cloudflare's published ranges with `real_ip_header CF-Connecting-IP`, so logs, rate limits and lead fraud checks see the real visitor. Until then, lead-related IP data is wrong.

## Risks and how to undo

| Risk | Impact | Mitigation |
|---|---|---|
| A DNS record is missed when moving | Email or verification breaks | Back up first (step 1); compare record by record (step 3) |
| Wrong SSL mode | Site loops or shows errors | Use Full (strict) only |
| Certificate renewal blocked | HTTPS expires in up to 90 days | Keep "Always Use HTTPS" off, or use an Origin Certificate; check `certbot renew --dry-run` after the switch |
| Visitor IPs become Cloudflare IPs | Logs and future rate limits are wrong | Step 10, before relying on IP-based checks |
| Video served through the CDN against Cloudflare's terms | Cloudflare could ask us to stop | Option A bypass (after reading the live terms) or option B R2 |
| Cloudflare outage | Site unreachable while it lasts | Rare; switch DNS back to Hostinger if prolonged |
| Hostinger DNS no longer used | All future DNS edits happen in Cloudflare | Note this for whoever manages the domain |

**Undo:** set the nameservers in Hostinger back to `aster.dns-parking.com` and `helios.dns-parking.com`. The Hostinger DNS zone is kept, so the old setup returns once the change spreads (minutes to hours).

## Decision needed

- Go ahead with Cloudflare Free? (yes / not now)
- Video: option A (bypass on the VPS) or option B (R2 subdomain)?

The developer cannot do steps 2 and 8: they need your Cloudflare and Hostinger accounts.
