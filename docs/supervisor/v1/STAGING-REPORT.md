# Task 112 local staging report

**Status: scripted local chain verified; live API smoke and VM acceptance remain open.** Tenant enrollment remains disabled in `manifest.json`.

## Controlled local probes

The focused selectors create independent journal roots under pytest's fresh temporary directory and remove their HTTP servers in `finally` blocks. Each installation starts with `JOURNAL_ROOT`, `JOURNAL_ENV`, `JOURNAL_ACTOR` and `JOURNAL_SESSION` cleared. Tenant A and tenant B use separate databases; the two-tenant selector verifies that A's credential cannot read or write B's usage or entry state. The restore candidate is copied under A's temporary root, not from a customer backup.

`tests/test_supervisor_bridge.py::test_controlled_loop_reaches_normal_driver_and_canonical_receipt` completes the scripted observe -> admission -> model/tool loop -> apply -> canonical read-back chain. The scripted Anthropic transport sits behind the loopback meter and records 16 input tokens, 10 output tokens, 4 provider requests and no retries. The authenticated `/usage` route settles those durable totals before `/apply`; the bridge accepts only its canonical verified receipt. The Plan fixture then lets the existing ordinary driver finish its current task and pick up the diagnostic without a human task-start or resume. This is an in-process Plan-driver fixture, not a live OpenClaw Gateway or a real Codex process.

`tests/test_supervisor_bridge.py::test_two_tenant_replay_restore_and_injection_boundaries` covers tenant separation, replay, restore fencing and malicious-input boundaries in the same disposable local setup. These checks do not prove container, host-network or per-tenant VM isolation.

The fixture pins OpenClaw `2026.10.8`, source commit `dc2523e5a5c7a309517fd7fa834add938231d526`, image `ghcr.io/openclaw/openclaw@sha256:82b6ce63048e75ca749dbc250e872ee21f4b1c098fc6bff94636e357bcb64bf5`, model `anthropic/claude-sonnet-5`, `high` thinking and no fallback. Contract schema SHA-256: `6b4b0e7cdce82633a2fafcae918b87bd1001226d26e45348cfe3fbe0802bc211`. Gateway-policy fixture SHA-256: `f320e5bf9a774448e867401d0803e4c160258c662da1f7fdb461766d19689ff6`.

The proposed grant envelope is 24,000 input tokens, 8,000 output tokens and 8 provider requests. The proxy enforces the aggregate token and request ceilings across token-count calls, generations and retries. At Anthropic's published Claude Sonnet 5 rates ($2/M standard input, $10/M output and $4/M for one-hour cache writes), the token ceilings bound model-token charges to at most $0.176 per run, assuming all input is billed at the most expensive listed cache-write rate. This leaves room below the requested $1 ceiling; the API-key smoke must still confirm the real selected profile and returned usage. See [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).

The latest focused journal test turns were output 6306 (21 passing selectors, including both planned staging selectors) and 6307 (2 passing authority/packaging selectors). Output 6304 also passed the controlled chain and three read-back/transport controls before the larger selection.

## Live provider smoke

No provider key has been read or used, and no live Gateway or provider request has been started. `journal secret propose 1 openclaw` was rejected by WorkerHelper because secret proposals are not an allowed worker command. The pinned container entrypoint runs Node, while the journal secret runner refuses `node` and `docker` as secret recipients; the searched host executable locations also yielded no standalone `openclaw` command. No proposal or user allow was recorded, so the smoke cannot proceed through `journal secret run` in this worker role. No alternate model, direct provider call or secret handoff was used.

If the user allows an available OpenClaw program, the run must use only the pinned model and high thinking route, route provider calls through the loopback meter, and record the selected API-key profile and redacted actual usage. The meter's durable 24,000/8,000/8 limits keep the standard Anthropic token-charge ceiling below $1 before tax or account-specific billing changes.

## Task 213 live smoke gate

The selected native SecretRun launcher was not built or proposed, and no live run was attempted. The current staging profile is an artifact for an operator-provisioned installation, not a self-contained local launch bundle. Compose requires a writer image revision, journal address, tenant id, pre-created Gateway and restore directories, a validated OpenClaw config, and a directory containing the other tenant credentials (`compose.json`). SecretRun supplies the key on stdin but deliberately runs with only a filtered `PATH`, language and temporary-home variables (`src/journal/features/secrets/support/secret_run.py`). The disposable scripted fixtures do not leave those tenant installation inputs behind.

The checked-in runtime contract points OpenClaw MCP at `/opt/journal-supervisor/bin/journal-supervisor-bridge` (`src/supervisor_bridge/contracts.py`), while the Gateway service in `compose.json` only mounts its state and the read-only hint spool plus its two config files. It does not package or mount that bridge executable. Without it, the pinned Gateway cannot reach the supervisor tools or the metering proxy, so a native wrapper around Compose alone cannot complete the admitted chain or yield trustworthy metered usage.

No launcher was offered to the user for approval because it could not complete the requested run with the available profile. Secret 1 remains unread, no service was started, and there is no live route, token usage or cost to report. The blocker is the missing self-contained disposable launch bundle and the missing Gateway bridge package; staging acceptance must supply both before a one-dollar smoke can be proposed safely.

## Not done

- The one real Anthropic smoke run capped at USD 1 has not run. Secret 1 remains untouched pending a usable direct OpenClaw program and the user's explicit allow.
- A live OpenClaw Gateway and actual Codex Plan process were not started. The controlled driver is in-process and does not prove real process compatibility.
- VM-only per-tenant network isolation, worker filesystem/secret isolation, UID/GID boundaries, backup rotation and restore epoch/stale-grant probes remain not done, as selected for this local task. The local two-tenant credential-denial and restore-candidate checks do not substitute for them.

Enrollment remains disabled. The acceptance evidence is limited to the passing focused selectors above and the local temporary roots they create.
