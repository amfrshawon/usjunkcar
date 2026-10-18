# Existing AI chatbot and future mobile applications

## Chatbot integration approach

The owner already built a chatbot elsewhere and will share it. Reuse that implementation through an adapter after inspection. Do not assume its provider, model, hosting, session store, tools, prompts or licensing. No production model/provider spend is authorized by this planning document.

Required handoff: repository or export, current website/demo, integration docs, deployment architecture, streaming protocol, auth/session model, tools/webhooks, knowledge sources, prompt versions, human-handoff mechanism, provider limits and error behavior. Credentials are configured directly in secret storage. Record what can be reused and what must change for `usjunkcars.si`.

## Adapter contract

Expose framework-independent operations such as `startConversation`, `streamReply`, `cancelReply`, `submitToolResult`, `handoff` and `verifyWebhook`. Define normalized events (`message_started`, `text_delta`, `tool_requested`, `tool_result`, `message_completed`, `handoff_requested`, `error`) and correlation IDs. Persist messages independently of a browser stream. Web and future mobile use the same conversation API; neither receives provider secrets.

Provider calls run server-side with timeouts, rate limits, token/cost budgets, cancellation and redacted logs. Support a fake adapter for CI and a disabled/provider-unavailable state for development before credentials arrive. A mock does not satisfy the fully operational chatbot milestone.

## Operational capabilities

The bot should explain approved services, qualify a vehicle, check service coverage, collect contact/consent, create a lead, attach permitted information and request staff follow-up. It should summarize conversations for staff and use the current business knowledge revision. It must never claim a lead was saved unless the domain service returned success.

| Tool | Server-side authority | Confirmation / restrictions |
| --- | --- | --- |
| `searchKnowledge` | Approved public knowledge only | Draft content and internal notes excluded |
| `checkCoverage` | Approved coverage lookup | No invented area availability |
| `createLead` | Restricted intake transaction | Seller confirms contact/vehicle summary and required consent |
| `updateIntake` | Only the caller's scoped in-progress intake | Cannot update arbitrary leads or staff-only fields |
| `getOfferGuidance` | Approved deterministic rules if supplied | No fabricated binding offer; otherwise ask staff |
| `requestPickup` | Records preference/request | Does not guarantee a slot; staff approval required until scheduling rules exist |
| `requestHumanHandoff` | Durable handoff event/outbox | Honest availability and response wording |
| `getSubmissionReceipt` | Scoped opaque receipt | No unrestricted lead lookup/search |

The model proposes tool calls; code validates schema, session, organization, permissions, current state and idempotency before execution. Prompt text cannot grant permissions. Treat visitor messages, retrieved documents and tool outputs as untrusted data. Keep staff/private knowledge out of the public bot retrieval collection. Tool retries must not duplicate leads, messages, appointments or notifications.

Do not allow arbitrary SQL, file paths, URLs, shell execution or general webhooks from the model. Restrict knowledge ingestion to approved sources and isolate it from public runtime input. Show the AI identity and a usable form/contact alternative. Human takeover pauses automated replies until staff explicitly releases the conversation.

## Knowledge and acceptance

Version service areas, opening hours, contact details, supported vehicle/title rules, FAQs and pricing explanations. Record source owner, approval and last revision; reindex when approved content changes. Never use the source site's prices/reviews as new-business truth.

Test: happy-path qualification; missing/unknown facts; outside coverage; no consent; prompt injection asking for another customer's lead; duplicate tool calls; provider timeout; interrupted streaming; reconnect; invalid tool data; webhook replay; staff takeover; storage failure; spend-limit exhaustion; redaction and retention. A seller submission must create exactly one staff-visible lead and an auditable conversation link. Test the real shared bot before calling this milestone complete.

## Mobile plan

Use React Native with Expo/Expo Router as the default proposal. Confirm the audience before design: (A) staff app for responding to leads and pickups, (B) seller app for requests/status/photos, or (C) both as separately scoped experiences. Provisionally prioritize staff; this assumption is not permission to build a customer account product.

Share TypeScript DTOs, validation, API client, status definitions and business rules. Build native UI, not a mandatory embedded copy of the website. Keep `/api/v1` independent of web-only cookies/Server Actions.

| Stage | Scope | Exit requirement |
| --- | --- | --- |
| Foundation during web build | API versioning, auth strategy, stable DTOs, upload flow | Contract tests from a non-browser client |
| Mobile design | Confirm audience; navigation, offline and notifications | Owner-reviewed screens and privacy/data scope |
| Staff app MVP (proposed) | Login/MFA, assigned leads, details, notes, tasks, status, photos | Permissions match web; iOS/Android device testing |
| Advanced operations | Push, pickup workflow, limited offline queue | Idempotent replay and conflict handling |
| Store distribution | Signing, app IDs, privacy disclosures, beta builds | Owner approval for each store release |

Mobile auth uses provider-supported PKCE/token flows and OS secure credential storage. Test refresh/revocation, logout and account disablement. Use universal/app links on `usjunkcars.si` with environment-specific identifiers; confirm app IDs/team IDs later. Never put access tokens or lead PII in deep links. Native calls use bearer auth; do not weaken authorization to accommodate CORS.

Push notifications contain a generic event and opaque reference, not phone numbers, addresses or VINs. Fetch detail after authentication. Offline MVP defaults to minimal read caching; later queued writes carry an idempotency key and expected version, and conflicts require user resolution. Encrypt any necessary sensitive local data and clear it on logout. No production data in mobile debug logs.

Backend support must outlive old app binaries. Additive API changes first, announce deprecations and enforce minimum versions only through an approved migration plan. EAS/build distribution is separate from the web `dev`/`main` pipeline and cannot auto-publish to stores from a web merge.

[Expo Router documentation](https://docs.expo.dev/router/introduction/) is the implementation reference for the proposed native navigation stack. This document selects a direction; it does not create mobile apps or developer accounts.
