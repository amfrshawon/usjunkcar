# Readiness, decisions still needed and evidence

Snapshot: 2026-10-15. This file separates the baseline, the planning handoff and future implementation.

## Current state

| Item | State |
| --- | --- |
| Repository | `https://github.com/amfrshawon/usjunkcar`, public at inspection |
| Existing `main` | Static homepage baseline commit `564a41a`; no independent backend |
| `dev` | Planning handoff branch containing these specifications; verify remote HEAD before starting implementation |
| Static design | Homepage markup/CSS/fonts/images; source-site links and business identity still present |
| Prior audit | Truncation found and fixed; lower homepage restored; desktop section measurements saved |
| Remaining audit | Full responsive/interaction/assets verification incomplete; known footer spacing difference in desktop measurement; historical report/preview stale |
| Next.js product | Not scaffolded in this repository |
| Database/auth/dashboard | Planned, not provisioned or implemented |
| Existing chatbot | Awaiting owner-provided implementation |
| CI/CD/protections/DNS | Specified, not configured or activated by this task |
| Mobile apps | Planned architecture only |

The documentation commit is not permission to publish the baseline. Do not interpret a Git branch as an environment deployment.

## Owner inputs and blocking scope

| Input | Why needed | Blocks |
| --- | --- | --- |
| Final ten public routes | Owner gave cap but no exact selection | Publication, not template development |
| Business name/logo/entity, phone/email | Replace inherited identity and contact routing | Public launch and real notifications |
| Service areas/hours/title rules/offer process | Truthful content, qualification and scheduling | Final content and operational tools |
| Legal/consent text and retention approval | Describe actual service/data processing | Real data collection launch |
| Existing chatbot repository/export/demo | Inspect architecture and reuse contract | Real chatbot integration; mocks can proceed |
| Hosting/Supabase/DNS account selection/access | Provision targets and verify ownership | Remote environments/deployments |
| Staff names/roles and owner MFA | Invite-only operations and approval reviewer | Production staff access |
| Email/SMS and VIN/report provider choices | Real delivery, decoding, paid report flows | Relevant integration activation |
| Mobile audience: staff, sellers or both | Determines native screens and permissions | Mobile feature design/implementation |
| Public vs private source-code preference | Public Git exposes committed draft designs even when routes are protected | Confidential designs in Git, if confidentiality desired |
| Budget/regions/backup service level | Select paid features and recovery capability | Purchasing/provisioning and operational promises |

No secrets belong in these answers or docs. Configure credentials through provider/CI controls. Unanswered inputs should be tracked as dependencies, not filled with invented business facts.

## Decision ledger

| ID | Decision | Status |
| --- | --- | --- |
| D01 | Next.js, new domain, dashboard/database, existing bot, ten-page cap | Owner requirements |
| D02 | Only `main`/`dev`; owner reviews before push and production approval | Owner requirements |
| D03 | Supabase SQL/Auth/Storage; TypeScript domain/API layer | Proposed default |
| D04 | Two Vercel projects, gated CLI deployments, no automatic Git bypass | Proposed default |
| D05 | Ten paths in `launch-pages.json` | Proposed, all unapproved for publication |
| D06 | Native React Native/Expo; staff app first | Proposed; audience unresolved |
| D07 | No real notification send from dev | Implementation requirement for environment isolation |
| D08 | Public source visibility retained | Existing state; no new visibility change authorized |

Record future changes here with rationale, owner decision and affected specs. Do not silently switch databases, merge dev/prod data, broaden the public-page count or replace the bot.

## Official references checked

The following pages were read on 2026-10-14. Verify current APIs and account-plan capabilities again during implementation, and lock actual package versions.

- [Next.js App Router](https://nextjs.org/docs/app): framework structure and route-handler direction. Parent installed guide also inspected at `node_modules/next/dist/docs/01-app/01-getting-started/15-route-handlers.md`; the new repository has no installed Next.js version yet.
- [Supabase SSR](https://supabase.com/docs/guides/auth/server-side): server session integration.
- [Supabase row-level security](https://supabase.com/docs/guides/database/postgres/row-level-security): data authorization.
- [Supabase environment management](https://supabase.com/docs/guides/deployment/managing-environments): migrations and separated data environments.
- [Vercel environments](https://vercel.com/docs/deployments/environments): environment concepts.
- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches): branch protections.
- [GitHub deployment environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments): reviewers, branch restrictions, plan availability and environment secrets.
- [Expo Router](https://docs.expo.dev/router/introduction/): proposed native navigation.

Database entities, business lifecycle, launch selection, role matrix, retention proposals and release policy are project design recommendations. They are not claims about undocumented behavior of the reference business or promises of unconfigured vendor features.
