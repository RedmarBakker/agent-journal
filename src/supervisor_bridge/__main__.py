import json
import os
import sys
from pathlib import Path

from supervisor_bridge.bridge import NoAggregateBudgetProof, SupervisorBridge
from supervisor_bridge.mcp import McpServer
from supervisor_bridge.state import DEFAULT_STATE_DIR, StateStore
from supervisor_bridge.transport import JsonHttpConnection, SupervisorHttpClient, TransportError


def state_directory() -> Path:
    return Path(os.environ.get("JOURNAL_SUPERVISOR_STATE_DIR", str(DEFAULT_STATE_DIR)))


def service_client() -> SupervisorHttpClient:
    url = os.environ.get("JOURNAL_SUPERVISOR_ADMISSION_URL", "")
    token = os.environ.get("JOURNAL_SUPERVISOR_ADMISSION_TOKEN", "")
    if not url or not token:
        raise ValueError("private journal supervisor route credentials are not configured")
    return SupervisorHttpClient(JsonHttpConnection(url, token))


def run(command: list[str]) -> int:
    if command == ["mcp"]:
        bridge = SupervisorBridge(service_client(), StateStore(state_directory()), NoAggregateBudgetProof())
        McpServer(bridge).serve()
        return 0
    if command == ["reconcile"]:
        state = StateStore(state_directory())
        try:
            bridge = SupervisorBridge(service_client(), state, NoAggregateBudgetProof())
        except ValueError as error:
            state.record_failure("service_unauthorized" if "token" in str(error) else "service_unavailable", False)
            print(json.dumps({"status": "failed", "reason": "configuration_unavailable"}, separators=(",", ":")))
            return 1
        result = bridge.reconcile("timer")
        print(json.dumps(result.to_dict(), separators=(",", ":")))
        return 0 if result.status in {"skipped", "blocked", "admitted", "hook_acknowledged"} else 1
    print("journal-supervisor-bridge accepts only mcp or reconcile", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(run(sys.argv[1:]))
    except (OSError, ValueError, TransportError) as error:
        print(f"journal-supervisor-bridge: {error}", file=sys.stderr)
        raise SystemExit(1)
