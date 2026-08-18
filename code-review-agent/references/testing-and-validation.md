# Testing And Validation

## Choosing Checks

Start from the repo's own signals: package scripts, CI config, Makefile, task runner, language manifests, and nearby test files. Prefer focused checks first, then broader checks when the change touches shared behavior.

Common checks:

- JavaScript/TypeScript: `npm test`, `npm run test`, `npm run typecheck`, `npm run lint`, `pnpm test`, `pnpm typecheck`, `yarn test`.
- Python: `pytest`, `python -m pytest`, `ruff check`, `mypy`, project-specific tox/nox tasks.
- Go: `go test ./...`, `go test ./path`, `go vet ./...`.
- Rust: `cargo test`, `cargo clippy`, `cargo check`.
- Java/Kotlin: `./gradlew test`, `./mvnw test`, `mvn test`.

Run the narrowest command that proves or disproves the suspected issue. If the change touches shared contracts, migrations, auth, serialization, or core libraries, broaden validation.

## When Tests Fail

Classify failures before reporting:

- Fails because of this change: include as a finding with command output summarized.
- Fails because the environment is missing dependencies or services: state the blocker and avoid overclaiming.
- Pre-existing failure: mention as validation noise only when it limits confidence.
- Flaky or timing-sensitive failure: rerun once if cheap, then report uncertainty.

## When Tests Are Missing

Treat missing tests as a finding only when a concrete regression path exists and a test would be the expected safety net. State the exact behavior that should be covered.

Good:

```text
The new fallback returns cached data across tenant IDs; add a test that requests the same object ID from two tenants and verifies isolation.
```

Weak:

```text
Add more tests.
```

## Validation Integrity

Do not let a passing test suite override code evidence of an untested path. Do not let a failing unrelated check become a code finding.

If a command cannot be run, say why. Examples: dependency missing, service unavailable, no test command found, generated files absent, or repo too large for the current task.

For reviews in GitHub, include CI status separately from local validation when available.
