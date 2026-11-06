import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

from supervisor_bridge.bridge import NoAggregateBudgetProof, SupervisorBridge
from supervisor_bridge.contracts import EVENT_WAKE_KINDS
from supervisor_bridge.event_hints import EventHintDirectory
from supervisor_bridge.mcp import McpServer
from supervisor_bridge.metering import (
    AnthropicProviderTransport,
    MeteredAggregateBudgetProof,
    MeteringProxy,
    MeteringProxyServer,
)
from supervisor_bridge.state import DEFAULT_STATE_DIR, StateStore
from supervisor_bridge.transport import JsonHttpConnection, OpenClawHookClient, SupervisorHttpClient, TransportError

PROXY_STARTUP_SECONDS = 10
EVENT_HINT_POLL_SECONDS = 1


def state_directory() -> Path:
    return Path(os.environ.get("JOURNAL_SUPERVISOR_STATE_DIR", str(DEFAULT_STATE_DIR)))


def service_client() -> SupervisorHttpClient:
    url = os.environ.get("JOURNAL_SUPERVISOR_ADMISSION_URL", "")
    token = os.environ.get("JOURNAL_SUPERVISOR_ADMISSION_TOKEN", "")
    if not url or not token:
        raise ValueError("private journal supervisor route credentials are not configured")
    ca_file = os.environ.get("JOURNAL_SUPERVISOR_TLS_CA_FILE", "")
    if urlsplit(url).hostname not in {"localhost", "127.0.0.1", "::1"} and not ca_file:
        raise ValueError("the private journal supervisor TLS CA file is not configured")
    return SupervisorHttpClient(JsonHttpConnection(url, token, ca_file=ca_file))


def hook_client() -> OpenClawHookClient | None:
    token = os.environ.get("OPENCLAW_HOOK_TOKEN", "")
    if not token:
        return None
    return OpenClawHookClient(os.environ.get("JOURNAL_SUPERVISOR_HOOK_URL", "http://127.0.0.1:18789"), token)


def configured_bridge(state: StateStore) -> SupervisorBridge:
    config_path = os.environ.get("OPENCLAW_CONFIG_PATH", "/home/node/.openclaw/openclaw.json")
    proof = MeteredAggregateBudgetProof(state, config_path)
    return SupervisorBridge(service_client(), state, proof, hook_client())


def process_event_hints(bridge: SupervisorBridge, hints: EventHintDirectory) -> None:
    for hint in hints.pending():
        event_id = hint["event_id"]
        if not hint["event_kind"]:
            hints.acknowledge(event_id)
            continue
        result = bridge.reconcile(
            "hint", wakeup_id=event_id, event_kind=hint["event_kind"], event_id=event_id,
        )
        if result.status in {"skipped", "hook_acknowledged"}:
            hints.acknowledge(event_id)


def watch_events() -> int:
    state = StateStore(state_directory())
    bridge = configured_bridge(state)
    directory = Path(os.environ.get("JOURNAL_SUPERVISOR_HINTS_DIRECTORY", "/var/lib/journal-supervisor/hints"))
    hints = EventHintDirectory(directory, state.directory / "processed-event-hints.json")
    while True:
        process_event_hints(bridge, hints)
        time.sleep(EVENT_HINT_POLL_SECONDS)


def run(command: list[str]) -> int:
    if command == ["proxy"]:
        state = StateStore(state_directory())
        proxy = MeteringProxy(state, AnthropicProviderTransport(os.environ.get("ANTHROPIC_API_KEY", "")))
        MeteringProxyServer(proxy).serve()
        return 0
    if command == ["wait-for-proxy"]:
        return wait_for_proxy()
    if command == ["mcp"]:
        state = StateStore(state_directory())
        bridge = SupervisorBridge(service_client(), state, NoAggregateBudgetProof())
        McpServer(bridge).serve()
        return 0
    if command and command[0] == "reconcile":
        event_wake = (
            len(command) == 4 and command[1] == "event" and command[2] in EVENT_WAKE_KINDS
        )
        if command != ["reconcile"] and not event_wake:
            print("reconcile accepts no arguments or event <kind> <id>", file=sys.stderr)
            return 2
        state = StateStore(state_directory())
        try:
            bridge = configured_bridge(state)
        except ValueError as error:
            state.record_failure("service_unauthorized" if "token" in str(error) else "service_unavailable", False)
            print(json.dumps({"status": "failed", "reason": "configuration_unavailable"}, separators=(",", ":")))
            return 1
        result = (bridge.reconcile("hint", wakeup_id=command[3], event_kind=command[2], event_id=command[3])
                  if event_wake else bridge.reconcile("timer"))
        print(json.dumps(result.to_dict(), separators=(",", ":")))
        return 0 if result.status in {"skipped", "blocked", "admitted", "hook_acknowledged"} else 1
    if command == ["watch-events"]:
        watch_events()
        return 0
    print("journal-supervisor-bridge accepts only proxy, wait-for-proxy, mcp, reconcile [event <kind> <id>] or watch-events", file=sys.stderr)
    return 2


def wait_for_proxy() -> int:
    deadline = time.monotonic() + PROXY_STARTUP_SECONDS
    while time.monotonic() < deadline:
        if MeteredAggregateBudgetProof.proxy_is_healthy():
            return 0
        time.sleep(0.1)
    print("the loopback metering proxy did not become ready", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(run(sys.argv[1:]))
    except (OSError, ValueError, TransportError) as error:
        print(f"journal-supervisor-bridge: {error}", file=sys.stderr)
        raise SystemExit(1)
