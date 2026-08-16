---
name: tech-lead-design-review
description: Review, critique, self-audit, or improve technical design docs, architecture proposals, system designs, RFCs, migration plans, API designs, data models, reliability plans, launch plans, and cross-team engineering proposals. Use when the user asks for Tech Lead-level design review, design-system thinking, architecture risks, review questions, a self-review checklist, or help turning a design into a rigorous review conclusion.
---

# Tech Lead Design Review

## Core Frame

Use the 10-part review path:

```text
Goal -> Boundary -> Data -> Reliability -> Evolution -> Security -> Observability -> Release -> Ownership -> Risk
```

Mnemonic:

```text
Is it worth it? Can it hold? Who owns it? Where can it fail?
```

The purpose is not to ask every possible question. The purpose is to expose the few risks most likely to make the design fail.

## Default Workflow

1. First restate the design in your own words before judging it.
2. Identify the highest-risk review areas for this design type.
3. Review each selected area using evidence from the design, code, metrics, incidents, schemas, APIs, or operational constraints.
4. Separate uncertainty from risk:
   - `Unknown`: the design does not say enough yet.
   - `Risk`: the design says enough to reveal a likely failure mode.
5. Convert observations into actionable changes.
6. End with a review conclusion: pass, conditional pass, or revise and review again.

## Review Areas

Use these areas as the working checklist.

### 1. Goal

Ask what problem the design solves, who benefits, why it matters now, how success will be measured, and which goal wins when goals conflict.

Watch for solution-first framing such as "introduce Kafka", "split into microservices", or "rewrite the service" without a clear user, business, or engineering outcome.

### 2. Boundary

Ask what is in scope, what is explicitly out of scope, what the system owns, what it depends on, and what external callers can rely on.

Watch for scope creep, temporary requirements becoming permanent capabilities, and APIs that expose internal implementation details.

### 3. Data

Ask what the core entities are, who owns each piece of data, what the source of truth is, how states transition, what consistency is required, and how data is migrated, corrected, deleted, and audited.

Watch for overloaded status fields, missing uniqueness constraints, unclear state machines, and multiple writers for the same source-of-truth data.

### 4. Reliability

Ask what happens when each critical step fails, which operations must be idempotent, how timeouts and retries work, what can be degraded, and how partial success is repaired.

Watch for happy-path-only diagrams, retries without idempotency, unbounded waits, silent background task failures, and "timeout means failure" assumptions.

### 5. Evolution

Ask what is likely to change in the next 6 to 12 months, which changes are confirmed, which are probable, and which are speculative.

Watch for both under-design and over-design: no extension point where change is likely, or heavy abstractions built for imagined futures.

### 6. Security

Ask how identity, authorization, resource ownership, tenant isolation, sensitive data handling, secrets, abuse prevention, and audit logs are handled.

Watch for frontend-only permission checks, resource IDs without ownership checks, logs containing secrets or sensitive data, and "internal means trusted" assumptions.

### 7. Observability

Ask how an engineer would investigate a real user complaint, which logs and IDs exist, which business and technical metrics matter, whether traces cross service and async boundaries, and whether alerts are actionable.

Watch for dashboards that do not guide action, missing request or trace IDs, `UNKNOWN_ERROR` everywhere, and background jobs that fail silently.

### 8. Release

Ask how the design moves from current state to target state, how it is gated, how data changes are migrated, how old callers remain compatible, how rollback works, and what metrics decide pause, continue, or rollback.

Watch for final-state-only designs, database changes that cannot be rolled back, missing old-client compatibility, and feature flags without cleanup plans.

### 9. Ownership

Ask who owns the system long-term, who is on call, who repairs data, where the runbook lives, how cross-team contracts are maintained, and whether knowledge is shared.

Watch for vague group ownership, alerts sent to unattended channels, manual database repair as the only fix path, and critical systems understood by one person.

### 10. Risk

Ask why the project would fail in a future postmortem, which assumptions are load-bearing, how those assumptions can be tested, who owns each risk, and what the stop-loss plan is.

Watch for "no known risks", vague risk statements, risks without owners, and mitigations that only say "add more tests".

## Output Format

For a review, lead with the most important issues. Use this structure:

```md
## Review

Conclusion: Pass / Conditional pass / Revise and review again

Highest-risk gaps:
- [Area] Finding. Evidence. Why it matters. Required action.

Questions:
- Question that blocks confidence.

Accepted tradeoffs:
- Tradeoff and why it is acceptable.

Next actions:
- Action, owner if known, and timing.
```

For a self-audit or workbook request, use this per-question structure:

```md
Question:
Status: OK / Unknown / Risk / Action / N/A
Judgment:
Evidence:
Question:
Action:
```

## Deep Reference

For detailed explanations, examples, self-audit prompts, and review templates, read:

```text
references/design-review-handbook.md
```

Read the reference when the user asks for a detailed handbook, wants to think through each question one by one, asks for teaching material, or provides a design that deserves a deep review.
