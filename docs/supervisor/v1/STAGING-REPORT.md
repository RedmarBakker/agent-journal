# Task 112 local staging report

**Status: blocked; successful end-to-end acceptance is not established.** This report covers only disposable local probes. Tenant enrollment remains disabled in `manifest.json`.

## Controlled local probes

The two planned selectors create temporary journal roots under pytest's fresh temporary directory, clear `JOURNAL_ROOT`, `JOURNAL_ENV`, `JOURNAL_ACTOR` and `JOURNAL_SESSION`, and stop their local HTTP servers in `finally` blocks. Tenant A and tenant B use separate databases; a credential from A is rejected by B without changing B's entry log. The restore candidate is a copy of A's temporary journal root, not a customer backup.

The scripted model path uses the pinned fixture and the loopback metering proxy with stubbed Anthropic responses. It records 3 generation requests, 24 input tokens, 15 output tokens and 6 bounded provider requests. No API key or external provider request is involved. The fixture pins OpenClaw `2026.10.8` at source commit `dc2523e5a5c7a309517fd7fa834add938231d526`, image `ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5`, model `anthropic/claude-sonnet-5`, `high` thinking and an empty fallback list. Contract schema SHA-256: `6b4b0e7cdce82633a2fafcae918b87bd1001226d26e45348cfe3fbe0802bc211`. Gateway-policy fixture SHA-256: `f320e5bf9a774448e867401d0803e4c160258c662da1f7fdb461766d19689ff6`.

## Blocker found in the merged handoff

**There is no service route for metered usage settlement.** The private writer routes expose `/admit`, `/observe`, `/apply` and `/receipt` only (`src/journal/http/routes/routes.py:91-94`). The bridge persists proxy usage in its local state, while `SupervisorMaintenance._usage_reason` requires a writer-side `SupervisorUsage` row in `known` status before it accepts an action (`src/journal/features/supervisor/support/supervisor_maintenance.py:301-308`). The controlled action is rejected with `usage_unknown` before it can create a diagnostic task. `SupervisorAdmissions.record_usage` exists, but is not exposed by these routes. This staging task owns the focused harness and report, so it does not add another journal service route.

The receipt envelope mismatch is fixed in `SupervisorHttpClient.receipt`: it now validates the journal envelope and returns its canonical `data` receipt. `tests/test_supervisor_bridge.py::test_private_adapters_use_only_fixed_authenticated_routes` covers both a valid envelope and malformed-envelope refusal. The controlled selector now reaches apply and receives a canonical, rejected `usage_unknown` receipt; it continues to assert the required success chain and does not assert that failure as expected behavior.

The two-tenant selector and the remaining focused controls passed in journal test turns 569-570 and are named again for the clock-out run after conflict resolution. The controlled selector does not prove a committed diagnostic, ordinary driver pickup or settled canonical success receipt. Its Plan driver fixture is in-process, not a real Codex process or an execution-isolation probe.

## Not done

- The one real Anthropic smoke run capped at USD 1 was not proposed or run. The scripted writer rejects the action because it has no metered-usage settlement route, so the required end-to-end gate has not passed. Journal secret 1 was not read or used.
- A real OpenClaw Gateway and actual Codex Plan process were not started. No worker filesystem, secret mount, network, UID/GID, container or VM boundary was tested.
- VM-only per-tenant network isolation, worker isolation, backup rotation, restore epoch change and stale-grant rejection remain not done. The local restore candidate does not stand in for those probes.

The planned selectors are `tests/test_supervisor_bridge.py::test_controlled_loop_reaches_normal_driver_and_canonical_receipt` and `tests/test_supervisor_bridge.py::test_two_tenant_replay_restore_and_injection_boundaries`. The first was rerun after Task 139 and remains blocked at `usage_unknown`; the second passed in test turn 569. The other focused controls passed in turns 569-570. The journal runs the clock-out selection; this worker does not run tests directly.
