# Hybrid Review Model

Hybrid Review separates the review thinking from the review output.

Think across these inputs:

- `Spec`: what the change was supposed to do.
- `Standards`: how this repository expects code to be shaped, tested, named, and operated.
- `Risk`: what can realistically break for users, callers, data, security, reliability, compatibility, performance, concurrency, or maintainers.

Report defect-first. Do not split the final report into Spec/Standards/Risk unless the user asks. Use the axes to find better findings, then rank findings by merge risk.

## Spec Source

Find the Spec Source before inferring intent. Search in this order:

1. User-provided issue, PR, ticket, spec path, or design doc.
2. PR description and linked issues.
3. Commit messages that mention issues, tickets, or feature names.
4. Changed docs under `docs/`, `specs/`, `.scratch/`, `rfcs/`, or `proposals/`.
5. Files under those directories that match the branch name or main changed feature name.
6. Tests, names, and diff shape.

If no source exists, infer intent and say so in `Review Basis`. Do not block the review merely because no spec exists.

Spec findings include missing behavior, partial behavior, wrong behavior, and scope creep. Quote or cite the source when possible.

## Standards Source

Look for repository-local guidance before using general taste:

- `CONTRIBUTING.md`, `CODING_STANDARDS.md`, `STYLEGUIDE.md`, `DEVELOPMENT.md`
- `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`
- docs under `docs/`, `engineering/`, `architecture/`, or `standards/`
- nearby code patterns and tests

Documented repo standards override generic preferences. If tooling already enforces a rule, skip it unless the changed config disables that enforcement.

Standards findings should still clear the normal finding quality bar: concrete code path, evidence, impact, and corrective action.

## Risk Axis

Always inspect the changed surface for:

- authorization, ownership, and tenant boundaries
- input validation and trust boundaries
- persisted data, migrations, backfills, and rollback
- external APIs, events, queue payloads, webhooks, and wire formats
- retries, idempotency, timeouts, cancellation, and partial failure
- concurrency, locking, caching, and stale data
- secrets, sensitive data, logs, and error messages
- observability, alerts, and debuggability
- tests that prove the risky behavior

Risk findings outrank style findings when the impact is real.

## Substantial Review

Use isolated subagent passes only when they improve signal enough to justify the overhead. Good triggers:

- more than roughly 12 changed files or 500 changed lines
- cross-service or cross-module behavior
- migrations, auth, billing, data deletion, security-sensitive logic, or public APIs
- unclear intent or missing Spec Source for a meaningful change
- large test changes that may hide behavior changes
- high disagreement risk between "matches spec" and "is safe to merge"

Each subagent should receive a pinned snapshot or explicit target, the relevant source material, and one narrow brief. Tell subagents not to invoke `$code-review-agent`, `/code-review`, or additional review agents.

If the worktree may move during review, prefer a saved diff snapshot over a command that recomputes the diff.
