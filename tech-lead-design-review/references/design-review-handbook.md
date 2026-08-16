# Tech Lead Design Review Handbook

> Review path:
>
> **Goal -> Boundary -> Data -> Reliability -> Evolution -> Security -> Observability -> Release -> Ownership -> Risk**
>
> Short version:
>
> **Is it worth it? Can it hold? Who owns it? Where can it fail?**

This handbook is for reviewing an existing technical design slowly and deliberately. It is not a ritual checklist. It is a way to turn "this looks fine" into sharper engineering judgment.

When reviewing a design, do not start by trying to prove that the design is wrong. Start by understanding it. Then look for the assumptions and failure modes that matter most.

---

## 0. How To Review An Existing Design

Use three passes.

### Pass 1: Understand, Do Not Judge

Read the design once without evaluating it.

Write:

```md
My understanding of the design:

Problem it solves:
Core approach:
Critical path:
Main dependencies:
Largest unknown:
```

If you cannot write this summary, you do not understand the design yet. Keep reading or ask clarifying questions before judging details.

### Pass 2: Mark Status

Use these statuses while reviewing:

```md
OK: The design explains this clearly and gives evidence.
Unknown: The design does not say enough yet.
Risk: The design reveals a likely failure mode.
Action: The design must change, test something, or add a missing plan.
N/A: This question does not apply.
```

Do not confuse `Unknown` with `Risk`.

`Unknown` means "I do not know yet."  
`Risk` means "I see something that can break."

That difference keeps the review fair.

### Pass 3: Answer Important Questions In Four Lines

For each important question, write:

```md
Judgment:
Evidence:
Question:
Action:
```

Example:

```md
Question: What happens on rollback?

Judgment:
The design does not yet have a safe rollback plan.

Evidence:
The new code writes an order_status value that the old service does not recognize.

Question:
When the old service reads the new status, does it fail, ignore it, or use a default path?

Action:
Make the old service compatible with the new status before enabling writes.
```

This format is small but powerful. It separates your opinion, the evidence, the open question, and the next move.

### Do Not Review Everything Equally

Choose the areas with the highest risk density.

For a small admin UI, focus on:

- Security
- Data
- Release
- Observability

For payments, billing, orders, identity, or permissions, focus on:

- Data
- Reliability
- Security
- Release
- Risk

For a new platform, service, or architecture, focus on:

- Goal
- Boundary
- Evolution
- Ownership
- Risk

The goal is not to ask more questions. The goal is to find the questions that matter.

---

## 1. Goal

### One-line Purpose

Goal review means translating the proposed solution back into value.

Many designs begin with a solution:

- Introduce Kafka.
- Split the monolith.
- Rewrite the order service.
- Add a new recommendation service.

These are actions, not goals. A Tech Lead should ask: why do this, for whom, and how will we know it worked?

### What You Need To Decide

```md
Problem:
Why it matters:
User or stakeholder:
Success measure:
Cost of not doing it:
Priority when goals conflict:
```

### Question 1: Who Is The User?

Do not assume the user is always the end customer.

The user may be:

- A consumer
- A merchant
- Operations
- Customer support
- Another engineering team
- An analyst
- An upstream system
- A downstream system

Ask who directly feels the improvement or the failure.

Write:

```md
Primary user:
Secondary users:
Most affected party:
```

If the user is unclear, the goal is probably unclear.

### Question 2: What Is The Current Problem?

Avoid vague claims:

```md
The system is slow.
The experience is bad.
The architecture is messy.
Reliability needs improvement.
```

Ask what is slow, bad, messy, or unreliable.

Better:

```md
The order confirmation page has a p95 latency of 4.8 seconds. During peak traffic, 3 percent of requests exceed 10 seconds, which causes duplicate submissions and support tickets.
```

Specific problems make technical tradeoffs easier.

### Question 3: What Evidence Shows This Is Worth Doing?

Look for:

- Metrics
- User feedback
- Support tickets
- Incident reports
- Cloud or vendor costs
- Development cycle time
- Error rates
- Business growth forecasts

If evidence is weak, say that honestly:

```md
Evidence is limited. This is currently a product judgment rather than a measured problem.
```

That is acceptable. Pretending weak evidence is strong evidence is not.

### Question 4: Why Now?

Some work is right but not urgent.

Ask:

- Did traffic grow?
- Did an incident happen?
- Is a business launch blocked?
- Is the old system blocking delivery?
- Is there now a team ready to maintain the change?
- Are upstream and downstream teams available now?

If there is no timing reason, priority should be questioned.

### Question 5: What Is The Success Standard?

"Ship it" is not a success standard.

Useful standards include:

- p95 latency below a target
- Error rate below a target
- Payment success rate preserved
- Cost reduced by a measurable amount
- Support tickets reduced
- Development lead time reduced
- Operational manual work reduced

Example:

```md
Goal:
Reduce order confirmation p95 latency from 4.8 seconds to below 1 second.

Constraint:
Billing accuracy must not regress.

Validation:
For one week after launch, p95 stays below 1 second and billing discrepancy rate remains at or below the current baseline.
```

### Question 6: Which Goal Wins When Goals Conflict?

Design goals often conflict:

- Speed vs accuracy
- Simplicity vs extensibility
- Cost vs reliability
- User experience vs fraud control
- Launch speed vs long-term architecture

Write:

```md
Most important goal:
Second goal:
Can sacrifice:
Cannot sacrifice:
```

Without priority, design discussion drifts.

### Red Flags

- The design starts with a technology choice instead of a problem.
- Success means "we launched."
- No observable outcome is defined.
- Different stakeholders disagree on the goal.
- The solution is heavy but the problem is not proven.

### Exit Standard

You can say:

```md
We are doing this so that [user] can do [thing] better in [scenario], and we will know it worked when [measure] changes.
```

---

## 2. Boundary

### One-line Purpose

Boundary review means turning "we could do everything" into "this system owns these responsibilities and not those."

Clear boundaries protect the system from slow complexity growth.

### What You Need To Decide

```md
In scope:
Out of scope:
Owned by this system:
Not owned by this system:
Upstream dependencies:
Downstream consumers:
Cross-team contracts:
```

### Question 1: What Exactly Is In Scope?

Use concrete scenarios, not vague nouns.

Vague:

```md
Support refunds.
```

Clear:

```md
Allow users to request a full refund from the order detail page.
Allow operations to view refund status in the admin console.
Automatically retry failed refund submissions.
```

Concrete scope makes testing and launch validation possible.

### Question 2: What Is Explicitly Out Of Scope?

Out of scope is not negative. It is how the design stays focused.

Example:

```md
This release does not support:
- Partial refunds
- Cross-currency refunds
- Automatic coupon re-issuance after refund
- Manual refund amount edits by operations
```

Not doing something now does not mean never doing it. It means the current release does not pay that complexity cost.

### Question 3: What Are Inputs And Outputs?

Ask:

- Who calls this system?
- What data enters?
- What does it return?
- What events does it emit?
- What data does it write?
- What external systems does it call?

Inputs and outputs reveal real boundaries.

### Question 4: What Decisions Does This System Own?

A refund system may create refund records and track refund state. It may not own fraud policy, customer credit scoring, customer support approval rules, or financial reconciliation.

Write:

```md
This system decides:
This system executes:
This system displays:
This system never decides:
```

Every new responsibility increases complexity.

### Question 5: How Are Edge Cases Treated?

Every edge case should be classified:

- Support it
- Reject it
- Defer it

Example:

```md
If an order has already shipped, this release rejects self-service refund and directs the user to support.

If payment status is unknown, this release does not submit the refund until payment state is confirmed.
```

Do not let edge cases sneak into the core path without being named.

### Question 6: Are Cross-team Boundaries Clear?

Ask:

- Who guarantees upstream field meanings?
- Who handles downstream failures?
- Who announces API changes?
- Who explains data delay?
- Who owns the SLA?
- Who receives alerts?

Verbal agreement is not enough for critical contracts.

### Red Flags

- No explicit out-of-scope section.
- One service owns unrelated responsibilities.
- Temporary needs become permanent platform capabilities.
- APIs expose internal table structure.
- Cross-team ownership relies on personal relationships.

### Exit Standard

You can say:

```md
This system owns A, B, and C. It does not own D, E, or F. Edge cases are either supported, rejected, or deferred intentionally.
```

---

## 3. Data

### One-line Purpose

Data review means following one piece of core data through its full life.

Code can be refactored. APIs can change. A wrong core data model is much more expensive.

### What You Need To Decide

```md
Core entities:
Entity relationships:
State transitions:
Source of truth:
Consistency requirements:
History and deletion policy:
Migration strategy:
Correction strategy:
```

### Question 1: What Are The Core Entities?

Start with domain concepts, not tables.

In an order system, these may be separate concepts:

- Order
- Payment
- Shipment
- Refund
- Invoice

They do not always need separate tables, but the concepts must be distinct.

Dangerous shortcut: putting everything displayed on one page into one table.

### Question 2: What Identifies Each Entity?

Ask:

- Where is the ID generated?
- Is it globally unique?
- Is there a business key?
- What prevents duplicates?
- Is there a database constraint?

Core data should not rely only on application code "trying not to duplicate."

### Question 3: What Is The Source Of Truth?

For each important field, ask which system owns truth.

Example:

```md
Payment status:
- Source of truth: payment service
- Local order service: cached projection
- Conflict rule: payment service wins
```

If multiple systems can write the same source-of-truth state, data will eventually conflict.

### Question 4: Is The State Machine Clear?

Ask:

- What are the states?
- What is the initial state?
- Which states are terminal?
- Which transitions are allowed?
- Which transitions are illegal?
- Can states move backward?
- Who triggers each transition?

Example:

```md
created -> submitted -> processing -> succeeded
created -> submitted -> failed
failed -> submitted
succeeded is terminal.
```

Watch for one overloaded `status` field:

```md
order.status = paid, shipped, refunded, risk_rejected
```

This mixes payment, fulfillment, refund, and risk.

Better:

```md
payment_status
fulfillment_status
refund_status
risk_status
```

### Question 5: What Consistency Is Required?

Not all data needs strong consistency.

Classify data:

- Immediately consistent
- Eventually consistent
- Temporarily inconsistent but recoverable
- Approximate or analytical

Billing, inventory, and permissions often require stricter consistency. Search indexes, analytics, and recommendations often tolerate delay.

If the design uses queues, caches, or async projections, name the inconsistency window:

```md
After payment succeeds, search index updates may lag by up to 5 minutes.
```

### Question 6: How Is Data Created, Updated, Deleted, And Corrected?

Follow the lifecycle:

- Who creates it?
- What validation happens on create?
- Who can update it?
- Is optimistic locking or versioning needed?
- Is deletion soft, hard, or compliance-driven?
- How do downstream systems learn about deletion?
- How is incorrect data repaired?

Deletion and correction are often missing from designs. They matter.

### Question 7: How Are Historical Data And Migration Handled?

Ask:

- What is old data quality?
- Is dry-run migration needed?
- How are invalid rows handled?
- How is migration verified?
- Can migration be retried?
- What is the fallback if migration fails?

Migration is not just a script. It is part of the system design.

### Red Flags

- Tables mirror page fields instead of domain concepts.
- One status field means too many things.
- No uniqueness constraints.
- Multiple systems write source-of-truth data.
- No state transition diagram.
- No deletion or correction strategy.
- No migration plan for old data.

### Exit Standard

You can explain a core record from creation to deletion: who owns it, who can change it, what states it can enter, how it is audited, and how it is repaired.

---

## 4. Reliability

### One-line Purpose

Reliability review means drawing the failure paths next to the success path.

Real systems fail. Networks shake, databases slow down, third parties time out, messages repeat, users click twice, and workers restart.

Reliability is not "nothing fails." Reliability is "failure stays controlled."

### What You Need To Decide

```md
Critical path:
Failure points:
Idempotency strategy:
Timeouts and retries:
Degradation strategy:
Compensation:
User-visible state:
```

### Question 1: What Is The Critical Path?

Not all paths are equally important.

High-risk paths include:

- Checkout
- Payment
- Refund
- Permission changes
- Data deletion
- Shipment
- Ledger entry
- Login

Critical paths deserve stricter design.

### Question 2: What Happens If Each Step Fails?

For each step ask:

- Does failure affect previous steps?
- What does the user see?
- What data state remains?
- Can it be retried?
- Who retries?
- Is retry safe?

Partial success is the most dangerous case:

```md
Local order created, payment request failed.
Payment provider charged the card, local order remains unpaid.
Refund succeeded externally, local refund state failed to update.
```

Partial success needs reconciliation or compensation.

### Question 3: Which Operations Must Be Idempotent?

Anything that can be retried should be reviewed for idempotency.

Common examples:

- Create order
- Submit payment
- Receive payment webhook
- Start refund
- Consume queue message
- Grant coupon
- Create ledger entry

Ask:

- What is the idempotency key?
- Where is it stored?
- How long is it retained?
- What does duplicate request return?
- What happens under concurrent requests?

Frontend button disabling is not idempotency.

### Question 4: How Do Timeouts And Retries Work?

No timeout can exhaust resources.  
No backoff can amplify incidents.  
No idempotency can corrupt data.

Ask:

- Does every external call have a timeout?
- Does timeout mean success, failure, or unknown?
- How many retries?
- Is there exponential backoff?
- Is there a maximum retry window?
- What state remains after final failure?

Important: timeout does not prove failure. The remote operation may have succeeded after the response was lost.

### Question 5: What Happens When Dependencies Fail?

Options include:

- Degrade to cached or reduced functionality
- Queue work for later
- Circuit-break the dependency
- Rate-limit callers
- Fail fast with a clear user state

Degradation must name what it sacrifices and what it preserves.

### Question 6: How Do Background Tasks Fail?

Ask:

- Is the task retryable?
- Is retry idempotent?
- Does failure alert?
- Is there a dead-letter queue?
- Is manual repair possible?
- Can engineers see backlog?
- Can engineers inspect task history by resource ID?

If background failure is discovered only through user complaints, the design is weak.

### Red Flags

- Only happy path diagrams exist.
- Exceptions all say "return error."
- External calls have no timeout.
- Retries have no idempotency.
- Partial success has no repair path.
- Background jobs fail silently.
- Third-party dependencies have no fallback.

### Exit Standard

You can say what happens when any critical step fails: where the system stops, what the user sees, and how data recovers.

---

## 5. Evolution

### One-line Purpose

Evolution review means separating real change from imagined change.

Too little design creates dead ends. Too much design creates complexity today for a future that may never arrive.

### What You Need To Decide

```md
Likely changes:
Confirmed changes:
Probable changes:
Speculative changes:
Extension points:
Intentionally unsupported changes:
Upgrade path:
```

### Question 1: What Will Change In The Next 6 To 12 Months?

Look at a practical horizon.

Possible changes:

- User volume
- Data volume
- Business rules
- Payment channels
- Regions and languages
- Tenants
- Third-party integrations
- Permission model
- Reporting dimensions

Classify:

```md
Confirmed:
Probable:
Speculative:
```

Design seriously for confirmed changes. Leave clean boundaries for probable changes. Do not pay much complexity for speculation.

### Question 2: Where Does The Business Change Most Often?

Different systems change in different places:

- Orders: promotions and lifecycle rules
- Payments: providers and routing
- Permissions: roles and policies
- Recommendations: ranking strategy
- Reporting: dimensions and filters

Frequent-change areas should be centralized, testable, and easy to reason about.

### Question 3: Is The Abstraction The Right Size?

Too little abstraction makes change painful.  
Too much abstraction makes understanding painful.

Ask:

- Does this abstraction have a real second use case?
- Is a second implementation confirmed or likely?
- Does the abstraction hide a stable concept?
- Can a new engineer understand it?

Bad smell:

```md
There is one payment provider, but the design includes a full plugin framework, dynamic routing rules, and multiple provider layers.
```

Better:

```md
Define a clear PaymentProvider interface. Implement one provider now. Add routing when the second provider is real.
```

### Question 4: Is Configuration Overused?

Configuration helps when behavior must change without deployment. It also makes behavior harder to understand.

Good candidates:

- Thresholds
- Feature switches
- Simple routing
- Basic display text

Poor candidates:

- Complex business workflows
- Ledger correctness rules
- High-risk permission policy
- Untestable combinations

If everything is configurable, nobody knows what production is doing.

### Question 5: Is Capacity Growth Considered?

Ask for order-of-magnitude reasoning:

- Current QPS
- Expected QPS
- Data growth per month or year
- Large table risk
- Hot keys
- Batch job impact
- Cache stampede or eviction risk

Not every design needs a full capacity model, but critical systems need numerical instincts.

### Question 6: What Is The Upgrade Path?

A simple plan is fine when the upgrade path is clear.

Example:

```md
Use one table for the first year because expected data is under 5 million rows.
If data exceeds 20 million rows, partition by tenant_id and created_at.
```

That is more pragmatic than premature sharding and safer than ignoring growth.

### Red Flags

- Three abstraction layers for one implementation.
- Many microservices before the team can operate them.
- Everything is configurable.
- No extension point where change is likely.
- Future requirements are large but unsupported by roadmap or evidence.
- Data growth is not estimated.

### Exit Standard

The design leaves room for likely changes without overpaying for imagined futures.

---

## 6. Security

### One-line Purpose

Security review means looking at the system from the wrong identity.

Imagine a normal user, another tenant's user, an operator, an admin, a script, an internal service, or a leaked token.

### What You Need To Decide

```md
Authentication:
Authorization:
Resource ownership:
Tenant isolation:
Sensitive data:
Secrets:
Audit logs:
Abuse prevention:
```

### Question 1: How Is Identity Proven?

Authentication answers: who are you?

Ask:

- What authentication mechanism is used?
- How are tokens verified?
- What happens when tokens expire?
- How do services authenticate to each other?
- Do internal jobs have identities?
- How are secrets stored and rotated?

Internal systems still need authentication.

### Question 2: How Is Permission Checked?

Authorization answers: can you do this operation?

Ask:

- Are roles defined?
- Are permission points defined?
- Are read, write, delete, export, and admin permissions separate?
- Are bulk operations more restricted?
- Do high-risk operations require approval or confirmation?

Hiding buttons in the UI is not authorization. The server must enforce it.

### Question 3: Is Resource Ownership Checked?

A user may be authenticated and allowed to view orders, but not allowed to view another user's order.

Ask:

- Does every `resource_id` lookup check ownership?
- Do reads include user_id or tenant_id constraints?
- Do updates and deletes also check ownership?
- Do bulk APIs check every item?

Test:

```md
User A calls the API with User B's resource_id. What happens?
```

### Question 4: Is Tenant Isolation Reliable?

In multi-tenant systems, tenant isolation is a core invariant.

Ask:

- Do all queries include tenant_id?
- Does the database layer enforce isolation?
- Do cache keys include tenant_id?
- Do async jobs carry tenant_id?
- Can logs and metrics be filtered by tenant_id?

Cache keys are easy to miss.

### Question 5: How Is Sensitive Data Handled?

Sensitive data includes:

- Phone numbers
- Emails
- Addresses
- Government IDs
- Bank cards
- Tokens
- API keys
- Financial data
- Medical data
- Internal notes

Ask:

- Is encryption at rest required?
- Is display masked?
- Is export allowed?
- Can logs contain this data?
- Can errors reveal it?
- Who can see plaintext?

Logging full request bodies is a common security failure.

### Question 6: Is There Audit Logging?

High-risk actions need traceability.

Audit logs should include:

- Actor
- Time
- Source
- Target
- Action
- Key before/after values
- Success or failure

Audit-worthy operations include:

- Permission changes
- Data export
- Resource deletion
- Refunds
- Ledger changes
- Configuration edits
- Admin login and actions

### Question 7: Is Abuse Prevented?

Ask:

- Is rate limiting needed?
- Is CAPTCHA or fraud control needed?
- Can IDs be enumerated?
- Can login be brute-forced?
- Can expensive exports be abused?
- Can repeated submission cause harm?
- Is abnormal behavior monitored?

Public APIs, login, search, export, SMS, email, and payment endpoints deserve extra care.

### Red Flags

- "This is internal, so no auth is needed."
- Permission is enforced only in the frontend.
- APIs do not check resource ownership.
- There is only one super-admin role.
- Logs include tokens or sensitive fields.
- Tenant filters rely on every developer remembering them.
- Sensitive actions have no audit log.

### Exit Standard

An unauthorized or wrong-tenant actor cannot read or modify data even if they guess IDs, reuse old links, or call internal-looking APIs.

---

## 7. Observability

### One-line Purpose

Observability review means starting from a real user complaint and asking what evidence would be needed.

The problem is not that systems fail. The problem is when they fail and nobody can tell where.

### What You Need To Decide

```md
Key logs:
Business metrics:
Technical metrics:
Trace propagation:
Alerts:
Dashboards:
Runbook:
```

### Question 1: How Would You Investigate A User Complaint?

Imagine support says:

```md
The user says payment failed a few minutes ago.
```

An engineer needs:

- user_id
- order_id
- request_id
- time window
- payment provider
- error code
- service logs
- provider response
- retry history
- state transition history

If these cannot be found, debugging becomes guessing.

### Question 2: Do Logs Have Context?

Useful fields:

- request_id
- trace_id
- user_id
- tenant_id
- resource_id
- operation
- error_code
- dependency
- latency

Critical operations should log:

- Start
- Success
- Failure
- State change

Do not log sensitive data.

### Question 3: Are Error Codes Useful?

Avoid one generic error.

Useful categories:

- Invalid input
- Permission denied
- Resource not found
- Invalid state
- Downstream timeout
- Downstream failure
- Idempotency conflict
- Internal error

Stable error codes help frontend, support, backend, alerts, and dashboards speak the same language.

### Question 4: What Are The Business Metrics?

Business metrics reveal user-visible failure:

- Checkout success rate
- Payment success rate
- Refund failure rate
- Job backlog size
- Import success rate
- Bill generation latency
- Message delay
- Search zero-result rate

A service can be up while the business flow is broken.

### Question 5: What Are The Technical Metrics?

Track:

- QPS
- p50, p95, p99 latency
- Error rate
- Timeout rate
- Retry count
- Queue backlog
- Database connection usage
- Cache hit rate
- CPU, memory, disk, network

Technical metrics show where pressure builds.

### Question 6: Does Trace Cross Boundaries?

Ask:

- Does trace_id flow through gateway, service, queue, worker, and downstream calls?
- Do async jobs preserve trace context?
- Can engineers see which step is slow?
- Can they distinguish client slowness, service slowness, and dependency slowness?

Microservices without trace are expensive to debug.

### Question 7: Are Alerts Actionable?

Good alerts have:

- Owner
- Clear action
- Reasonable threshold
- Context links
- Escalation path
- Low noise

An alert nobody responds to is not really an alert.

### Question 8: Are Background Jobs Visible?

Track:

- Success count
- Failure count
- Retry count
- Backlog
- Oldest queued age
- Dead-letter count
- Per-resource execution history

Background jobs often fail quietly. Design against that.

### Red Flags

- Debugging requires searching random logs.
- No request_id or trace_id.
- Error code is always unknown.
- Only technical metrics exist.
- Alerts have no owner.
- Background jobs fail silently.
- Dashboards are attractive but not actionable.

### Exit Standard

If a user reports "my operation failed," an engineer can find what happened within about 10 minutes.

---

## 8. Release

### One-line Purpose

Release review means designing the path from current state to target state.

A final architecture diagram is not a launch plan.

### What You Need To Decide

```md
Release stages:
Feature flag:
Gray rollout:
Data migration:
Compatibility:
Rollback:
Validation metrics:
Cleanup:
```

### Question 1: Does The Release Need Stages?

Complex changes should be staged:

1. Add new structure without traffic.
2. Shadow-write or dual-write.
3. Backfill historical data.
4. Read from the new path for a small cohort.
5. Expand gradually.
6. Remove old logic.

Not every change needs all stages. Database changes, critical flows, large migrations, and client compatibility usually do.

### Question 2: Is A Feature Flag Needed?

Ask:

- What exactly does the flag control?
- Is rollout by user, tenant, region, percentage, or environment?
- What state does the system enter when the flag is off?
- Does the flag affect writes?
- Who can change it?
- When is it removed?

A feature flag is not just an `if`; it has a lifecycle.

### Question 3: Are Database Changes Compatible?

Safer sequence:

1. Add fields without deleting old ones.
2. Make both old and new code able to read.
3. Dual-write.
4. Backfill.
5. Switch reads.
6. Verify.
7. Clean up old fields.

Dangerous changes:

- Change a field's meaning in place
- Delete a field immediately
- Add non-null constraints without preparation
- Migrate large tables without batching
- Write values old code cannot read

### Question 4: Are Old Clients And Callers Compatible?

Especially for mobile clients, users do not upgrade all at once.

Ask:

- Can old clients call the new API?
- What happens when old clients miss new fields?
- Can the server accept old request formats?
- Is API versioning needed?
- Can downstream event consumers handle new fields?

The server cannot assume the world is on the latest version.

### Question 5: What Does Rollback Actually Roll Back?

Separate:

- Code rollback
- Config rollback
- Data rollback
- Traffic rollback
- Job rollback
- External state rollback

The key question:

```md
After rollback, what happens to data written by the new version?
```

If old code cannot read new data, code rollback may make things worse.

### Question 6: How Is Launch Validated?

Define:

- Which metrics to watch
- How long to watch
- Who watches
- What allows expansion
- What pauses rollout
- What triggers rollback

Example:

```md
After 5 percent rollout, observe for 30 minutes:
- p95 latency no more than 20 percent above baseline
- error rate below 0.5 percent
- payment success rate no lower than baseline
- no new P0/P1 alerts
```

### Question 7: When Is Old Logic Cleaned Up?

Ask:

- When are old fields removed?
- When are old endpoints retired?
- When is the feature flag removed?
- When does dual-write stop?
- Who owns cleanup?

Without cleanup, migrations never really finish.

### Red Flags

- The design only describes final state.
- Rollback means "revert the code."
- Database change and code change are tightly coupled.
- Large migration has no dry run.
- No rollout or validation metrics.
- Old clients are not discussed.
- Temporary logic has no cleanup owner.

### Exit Standard

You can explain how the design launches step by step, and what happens if each step fails.

---

## 9. Ownership

### One-line Purpose

Ownership review means treating the system as a long-term asset, not a project that ends at launch.

Systems without ownership become organizational debt.

### What You Need To Decide

```md
Owner:
Backup owner:
On-call:
Runbook:
Data repair:
Documentation:
Cross-team contracts:
Long-term maintenance cost:
```

### Question 1: Who Owns The System?

Owner means more than a team name.

Ask:

- Who is responsible for long-term quality?
- Who owns architecture evolution?
- Who reviews future requirements?
- Who pays down technical debt?
- Who understands the critical path?

Prefer a named owner or a clear rotation.

### Question 2: Who Is On Call?

Ask:

- Where do alerts go?
- Who handles off-hours incidents?
- How are P0/P1 incidents escalated?
- Who contacts downstream owners?
- Does on-call have access to required tools?

Ambiguity becomes pain during incidents.

### Question 3: Is There A Runbook?

A runbook should include:

- Common alerts
- Debugging entry points
- Dashboard links
- Log queries
- Common repair actions
- Rollback steps
- Contacts
- Data repair flow

Without a runbook, incident response relies on improvisation.

### Question 4: Who Repairs Data?

Ask:

- Who has permission?
- Is there a repair tool?
- Is approval needed?
- Is repair audited?
- Can jobs be replayed?
- Can state be rebuilt from events?

If the only repair path is direct database edits, risk is high.

### Question 5: Are Cross-team Contracts Clear?

Write down:

- API semantics
- Field meanings
- Error codes
- SLA
- Rate limits
- Data delay
- Change notification
- Contacts
- Escalation path

Personal relationships move fast but do not replace contracts.

### Question 6: Is Knowledge Shared?

Ask:

- Is there a design doc?
- Is there an architecture diagram?
- Is there onboarding documentation?
- Are code owners defined?
- Is there a backup maintainer?

If one person leaving makes the system unmaintainable, that is a design risk.

### Red Flags

- Owner is a vague group.
- Alerts go to an ignored channel.
- No runbook.
- Data repair means manual database edits.
- Cross-team dependency is verbal.
- Only one person understands the system.
- No retirement or cleanup plan.

### Exit Standard

You can say who maintains the system, who wakes up when it fails, who repairs data, and who evolves it later.

---

## 10. Risk

### One-line Purpose

Risk review means writing a small postmortem before the project fails.

Assume the project failed three months later. What would the postmortem say?

### What You Need To Decide

```md
Largest risk:
Load-bearing assumptions:
Validation plan:
Mitigation:
Owner:
Stop-loss plan:
Accepted residual risk:
```

### Question 1: Why Would This Design Fail?

Do not write "no known risks."

Common risk types:

- Product risk: people do not use it, or it solves the wrong problem.
- Technical risk: performance, reliability, complexity, or technology choice is uncertain.
- Data risk: migration failure, inconsistency, or poor historical quality.
- Dependency risk: third-party, upstream, or platform dependency is unstable.
- Release risk: cannot gray-rollout, rollback, or support old clients.
- Organizational risk: ownership unclear, team lacks operations capacity, cross-team work is slow.

Specific:

```md
Historical order states may not map cleanly to the new state machine.
```

Too vague:

```md
Migration is risky.
```

### Question 2: Which Assumptions Are Load-bearing?

Examples:

- Third-party API latency is acceptable.
- Historical data is clean enough.
- Traffic growth stays within a certain range.
- Upstream fields arrive on time.
- Old client usage drops quickly.
- The new model covers all business states.

Make load-bearing assumptions explicit.

### Question 3: Can Risks Be Tested Early?

Examples:

- Migration risk: dry run.
- Performance risk: load test.
- Third-party risk: real-call sampling.
- Compatibility risk: old-client regression.
- Product risk: beta or gray rollout.
- Algorithm risk: offline evaluation and small traffic experiment.

If a risk cannot be tested early, say why.

### Question 4: What Is The Mitigation?

Risk responses include:

- Lower the probability.
- Lower the impact.
- Detect earlier.
- Stop faster.
- Explicitly accept.

Example:

```md
Risk:
Third-party payment webhook delay is unpredictable.

Mitigation:
Mark local payment state as pending, poll provider status in the background, alert after 10 minutes, and provide support with a lookup path.
```

### Question 5: Who Owns Each Risk?

Write:

```md
Risk owner:
Validation date:
Mitigation action:
Must complete before launch: yes/no
```

Unowned risks are unmanaged risks.

### Question 6: What Is The Stop-loss Plan?

Stop-loss options:

- Disable feature flag
- Stop rollout
- Route traffic back
- Pause background workers
- Block writes
- Switch to old path
- Use manual operations
- Prepare customer support response

The worst case does not need a perfect path, but it needs a path.

### Red Flags

- Risk section says "none."
- Risks are abstract.
- Risks have no owner.
- Risks have no validation plan.
- Mitigation only says "add more tests."
- External dependencies are treated optimistically.
- No stop-loss plan exists.

### Exit Standard

You can say why the project is most likely to fail, and what has been done to validate, reduce, own, or accept that risk.

---

## 11. Self-review Cadence

### 15-minute Review

Use for small designs or early pre-review.

```md
1. Spend 3 minutes writing your understanding.
2. Spend 10 minutes scanning the 10 areas.
3. Spend 2 minutes naming the largest risk and conclusion.
```

Output:

```md
Clearest part:
Least clear part:
Must fix before launch:
```

### 45-minute Review

Use before a formal design review.

```md
1. Restate the design.
2. Mark each review area high, medium, or low focus.
3. For high-focus areas, write judgment, evidence, question, action.
4. For medium-focus areas, record only meaningful risks.
5. For low-focus areas, confirm non-applicability.
6. Produce a review conclusion.
```

Output:

```md
Must change:
Must complete before launch:
Suggested improvements:
Accepted risks:
Follow-up observations:
```

### Deep Review

Use for core systems, payment, billing, identity, permissions, migrations, or cross-team architecture.

```md
1. Draw the main flow.
2. Draw the failure flow.
3. Draw the data state machine.
4. Write the release stages.
5. Write the risk table.
6. Confirm ownership with dependent teams.
```

Deep review is not about writing a long document. It is about making risky systems rely less on luck.

---

## 12. Self-review Template

```md
# Design Self-review

Design:
Reviewer:
Date:

## 0. Understanding

Problem:
Core approach:
Critical path:
Dependencies:
Largest unknown:

## 1. Goal

Judgment:
Evidence:
Question:
Action:

## 2. Boundary

Judgment:
Evidence:
Question:
Action:

## 3. Data

Judgment:
Evidence:
Question:
Action:

## 4. Reliability

Judgment:
Evidence:
Question:
Action:

## 5. Evolution

Judgment:
Evidence:
Question:
Action:

## 6. Security

Judgment:
Evidence:
Question:
Action:

## 7. Observability

Judgment:
Evidence:
Question:
Action:

## 8. Release

Judgment:
Evidence:
Question:
Action:

## 9. Ownership

Judgment:
Evidence:
Question:
Action:

## 10. Risk

Judgment:
Evidence:
Question:
Action:

## Conclusion

Conclusion: Pass / Conditional pass / Revise and review again

Must change:
- 

Must complete before launch:
- 

Suggested improvements:
- 

Accepted risks:
- 

Follow-up observations:
- 
```

---

## 13. One-page Memory Sheet

```md
Goal:
Why do this, for whom, and how do we measure success?

Boundary:
What is in scope, what is out of scope, and who owns what?

Data:
What are the core entities, states, owners, and consistency rules?

Reliability:
What fails, what retries, what must be idempotent, and how do we recover?

Evolution:
What will probably change, and did we avoid both dead ends and over-design?

Security:
Who can access or modify what, and how do we enforce ownership and isolation?

Observability:
When a user reports failure, can we find what happened quickly?

Release:
How do we gray-rollout, migrate, validate, rollback, and clean up?

Ownership:
Who owns, operates, repairs, and evolves the system?

Risk:
Why would this fail, how do we test that early, and how do we stop loss?
```

Shorter:

```md
Is it worth it?
Can it hold?
Who owns it?
Where can it fail?
```
