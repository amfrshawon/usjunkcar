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
