import importlib.util
import json
from pathlib import Path

import pytest

from supervisor_bridge.bridge import NoAggregateBudgetProof, SupervisorBridge
from supervisor_bridge.contracts import (
    FIXTURE_PATH,
    OPENCLAW_TOOL_NAMES,
    TOOL_NAMES,
    ContractError,
    RunReference,
    effective_tool_inventory,
    load_contract_schema,
    tool_input_schemas,
    validate_pinned_fixture,
)
from supervisor_bridge.hints import HintSpool
from supervisor_bridge.mcp import McpServer
from supervisor_bridge.state import StateStore
from supervisor_bridge.transport import (
    AuthorizationError,
    HookAcknowledgement,
    JsonHttpConnection,
    OpenClawHookClient,
    ReceiptNotFound,
    RetryableTransportError,
    SupervisorHttpClient,
    TransportError,
    hook_request,
)


RUN = {
    "run_id": "run-1",
    "episode_id": "episode-1",
    "pending_action_id": "action-1",
    "grant_id": "grant-1",
    "grant_version": 1,
    "installation_epoch": 2,
    "fence": 7,
    "lease_expires_at_ms": 1793404800000,
    "budget_reservation_id": "reservation-1",
    "reserved_cost_microusd": 12000,
}
RUN_REF = {key: RUN[key] for key in (
    "run_id", "episode_id", "pending_action_id", "grant_id", "grant_version", "installation_epoch", "fence"
)}


class StubJournal:
    def __init__(self, admissions=None, observations=None):
        self.admissions = list(admissions or [])
        self.observations = list(observations or [])
        self.calls = []

    def admit(self, source, observation_cursor):
        self.calls.append(("admit", source, observation_cursor))
        if self.admissions:
            return self.admissions.pop(0)
        return {"status": "skipped", "reason": "empty"}

    def observe(self, request):
        self.calls.append(("observe", request))
        return {
            "protocol_version": 1,
            "run": dict(RUN),
            "snapshot": {},
            "page": {
                "protocol_version": 1,
                "cursor": request["cursor"],
                "next_cursor": "cursor-after-page",
                "node_heartbeat_at_ms": 1793404500000,
                "observation_watermark_ms": 1793404500000,
                "observations": list(self.observations),
            },
            "server_now_ms": 1793404500000,
        }

    def apply(self, request):
        self.calls.append(("apply", request))
        return {"status": "accepted"}

    def receipt(self, action_id):
        self.calls.append(("receipt", action_id))
        return make_receipt()


class PendingReceiptJournal(StubJournal):
    def receipt(self, action_id):
        self.calls.append(("receipt", action_id))
        raise ReceiptNotFound("not available yet")


class StubHook:
    def __init__(self):
        self.calls = []

    def send(self, run):
        self.calls.append(run)
        return HookAcknowledgement("gateway-run-1")


class VerifiedBudget:
    def is_verified(self, _run):
        return True


class RetryHook:
    def __init__(self, error):
        self.error = error
        self.calls = 0

    def send(self, _run):
        self.calls += 1
        raise self.error


class StubResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, _maximum=-1):
        return self.body


class StubOpener:
    def __init__(self, bodies):
        self.bodies = list(bodies)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        return StubResponse(self.bodies.pop(0))


def make_receipt():
    return {
        "protocol_version": 1,
        "action_id": "action-1",
        "episode_id": "episode-1",
        "run_id": "run-1",
        "grant_id": "grant-1",
        "grant_version": 1,
        "scope": {
            "tenant_id": "tenant-1",
            "project_id": "project-1",
            "environment_id": 4,
            "manager_id": "manager-1",
            "writer_node_id": "node-1",
            "installation_epoch": 2,
        },
        "fence": 7,
        "intent_sha256": "a" * 64,
        "actor_kind": "plugin",
        "actor_id": "journal-supervisor",
        "status": "applied",
        "reason": None,
        "recorded_at_ms": 1793404500000,
        "observation_ids": ["observation-1"],
        "affected_refs": [],
        "changes": [],
        "verification": "verified",
        "outcome": "useful_evidence",
        "proposed_operations": [{"kind": "plan_priorities", "plan_id": 1, "text": "Review the failed check."}],
    }


def admitted():
    return {"status": "admitted", "run": dict(RUN)}


def action_arguments(run_ref=None):
    return {
        "run_ref": dict(run_ref or RUN_REF),
        "observation_ids": ["observation-1"],
        "expected_revisions": [
            {"ref": {"table": "plans", "id": 1}, "revision": "plan-revision"},
            {"ref": {"table": "checks", "id": 3}, "revision": "check-revision"},
        ],
        "operations": [{"kind": "plan_priorities", "plan_id": 1, "text": "Review the failed check."}],
        "rationale": "The latest enrolled verification failed.",
    }


def test_empty_or_overlap_reconcile_uses_no_model(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "empty"}, {"status": "skipped", "reason": "busy"}])
    hook = StubHook()
    bridge = SupervisorBridge(journal, StateStore(tmp_path), hook=hook)

    assert bridge.reconcile("timer").reason == "empty"
    assert bridge.reconcile("hint").reason == "busy"
    assert [call[0] for call in journal.calls] == ["admit", "admit"]
    assert hook.calls == []


def test_hints_and_timer_share_one_admission(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "empty"}, {"status": "skipped", "reason": "empty"}])
    bridge = SupervisorBridge(journal, StateStore(tmp_path))

    bridge.reconcile("hint")
    bridge.reconcile("timer")

    assert journal.calls == [("admit", "hint", None), ("admit", "timer", None)]


def test_hint_spool_deduplicates_and_bounds_row_references(tmp_path):
    spool = HintSpool(tmp_path)
    for row_id in (1, 1, *range(2, 260)):
        spool.enqueue_event_line(json.dumps({
            "v": 1,
            "event": "tasks.created",
            "data": {"table": "tasks", "id": row_id, "by": "user"},
        }))

    references, overflow = HintSpool(tmp_path).peek_batch()
    assert len(references) == 100
    assert references[0] == {"table": "tasks", "id": 1}
    assert overflow is True
    assert len(spool.read_locked()["references"]) == 256


def test_plugin_hook_never_waits_for_model_or_remote_network(tmp_path, monkeypatch):
    plugin_path = Path(__file__).resolve().parents[1] / "plugins" / "journal-supervisor-hints" / "run.py"
    spec = importlib.util.spec_from_file_location("journal_supervisor_hint_plugin", plugin_path)
    plugin = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(plugin)
    monkeypatch.setenv("JOURNAL_ROOT", str(Path(__file__).resolve().parents[1]))
    monkeypatch.setenv("JOURNAL_PLUGIN_DATA", str(tmp_path))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("the synchronous plugin callback attempted remote work")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    monkeypatch.setattr("socket.socket", forbidden)
    response = json.loads(plugin.answer({
        "v": 1,
        "event": "checks.updated",
        "data": {"table": "checks", "id": 3, "by": "user", "changed": ["interval_minutes"]},
    }))

    assert response == {"v": 1, "answer": "allow"}
    references, overflow = HintSpool(tmp_path / "transport").peek_batch()
    assert references == [{"table": "checks", "id": 3}]
    assert overflow is False


def test_offline_gateway_reconciliation_recovers_missed_events(tmp_path):
    state = StateStore(tmp_path)
    state.record_cursor("journal-cursor-7")
    observation = json.loads(FIXTURE_PATH.read_text())["instances"]["Observation"]
    journal = StubJournal([admitted()], [observation])
    hints = HintSpool(tmp_path / "hints")
    assert hints.peek_batch() == ([], False)

    bridge = SupervisorBridge(journal, state, VerifiedBudget(), StubHook())
    bridge.reconcile("timer")
    server = McpServer(bridge)
    observed = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": TOOL_NAMES[0], "arguments": {"run_ref": RUN_REF, "cursor": "journal-cursor-7"}},
    })
    response = json.loads(observed["result"]["content"][0]["text"])

    assert journal.calls[0] == ("admit", "timer", "journal-cursor-7")
    assert journal.calls[1][0] == "observe"
    assert journal.calls[1][1]["cursor"] == "journal-cursor-7"
    assert response["page"]["observations"] == [observation]
    assert state.observation_cursor() == "journal-cursor-7"


def test_reference_only_hook_cannot_override_agent_session_or_scope():
    run = RunReference.from_run(RUN)
    body, headers = hook_request(run)

    assert set(body) == {"message", "name", "agentId", "sessionMode", "deliver", "thinking", "model", "timeoutSeconds"}
    assert body["agentId"] == "supervisor"
    assert body["sessionMode"] == "isolated" and body["deliver"] is False
    assert "sessionKey" not in body and "sessionId" not in body
    assert json.dumps(run.to_dict(), sort_keys=True, separators=(",", ":")) in body["message"]
    assert headers == {"Content-Type": "application/json", "Idempotency-Key": "run-1"}


def test_private_adapters_use_only_fixed_authenticated_routes():
    opener = StubOpener([
        b'{"status":"skipped","reason":"empty"}',
        b'{"runId":"gateway-run-1"}',
    ])
    connection = JsonHttpConnection("http://127.0.0.1:9134", "journal-service-token")
    connection.opener = opener
    client = SupervisorHttpClient(connection)
    assert client.admit("timer", None) == {"status": "skipped", "reason": "empty"}
    with pytest.raises(TransportError):
        connection.post("/_supervisor/v1/admin", {})

    hook = OpenClawHookClient("http://localhost:18789", "openclaw-hook-token")
    hook.opener = opener
    assert hook.send(RunReference.from_run(RUN)).gateway_run_id == "gateway-run-1"

    service_request, service_timeout = opener.requests[0]
    hook_request_sent, hook_timeout = opener.requests[1]
    assert service_request.full_url == "http://127.0.0.1:9134/_supervisor/v1/admit"
    assert service_request.get_header("Authorization") == "Bearer journal-service-token"
    assert json.loads(service_request.data) == {"protocol_version": 1, "source": "timer", "observation_cursor": None}
    assert service_timeout == hook_timeout == 20
    assert hook_request_sent.full_url == "http://localhost:18789/hooks/agent"
    assert hook_request_sent.get_header("Authorization") == "Bearer openclaw-hook-token"
    assert hook_request_sent.get_header("Idempotency-key") == "run-1"
    assert set(json.loads(hook_request_sent.data)) == {
        "message", "name", "agentId", "sessionMode", "deliver", "thinking", "model", "timeoutSeconds"
    }


def test_pinned_command_and_tool_config_match_contract(tmp_path):
    fixture = json.loads(FIXTURE_PATH.read_text())
    validate_pinned_fixture(fixture)
    schemas = tool_input_schemas(load_contract_schema())

    assert tuple(schemas) == TOOL_NAMES
    assert fixture["cron_add_params"]["payload"]["argv"] == [
        "/opt/journal-supervisor/bin/journal-supervisor-bridge", "reconcile"
    ]
    assert fixture["openclaw_config"]["mcp"]["servers"]["journal"]["args"] == ["mcp"]
    assert fixture["openclaw_config"]["tools"]["allow"] == list(OPENCLAW_TOOL_NAMES)
    assert effective_tool_inventory(fixture, set()) == []
    assert effective_tool_inventory(fixture, {"journal__journal_supervisor-observe", "shell", "browser"}) == [
        "journal__journal_supervisor-observe"
    ]
    server = McpServer(SupervisorBridge(StubJournal(), StateStore(tmp_path)))
    listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in listed["result"]["tools"]] == list(TOOL_NAMES)

    expanded = json.loads(json.dumps(fixture))
    expanded["openclaw_config"]["agents"]["entries"]["supervisor"]["tools"]["allow"].append("shell")
    with pytest.raises(ContractError):
        validate_pinned_fixture(expanded)


def test_unverified_aggregate_budget_never_invokes_hook(tmp_path):
    journal = StubJournal([admitted()])
    hook = StubHook()
    state = StateStore(tmp_path)
    bridge = SupervisorBridge(journal, state, NoAggregateBudgetProof(), hook)

    result = bridge.reconcile("timer")

    assert result.status == "blocked" and result.reason == "unknown_cost"
    assert hook.calls == []
    snapshot = state.snapshot()
    assert snapshot["usage_settlement"] == "unknown_cost"
    assert snapshot["last_error"] == "aggregate_budget_unproven"
    assert snapshot["active_run"] is None
    assert snapshot["blocked_run"] == RUN_REF


def test_hook_acknowledgement_is_not_write_completion_or_a_second_run(tmp_path):
    journal = StubJournal([admitted(), admitted()])
    hook = StubHook()
    state = StateStore(tmp_path)
    bridge = SupervisorBridge(journal, state, VerifiedBudget(), hook)

    first = bridge.reconcile("timer")
    second = bridge.reconcile("hint")

    assert first.status == "hook_acknowledged"
    assert first.reason == "ack_is_not_completion"
    assert second.reason == "hook_not_repeated"
    assert len(hook.calls) == 1
    assert state.snapshot()["receipt"] is None


def test_hook_retry_is_bounded_and_invalid_credentials_do_not_fallback(tmp_path):
    retrying = RetryHook(RetryableTransportError("bounded retry"))
    retry_state = StateStore(tmp_path / "retry")
    retry_bridge = SupervisorBridge(StubJournal([admitted()]), retry_state, VerifiedBudget(), retrying)

    retry_result = retry_bridge.reconcile("timer")

    assert retry_result.reason == "retry_limit"
    assert retrying.calls == 2
    assert retry_state.snapshot()["retry_count"] == 2

    unauthorized = RetryHook(AuthorizationError("credential rejected"))
    auth_state = StateStore(tmp_path / "auth")
    auth_bridge = SupervisorBridge(StubJournal([admitted()]), auth_state, VerifiedBudget(), unauthorized)
    auth_result = auth_bridge.reconcile("timer")

    assert auth_result.reason == "hook_unauthorized"
    assert unauthorized.calls == 1
    assert auth_state.snapshot()["hook_status"] == "unauthorized"


def test_mcp_observe_and_apply_require_current_fence(tmp_path):
    journal = StubJournal([admitted()])
    state = StateStore(tmp_path)
    state.record_admitted(RunReference.from_run(RUN))
    server = McpServer(SupervisorBridge(journal, state))
    wrong = dict(RUN_REF, fence=8)

    observe = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": TOOL_NAMES[0], "arguments": {"run_ref": wrong, "cursor": None}},
    })
    apply = server.handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": TOOL_NAMES[1], "arguments": action_arguments(wrong)},
    })

    assert observe["result"]["isError"] is True
    assert apply["result"]["isError"] is True
    assert not [call for call in journal.calls if call[0] in {"observe", "apply", "receipt"}]


def test_apply_reads_back_canonical_receipt_before_reporting_completion(tmp_path):
    journal = StubJournal([admitted()])
    state = StateStore(tmp_path)
    hook = StubHook()
    bridge = SupervisorBridge(journal, state, VerifiedBudget(), hook)
    bridge.reconcile("timer")
    server = McpServer(bridge)

    observed = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": TOOL_NAMES[0], "arguments": {"run_ref": RUN_REF, "cursor": None}},
    })
    assert observed["result"]["isError"] is False
    assert state.observation_cursor() is None

    applied = server.handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": TOOL_NAMES[1], "arguments": action_arguments()},
    })

    assert applied["result"]["isError"] is False
    assert [call[0] for call in journal.calls] == ["admit", "observe", "apply", "receipt"]
    assert json.loads(applied["result"]["content"][0]["text"])["verification"] == "verified"
    assert state.observation_cursor() == "cursor-after-page"
    assert state.snapshot()["receipt"]["action_id"] == RUN["pending_action_id"]


def test_apply_ack_without_readback_is_not_reported_as_complete(tmp_path):
    journal = PendingReceiptJournal()
    state = StateStore(tmp_path)
    state.record_admitted(RunReference.from_run(RUN))
    bridge = SupervisorBridge(journal, state)

    with pytest.raises(ReceiptNotFound):
        bridge.apply(action_arguments())

    assert [call[0] for call in journal.calls] == ["apply", "receipt"]
    assert state.snapshot()["receipt"] is None
    assert state.snapshot()["last_error"] == "receipt_pending"

