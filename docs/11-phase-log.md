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
