# Infrastructure configuration — 2026-10-15

> HISTORICAL / SUPERSEDED: The owner selected their existing Hostinger VPS. Do not execute the Vercel token, DNS or activation instructions below. Current authoritative setup: [VPS setup](10-vps-setup.md) and [release runbook](06-cicd-and-release-runbook.md). Dormant Vercel projects are no longer deployment targets.

The owner requested connecting the domain and configuring development/production CI/CD. This extends the planning-only scope. Application development and publication still follow the separate owner review process.

## Configured resources

| Branch | GitHub environment | Vercel project | Domain |
| --- | --- | --- | --- |
| `dev` | `development` | `usjunkcar-dev` / `prj_CJwvmCfXbOGgTuSUX71n5HW9izIc` | `https://dev.usjunkcars.si` |
| `main` | `production` | `usjunkcar-prod` / `prj_zsFoaQNOc7M5uhmBzqrOSzzflFzs` | `https://usjunkcars.si` |

Both projects belong to Vercel team `amfrshawons-projects` (`team_UsWcYsLNsRZinsKuL9xrTeYr`). They were requested with Next.js, root `apps/web`, separate `APP_ENV`/`SITE_URL`, and no Git integration. Both project-domain ownership checks returned verified; this is distinct from correct DNS routing and HTTPS readiness.

Runtime variable creation was requested with project creation, but the connector returned HTTP 403 when listing variables or attempting an explicit upsert. Their persistence is **unverified**. The local Vercel CLI has no authenticated session. The deployment preflight checks the actual plain `APP_ENV` and `SITE_URL` using the environment's token and refuses deployment if absent/wrong. Verify/set these non-secret values in each project's **Production** context:

| Project | `APP_ENV` | `SITE_URL` |
| --- | --- | --- |
| `usjunkcar-dev` | `development` | `https://dev.usjunkcars.si` |
| `usjunkcar-prod` | `production` | `https://usjunkcars.si` |

Development Vercel authentication is enabled for all deployments. Production protects generated deployment URLs and previews, while its approved custom production domain is intended to be public. Do not weaken development protection to make smoke tests pass.

GitHub environment policies allow only `dev` for development and only `main` for production. Production requires reviewer `amfrshawon`, allows the solo owner to review their own run, and disables administrator bypass. Branch protection denies deletion/force pushes on both branches. `main` additionally requires a PR, the `Validate` check, an up-to-date branch and resolved conversations; rules apply to administrators. Zero independent PR approvals avoids a solo-owner deadlock; explicit owner release approval is still required.

## Executable workflow and current limits

`.github/workflows/pipeline.yml` runs validation on pushes to `dev`/`main` and PRs into `main`. Only a same-repository `dev` release PR is accepted. Actions are pinned to verified commit SHAs; Vercel CLI is pinned to `64.0.2`.

`infra/deployment.json` fixes repository, team, projects and origins. Both `enabled` flags are deliberately **false**: the repository has no Next.js app, database or release-ready business content. CI can pass configuration checks while reporting that deployment is disabled. It must not serve the root static clone. Creating an app automatically activates the application-check requirements, even while deployment is disabled.

Once enabled, the deployment job waits for the relevant GitHub environment, checks the current branch SHA, protection rules, project/organization, root and framework, then pulls configuration, applies the reviewed predeployment contract, builds, stages without assigning domains, tests, rechecks the SHA and promotes the same artifact. There are no executable rollback or database jobs independent of this contract yet. No real deployment has been demonstrated by this setup.

Verification: four local deployment-guard tests passed, Actionlint 1.7.12 reported no workflow errors, and [the initial dev CI run](https://github.com/amfrshawon/usjunkcar/actions/runs/38621919333) passed validation with deployment correctly skipped. This is configuration evidence only, not app or live-release evidence.

## DNS status and required records

At initial inspection, authoritative nameservers were `aster.dns-parking.com` and `helios.dns-parking.com`, the apex A record was `2.57.91.91`, and the site displayed a Hostinger parking page. No development CNAME existed. The owner completed Hostinger sign-in, and the DNS edits below were saved successfully on 2026-10-15.

Applied the following preferred records returned by Vercel's project-specific configuration:

| Type | Host | Value |
| --- | --- | --- |
| A | `@` | `216.198.79.1` |
| A | `@` | `64.29.17.1` |
| CNAME | `dev` | `a34dcb59e9859370.vercel-dns-017.com` |

The parking A record was replaced. The existing `www` CNAME to `usjunkcars.si` was preserved, and `www.usjunkcars.si` was attached to the production Vercel project with a 308 redirect to the apex. No nameservers or unrelated records were changed. The inspected zone contained no mail records.

Both authoritative nameservers, Cloudflare DNS (`1.1.1.1`) and Google DNS (`8.8.8.8`) returned the new apex A records and development CNAME. Vercel reported `misconfigured: false` for both domains. An automatically renewing Vercel certificate was issued for apex/dev/www (`cert_8EIUO3ibrKZs6xvwuACElUO0`). Certificate issuance and correct DNS still do not constitute a deployed application; repeat HTTPS/application checks after the first approved deployment.

Subsequent HTTPS probes to apex, dev and www all completed with certificate verification result `0` and HTTP `404`. TLS is working; no application deployment exists yet, so application routing and the configured www redirect are not live. This is not a lead-generation site launch.

## Required owner actions

- Create a Vercel token with access to the named team and save it directly as `VERCEL_TOKEN` in both GitHub environments at [repository environments](https://github.com/amfrshawon/usjunkcar/settings/environments). Do not paste credentials into chat or Git. Token presence was not confirmed during initial setup.
- Verify/set the two plain runtime variables in the Vercel project settings above; connector access was denied and local CLI login is absent.
- [Infrastructure PR #1](https://github.com/amfrshawon/usjunkcar/pull/1) is open. The owner explicitly chose **keep it on dev for review** on 2026-10-15; do not merge until new approval. Merging infrastructure with deployment flags false would not publish the site. Enabling production later requires the actual site/release review and the protected production environment approval.

Credentials are entered by the owner directly in the CI provider; no authentication secret is retrieved from local stores or recorded in this repository.

## Next agent activation contract

1. Implement the planned workspace at `apps/web`, pin pnpm in root `packageManager`, and commit `pnpm-lock.yaml`. Read installed Next.js docs. Retain the reference outside the hosted app.
2. Implement root `ci:check`: lint/type checks, domain logic, database/RLS against disposable test data, build, route-cap/private-access and browser/accessibility checks. No production credentials in this job.
3. Implement root `ci:predeploy`: validate the actual runtime publication registry (not only the planning JSON), business/domain approvals, backup readiness, environment-specific Supabase project ID and additive migrations. Use environment-scoped `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD` and variable `SUPABASE_PROJECT_ID`; provision these when the database is built. Fail on absent/mismatched targets. The script must not be a placeholder that exits successfully.
4. Implement root `ci:smoke`: target `BASE_URL`, verify the expected environment/release, published-route cap and private-route denial, and exercise synthetic intake/staff checks with no real notifications. Use `vercel curl <path> --deployment "$BASE_URL"` for authenticated protected HTTP tests; CLI handles protection. Browser tests need an approved protected-access fixture. Do not log tokens or export authentication traces. The same suite runs before promotion and against the custom domain afterward.
5. Verify both project settings, Git integration absence, DNS, secrets and environment policies. Enable **dev only** in the reviewed configuration and push when instructed. Confirm a real successful run and record its URL/SHA.
6. After owner review, approve the actual production routes/content and enable production in the release PR. Merge only after explicit approval. The protected environment then requires the owner's deployment review before secrets/migrations are available.

Do not interpret a green docs-only CI run, project-domain ownership verification or a skipped deploy job as an end-to-end working release pipeline. Keep this record current when dependencies are completed.
