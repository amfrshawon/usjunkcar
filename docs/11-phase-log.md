# Phase log

## 2026-10-15 · P1 foundation + marketing pages on Next.js (local `dev`)

- **Stack:** Next.js 16.3.8 (App Router, TypeScript 5.9.3, React 19.2.9), pnpm 10.34.7 workspace with `node-linker=hoisted` so standalone releases contain no symlinks. Node 24.22.0 pinned for the VPS.
- **Routes:** `/`, `/locations/`, `/about/`, `/faq/`, `/contact/`, `/privacy-policy/`, plus `/sitemap.xml`, `/robots.txt`, `/api/v1/health` and a styled 404.
- **Content:** `scripts/extract-web-content.py` extracts the reviewed static pages into `content/` (shell fragments, page bodies, `publication.json` registry). The static pages at the repository root remain the design reference and are no longer deployed.
- **Publication gate:** every route is `review` (dev/local only). Production renders only published routes with an approval record; everything else is a real 404, including encoded and `?preview=true` variants.
- **Release:** `ci:check` (registry validation, typecheck, development and production builds, 8 site tests each), `ci:package` (environment-matched standalone archive), `ci:predeploy` (publication gate; fails if migrations appear before a runner exists).
- **Config:** `staticDevPreview` off, `dev.enabled` on, `main.enabled` off.
- **Tests:** `pnpm run ci:check` passed (16/16); infrastructure unittest and preview tests passed; CI-mode package passed the receiver's archive and manifest validation.
- **Not done (later phases):** Supabase database and migrations, quote intake, staff dashboard, chatbot adapter, Tailwind design system, moving the static fixture into `reference/`, replacing reference icons/photos, Peddle live publisher ID, owner route approvals.

## 2026-10-18 · Homepage load speed, mobile first (local `dev`, not pushed)

- **Why:** Lighthouse mobile on https://usjunkcars.si/ (2026-10-18, before the video release) scored 70 (FCP 3.3 s, LCP 5.2 s). The LCP element is the hero board background. First paint was waiting on ~400 KiB: a 110 KiB HTML document (half of it React's flight copy of the same fragments), ~140 KiB of Next.js client JavaScript, six render-blocking stylesheets (289 KiB raw, 89 % unused), five 30 KiB font files, a 66 KiB truck image picked at 1312 px for a 441 px slot, a 29 KiB logo SVG, the video poster, and GTM/Peddle on `load`.
- **Rendering:** content pages (`/`, `/about/`, `/contact/`, `/faq/`, `/locations/`, `/privacy-policy/`, `/terms-and-conditions/`) are now static route handlers (`app/**/route.ts`) that return complete HTML from `src/server/document.ts` instead of React pages. They have no client components, so the flight payload and client runtime did nothing. Head tags, canonical/OG/Twitter metadata, robots, JSON-LD, GTM noscript, shell fragments and scripts are the same as before. Non-public routes still return 404 with the branded 404 page. `app/layout.tsx` + `not-found.tsx` remain for unknown URLs.
- **CSS:** `scripts/build-css.mjs` (runs before `next build`/`next dev`) uses PurgeCSS 7.0.2 over all content, shells, public scripts, fragments and TSX to build `content/generated/site.css` (gitignored, 301 → 75 KiB raw, ~13 KiB gzip), inlined in every page. Attribute selectors on every attribute the stylesheets use are always kept (the first pass had dropped the `mailto:`/`tel:` link styling on the legal pages). The six source stylesheets stay in `public/` as the editable originals.
- **Fonts:** Manrope woff2 files subset to Latin (U+0000-00FF plus common punctuation, €, ™, arrows) with all tables, hinting and layout features kept, 152 → 73 KiB. Command: `pyftsubset <orig>.woff2 --flavor=woff2 --layout-features='*' --glyph-names --legacy-kern --notdef-outline --name-IDs='*' --name-languages='*' --hinting --hinting-tables='*' --drop-tables= --no-prune-unicode-ranges --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2190-2199,U+2212,U+2215,U+FEFF,U+FFFD"` (fontTools 4.60.2; originals are in git history). Every character in the site content is covered; emoji were never in Manrope. A leaner subset (default tables) shifted text by a sub-pixel at 1× DPR and was rejected.
- **Third parties:** GTM (`gtmBootstrap`) and Peddle (`peddleBootstrap`) set up `dataLayer`/the Peddle stub immediately but fetch their scripts 0.5 s after `load` + idle, or on the first pointerdown/keydown/scroll. Queued events and `boot`/`open`/`hydrate` calls are processed when they arrive. `peddle-offer.js` now uses one delegated click listener so lazily added controls open the offer too.
- **Homepage assets:** hero board preloaded at high priority and served as the existing WebP (16 → 10 KiB; same artwork, mean pixel difference 1.5/255, as already used for the CTA banner); hero truck `srcset` uses width descriptors and measured `sizes` (870w instead of 1312w on a 412 px, 1.75× phone); `logo-stacked.svg` optimised with SVGO 3.3.2 (precision 3, title/viewBox kept; 29 → 15 KiB gzip); the video poster is attached by `video-player.js` when the card is within 1.5 screens (a `<noscript>` style keeps it for no-JS); the US map SVG (103 KiB, 33 KiB gzip) moved to `public/fragments/us-map.html` and is fetched by `clone.js` near the viewport into its fixed-height box; 37 unreferenced symbols removed from `content/shell/sprite.svg` (26 → 4.5 KiB).
- **Caching (`next.config.ts`):** versioned scripts (`/*.js?v=`) and `/frontend/fonts/` are `public, max-age=31536000, immutable` (rename a font file when it changes); `/images/` and `/video/` are `public, max-age=604800, stale-while-revalidate=86400`. dev nginx still overrides with `private, no-store`.
- **Compression note:** Next 16.3.8's server does not gzip route-handler responses. Production is unaffected because the VPS nginx already gzips (verified: `/sitemap.xml`, also a route handler, is gzipped on usjunkcars.si but not by Next locally). Local measurements therefore ran both builds behind a small gzip proxy that mimics nginx.
- **Measurements** (Lighthouse 12.8.2, mobile preset with simulated throttling, local production builds behind the gzip proxy, 5 runs each):

  | | Score | FCP | LCP | Speed Index | TBT | CLS | Transfer |
  |---|---|---|---|---|---|---|---|
  | Before (`2656795`) | 77–78 | 3.0–3.2 s | 4.7 s | 3.0–3.2 s | 0–20 ms | 0.001 | ~825 KiB |
  | After | 97–98 | 1.4–1.5 s | 2.3–2.4 s | 1.4–1.5 s | 0–20 ms | 0.001 | ~356 KiB |

  Desktop preset, one run each: 99 → 100 (LCP 0.8 → 0.5 s). Real-world PSI numbers on the VPS will differ (TLS, network); re-run PSI after the release.
- **Verification:**
  - **Rendering:** full-page screenshots of all 7 content pages + 404 at 412 px/1.75× and 1440 px, plus a DOM comparison of every element's box and computed styles. The only differences are the intended ones (WebP hero, `is-near` class, truck resolution); mobile inner pages are pixel-identical.
  - **Behaviour** (headless Chrome, production build): GTM loads ~0.55 s after `load` and fires `gtm.js/dom/load`; Peddle loads ~0.6 s after `load`; a map state click opens the Peddle iframe and logs `offer_open`; the map loads with 51 labelled state links; the video poster, preview and full-screen player work. No page errors.
  - **CI:** `pnpm run ci:check` passed, including a new site test asserting content pages carry no React payload or stylesheet links, inline the site CSS, and preload the hero.
- **Not done / open:**
  - The locations page still inlines its own map SVG.
  - The lazy-loaded waving-flag SVG (`usa-flag-waving.svg`, 32 KiB gzip) is unchanged; a lighter version would need a visual review.
  - PSI on production after release.

## 2026-10-18 · Launch video delivery (`dev`, on top of the blog commits `ac4dc91`)

- **Why:** the inline preview was the whole 57 s film without sound (2.4 MB) and played as soon as the card was visible. The film (9.0 MB) and vertical cut (3.9 MB) were H.264 only, the poster was a 74 KB JPEG, and `/video/` files were cached for a week because their names never changed.
- **Teaser:** the inline preview is now an 8.4 s silent loop of five scenes from the 1080p60 master: Super Intelligent pricing, the phone "offer ready" screen, the free tow, "paid on the spot", and the end card with usjunkcars.si and the phone number, joined by 0.3 s fades. It is 362 KB as AV1 WebM and 452 KB as H.264 MP4, against 2,431 KB before.
- **AV1 + MP4:** the teaser, film (1080p30, AV1 + Opus 96k, 3.31 MB vs 8.95 MB) and vertical cut (720×1280, 2.06 MB vs 3.86 MB) each ship as AV1 WebM plus the H.264 MP4. `video-player.js` picks AV1 only when `canPlayType` answers "probably" (`av01.0.05M.08`, or `av01.0.08M.08, opus` for the versions with sound). If an AV1 file still fails to load or decode, the element switches to the MP4 once. Quality (SSIM against the master, higher is better): teaser 0.986 (AV1) vs 0.982 (H.264), film 0.986 vs 0.983, vertical 0.985 vs 0.983. VP9 was tried for the teaser and rejected: 612 KB, larger than H.264.
- **Poster:** the same brand end card (48.2 s), re-cut from the master as AVIF/WebP: 1280 px 28/34 KB, 768 px for screens ≤ 640 px 15/19 KB. The JPEG is kept as the fallback for browsers without `image-set()` `type()` and for the `<noscript>` style. It still attaches only near the viewport (speed-up phase).
- **Fingerprinted names and caching:** every `/video/` file is named `<name>.<first 8 hex of SHA-256>.<ext>`, so a changed file gets a new URL. A `next.config.ts` rule after the one-week `/video/*` rule gives these names `public, max-age=31536000, immutable`. Renamed: `usjunkcars-launch-1080.25610612.mp4`, `-vertical.5c87ec32.mp4`, `-poster.c24edaa1.jpg`. Removed: `usjunkcars-launch-preview-720.mp4`. The encode script and masters are in the untracked `Claude/launch-video/` (`web/encode.sh` is deterministic: two runs, identical hashes; ffmpeg 9.0.2, SVT-AV1 4.2.0, libwebp, avifenc).
- **Nginx `/video/` decision:** not changed. Node already answers Range requests (206), and with year-long immutable caching repeat visitors do not ask again. Serving from nginx (`alias /srv/usjunkcars/<branch>/current/apps/web/public/video/`) would save Node one stream per new visitor, but it needs three things first. (1) Check that the nginx user can read the restricted release directory. (2) Repeat dev's `X-Robots-Tag`/`no-store` headers in that location, because a location `add_header` replaces the server-level ones. (3) Install it by hand on the shared VPS. Worth doing only if video traffic grows, or as part of a CDN decision (`docs/15-cdn-recommendation.md`, owner decision; no DNS was changed).
- **SEO:** the VideoObject `uploadDate` is now `2026-10-18T13:39:22+06:00` (the production merge of the video), and `thumbnailUrl`/`contentUrl` point at the fingerprinted JPEG/MP4. `sitemap.ts` adds a `video:video` block for every route whose JSON-LD has a VideoObject, built from that VideoObject (title, description, thumbnail, content URL, duration 57, publication date), with the text XML-escaped because Next does not escape it.
- **Measurements** (local development builds of `9dd7aca` and this change on that base, no gzip proxy; after rebasing onto `ac4dc91` the CI check and the headless checks were re-run with the same results):
  - Lighthouse 12.8.2 mobile, 3 runs each: 93 → 93, FCP 2.0–2.1 s, LCP 3.0 s, TBT 10–20 ms, CLS 0.001, ~482 KiB both. On a phone the video section starts well below the first screen, so the first load does not change.
  - Headless Chrome 152, cache disabled, page load then scroll to the video and watch 10 s:

    | | First load | /video/ bytes on first load | After scroll + 10 s | /video/ bytes |
    |---|---|---|---|---|
    | Desktop 1366×800, before | 501 KB | 72 KB (JPEG poster) | 2,960 KB | 2,447 KB |
    | Desktop, after | 457 KB | 28 KB (AVIF poster) | 895 KB | 382 KB |
    | Phone 390×844 @3×, before | 468 KB | 0 | 2,955 KB | 2,447 KB |
    | Phone, after | 470 KB | 0 | 878 KB | 369 KB |

    Opening the film now costs 3.3 MB instead of 9.0 MB, and the vertical cut 2.1 MB instead of 3.9 MB, in AV1 browsers.
- **Verification:**
  - **Headless Chrome 152, 18 behaviour checks passed:**
    - The teaser is AV1, muted and looping. It plays only while visible and pauses when scrolled away.
    - The full-screen player opens with the AV1 film and sound on (audio decoded). Tap to mute, tap to unmute and the volume slider (0.4) all work, and close stops the film.
    - On a phone held upright: the 768 AVIF poster, and the vertical AV1 cut (720×1280).
    - With AV1 reported unsupported, the MP4 teaser and film play. With a broken AV1 URL, both switch to the MP4 and play.
    - The 19th check expected no `/video/` request before scrolling. On a 1366×800 desktop the card is already within 1.5 screens, so the poster loads at once by design, as before.
  - **Server:** every file returns 206 to a Range request with a single `immutable` Cache-Control.
  - **CI:** `pnpm run ci:check` passed, including a new site test (both environments) that checks every `/video/` URL on the homepage:
    - it is fingerprinted, and the hash matches the file;
    - it supports Range and is cached immutably;
    - the poster comes in AVIF/WebP/JPEG, and each video has an AV1 WebM and an MP4;
    - `uploadDate` has a timezone, and the sitemap's `video:video` matches the VideoObject.
- **Not done / open:**
  - Safari/iOS were not tested on a device. iPhones without AV1 hardware decoding should report no AV1 support and get the MP4s; that path was simulated in Chrome.
  - PSI on production after the release.
  - The VideoObject `embedUrl` points at the homepage section, not a standalone player page.
  - Two of the teaser's scenes show claims already in the film ("about two minutes", free towing, paid on the spot) and need the same owner approval as the film (`docs/13-launch-video-script.md`).
