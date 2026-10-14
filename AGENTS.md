# Instructions for every development agent

## Owner requirements

- Build USJunkCars.si using Next.js, PostgreSQL, a staff lead dashboard and the owner's existing AI chatbot.
- Recreate all reference page families and interactions; expose at most ten public content pages initially, including home and legal pages.
- Unpublished designs require authenticated preview access. Hidden links and `noindex` are not access control.
- Production: `https://usjunkcars.si`. Development: `https://dev.usjunkcars.si`.
- Prepare `/api/v1` for future iOS and Android apps.
- Read `docs/00-product-plan.md` through `docs/08-readiness-and-open-inputs.md` before implementing a phase.

## Branch and approval rules

Use exactly two long-lived remote branches: `dev` and `main`. Do not create additional remote branches unless requested.

1. Implement and test locally on `dev`; completion alone does not authorize a commit/push.
2. Present the result, evidence and limitations for review.
3. An explicit instruction such as “push to dev” authorizes committing and pushing the reviewed scope to `dev` only. Changed scope needs review again.
4. Development deployment targets only `dev.usjunkcars.si` with development credentials/data.
5. Use a `dev` → `main` release PR only after the owner approves the identified release/commit. Never infer production approval from development approval.
6. Production targets only `usjunkcars.si`, through protected environment checks.
7. Never force-push or replace `main` history. A push is not proof of a successful deployment.

Publishing the planning documents in this handoff is explicitly authorized. Future implementation pushes follow the rules above.

## Implementation constraints

- This repository is nested inside an unrelated furniture app. Confirm `git rev-parse --show-toplevel` and never commit parent-app files.
- Keep the static reference for comparison, outside `apps/web/public` during migration. It contains old-domain links and inherited business claims.
- Read the installed Next.js guides in `node_modules/next/dist/docs/` before framework changes. If the selected version has no bundled guides, use its official docs and record the version. Do not assume older conventions apply.
- Pin compatible stable dependencies and package manager; commit the lockfile.
- Share domain rules and validation between web, route handlers and future mobile. Do not implement mobile-required behavior only as Server Actions.
- Validate and authorize every lead operation; include audit events and environment isolation.
- No secrets, real leads, transcripts, signed storage links or production dumps in Git or verification artifacts.
- Reference-site assets, ratings, offers, phone numbers and company claims are not verified claims of the owner's business. Record approved identity/content before public launch.
- No reference-site submission endpoints in the final app. Domain migration and the ten-page allowlist are release gates.
- The owner will provide the existing chatbot. Start with an adapter contract and mocks; do not replace it or invent credentials.
- Record unfinished work honestly. A screenshot/build alone does not prove complete verification.

## Phase completion

Report behavior changed, tests, affected routes, migration impact, open inputs and the reviewed revision/diff. Stop at the next commit/push/release boundary unless the owner has already explicitly authorized that boundary.
