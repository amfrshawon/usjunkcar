# Analytics, tracking and search consoles

Set up 2026-10-18 in the owner's Google (amfr.shawon@gmail.com) and Microsoft accounts. None of these IDs are secrets.

| Service | Account / property | ID |
|---|---|---|
| Google Tag Manager | Account `USJunkCars`, container `usjunkcars.si` (Web) | `GTM-TNC9P49R` |
| Google Analytics 4 | Account `USJunkCars` (412393626), property `usjunkcars.si` (559459116), stream `usjunkcars.si web` | `G-0XGJCXMRV5` |
| Microsoft Clarity | Project `usjunkcars.si` | `yzil4ejd4f` |
| Google Search Console | Domain property `usjunkcars.si`, verified by DNS TXT | sitemap submitted, 7 pages |
| Bing Webmaster Tools | `https://usjunkcars.si/`, verified by DNS CNAME | sitemap submitted |

## How it fits together
- The site loads only GTM (`apps/web/src/server/config.ts` → `gtmBootstrap`, plus the `<noscript>` frame in `layout.tsx`). It loads in every environment so GTM Preview works on localhost and dev.
- Every tag in the container fires only when **Page Hostname equals `usjunkcars.si`**, so local and dev traffic never reaches GA4 or Clarity.
- GA4: Google tag with `allow_google_signals=false` and `allow_ad_personalization_signals=false`, matching the Privacy Policy. Event retention is 14 months; `cta_location`, `cta_text` and `zip_entered` are registered as event-scoped custom dimensions; enhanced measurement is on (page views, scrolls, outbound clicks, site search, video, file downloads).
- Clarity: Custom HTML tag on page view. It masks typed text by default.
- The container configuration is versioned at `infra/gtm/container-v1.json`. It is importable through GTM Admin → Import Container (Overwrite).

## Site events (`apps/web/public/analytics.js`)
Pushed to `dataLayer` and sent to GA4 by the tag `GA4 - Event - site actions`:

| Event | When | Parameters |
|---|---|---|
| `offer_open` | Any instant-offer control (`[data-peddle-offer]`) | `cta_location`, `cta_text` |
| `phone_click` | Any `tel:` link that is not an offer control | `cta_location`, `cta_text` |
| `email_click` | Any `mailto:` link | `cta_location`, `cta_text` |
| `zip_submit` | Hero ZIP search submitted | `cta_location`, `zip_entered` (true/false; the ZIP itself is never sent) |
| `faq_open` | An FAQ answer is expanded | `cta_location`, `cta_text` (the question) |

`cta_location` is `header`, `footer`, or the heading of the section the control sits in.

## Still to do (manual)
1. After the first live events arrive in GA4, go to Admin → Events and star `offer_open` and `phone_click` as **key events**. GA4 only lists an event after it has been received.
2. Optional: link GA4 to Search Console (GA4 Admin → Product links) and Clarity to GA4 (Clarity Settings → Setup → Google Analytics).
3. Offer completions happen inside Peddle's cross-origin form and cannot be seen by this site. Track them from Peddle's own reporting.

## DNS records added (Hostinger)
- `TXT @ "google-site-verification=_XPJ55TtfZFWkIV37rXoFRRiSEgnWgpXbTxMgGiorMU"`: keeps Search Console verified. Do not remove.
- `CNAME f22ad0575a93b157564d0049600ec0af → verify.bing.com.`: keeps Bing verified. Do not remove.
