# Supervisor version 2 contract

## Grant

A version 2 grant belongs to one journal environment. It names the owner, watched plans, per-command decisions, wake interval, event wakeups, limits, expiry, pause and revocation state. Area switches and command decisions can narrow the grant; they cannot widen what the catalogue permits. The owner remains the only person who can change a grant.

## Tiers and catalogue

`src/journal/features/supervisor/capability_catalogue.py` is the one source for command tiers. A command is `read`, `tier 1`, `tier 2`, `tier 3` or `never`. Reads are always allowed. Tier 1 and tier 2 commands follow their saved grant decision. Tier 3 commands default to On and Propose; the owner can choose Not allowed, Proposes only or May act for each verb. The Control page lists the first five decisions and its Show all disclosure contains every tier 3 verb. Grant changes remain Never and cannot be enabled.

The bridge offers only operations that map to catalogue commands. It runs them through the journal command funnel, checks the grant and narrowing rules there, reads changed rows back, settles metered usage and records the outcome. An unknown or Never command is refused before settlement.

## Wake-ups

A grant may wake on its 15, 30 or 60 minute interval and on selected events: failed check, stalled task, stale worker, message to supervisor or question to supervisor. A wake gathers only the rows inside the grant's environment and plan scope. It includes no more than five matching owner-feedback examples as data.

## Receipts and undo

Each run has a receipt that identifies its grant version, run reference, result, reason and changed rows. Applied actions record the catalogue command, tier, before and after values, actor and readback result. An owner may undo an applied tier 1 action through the same journal command funnel. Undo uses the receipt's before values and records the owner as actor. It is refused if the current rows no longer match the receipt's after values, if the receipt is not an applied tier 1 action, or if it has already been undone.

## Proposals and feedback

An action set to Propose is stored as a proposal, with its operations and source receipt. The owner can accept or reject it through Control. Acceptance rechecks the grant, rules and current rows before applying the operations; a stale or newly refused proposal does not write. The owner can save feedback on a decision. Later wakes may include up to five matching examples as context, but feedback never changes a grant or applies an action.

## Narrowing rules

The owner may add a rule for a catalogue command, optionally scoped to a row. A `never` rule refuses that command on its matching row; a `propose` rule forces a proposal. The command check applies these rules before an action. A rule cannot enable an off capability, change a tier, or turn Propose into Act. Rules for grant changes are refused because that command is Never.

## Migration and open work

The version 1 one-plan grant is read through its compatibility path and represented as a version 2 environment grant for that plan. Its legacy bounded-write mode maps to Act and shadow mode maps to Propose for the mapped capabilities. Version 2 configuration and receipts use the environment grant and canonical command catalogue.

The journal-side grant, catalogue checks, command funnel, receipts, proposals, feedback and stories are implemented. Deployment to a live supervisor, the operator migration procedure and a live end-to-end smoke run remain open; the v1 runtime packaging is not evidence that the v2 deployment is complete.
