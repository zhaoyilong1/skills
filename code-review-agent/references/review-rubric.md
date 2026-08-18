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

When any of these are missing, route the concern through Triage Lanes instead of forcing it into Findings:

- If the uncertainty blocks review confidence, make it an Open Question.
- If the concern is important but unproven, make it a Residual Risk.
- If the concern is low-impact, mostly style, or speculative, omit it.

## Finding Gate

Before reporting a Finding, verify all four gates:

- `Evidence`: the failing path is supported by code, tests, docs, schema, API contract, runtime behavior, or a clear source-to-sink trace.
- `Impact`: the issue can affect users, callers, data, security, reliability, compatibility, operations, or future changes in a concrete way.
- `Fixability`: the author can take a specific corrective action or add a specific test.
- `Confidence`: the claim is strong enough to state as a defect rather than a possibility.

If any gate fails, do not report it as a Finding. Move it to an Open Question or Residual Risk, or omit it if it is low value.

## Triage Lanes

Use broad recall to discover candidate concerns, then sort them:

- `Findings`: high-confidence defects that pass the Finding Gate. These can block merge when severity warrants it.
- `Open Questions`: uncertainty that blocks confidence and requires user, product, spec, or author input.
- `Residual Risks`: important plausible concerns that may matter but are not proven enough to be Findings.
- `Omit`: preferences, low-impact speculation, duplicate concerns, and issues already handled by tooling.

Keep Residual Risks short. They should preserve important review context without sounding like disguised Findings.

## Self-Check

Before final output:

- Dedupe overlapping findings and keep the strongest representative.
- Downgrade weak Findings into Open Questions or Residual Risks.
- Verify severity against realistic merge risk.
- Confirm each Finding has evidence, impact, and a concrete fix or test direction.
- Remove style-only comments unless they hide a correctness or maintenance risk.
- Ensure the output stays Findings First rather than a full Spec/Standards/Risk report.

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
- Do not use Residual Risks as a back door for low-confidence Findings.

## Approval Guidance

Use one of these conclusions:

- `Approve`: No blocking findings and validation is adequate for the change size.
- `Approve with nits`: Only optional or cosmetic issues remain.
- `Request changes`: At least one `P0` or `P1`, or validation reveals a failing required check.
- `Conditional approval`: The change looks sound, but a specific missing validation step should run before merge.

Residual Risks alone do not require changes unless they expose a specific validation step that should run before merge.
