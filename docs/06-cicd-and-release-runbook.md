# CI/CD, branches and approval runbook

## Status and owner contract

This is the release specification. The initial planning task configured no infrastructure. The owner requested infrastructure setup on 2026-10-15; [the setup record](09-infrastructure-setup.md) now tracks actual projects, controls and remaining dependencies. The implemented combined workflow follows the stages below; it stays disabled for application deployment until the Next.js app and required checks exist.

The owner's workflow is: develop locally → owner reviews → owner says “push to dev” → commit/push that scope → CI deploys `dev.usjunkcars.si` → owner reviews that environment → owner approves the identified release → promote through `main` → CI deploys `usjunkcars.si`.

Chat approval is an operating rule, not something GitHub can infer from a successful build. Record the reviewed scope/commit and approval reference. Do not encode “all green means merge” automation.

## Fixed branch/environment mapping

| Git branch | GitHub environment | Vercel project (proposed) | Business environment | Domain |
| --- | --- | --- | --- | --- |
| `dev` | `development` | `usjunkcar-dev` | development | `dev.usjunkcars.si` |
| `main` | `production` | `usjunkcar-prod` | production | `usjunkcars.si` |

Exactly two long-lived remote branches. Work locally on `dev`; serialize agents' work to avoid sharing a mutable checkout concurrently. Additional isolated branches/worktrees require the owner's request if needed later. Never point the static root fixture at a hosting project; the future app root is `apps/web`.

Use separate Supabase projects, storage buckets, auth redirects, bot credentials and email sending policies. Production secrets never enter development/PR workflows. Use a single deployment controller: CLI in GitHub Actions. Disable Vercel Git automatic deployments for these targets so they cannot bypass CI/approval. Recheck that setting after reconnecting Git integrations.

## GitHub controls to implement

- `main`: no force pushes or deletion; require a release PR, required checks and current branch base; limit bypass. Never use a direct implementation push to `main`.
- `dev`: no force pushes/deletion; owner/authorized agent pushes only after review. Run full CI after every approved push.
- `production` environment: required reviewer `amfrshawon`, branch restriction `main`, no automatic bypass. The current repo is public; confirm available protections before setup. If there is only one human owner, allow that owner to approve their own deployment run. Requiring a separate PR reviewer who does not exist would deadlock releases.
- For a solo owner, main PR may have zero mandatory independent reviews while requiring checks; the owner's explicit release approval and protected deployment approval remain mandatory. When another human reviewer joins, require review and dismiss stale approvals.
- `development` environment: branch restriction `dev`, separate secrets, test-only notifications.
- Keep workflow permissions `contents: read` by default. No PR-from-fork secrets, `pull_request_target` execution of untrusted code, or secret-bearing artifact uploads.
- Pin GitHub Actions to reviewed SHAs and CLI/package tools to exact tested versions. Restrict changes to deployment and publication policy files for review.

## Workflow specification to implement later

| Workflow | Trigger | Jobs and constraints |
| --- | --- | --- |
| `ci.yml` | Local equivalent; pushes to `dev`/`main`; PR targeting `main` | Frozen install, lint, typecheck, unit/domain, SQL/RLS, OpenAPI, build, browser/accessibility, route-cap/domain checks |
| `deploy-dev.yml` | Successful CI for current `dev` head | Validate target, migrate dev, build/stage dev project, smoke test, assign dev domain |
| `release-main.yml` | Successful CI for approved `main` merge | Wait for protected environment approval; validate SHA/target; additive migration; stage production; smoke test; promote same staged artifact |
| `rollback.yml` | Explicit owner-approved manual dispatch | Known prior production deployment only; no arbitrary URL/branch; verify schema compatibility |

Prefer a shared CI workflow invoked by the deployment workflow or explicit `needs` dependencies. A separate `workflow_run` deployment must validate successful conclusion, source repository, branch and exact head SHA; never deploy whatever happens to be latest. Preflight must confirm GitHub environment protection exists because referencing a missing environment can create an unprotected one.

Use concurrency per environment. Cancel obsolete build/test runs but never interrupt an in-progress migration or promotion. Before promotion verify the release is still current and its approval applies; an older successful run must not overwrite a newer release.

## Development release

1. Owner reviews the local diff/screens/tests. On “push to dev,” commit only that reviewed scope and push `dev`.
2. CI tests the exact SHA, including ten-page publication gate, draft-access tests and no old business domains in built output.
3. Deployment preflight verifies dev project/origin/DB ID and test-recipient policy.
4. Apply additive dev migrations. Build with dev application variables. Stage a deployment in the dev Vercel project without assigning the domain.
5. Test that deployment: page rendering, authenticated dashboard, a synthetic lead, storage/notifications mocks and `/health`.
6. Promote that dev-project deployment to `dev.usjunkcars.si`. Save SHA, deployment ID, migration version and test results. Show the owner the review URL.

## Production promotion

1. Identify the exact successful development SHA and approved scope. Stop if `dev` changed after the owner's review.
2. Open a `dev` → `main` release PR. Include changes, tests, route allowlist diff, migrations, provider changes and rollback plan. Obtain the owner's explicit release approval before merging.
3. CI validates the merge result. The production workflow waits for owner approval through the protected GitHub environment before accessing production secrets or applying migrations.
4. Confirm production project, origin, DB ID, backup/restore readiness and allowlist. Apply only approved backward-compatible migrations.
5. Build with production variables, stage a **production-context deployment** without domain assignment, and test that artifact. Do not promote the development build: its variables and database are different.
6. Smoke tests use dedicated synthetic records, no real outbound messages and no unapproved route publication. If checks fail, stop without assigning `usjunkcars.si`.
7. Promote the same staged production artifact. Verify domain/certificate, approved URLs, privacy denial, lead intake, dashboard and error rates. Record the release SHA/deployment/migration/publication revisions.
8. Bring `dev` forward with `main` after the merge if required (no force-push), preserving exactly the two branches. Reconcile any merge commit and rerun checks.

Planned CLI sequence, not commands to execute during planning: pull the correct project's environment; build production-context output; deploy prebuilt with domain assignment skipped; run smoke tests; promote its deployment ID. Vercel tokens remain environment variables, not command-line flags. Bypass secrets used by smoke tests must not appear in URLs, screenshots or logs.

## Database and rollback

DB migrations do not run inside request handling or every frontend build. Use a single migration job with target verification and serialization. Back up before risky changes. Expand/contract keeps the previous app release compatible. Data backfills have checkpoints and a separate monitored job.

If the new deployment fails after release: stop new promotion, record the failure, and with owner authorization roll back to the recorded compatible deployment. Do not reset the DB. Disable unsafe features if needed and deploy a forward fix. If schema/data recovery is necessary, restore to an isolated project first and reconcile leads received since the backup. A destructive rollback needs a separate explicit plan/approval. Verify whether domain auto-assignment must be restored after hosting rollback.

## DNS and activation checklist

Owner provides access through the selected hosting/DNS flow. Verify ownership of apex and dev subdomain; use the exact DNS records the hosting service supplies. Configure certificate, www→apex if desired, mail authentication records, auth callbacks, webhook URLs and mobile association paths. Do not guess DNS record targets or remove existing mail records.

The pipeline is “configured” only after project mappings, secrets, protections and DNS are verified; “working” requires a successful dev deploy and a demonstrated production gate. Document any account-plan restrictions instead of silently dropping protection.

## Sources

[GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) describes check/review controls. [GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) documents reviewer/branch gates and plan limits. [Vercel environments](https://vercel.com/docs/deployments/environments) distinguishes deployment contexts. This runbook chooses an explicit two-project release policy; it is not a statement that these settings are already active.
