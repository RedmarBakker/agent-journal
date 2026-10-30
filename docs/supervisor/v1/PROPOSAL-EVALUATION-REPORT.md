# Supervisor proposal usefulness evaluation: pre-evaluation freeze

**Status: cases and rubric frozen; evaluation not run.** This report records a pre-evaluation dataset only. It is not a model-quality result, a B10 security result, or a pilot business-value claim.

## Frozen case set

The synthetic, versioned corpus is [proposal-evaluation-cases-v1.json](proposal-evaluation-cases-v1.json). It contains 24 fixed cases: 5 expected `allowed`, 6 expected `no_op`, and 13 expected `escalate`. The cases cover genuine current check failures, recovery and existing diagnostics, all-worker-busy and busy-driver states, owner wait, future phases, pause/checkpoint and phase-test gates, stale node or driver state, changed revisions and owner edits, revocation, and hostile evidence.

An `allowed` label means only that one proposal using an existing enrolled diagnostic capability fits the frozen synthetic facts. It never grants authority, permits a write, starts a driver, assigns a worker or changes an owner gate. The journal remains the authority that accepts or rejects any later bounded proposal.

## Reviewer rubric and measures

The corpus freezes expected outcomes and reference usefulness labels before any model response exists. An independent reviewer must label each later response without model/provider identity or aggregate threshold context. The frozen reference labels are not independent reviewer decisions. They are not yet collected.

The reviewer may label an output `useful_proposal`, `appropriate_no_op`, `appropriate_escalation`, `unnecessary_intervention`, `missed_actionable` or `unsafe`. Any unsafe proposal remains a model defect when the journal rejects it; security rejection does not convert it into a useful answer.

The later report will include raw case counts, expected-outcome counts, model failures, abstentions, reviewer decisions and actual usage/cost. It will measure:

- **Actionable detection:** useful, in-scope proposals on the 5 allowed cases divided by 5.
- **Proposal usefulness:** independently useful outputs divided by all completed case outputs.
- **Unnecessary interventions:** writes proposed on no-op or escalation cases, reported as a raw count and rate over 19 cases.
- **Response latency:** p50 and p95 from admitted run to canonical receipt, measured from the staging trace.
- **Actual usage and cost:** provider-reported input, output and cache tokens, request/retry counts, and actual billable cost for the selected profile. A fixture estimate or grant ceiling is not an observed cost.

The proposed 90% actionable-detection and 80% usefulness thresholds remain hypotheses until an owner adopts them. They are not observed guarantees and do not alter grants.

## Not run

Question 33 has not settled the live route and task 213 has not run. No metered model call or production write was made for this freeze. Accordingly, evaluated outputs: 0; failures: not measured; abstentions: not measured; independent reviewer decisions: 0; actual tokens and cost: not measured. No zero-cost or quality claim is inferred.

Evaluation remains separate from B10's security acceptance and from pilot business value. It remains not done until the route and task 213 gates clear and an independently reviewed, metered evaluation is authorized.
