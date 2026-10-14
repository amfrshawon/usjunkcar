# Product plan and decision record

Date: 2026-10-15. Status: implementation proposal for owner review and another agent's development. Planning and Git handoff are the current task; application deployment is a later milestone.

## Outcome

Sellers understand the service, provide vehicle information through a form or chatbot, receive an honest confirmation and are contacted by staff. Staff qualify, assign, quote, schedule and close leads with an auditable history. Future mobile apps share these backend services.

## Requirements traceability

| Owner requirement | Commitment | Evidence needed |
| --- | --- | --- |
| Next.js clone and relevant technology | App Router, TypeScript, React, Tailwind, accessible UI | Visual and interaction comparisons for every template |
| A-to-Z design, ten pages live initially | Full route inventory, private previews, production allowlist | Anonymous crawl finds only approved pages; guessed draft URLs denied |
| Database | Separate Supabase PostgreSQL dev/prod projects, migrations, RLS | Reproducible schema, role tests, restore drill |
| Lead dashboard | Pipeline, details, assignment, tasks, offers, appointments, reporting | Form/chat → durable lead → authorized staff workflow |
| Existing operational AI chatbot | Scoped adapter, real tools, staff handoff | Integration and failure tests using owner's implementation |
| New domain everywhere | Central production/development origin configuration | Crawl links, metadata, callbacks, mail and mobile config |
| Two branches, approval-based CI/CD | `dev` staging and `main` production with distinct targets | Working pipeline and approval/rollback evidence |
| Plan in Git | Specifications, launch proposal, implementation prompt | Docs committed/pushed to `dev` |
| iOS and Android later | Versioned API and shared schemas | Mobile-compatible contracts used by web |

## Proposed defaults

| Topic | Default | Reason / condition |
| --- | --- | --- |
| App | One Next.js web app for marketing and dashboard | Shared service layer, fewer moving parts |
| Backend | Route Handlers + TypeScript domain services | HTTP interface usable by mobile |
| Data/auth/files | Supabase PostgreSQL, Auth, private Storage | SQL migrations and coherent access policies |
| Data client | Supabase JS, generated DB types, SQL RPC for transactions | Preserve caller identity/RLS; one migration system |
| Hosting | Two Vercel projects, gated GitHub Actions | Separate domains, credentials and release targets |
| UI | Tailwind; accessible primitives and shadcn/ui for staff controls as useful | Marketing follows reference; dashboard follows workflow |
| Contracts | Zod, OpenAPI and typed client | Reusable validation and integration contract |
| Notifications | Email adapter first; SMS/WhatsApp if selected later | Provider and business sending identity pending |
| Async work | Transactional outbox + scheduled worker with retries | Save leads even if providers fail |
| Mobile | React Native/Expo; provisionally staff operations first | Owner confirms staff versus seller audience before screens |
| Scale | One business with organization-owned records | Clear permissions without premature subscription SaaS |

These are recommendations, not hidden owner approvals. Implement foundations against these defaults and record material substitutions.

## Scope

Plan now. Build all page-family templates in private preview, the backend, staff dashboard, chatbot adapter and selected launch pages next. Launch only after infrastructure, business identity and the chosen routes are approved. Mobile implementation and app-store publication are separate phases.

“A to Z” requires an inventory of reference routes, content families, interactive states and integrations. Ten mock pages do not satisfy it. Enumerating the full site is the first implementation phase. Every discovered route then receives an implementation/preview/deferred status; do not claim all source URLs are replicated without that evidence.

Paid vehicle reports, VIN data and exact cash valuations require provider access/business rules. Design these screens privately and document adapters. Never fabricate report or offer results to make a mock appear functional.

## Launch inputs

Business name/logo, phone/email, legal entity, actual areas/hours/title rules, offer process, consent/legal text, final ten routes, team roles, provider accounts, chatbot implementation and mobile audience remain owner decisions. See [readiness](08-readiness-and-open-inputs.md).

## Success

Accepted submissions are stored once, visible only to authorized staff, attributable and auditable. Visitors cannot read leads or drafts. Development never contacts real sellers. Production is approved explicitly. Every page family has visual/functional evidence and named external dependencies.
