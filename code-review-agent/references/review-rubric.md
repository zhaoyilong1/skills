# Review Rubric

## Severity

Use severity to communicate merge risk.

- `P0`: Must block immediately. Causes data loss, security compromise, severe outage, billing corruption, or a release-stopping incident.
- `P1`: Should block merge. A realistic user, API, data, security, reliability, compatibility, or operational path breaks.
- `P2`: Should fix soon. Meaningful correctness, maintainability, observability, or test gap with moderate blast radius or clear future failure pressure.
- `P3`: Optional improvement. Do not include in normal review unless the user asks for polish or cleanup.

Prefer fewer, stronger findings. One proved `P1` is more useful than ten speculative comments.

## Finding Quality Bar

A review finding must include:

- A specific changed behavior or newly exposed path.
- A file/line reference tight enough for the author to act.
- Evidence from code, tests, docs, schema, API contract, or runtime behavior.
- Impact stated in user, caller, data, security, or operational terms.
- A plausible fix or test direction.

Downgrade to an open question when any of these are missing:

- The code path may be impossible.
- The intended behavior is unclear.
- The concern depends on unstated product requirements.
- The issue is mostly style or preference.

## Common High-Value Findings

- Changed authorization checks allow cross-user, cross-tenant, or privilege escalation.
- A migration, backfill, or schema change is not backward-compatible with existing code.
- A public API, event, queue payload, CLI flag, or persisted format changes without compatibility handling.
- A retry or background job can duplicate side effects because the operation is not idempotent.
- A timeout, cancellation, or partial failure path leaves durable state inconsistent.
- New code assumes non-null, non-empty, ordered, unique, or trusted inputs without enforcement.
- A cache is updated, invalidated, or keyed incorrectly.
- A concurrency path races on shared memory, database rows, files, locks, or external side effects.
- Sensitive values are logged, returned to clients, embedded in errors, or stored without controls.
- Tests assert implementation details while missing the behavior that can regress.

## Review Anti-Patterns

- Do not summarize the diff before findings unless the user asked only for a summary.
- Do not comment on formatting handled by automated tools.
- Do not request broad refactors when a narrow fix resolves the risk.
- Do not mark missing tests as severe unless the untested path is risky and realistically breakable.
- Do not present a best-practice preference as a bug.
- Do not claim a security issue without tracing resource ownership, trust boundary, or data exposure.
- Do not ignore generated files, lockfiles, migrations, configuration, feature flags, or deployment files when they affect runtime behavior.

## Approval Guidance

Use one of these conclusions:

- `Approve`: No blocking findings and validation is adequate for the change size.
- `Approve with nits`: Only optional or cosmetic issues remain.
- `Request changes`: At least one `P0` or `P1`, or validation reveals a failing required check.
- `Conditional approval`: The change looks sound, but a specific missing validation step should run before merge.
