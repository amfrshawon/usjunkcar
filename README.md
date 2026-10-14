# USJunkCars.si — development handoff

Lead-generation website, lead dashboard, AI assistant, and a shared backend for future iOS and Android apps.

## Start here

Read [AGENTS.md](AGENTS.md), the [product plan](docs/00-product-plan.md), and the [implementation roadmap](docs/07-roadmap-and-verification.md) before development. These specifications describe the target system; they do not claim it already exists.

| Specification | Purpose |
| --- | --- |
| [Product plan](docs/00-product-plan.md) | Requirements, scope and decisions |
| [Architecture](docs/01-architecture.md) | Stack, structure, environments and domains |
| [Website and publishing](docs/02-website-and-publishing.md) | A-to-Z page families, ten-page limit, private previews |
| [Database](docs/03-database-and-security.md) | Entities, constraints, permissions and migrations |
| [API and dashboard](docs/04-api-and-lead-dashboard.md) | Lead flow, endpoints and staff operations |
| [Chatbot and mobile](docs/05-chatbot-and-mobile.md) | Existing-bot adapter and future apps |
| [CI/CD and releases](docs/06-cicd-and-release-runbook.md) | Approval, branches, deployments and rollback |
| [Roadmap and verification](docs/07-roadmap-and-verification.md) | Backlog, acceptance tests and next-agent prompt |
| [Readiness and evidence](docs/08-readiness-and-open-inputs.md) | Current state, open inputs and references |
| [Launch proposal](docs/launch-pages.json) | Ten candidate public URLs; none approved for publication yet |
| [Infrastructure setup](docs/09-infrastructure-setup.md) | Actual hosting projects, GitHub controls, DNS and activation dependencies |

## Required addresses and branches

- Production: `https://usjunkcars.si`
- Development: `https://dev.usjunkcars.si`
- Staff dashboard: `/dashboard` on each environment's own origin
- Shared API: `/api/v1` on each environment's own origin

Only `main` and `dev` are long-lived remote branches. Implementation work stays local on `dev` until the owner reviews it and explicitly requests a commit/push. Production releases require separate approval for the identified release. Publishing these planning docs is authorized; publishing the application is a later milestone.

Infrastructure configuration was requested on 2026-10-15. The branch-aware GitHub workflow validates this repository now, and gates deployment until the Next.js app is implemented and enabled. Hosting projects and protected GitHub environments have been created. See the setup record for unfinished DNS/credential/application dependencies; configuration is not evidence of a live deployment.

## Current repository

The root contains a static homepage reference captured from `https://www.usjunkcars.com/`. Run `npm run dev` to view it at `http://localhost:4173`. No Next.js app, independent backend, database, auth or dashboard exists here yet. Many links, phone numbers and claims still belong to the reference business. Do not launch this fixture as the new website.

The audit recovered truncated HTML and restored the lower homepage and local interactions. Desktop measurements are in `audit/desktop-layout.json`. The complete mobile, interaction and asset audit was not finished before this planning handoff. `preview.png` and `asset-report.json` are historical artifacts, not release evidence.

The next agent should retain a sanitized fixture outside the public application directory, build `apps/web`, and account for every reference page family before claiming an A-to-Z clone.
