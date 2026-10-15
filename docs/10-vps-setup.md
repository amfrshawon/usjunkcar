# Current VPS setup and developer handoff

The owner authorized infrastructure completion on 2026-10-15 and selected their existing Hostinger VPS. This supersedes Vercel. Application publication still requires localhost review, dev approval, desktop/mobile dev review, then separate main approval.

## Infrastructure

| Target | Development | Production |
| --- | --- | --- |
| Branch | dev | main |
| GitHub environment | development | production |
| Origin | https://dev.usjunkcars.si | https://usjunkcars.si |
| VPS account/service | usjunkcars-dev | usjunkcars-main |
| Loopback port | 3401 | 3400 |
| Candidate port | 3403 | 3402 |
| Release directory | /srv/usjunkcars/dev | /srv/usjunkcars/main |
| Runtime environment file | /etc/usjunkcars/dev.env | /etc/usjunkcars/main.env |

VPS: `69.62.69.84`. Node `24.22.0` is isolated under `/usr/local/lib/usjunkcars/node`; existing websites' runtimes and PM2 processes are untouched. Nginx handles the three USJunkCars hostnames. Systemd runs separate non-root users with restricted filesystem access and resource limits. No application process runs until a reviewed release exists.

Hostinger DNS: apex A `69.62.69.84`; dev and www CNAME `usjunkcars.si`; TTL 300. Nameservers remain aster/helios.dns-parking.com. HTTPS uses `/etc/letsencrypt/live/usjunkcars.si`, scheduled Certbot renewal and the existing Nginx reload hook. WWW redirects to apex. Production currently returns a neutral 503 holding page with noindex; it is not a launch. Dev requires HTTP Basic authentication and sends noindex/no-store, including its holding response.

Private review credentials are saved outside Git on the owner's computer at `~/.config/usjunkcars/preview-access.json` (mode 600). Do not copy them into chat, screenshots or public docs. Share only through a private channel. The server stores a password hash at `/etc/usjunkcars/preview.htpasswd`.

Each GitHub environment has its own `VPS_SSH_KEY`. Temporary private generation files were removed after upload. Root-owned authorized keys restrict access to the root-owned release receiver for that environment; shell commands, forwarding and PTYs are disabled. Pinned host key: `infra/vps/known_hosts`. No Vercel token is needed; dormant Vercel projects are unused.

## Next agent: application activation contract

1. Read AGENTS.md and the product specifications. Read installed Next.js guides before framework code. Build `apps/web` using standalone output and workspace tracing. Keep the root static fixture out of the public app. Pin pnpm/dependencies and commit the lockfile with approved application work.
2. Implement root `ci:check`: lint/types, domain/API tests, SQL/RLS, build, actual route cap (ten public content pages), private-route denial, business/domain guards, browser/accessibility and synthetic lead/staff flows. No production credentials in this job.
3. Implement root `ci:package` with `APP_ENV`, `SITE_URL` and correct environment public build variables. Produce root `release.tar.gz` containing `apps/web/server.js`, standalone dependencies, `.next/static`, approved public assets and root `release.json`. Tar must contain ordinary files/directories only, dereferenced links, no `.env*`, `.git`, `.ssh` or secrets, and at most 400 MiB compressed/expanded. Build Linux x64 in CI. Do not package source fixtures.
4. Manifest must be exactly `{"commit":"<GITHUB_SHA>","branch":"dev or main","kind":"nextjs-standalone"}`. Listen on `HOSTNAME`/`PORT`. GET `/api/v1/health` must return HTTP 200 with `{"data":{"status":"ok","commit":"<RELEASE_SHA>","environment":"development or production"}}`, without sensitive data. Preserve monorepo `apps/web/server.js` layout. Stage and live use the same artifact.
5. Implement root `ci:predeploy`: validate approved identity/content, actual publication registry, environment/DB target, backups and additive migrations. Proposed Supabase inputs are environment secrets `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD` and variable `SUPABASE_PROJECT_ID`; these are not provisioned yet. Do not touch unrelated VPS PostgreSQL databases. Put runtime secrets in the respective environment file preserving ownership/mode; use single-line KEY=value entries. Add public build values to CI when the database is provisioned.
6. Add full application smoke tests before promotion and after deployment. The receiver currently verifies release health only; intake, storage, auth, notification and route tests remain required. Dev Basic Auth must coexist with application dashboard/API auth; handle that in test fixtures without exposing secrets.
7. Start localhost and obtain owner review. Enable only dev's flag in the approved dev release; push only on approval. Verify an actual successful run and protected URL, then have the owner review desktop/mobile. A skipped deploy is not a successful release.
8. Enable production only in the finally approved release, merge only with explicit owner approval, and complete protected environment review. PR #1 remains unmerged until that instruction. Main receives this VPS workflow when the reviewed PR is merged.

## Operational limits

Update 2026-10-15: the owner explicitly requested publishing the current localhost build to dev. `staticDevPreview: true` now permits a private homepage-only release on dev, independently of the disabled full-application switches. The archive kind is `static-preview`, accepted only for dev; the server also refuses production runtime. It packages an allowlist of static assets, rewrites reference-domain links, blocks contact clicks/form submissions, and does not expose repository files. Disable `staticDevPreview` before implementing `apps/web/package.json`. Production remains a holding page and PR #1 stays unmerged. This preview does not implement lead intake, search, other pages, a database or dashboard.

Verification on 2026-10-15: seven infrastructure tests and Actionlint passed; both scoped SSH keys rejected arbitrary shell commands; all 13 pre-existing Nginx vhost checksums were unchanged. HTTPS checks showed no regression across those 13 sites (one pre-existing dev 502 independently recovered to 200). New apex returned 503/noindex, dev returned 401 without credentials and 503 with valid credentials, and www returned 308 to apex, all with valid TLS. Certbot renewal timer is active.

The application, database, dashboard, chatbot, mobile apps and launch content are not built by this infrastructure task. No application release has been tested end to end. Both deployment flags remain false. Configuration, HTTPS, authentication and coexistence checks establish infrastructure readiness only.

For fresh-server recovery, inspect `infra/vps/bootstrap.sh`: it is one-time bootstrap and refuses an existing vhost. Restore secrets privately, issue/restore TLS, install `infra/vps/nginx.conf`, validate and reload Nginx. Never rerun bootstrap over an existing installation or restart unrelated services. Keep infrastructure/runtime backups before changes.
