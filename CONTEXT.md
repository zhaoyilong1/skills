# Skills

This context names the review-agent concepts used by the skills in this repository.

## Language

**Code Review Agent**:
A skill that reviews code changes for merge risk by checking intent, repository standards, and defects before reporting actionable findings.
_Avoid_: review bot, lint agent

**Hybrid Review**:
A review model that checks Spec, Standards, and Risk as separate inputs, then reports the final result defect-first by severity.
_Avoid_: two-axis review, general review

**Triage Lane**:
A reporting category that separates proven Findings, blocking Open Questions, and important Residual Risks after broad review discovery.
_Avoid_: bucket, category

**Finding Gate**:
The evidence, impact, fixability, and confidence check a candidate concern must pass before it can be reported as a Finding.
_Avoid_: confidence score, severity gate

**Spec Source**:
The issue, PR description, design doc, ticket, or inferred intent that explains what a code change was meant to do.
_Avoid_: requirement doc, prompt

**Standards Source**:
A repository-local document or convention that defines how code should be written in that repo.
_Avoid_: style guide when the source also includes architecture or testing rules

**Substantial Review**:
A review whose size, risk, or ambiguity justifies isolated review passes rather than one inline pass.
_Avoid_: big PR

**Finding**:
A high-confidence review comment tied to a concrete code path, impact, and corrective action.
_Avoid_: nit, suggestion, concern

**Residual Risk**:
An important plausible concern that should be visible to the user but does not meet the Finding Gate.
_Avoid_: weak finding, nit

**Self-Check**:
The final review pass that deduplicates, downgrades weak claims, verifies severity, and confirms actionability before output.
_Avoid_: polish pass, summary check
