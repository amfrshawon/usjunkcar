# Database, authorization and data operations

## Conventions

PostgreSQL with SQL migrations; UUID IDs, UTC `timestamptz`, explicit foreign keys and constraints. Display appointment times in their stored IANA timezone. Use integer minor currency units with ISO currency (USD initially), never floats. Phone numbers are normalized server-side. VIN is optional at intake and validated if present. One lead represents one vehicle opportunity; duplicate people/vehicles can have later legitimate opportunities.

All business records carry `organization_id`. Initially one organization is seeded; no public organization-creation or billing system. Organization and role come from verified membership, never a body parameter. Membership/status are checked from authoritative DB data on each sensitive action so role revocation does not wait for a token to expire.

## Entity contract

| Table | Important fields | Rules/indexes |
| --- | --- | --- |
| `organizations` | id, name, business_config | One initial business; owner-managed |
| `profiles` | user_id → auth user, display_name, active | No role self-editing |
| `memberships` | org_id, user_id, role, active | Unique org/user; role enum |
| `leads` | id, org_id, public_reference, contact_name, phone, email?, status, source, assigned_to?, version, created_at, updated_at | Unique opaque reference; org/status/created and assignee/status indexes |
| `contact_requests` | id, org_id, public_reference, name, phone?, email?, message, status, assigned_to?, linked_lead_id?, version, created_at, updated_at | At least one usable contact method; new/in_progress/resolved/spam; no vehicle required |
| `lead_vehicles` | lead_id, year?, make?, model?, VIN?, mileage?, condition, title_status, running_status | One per lead initially; constrained enums, unknown allowed |
| `lead_locations` | lead_id, ZIP, city?, state?, pickup_address?, timezone | Full address only when operationally needed |
| `lead_attribution` | lead_id, first/last UTM fields, landing_path, referrer_host, campaign IDs? | Length limits; no full sensitive referrer URLs |
| `lead_consents` | lead_id, purpose, channel, consent_value, policy_version, text_version, recorded_at, source | Append-only evidence; distinguish service contact and marketing |
| `lead_events` | id, org_id, lead_id, actor_type/id, event_type, safe payload, timestamp | Append-only; no raw secrets/whole request bodies |
| `lead_notes` | org_id, lead_id, author_id, body, edited_at | Authorized staff; changes audited |
| `lead_tasks` | lead_id, assignee, due_at, state, type | Due-task index; reminders through outbox |
| `lead_offers` | lead_id, amount_minor, currency, status, expiry, approved_by | Offer lifecycle; revisions retained, no overwrite of accepted offer |
| `appointments` | lead_id, starts_at, ends_at, timezone, status, assigned_team? | End > start; scheduled only after confirmation |
| `lead_files` | org_id, lead_id, storage_key, mime, bytes, checksum, scan_status | Private bucket; quarantine until validated |
| `conversations` | id, org_id, lead_id?, channel, provider_session_id?, session_hash, state | Visitor credential hash; no list access to visitors |
| `conversation_messages` | conversation_id, role, content, provider_message_id?, created_at | Unique provider ID where available; bounded retention |
| `chat_tool_executions` | conversation_id, tool, idempotency_key, actor, result_state, timestamp | Server-validated tools; audit without secret payloads |
| `outbox_jobs` | id, org_id, kind, entity_id, dedupe_key, state, attempts, next_attempt_at, lease_until, error_code | Unique dedupe key; claim via lock/lease; bounded retries |
| `webhook_receipts` | provider, environment, event_id, received_at, processed_at | Unique provider/environment/event; signature verified first |
| `idempotency_records` | scope, key_hash, request_hash, response_code, response_body_safe, expires_at | Unique scope/key; different body for same key → conflict |
| `page_revisions` | page_id, revision, structured_content, state, approved_by/at | Immutable approved revisions; no public draft read |
| `publication_records` | path, revision, release_sha, owner_approval, published_at | Reconciles with Git allowlist; cannot add route alone |
| `audit_logs` | org_id, actor, action, resource, timestamp, request_id | Role/export/publication/settings changes; append-only |
| `device_registrations` (mobile phase) | user_id, platform, token, last_seen, revoked_at | Revoke logout; no sensitive push payloads |

Add composite organization-aware FKs where necessary so a lead in one org cannot reference another org's staff/file/record. Index foreign keys and query/filter paths. Define delete behavior explicitly; normal business deletion is an authorized retention/redaction workflow, not cascading accidental destruction.

Contact requests have the same staff assignment, tenant isolation and consent-evidence requirements as leads. Use a dedicated `contact_request_consents` table with the evidence fields above and a constrained contact-request foreign key. Save contact request, consent and notification outbox job atomically. Record staff changes in audit logs. Conversion to a vehicle lead is explicit, transactional and links the records; retain the original message and consent history without automatically expanding consent.

## Role matrix

| Operation | Owner | Admin | Manager | Agent | Viewer |
| --- | --- | --- | --- | --- | --- |
| Read leads | All | All | All | Assigned | Aggregates/redacted only |
| Notes, contact, permitted status changes | Yes | Yes | Yes | Assigned | No |
| Assign/reassign and bulk actions | Yes | Yes | Yes | No | No |
| Approve offer / pickup | Yes | Yes | Yes | Propose only | No |
| Export PII | Yes | Explicit permission | No by default | No | No |
| Manage team/roles | Yes | Limited; cannot grant owner | No | No | No |
| Business settings | Yes | Explicit permission | No | No | No |
| Preview draft content | Yes | Yes | Explicit editor permission | No | No |
| Authorize production/publication | Owner only | No | No | No | No |

## Enforcement layers

Verify sessions server-side; do not trust a browser-provided role. Apply service-level permissions and RLS on every business table/storage object. Staff requests use the caller's authenticated client/JWT so RLS remains effective. Private reads use no-store caching and must never be embedded in public cached pages.

Anonymous visitors cannot read/update leads or write tables directly. A narrowly scoped public-intake service validates input, abuse checks and allowed fields, then calls a constrained transaction to create records. A service credential can bypass RLS: limit it to explicit intake/worker code, never expose it to clients or use it to skip staff authorization. Privileged SQL functions have a fixed search path, constrained execution grants and no dynamic SQL from input. Test that the publishable key alone cannot invoke privileged functions.

Invite staff; no public staff sign-up. Require owner/admin MFA before production. Rate-limit authentication and intake; use CSRF protection for cookie-authenticated state changes, strict same-origin checks, sensible CSP and secure cookies. Bearer-token mobile calls still require authentication/authorization; CORS is not an access-control substitute.

## Lead durability, duplicates and uploads

The submission transaction creates lead, vehicle/location, consent evidence, attribution, initial event and outbox notification. A transaction failure returns failure and creates no partial lead. Idempotency prevents retry duplicates. Business duplicate detection flags matching normalized phone/VIN/time-window candidates; do not silently discard or merge them. Staff merge records only with an audit trail and preserved source/consent history.

Issue short-lived upload capabilities bound to a submission session or authorized lead. Limit count, type and bytes; verify actual content, scan where supported, reject executables and store outside public buckets. Public upload credentials cannot list/download objects. Staff download links are short-lived and require permission. Remove abandoned uploads on a scheduled retention policy.

## Migrations, retention and recovery

Test migrations from empty DB and from previous release. Development and production project IDs must never match. Use additive expand/contract migrations, deploy compatible code, backfill, then remove obsolete fields in a later approved release. Serialize migrations. Never run resets/seeds on production. Rollback of application code does not roll back data/schema automatically.

Proposed operational targets for owner/provider review: recovery point ≤24 hours and recovery time ≤4 hours. Select a backup plan that meets them and verify a restore to an isolated project before launch. Prefer tighter point-in-time recovery if lead volume warrants it; do not promise unprovisioned features.

Proposed retention pending legal/business approval: unconverted leads 12 months, unlinked chat 90 days, abandoned uploads 24 hours, security/audit events 12 months. Completed transaction records may require a different policy. Implement scheduled purge/redaction, access/export/deletion requests, legal holds where instructed and retention checks for provider copies. Do not treat these proposed periods as legal advice or approved policy.

[Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) is the foundation for database access policies. [Environment management](https://supabase.com/docs/guides/deployment/managing-environments) supports migration-based local/staging/production workflows. The schema and permissions above are this project's design.
