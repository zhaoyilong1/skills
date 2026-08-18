# Skills

This context names the review-agent concepts used by the skills in this repository.

## Language

**Code Review Agent**:
A skill that reviews code changes for merge risk by checking intent, repository standards, and defects before reporting actionable findings.
_Avoid_: review bot, lint agent

**Hybrid Review**:
A review model that checks Spec, Standards, and Risk as separate inputs, then reports the final result defect-first by severity.
_Avoid_: two-axis review, general review

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
