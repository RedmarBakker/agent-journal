# Journal supervisor contract, version 2

This contract defines the journal supervisor as the owner's controller for one environment. It replaces version 1's grant for one plan, one phase and three typed operations. The journal catalogue is the only source of command tiers: [capability_catalogue.py](../../../src/journal/features/supervisor/capability_catalogue.py). This document defines how the catalogue, grant, wake-ups, actions and owner controls fit together; it does not duplicate the catalogue's full command list.

This is a product contract, not a deployment approval. The version 1 staging and isolation gates in [the version 1 contract](../v1/contract.md) remain open until separately proved and authorized.

## Grant and scope

Each environment has one grant owned by its user. The grant names either all watched plans or an explicit plan list. It also holds capability settings, wake-up settings, limits, an expiry, pause and revocation state, and owner-authored narrowing rules. The owner is the only person who may create, change, pause or revoke it. The supervisor cannot edit its own grant.

A capability is a catalogued noun and verb. The owner may switch a capability on or off and choose Act or Propose where its tier permits. A whole catalogue area may be set at once, with tier 3 choices still made per verb. An absent tier 3 choice means Propose only. Grant changes are revision-checked. Narrowing rules are stored with the grant and cannot add capabilities, plans, time, actions, tokens or cost.

The grant sets a scheduled wake interval of 15, 30 or 60 minutes and enables any desired event wake-ups: failed check, stalled task, stale worker, message to the supervisor, and question to the supervisor. It also sets limits for daily turns, per-turn input and output tokens, provider requests and duration, daily cost, action bundles per day and episode, and new diagnostics per episode. It has a validity time and can be paused or revoked. A wake or action that cannot be admitted within the current grant is refused or skipped.

## Catalogue and safety tiers

The catalogue contains each supervisor-capable command as an area, noun, verb and one tier. It is built from journal command classes. The grant never assigns or changes a tier. The command inventory and tier value live only in `src/journal/features/supervisor/capability_catalogue.py`; other views and tools read that source.

The five catalogue values have these meanings:

- **Read:** always allowed and does not consume a write capability.
- **Tier 1:** reversible journal changes that are not visible to others until they look. An enabled capability may act. The receipt records the prior values so its owner can undo it while those rows still match.
- **Tier 2:** reversible changes that affect people or agents, such as messages, task movement, or worker state. Each capability follows its grant's Act or Propose setting.
- **Tier 3:** changes that are irreversible, reach outside the journal, spend money, widen authority, or answer for the owner. The default is Propose only. In Control, **Needs your decision** lets the owner set Not allowed, Propose only or May act for each tier 3 verb; **Show all** lists every one. Not allowed refuses the command, Propose only stores it for the owner, and May act permits it under the grant. A change to the supervisor's own grant stays Never and cannot be set.
- **Never:** not grantable. Memory-changing verbs and every grant edit are Never.

The journal checks the grant, catalogue tier and narrowing rules at command execution. A prompt, example, message, or model suggestion cannot add permission. The bridge has generated read tools for catalogued read verbs and one generated `run_or_propose` tool for writes. It sends a typed operation through the existing fenced maintenance service. That service selects its operation schema from the catalogue and grant; `plan tell` runs through `Console` as the supervisor role and records the created message in its command receipt. The old `apply_maintenance` tool is no longer exposed. The existing admission fence, metering and usage settlement remain in force. Typed support for the rest of the writable catalogue is still open.

## Wake-ups

The supervisor wakes on the grant's schedule and enabled events. A scheduled wake reviews the watched environment; an event wake starts with its triggering event and reads the current rows needed to decide. Before a model call, the journal compares the current environment change marker and observation cursor with the values at the last wake. When nothing changed and no event is pending, it records a quiet skip without a model call or provider cost.

Every wake is admitted against the current grant and limits. The provider request and retry envelope is metered. Usage is settled before an action is accepted, and a missing or uncertain usage result fails closed. Fences and grant revisions prevent a stale or duplicate wake from applying an action.

## Decisions, receipts and proposals

Each decision records its grant version, run reference, observations, outcome, reason, selected command, changed rows and settled usage. An applied action receipt records the catalogue tier, before and after values, actor and readback result. The reason is an explanation, not hidden model reasoning. Skips are recorded too.

An applied tier 1 receipt retains the before values. The receipt owner can request undo through the journal command funnel, with the owner as actor. Undo is refused if the receipt is not an applied tier 1 action or its affected rows or phase changed since the action. A successful undo is recorded and counted as **Undone by you**.

A proposal stores the exact command and arguments without executing them. The owner can accept it, which runs the command through the same journal funnel as the owner, or decline it. A proposal is never reported as an applied change. The owner can read receipts, proposals and skips in the supervisor's records.

## Feedback and narrowing rules

The owner may mark a decision Useful or Not useful, leave a comment and choose a correction. Feedback is stored against that decision with the owner as actor. Each wake may include up to five matching examples as data. Examples do not act as instructions or grant authority.

The owner may turn a correction into a narrowing rule, such as refusing a verb on a row or requiring Propose. The journal checks the rule when it checks the command. A rule can only refuse or require a proposal; it cannot enable a capability, change Propose to Act, widen plan scope, raise a limit or extend validity. Removing a rule only removes that restriction; it does not change the grant's other settings.

## Migration from version 1

Version 1 had a single-plan, single-phase grant with the typed capabilities `diagnostic_task`, `plan_priorities` and `check_interval`. Version 2 converts those flags to `task create`, `plan priorities` and `check edit`, respectively. The old plan becomes the explicit watched-plan list; it does not expand to every plan in the environment. A version 1 Shadow grant maps to Propose and a bounded-write grant maps to Act. The conversion retains the owner, driver environment, limits, validity and revoked state, and starts with the 15-minute interval and failed-check event wake-up.

No new capability is inferred during conversion. The converted grant must remain owner-reviewable before a v2 run. Moving real persisted grants to v2, proving the migration against deployed data, and deciding the cutover and rollback procedure remain deployment work; this contract does not silently migrate or authorize a live grant.

## Decided and still open

The per-environment grant, catalogue as the single tier source, safety tiers, event and scheduled wake-ups, quiet skip, generated run-or-propose path, receipts and owner undo, proposals, feedback examples, narrowing-only rules and conservative version 1 mapping are decided here.

Live enrollment is still closed. The exact deployed provider and billing profile, isolated writer and execution identities, effective model tool inventory, production migration and recovery path, and customer data permission need controlled staging evidence and owner authorization. The v1 fixture and plugin remain staging artifacts; this contract does not mark them as installed or ready for customer use.
