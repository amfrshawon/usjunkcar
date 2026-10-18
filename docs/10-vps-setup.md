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

### Private repository: branch check token
The repository is private since 2026-10-18. Before switching releases, the receiver confirms with GitHub that the branch still points at the commit being deployed. That call needs a read-only token in `/etc/usjunkcars/<branch>.github-token` (`root:usjunkcars-<branch>`, mode 640). The token is never loaded into the app's environment. Without the file, every deploy is refused. Owner steps, as root on the VPS:

1. On GitHub, create a fine-grained personal access token. Settings → Developer settings → Fine-grained tokens. Choose resource owner `amfrshawon`, *Only select repositories* → `usjunkcar`, and Repository permissions → **Contents: Read-only** (Metadata read is added automatically). Set the expiry to 1 year and note the renewal date.
2. Back up and install the receiver from this repository (copy it to the VPS first, for example with `scp infra/vps/receive-release.py root@69.62.69.84:/tmp/`):
   `cp -p /usr/local/lib/usjunkcars/receive-release.py /usr/local/lib/usjunkcars/receive-release.py.bak-$(date +%F)`
   `install -m 755 -o root -g root /tmp/receive-release.py /usr/local/lib/usjunkcars/receive-release.py && rm /tmp/receive-release.py`
3. Store the token for both branches, without echoing it or writing it to shell history:
   `read -rs TOKEN && for b in dev main; do install -m 640 -o root -g "usjunkcars-$b" /dev/null "/etc/usjunkcars/$b.github-token"; printf '%s\n' "$TOKEN" > "/etc/usjunkcars/$b.github-token"; done; unset TOKEN`
4. Re-run the latest failed deploy, for example `gh run rerun <run id> --failed`.

To renew the token, repeat step 3. To roll back the receiver, restore the `.bak-*` copy.

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

## Launching the Next.js app on production (owner steps)

`apps/web` is now a Next.js 16.3.8 app (pnpm 10.34.7, standalone output). With the app present, the static preview and the static production switch are disabled by the infrastructure check. Production launch works like this:

1. **Approve pages.** In `content/publication.json`, for each page approved for launch set `"status": "published"`, add `"production"` to `environments`, and record `"approval"` (for example `"owner 2026-10-15"`). The homepage must be approved. Unapproved pages return 404 in production, and `ci:predeploy` fails if any approved page links to an unapproved one.
2. **Enable production** by setting `environments.main.enabled` to `true` in `infra/deployment.json`.
3. **Release** through the reviewed `dev` → `main` pull request. CI runs `ci:check`, the protected `production` environment waits for owner approval, then `ci:package` builds the production artifact and the receiver health-checks it before switching.

The installed receiver already accepts `nextjs-standalone` releases, so no server change is needed for the app path.

## (Superseded) Launching the static site on production

The repository can now release the static site (homepage, Locations, About, FAQ, Contact, Privacy Policy) to `https://usjunkcars.si` without the Next.js app. It stays off until the owner switches it on.

1. **Reinstall the release receiver on the VPS (root, one time).** The updated `infra/vps/receive-release.py` accepts a `static-site` release on `main`; the copy installed on the server rejects it. Copy it to the server and run `install -m 755 receive-release.py /usr/local/lib/usjunkcars/receive-release.py`. Back up the installed file first.
2. **Confirm the GitHub `production` environment** still requires the owner's review and only allows the `main` branch. The deployment preflight checks this and refuses to deploy otherwise.
3. **Switch the static site on** in the release pull request by setting `"staticProduction": true` in `infra/deployment.json`. Keep `main.enabled` false; it is reserved for the Next.js app.
4. **Merge the reviewed `dev` → `main` pull request.** CI packages the public site (no preview guard, indexable, no dev links), the receiver health-checks it on port 3402, then switches port 3400. Nginx stops showing the holding page as soon as port 3400 answers.
5. **Verify:** `https://usjunkcars.si/` returns 200, `/api/v1/health` reports `production`, pages have no `noindex` header, and the Peddle offer opens.

**Roll back:** set `"staticProduction": false` and redeploy, or restore the previous release symlink on the VPS; with nothing on port 3400, Nginx serves the holding page again.

Before switching on, replace the Peddle staging ID (329729, staging embed host) with the live publisher ID and host.
