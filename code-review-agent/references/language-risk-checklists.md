# Language And Surface Checklists

Use these prompts to focus review. Do not mechanically report checklist items without evidence.

## TypeScript And JavaScript

- Verify async paths await required promises and handle rejection.
- Check `undefined`, `null`, empty arrays, optional fields, and JSON parse failures.
- Check type narrowing around unions, `any`, casts, non-null assertions, and unchecked indexed access.
- Review package and lockfile changes for major version shifts, transitive risk, and build/runtime mismatch.
- For Node services, check request validation, error middleware, streaming/body limits, timeouts, and process-level handlers.

## React And Frontend

- Check state synchronization between props, URL, server data, optimistic updates, and local storage.
- Verify loading, empty, error, permission-denied, and stale-data states.
- Check event handlers for stale closures, double submits, disabled states, and cleanup of effects/subscriptions.
- Review accessibility only when behavior regresses: focus order, keyboard access, labels, contrast, live regions, and motion.
- Check that user-controlled content is escaped and unsafe HTML is justified.

## Python

- Check mutable defaults, timezone-aware datetime handling, path traversal, broad exception swallowing, and resource cleanup.
- Review dependency and environment changes for interpreter/version compatibility.
- Check ORM queries for N+1 behavior, transaction boundaries, locking, and migration compatibility.
- Verify type hints do not mask runtime shape differences from dictionaries, JSON, or external APIs.

## Go

- Check ignored errors, context propagation, goroutine leaks, channel close/send races, and data races around shared maps/slices.
- Verify `defer` placement in loops and resource cleanup.
- Review pointer/value receiver changes and nil interface behavior.
- Check JSON tags, zero values, and backward compatibility for structs used over the wire.

## Java And Kotlin

- Check nullability boundaries, collection mutability, exception translation, thread-safety, and transaction annotations.
- Review serialization changes for API or persisted compatibility.
- Check dependency injection lifecycle, singleton state, and test fixture realism.

## SQL, Schemas, And Migrations

- Verify expand-and-contract compatibility when old and new app versions may run together.
- Check locks, table scans, index creation strategy, defaults, backfills, and rollback plan.
- Confirm uniqueness, foreign keys, check constraints, and cascade behavior match application assumptions.
- Check data migrations for idempotency and restart safety.

## APIs And Integrations

- Check auth, resource ownership, rate limits, pagination, retries, idempotency keys, error mapping, and timeout behavior.
- Verify request/response schemas remain compatible with old clients.
- Check webhook signature verification, replay handling, ordering, and duplicate delivery.

## Infrastructure And Configuration

- Check secrets handling, environment-specific defaults, IAM/permission changes, network exposure, and logging level changes.
- Review CI/CD, Docker, Terraform, Kubernetes, and feature flag changes for rollout and rollback behavior.
- Confirm config defaults fail closed for auth, payments, destructive actions, and production data access.

## Tests

- Prefer behavior tests that fail on the reviewed regression path.
- Check that mocks preserve important production behavior such as latency, errors, retries, permissions, and serialization.
- Watch for snapshots that bless wrong output without asserting meaning.
- Check flaky timing, sleeps, ordering assumptions, and reliance on test execution order.
