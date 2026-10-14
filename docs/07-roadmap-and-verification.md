# Implementation roadmap and acceptance contract

## Work sequence

Each phase produces a reviewable local result and updates a phase log with work completed, tests, known gaps and next steps. Commit/push only after the owner's instruction. A phase may prepare later work but must not mark external integrations complete using mocks.

| Phase | Deliverables | Exit criteria / dependencies |
| --- | --- | --- |
| P0 — Inventory and decisions | Full source URL/template inventory, original desktop/mobile screenshots, chosen launch routes, business identity input list, completed baseline audit | Every known family accounted for; truncation and missing-section checks; owner confirms route selection before publication |
| P1 — Foundation | Next.js workspace, pinned versions, local Supabase, environment schema, shared packages, formatting/test scripts, isolated reference fixture | Reproducible install/build; docs of selected Next.js version; no public old-domain fixture |
| P2 — Design and publication | Marketing design system, all page-family templates with representative data, private preview gallery, runtime route registry, launch pages | Every family reviewed at all breakpoints; anonymous drafts/RSC/API/static output denied; allowlist cap enforced |
| P3 — Data and intake | Migrations, RLS, staff auth, lead transactions, form/contact API, file validation, outbox | Accepted submission survives retries/provider failure; permissions and transaction tests pass |
| P4 — Staff dashboard | List/board/detail, assignment, tasks, offers, pickup calendar, metrics, audit and failure queue | End-to-end seller→staff flow, conflict handling, role boundaries, responsive controls |
| P5 — Existing bot | Inspect owner's implementation, adapter, knowledge approval, scoped tools, streaming, handoff | Real bot creates one durable lead; injection/retry/outage tests; no private-data leakage |
| P6 — Infrastructure | Two Vercel/Supabase environments, GitHub workflows/protections, DNS, backups, telemetry | Approved dev push reaches protected dev domain; production cannot bypass approval; target-mismatch test fails safely |
| P7 — Launch review | Real identity/content/legal approvals, selected ten pages, performance/a11y/SEO audit, operational runbook | Owner acceptance, production gate and rollback rehearsal, then explicit launch approval |
| P8 — Mobile | Confirm audience, native designs, shared client, iOS/Android auth/files/push and beta distribution | Device testing, version compatibility, secure local storage; separate store-release approval |

P2 and P3 share contracts; do not postpone API design until after dashboard UI. Infrastructure can be prepared earlier, but public domain assignment remains a release action. Native app implementation begins only after web contracts stabilize and audience is confirmed.

## Acceptance matrix

| Area | Required checks |
| --- | --- |
| Completeness | Full source capture contains closing footer, no `[Truncated]`, every inventoried section/family accounted for |
| Visual fidelity | Same viewport/font/banner/carousel state; header-to-footer screenshots at 1440, 1280, 768, 390, 360; deviations documented |
| Interactions | Menu, accordions, map, search, review/brand controls, video, dismiss banner, return-to-top, keyboard/touch, resize/reset |
| Assets | All referenced local images/fonts/CSS resolve; no failed lazy images at bottom; no source analytics; approved video/provider dependencies |
| Publication | Anonymous crawl ≤10 approved content routes; no drafts in sitemap, links, search, static output or RSC/API responses; encoded/query route probes denied |
| Metadata/domains | Apex canonical/OG/schema, dev noindex/access control, correct email/callback links, no original operator contact endpoints |
| Intake | Required fields, unknown values, outside coverage, whitespace/invalid input, consent, success state, duplicate click, timeout/retry, idempotency collision |
| Database | Clean and upgrade migrations; transaction rollback; constraints; indexes; restore drill; dev/prod isolation |
| Authorization | Anonymous/publishable-key denial, each role and ownership scope, disabled user, cross-org ID substitution, storage URL access |
| Dashboard | Filters/pagination, assignment, allowed/denied stage moves, version conflicts, note/offer history, overdue tasks, exports and metrics definitions |
| Async work | Mail failure after save, retries/lease expiry, duplicate webhook, signature failure, dead-letter visibility, manual retry audit |
| Chat | Real provider and mocks, scoped tools, no fabricated success, consent, injection, replay, outage, reconnect and human handoff |
| CI/CD | Wrong branch/project/DB fails; stale SHA cannot deploy; PR cannot access production secrets; approval gate blocks; same artifact tested/promoted |
| Security/privacy | Secrets/output scans, CSRF, session revocation, rate limits, upload type/size/ownership, redacted logs, private cache denial and retention |
| Accessibility | Keyboard-only flows, visible focus, labels/errors, contrast, reduced motion, screen-reader smoke tests; automated scan plus manual checks |
| Performance | Public bundle/image/font budgets; lab checks on representative devices; measure real-user vitals after launch |
| Mobile readiness | OpenAPI validation, typed client compatibility, bearer-token authorization, additive version changes, upload retry semantics |

Use Vitest or equivalent for domain rules, SQL/RLS tests against disposable Supabase, and Playwright for browser flows. Avoid implementation-mirroring tests. Strong regression examples: the previously truncated lower homepage must be present; an unapproved eleventh route must fail; retrying intake must not create a second lead; an agent must not read an unassigned lead; production deployment cannot start before approval.

## Definition of done for launch

All intended templates designed privately; every discovered route mapped with honest status; exact public subset approved and capped; real leads flow through backend and staff dashboard; chatbot works through the shared service; owner identity/legal text approved; no original business endpoints remain; infrastructure/protections/backups tested; open blockers resolved or explicitly accepted; owner approves production.

Do not treat the root static clone as the finished app, placeholder dashboards as working data flows, or an AI-generated offer as an approved price. Do not call future mobile apps complete because their contracts exist.

## Handoff prompt for the next AI agent

> Work in the `amfrshawon/usjunkcar` repository on `dev`. Read `AGENTS.md`, `README.md` and all numbered planning documents. Build the Next.js lead-generation system for `usjunkcars.si`, a private staff dashboard and database, and an adapter for the owner's existing chatbot. Begin with P0/P1, preserving the reference fixture and unrelated parent project. Inventory all source page families, then build every template privately while enforcing at most ten approved public content pages. Use separate dev/prod data and the versioned API designed for future iOS/Android apps. Read the installed Next.js docs before framework changes. Record unresolved business/chatbot inputs; use clearly marked mocks only where inputs are missing. Test and present each phase locally. Do not commit or push implementation changes until the owner says “push to dev.” Do not merge/release to `main` without explicit approval for the reviewed revision. Follow the CI/CD runbook; do not deploy the existing static fixture or silently change the stack/scope.

## Progress log format

For each phase record date, branch/local revision, requirements covered, files/routes changed, test commands and results, evidence paths, open dependencies, migration impact and owner review/push/release instruction. Keep real lead data and secrets out of evidence. Maintain a backlog for unfinished work instead of obscuring it in a completion summary.
