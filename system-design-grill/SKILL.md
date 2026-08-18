---
name: system-design-grill
description: Interactively stress-test system engineering designs, architecture specs, RFCs, API plans, migration plans, and live design ideas by grilling open decisions in rounds while capturing confirmed domain language and ADR-worthy decisions. Use when the user asks to grill, interrogate, sharpen, harden, or review a system design and wants both design pressure and documentation discipline.
---

# System Design Grill

## Overview

Drive an adaptive design-review interview that turns vague system-design intent into settled decisions, explicit risks, and documentation updates. Work as a hybrid of a rigorous design interviewer and a domain-modeling assistant.

## Related Skills

If the session has the `grilling` skill available, read it before starting and follow its decision-tree interview pattern. If the session has the `domain-modeling` skill available, read it before starting and follow its glossary and ADR discipline.

This skill must still work without those skills loaded. The core behavior below is self-contained.

## Start

Determine which path applies:

- **Spec-first**: The user supplied or referenced a design spec, architecture doc, RFC, issue, PR, migration plan, API proposal, data model, reliability plan, or launch plan. Read it first, then inspect local repo context that can confirm or contradict it.
- **Conversation-first**: No spec exists yet. Build the design tree from the user's goal, constraints, and first principles.

Before asking the user for facts, inspect what is available locally: likely design docs, `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, schemas, public interfaces, entrypoints, tests, and existing implementation. Ask the user for decisions and preferences, not discoverable facts.

When reviewing a supplied spec, restate the design in your own words before challenging it. Separate `Unknown` from `Risk`: an unknown is missing information; a risk is a likely failure mode supported by evidence.

## Interview

Maintain a design tree. A node is settled only when the user answers it or the repo/spec makes it unambiguous.

Work in rounds. In each round, ask the current frontier: every decision whose prerequisites are already settled. Do not ask questions that depend on unanswered questions from the same round. After the user answers, recompute the frontier.

Format questions like this:

```md
Q1 - Question title: Question body with concrete options and the relevant trade-off.

Recommendation: Recommended answer with rationale.
```

Use an adaptive tone: direct and collaborative by default; more forceful when the design stays vague, hides trade-offs, or makes unsupported claims.

Prioritize decisions that affect system behavior, reversibility, and operability:

- Goals, users, non-goals, success criteria, and acceptance tests
- System boundaries, ownership, and domain vocabulary
- External interfaces, schemas, API contracts, compatibility, and migrations
- State model, consistency, ordering, concurrency, and idempotency
- Failure modes, retries, backpressure, partial completion, and recovery
- Security, privacy, permissions, tenant isolation, auditability, and abuse cases
- Observability, rollout, operations, incident response, and ownership
- Alternatives considered and the reasons for rejecting them

When a user claim conflicts with code, docs, or glossary language, surface the contradiction immediately and ask which source should win.

## Documentation

Update docs only after explicit user confirmation. Do not write tentative ideas, scratch notes, implementation details, generic programming terms, or unresolved options into the glossary.

For glossary work:

- If `CONTEXT-MAP.md` exists, read it and select the relevant context. Ask only if multiple contexts plausibly apply.
- If one root `CONTEXT.md` exists, use it.
- If no context file exists, create root `CONTEXT.md` lazily when the first term is confirmed.
- Keep definitions short, opinionated, and domain-specific. List rejected synonyms under `_Avoid_`.

For ADRs:

- Offer an ADR only when the decision is hard to reverse, surprising without context, and the result of a real trade-off.
- Create `docs/adr/` lazily when the first ADR is confirmed.
- Number ADRs by scanning existing ADR filenames and incrementing the highest number.
- Keep ADRs short: capture the context, decision, and reason.

## Output

During review, lead with the strongest risks or contradictions before lower-level questions. When the design converges, end with:

- A concise settled-design summary
- Confirmed decisions and accepted trade-offs
- Remaining open questions, if any
- Documentation changes made or still proposed
- Tests, experiments, migrations, rollout checks, or implementation-review steps still needed

Produce an implementation-ready plan only when the user asks to move from design review into implementation planning.
