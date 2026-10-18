# Localhost → dev → production release runbook

The owner's approval applies to an identified scope/revision, never all future work. Passing CI is not owner approval.

1. Implement on local `dev`, test, start localhost, and show the owner the actual preview and changes. Do not commit/push application work until the owner approves that scope and requests dev promotion.
2. Commit/push the reviewed scope to `dev`. GitHub Actions validates it and, once the dev deployment flag is approved/enabled, deploys to private `https://dev.usjunkcars.si`. The owner reviews desktop and mobile using the private preview credentials.
3. After final approval of that exact dev release, use the existing `dev` → `main` PR. Do not merge PR #1 without separate approval. If dev changes after review, obtain review of the new scope.
4. CI validates main. The protected `production` environment requires owner `amfrshawon` to approve deployment before production credentials are exposed. Only main may deploy to `https://usjunkcars.si`.

Only dev/main are long-lived remote branches. Both deny force pushes/deletion. Main requires a PR, current base, `Validate` and resolved conversations, including for administrators. Zero independent PR reviewers supports the solo owner; explicit release approval is still required. Production environment administrator bypass is disabled.

## Implemented deployment flow

`.github/workflows/pipeline.yml` validates infrastructure on pushes and same-repository dev PRs into main. With an app present it requires frozen pnpm installation and `ci:check`. Deployment also requires the target's `enabled` flag in `infra/deployment.json`. Both flags are currently false.

The deploy job waits for its GitHub environment, verifies branch/head and protection policies, builds an environment-specific artifact with `ci:package`, and runs `ci:predeploy` for publication/data gates and additive migrations. It rechecks freshness, then streams `release.tar.gz` over host-key-pinned SSH using a restricted environment-specific key.

The VPS receiver checks archive safety and identity, starts a candidate on a private loopback port, verifies SHA/environment health, checks branch freshness, atomically switches the release and restarts only its systemd service. Failed live health restores the previous release. External HTTPS checks confirm dev authentication or production response. Concurrency serializes deployments; never cancel active migrations/promotions.

The application must implement meaningful `ci:check`, `ci:package`, `ci:predeploy`, migrations and full lead/browser smoke tests. Do not substitute successful no-ops. See [the artifact contract](10-vps-setup.md). Current infrastructure checks do not prove a real application deployment.

## Data and rollback

Use separate development/production database projects and credentials. Dev sends only test notifications. No production data in localhost or dev. Database provisioning, backups, restore rehearsal and application telemetry remain application-phase work.

Migrations must be approved, additive and compatible with the previous release. Do not migrate inside request handlers or silently reset databases. Failed migrations stop deployment. Destructive changes require a separate reviewed plan.

For an owner-approved rollback, select the recorded compatible release under `/srv/usjunkcars/<branch>/releases`, verify manifest/schema compatibility, atomically repoint `current`, restart only `usjunkcars-<branch>.service`, and verify SHA/environment health plus HTTPS. Never automatically revert the database or delete leads. Retain the previous artifact; monitor disk usage and remove only old unreferenced releases under an agreed retention policy.

Runtime secrets belong in `/etc/usjunkcars/<branch>.env` with root/environment-group ownership and mode 640. Deployment keys belong solely to their GitHub environments. Do not print secrets or add them to Git.
