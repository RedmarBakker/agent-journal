import hashlib
import importlib.util
import hashlib
import json
from io import BytesIO
from pathlib import Path
from shutil import copytree
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

from journal.app import App
from journal.config import Config
from journal.db.connection import Connection
from journal.events.rows.check_completed import CheckCompleted
from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.features.supervisor.support.supervisor_maintenance import diagnostic_task_values
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
from journal.http.server import Server
from journal.models.support.ref import Ref
from journal.models.task_state import TaskState
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from supervisor_bridge.bridge import NoAggregateBudgetProof, SupervisorBridge
from supervisor_bridge.event_hints import EventHintDirectory
from supervisor_bridge.contracts import (
    FIXTURE_PATH,
    METERED_PROVIDER_API_KEY_PLACEHOLDER,
    OBSERVE_TOOL,
    OPENCLAW_TOOL_NAMES,
    PINNED_OPENCLAW_COMMIT,
    PINNED_OPENCLAW_VERSION,
    READ_TOOL_COMMANDS,
    RUN_OR_PROPOSE_TOOL,
    RECEIPT_TOOL,
    TOOL_NAMES,
    ContractError,
    RunReference,
    effective_tool_inventory,
    load_contract_schema,
    tool_input_schemas,
    validate_pinned_fixture,
    validate_operation,
)
from supervisor_bridge import __main__ as supervisor_main
from supervisor_bridge.__main__ import service_client
from supervisor_bridge.hints import HintSpool
from supervisor_bridge.mcp import McpServer
from supervisor_bridge.metering import (
    AnthropicProviderTransport,
    METERED_PROVIDER_BASE_URL,
    MeteredAggregateBudgetProof,
    MeteringProxyServer,
    MeteringError,
    MeteringProxy,
    ProviderResponse,
)
from supervisor_bridge.state import StateStore
from supervisor_bridge.transport import (
    AuthorizationError,
    HookAcknowledgement,
    JsonHttpConnection,
    OpenClawHookClient,
    RetryableTransportError,
    ServiceRefusal,
    SupervisorHttpClient,
    TransportError,
    hook_request,
)
from tests.test_features import booted
from tests.in_process import posted
from tests.test_supervisor_authority import admitted as authority_admitted
from tests.test_supervisor_authority import seeded as authority_seeded
from tests.test_supervisor_driver import add_phase_task
from tests.test_supervisor_driver import prepare_driver_processes
from tests.test_supervisor_driver import add_phase_task
from tests.test_supervisor_driver import start_normal_driver
from tests.test_supervisor_driver import stop_normal_driver


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

    def admit(self, source, observation_cursor, wakeup_id=None, kind=None, event_kind=None, event_id=None):
        call = ("admit", source, observation_cursor)
        call += (wakeup_id, kind)
        self.calls.append(call if event_kind is None else (*call, event_kind, event_id))
        if self.admissions:
            return self.admissions.pop(0)
        return {"status": "skipped", "reason": "empty"}

    def observe(self, request):
        self.calls.append(("observe", request))
        return {
            "protocol_version": 1,
            "run": dict(RUN),
            "snapshot": {"grant": {
                "grant_id": RUN["grant_id"],
                "grant_version": RUN["grant_version"],
                "limits": {
                    "max_input_tokens_per_turn": 24000,
                    "max_output_tokens_per_turn": 8000,
                    "max_provider_requests_per_turn": 8,
                },
            }},
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
        return make_receipt()

    def settle_usage(self, run, usage):
        self.calls.append(("settle_usage", run, usage))
        return {
            "status": "settled", "usage_id": 24, "run_id": run.run_id, "fence": run.fence,
            "usage_status": "known", "duplicate": False,
        }

    def receipt(self, action_id):
        self.calls.append(("receipt", action_id))
        return make_receipt()


class PendingReceiptJournal(StubJournal):
    def apply(self, request):
        self.calls.append(("apply", request))
        return {"status": "accepted"}


class ProposalJournal(StubJournal):
    def apply(self, request):
        self.calls.append(("apply", request))
        receipt = make_receipt()
        receipt["status"] = "proposed"
        receipt["verification"] = "not_applied"
        receipt["command_receipts"] = []
        return receipt


class GrantChangedJournal(StubJournal):
    def apply(self, request):
        self.calls.append(("apply", request))
        raise ServiceRefusal("grant version changed")


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
        body = self.bodies.pop(0)
        if isinstance(body, Exception):
            raise body
        return StubResponse(body)


class StubProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def post(self, path, payload, accept):
        self.requests.append((path, payload, accept))
        return self.responses.pop(0)


def metered_state(directory, max_input=100, max_output=100, max_requests=8):
    state = StateStore(directory)
    run = RunReference.from_run(RUN)
    state.record_admitted(run)
    state.record_budget_limits(run, {
        "max_input_tokens_per_turn": max_input,
        "max_output_tokens_per_turn": max_output,
        "max_provider_requests_per_turn": max_requests,
    })
    state.record_budget_verified(run)
    return state


def metered_state_with_usage(directory):
    state = metered_state(directory, max_input=24000, max_output=8000, max_requests=8)
    provider = StubProvider([provider_input_tokens(3), provider_response(3, 2)])
    assert MeteringProxy(state, provider).forward(model_request()).status == 200
    return state


def provider_input_tokens(count):
    return ProviderResponse(200, json.dumps({"input_tokens": count}).encode())


def provider_response(input_tokens, output_tokens, cache_creation_input_tokens=0, cache_read_input_tokens=0):
    return ProviderResponse(200, json.dumps({
        "id": "message-1",
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "cache_read_input_tokens": cache_read_input_tokens,
        },
    }).encode())


def model_request(max_tokens=20):
    return {
        "model": "anthropic/claude-sonnet-5",
        "messages": [{"role": "user", "content": "Review the current failed check."}],
        "tools": [{
            "name": "observe",
            "description": "Read journal evidence",
            "input_schema": {"type": "object", "properties": {}},
        }],
        "max_tokens": max_tokens,
        "stream": True,
        "thinking": {"type": "adaptive"},
    }


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
        "rationale": "Review the failed check before making this bounded change.",
        "recorded_at_ms": 1793404500000,
        "observation_ids": ["observation-1"],
        "affected_refs": [],
        "changes": [],
        "verification": "verified",
        "outcome": "useful_evidence",
        "proposed_operations": [{"kind": "plan_priorities", "plan_id": 1, "text": "Review the failed check."}],
        "command_receipts": [{
            "command": "plan priorities",
            "arguments": {"plan_id": 1, "text": "Review the failed check."},
            "area": "Plans and tasks",
            "tier": "tier 1",
            "status": "applied",
            "reason": None,
            "rows_changed": [],
            "readback_verification": "verified",
            "settled_cost": {"status": "settled", "usd": "0.000001", "scope": "run"},
        }],
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
        "area": "Plans and tasks",
        "noun": "plan",
        "verb": "priorities",
        "arguments": {"plan_id": 1, "text": "Review the failed check."},
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


def test_early_scheduled_reconcile_uses_no_model(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "scheduled_interval_not_elapsed"}])
    hook = StubHook()
    bridge = SupervisorBridge(journal, StateStore(tmp_path), hook=hook)

    result = bridge.reconcile("timer")

    assert result.status == "skipped" and result.reason == "scheduled_interval_not_elapsed"
    assert hook.calls == []


def test_quiet_scheduled_reconcile_is_stored_without_a_model_call_or_cost(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "quiet"}])
    state = StateStore(tmp_path)
    hook = StubHook()
    bridge = SupervisorBridge(journal, state, hook=hook)

    result = bridge.reconcile("timer")

    assert result.status == "skipped" and result.reason == "quiet"
    assert state.snapshot()["last_admission"] == "quiet"
    assert state.active_run() is None
    assert state.snapshot()["metering"]["provider_requests"] == 0
    assert hook.calls == []


def test_hints_and_timer_share_one_admission(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "empty"}, {"status": "skipped", "reason": "empty"}])
    bridge = SupervisorBridge(journal, StateStore(tmp_path))

    bridge.reconcile("hint")
    bridge.reconcile("timer")

    assert [call[:3] for call in journal.calls] == [("admit", "hint", None), ("admit", "timer", None)]


def test_event_hint_uses_shared_admission_with_its_fixed_kind_and_id(tmp_path):
    journal = StubJournal([{"status": "skipped", "reason": "empty"}])
    bridge = SupervisorBridge(journal, StateStore(tmp_path))

    result = bridge.reconcile(
        "hint", wakeup_id="a" * 64, event_kind="failed_check", event_id="a" * 64,
    )

    assert result.status == "skipped" and result.reason == "empty"
    assert journal.calls == [(
        "admit", "hint", None, "a" * 64, "checks.updated", "failed_check", "a" * 64,
    )]


def test_supervisor_client_sends_the_event_identity_with_a_hint():
    opener = StubOpener([b'{"status":"skipped","reason":"empty"}'])
    connection = JsonHttpConnection("http://127.0.0.1:9134", "journal-service-token")
    connection.opener = opener
    client = SupervisorHttpClient(connection)

    client.admit("hint", None, "a" * 64, "checks.updated", "failed_check", "a" * 64)

    request = opener.requests[0][0]
    assert json.loads(request.data) == {
        "protocol_version": 1,
        "source": "hint",
        "observation_cursor": None,
        "wakeup_id": "a" * 64,
        "kind": "checks.updated",
        "event_kind": "failed_check",
        "event_id": "a" * 64,
    }


def test_event_hint_directory_remembers_consumed_event_files(tmp_path):
    directory = tmp_path / "hints"
    directory.mkdir()
    hint = {
        "v": "1", "event": "check_failed", "at": "2026-10-29T10:00:00+00:00",
        "environment": "pilot", "table": "checks", "id": "4", "event_kind": "failed_check",
    }
    body = json.dumps(hint, sort_keys=True, separators=(",", ":"))
    event_id = hashlib.sha256(body.encode()).hexdigest()
    (directory / f"{event_id}.json").write_text(body)
    queue = EventHintDirectory(directory, tmp_path / "state" / "processed-hints.json")

    assert queue.pending() == [{"event_id": event_id, "event_kind": "failed_check", "at": hint["at"]}]
    queue.acknowledge(event_id)

    assert queue.pending() == []


def test_gateway_event_consumer_admits_enabled_hints_and_acknowledges_skips(tmp_path):
    class HintQueue:
        def __init__(self):
            self.items = [
                {"event_id": "a" * 64, "event_kind": "failed_check", "at": "t1"},
                {"event_id": "b" * 64, "event_kind": "", "at": "t2"},
                {"event_id": "c" * 64, "event_kind": "stale_worker", "at": "t3"},
            ]
            self.acknowledged = []

        def pending(self):
            return self.items

        def acknowledge(self, event_id):
            self.acknowledged.append(event_id)

    class Bridge:
        def __init__(self):
            self.calls = []
            self.statuses = ["skipped", "failed"]

        def reconcile(self, source, kind=None, wakeup_id=None, event_kind=None, event_id=None):
            self.calls.append((source, kind, wakeup_id, event_kind, event_id))
            return SimpleNamespace(status=self.statuses.pop(0))

    queue, bridge = HintQueue(), Bridge()

    supervisor_main.process_event_hints(bridge, queue)

    assert bridge.calls == [
        ("hint", None, "a" * 64, "failed_check", "a" * 64),
        ("hint", None, "c" * 64, "stale_worker", "c" * 64),
    ]
    assert queue.acknowledged == ["a" * 64, "b" * 64]


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
    assert references[0] == {"kind": "tasks.created", "table": "tasks", "id": 1}
    assert overflow is True
    assert len(spool.read_locked()["references"]) == 256


def test_hint_spool_keeps_distinct_event_kinds_for_one_row(tmp_path):
    spool = HintSpool(tmp_path)
    for kind in ("tasks.created", "tasks.updated"):
        spool.enqueue_event_line(json.dumps({
            "v": 1,
            "event": kind,
            "data": {"table": "tasks", "id": 1, "by": "user"},
        }))

    references, overflow = spool.peek_batch()

    assert references == [
        {"kind": "tasks.created", "table": "tasks", "id": 1},
        {"kind": "tasks.updated", "table": "tasks", "id": 1},
    ]
    assert overflow is False


def test_hint_spool_migrates_queued_rows_without_an_event_kind(tmp_path):
    directory = tmp_path / "transport"
    directory.mkdir()
    key = hashlib.sha256(b"tasks:1").hexdigest()
    (directory / "hints.json").write_text(json.dumps({
        "references": [{"key": key, "ref": {"table": "tasks", "id": 1}}],
        "overflow": False,
    }))

    references, overflow = HintSpool(directory).peek_batch()

    assert references == [{"kind": "tasks.updated", "table": "tasks", "id": 1}]
    assert overflow is False
    assert HintSpool(directory).read_locked()["references"][0]["ref"]["kind"] == "tasks.updated"


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
    assert references == [{"kind": "checks.updated", "table": "checks", "id": 3}]
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
        "params": {"name": OBSERVE_TOOL, "arguments": {"run_ref": RUN_REF}},
    })
    response = json.loads(observed["result"]["content"][0]["text"])

    assert journal.calls[0][:3] == ("admit", "timer", "journal-cursor-7")
    assert journal.calls[1][0] == "observe"
    assert journal.calls[1][1]["cursor"] is None
    assert journal.calls[2][0] == "observe"
    assert journal.calls[2][1]["cursor"] == "journal-cursor-7"
    assert observed["result"]["isError"] is False
    assert response["page"]["observations"] == [observation]
    assert state.observation_cursor() == "journal-cursor-7"


@pytest.mark.parametrize("status", [400, 403])
def test_mcp_tool_returns_the_bounded_writer_refusal_without_its_credential(tmp_path, status):
    token = "service-credential-must-stay-private"
    refusal = f"supervisor run is not current; {token} " + "x" * 400
    connection = JsonHttpConnection("https://writer", token)

    class RefusingWriter:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, status, "Forbidden", {}, BytesIO(
                json.dumps({"error": refusal}).encode(),
            ))

    connection.opener = RefusingWriter()
    state = StateStore(tmp_path)
    state.record_admitted(RunReference.from_run(RUN))
    server = McpServer(SupervisorBridge(SupervisorHttpClient(connection), state))

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": OBSERVE_TOOL, "arguments": {"run_ref": RUN_REF}},
    })["result"]
    message = result["content"][0]["text"]

    assert result["isError"] is True
    assert "supervisor run is not current" in message
    assert token not in message
    assert len(message) < 300


def test_supervisor_hook_uses_a_fixed_trusted_mapping_and_only_a_run_reference():
    run = RunReference.from_run(RUN)
    body, headers = hook_request(run)

    assert set(body) == {"run_ref"}
    assert body["run_ref"] == run.to_dict()
    assert headers["Idempotency-Key"] == run.run_id
    assert headers["Content-Type"] == "application/json"
    fixture = json.loads(FIXTURE_PATH.read_text())
    mapping = fixture["openclaw_config"]["hooks"]["mappings"][0]
    assert mapping["match"] == {"path": "journal-supervisor"}
    assert mapping["agentId"] == "supervisor"
    assert mapping["action"] == "agent" and mapping["sessionMode"] == "isolated"
    assert mapping["allowUnsafeExternalContent"] is True
    assert "{{run_ref}}" in mapping["messageTemplate"]
    assert "one catalogued command" in mapping["messageTemplate"]
    assert mapping["messageTemplate"] == (
        "Handle this admitted journal supervisor run. Read the journal snapshot with "
        "journal_supervisor.observe or a generated catalogue read tool, then use only its evidence. "
        "If justified, call journal_supervisor.run_or_propose with one catalogued command. "
        "Read journal_supervisor.receipt after the decision and finish. Run reference: {{run_ref}}"
    )
    assert headers == {"Content-Type": "application/json", "Idempotency-Key": "run-1"}


def test_service_client_uses_the_admission_url_and_token_environment(monkeypatch):
    monkeypatch.setenv("JOURNAL_SUPERVISOR_ADMISSION_URL", "http://127.0.0.1:8421")
    monkeypatch.setenv("JOURNAL_SUPERVISOR_ADMISSION_TOKEN", "tenant-admission-token")
    monkeypatch.setenv("JOURNAL_SUPERVISOR_CREDENTIAL", "unused-legacy-name")

    client = service_client()

    assert client.connection.base_url == "http://127.0.0.1:8421"
    assert client.connection.token == "tenant-admission-token"


def test_service_client_requires_a_ca_for_the_non_loopback_writer(monkeypatch):
    monkeypatch.setenv("JOURNAL_SUPERVISOR_ADMISSION_URL", "https://writer:8422")
    monkeypatch.setenv("JOURNAL_SUPERVISOR_ADMISSION_TOKEN", "tenant-admission-token")
    monkeypatch.delenv("JOURNAL_SUPERVISOR_TLS_CA_FILE", raising=False)

    with pytest.raises(ValueError, match="TLS CA file is not configured"):
        service_client()


def test_retryable_admission_records_http_status_cause(tmp_path):
    failure = HTTPError("https://writer/_supervisor/v1/admit", 503, "upstream unavailable", {}, None)
    connection = JsonHttpConnection("https://writer", "private-admission-token")
    connection.opener = StubOpener([failure])
    state = StateStore(tmp_path)

    result = SupervisorBridge(SupervisorHttpClient(connection), state).reconcile("timer")

    assert result.reason == "service_unavailable"
    assert state.snapshot()["last_error"] == "service_unavailable: HTTP 503"
    assert state.snapshot()["retry_count"] == 1


def test_retryable_admission_records_only_safe_url_error_class(tmp_path):
    secret = "private-admission-token"
    connection = JsonHttpConnection("https://writer", secret)
    connection.opener = StubOpener([URLError(secret)])
    state = StateStore(tmp_path)

    result = SupervisorBridge(SupervisorHttpClient(connection), state).reconcile("timer")

    assert result.reason == "service_unavailable"
    assert state.snapshot()["last_error"] == "service_unavailable: URLError"
    assert secret not in state.path.read_text()


def test_private_adapters_use_only_fixed_authenticated_routes():
    receipt = make_receipt()
    receipt_envelope = {
        "status": receipt["status"], "reason": receipt["reason"], "receipt_id": 23,
        "data": receipt, "report": {"verification": {"verification": "verified"}}, "duplicate": False,
    }
    run = RunReference.from_run(RUN)
    apply_request = {
        "protocol_version": 1, "run_id": run.run_id, "installation_epoch": run.installation_epoch,
        "fence": run.fence, "grant_version": run.grant_version, "episode_id": run.episode_id,
        "action_id": run.pending_action_id, "observation_ids": [], "expected_revisions": [],
        "operations": [], "rationale": "Apply the admitted bundle.",
    }
    usage = {
        "input_tokens": 1, "output_tokens": 2, "cache_creation_input_tokens": 1,
        "cache_read_input_tokens": 1, "total_input_tokens": 3, "provider_requests": 2,
        "provider_retries": 0,
    }
    settlement = {
        "status": "settled", "usage_id": 24, "run_id": run.run_id, "fence": run.fence,
        "usage_status": "known", "duplicate": False,
    }
    opener = StubOpener([
        b'{"status":"skipped","reason":"empty"}',
        json.dumps(settlement).encode(),
        json.dumps(receipt_envelope).encode(),
        json.dumps(receipt_envelope).encode(),
        b'{"runId":"gateway-run-1"}',
    ])
    connection = JsonHttpConnection("http://127.0.0.1:9134", "journal-service-token")
    connection.opener = opener
    client = SupervisorHttpClient(connection)
    assert client.admit("timer", None, "wakeup-1", "scheduled") == {"status": "skipped", "reason": "empty"}
    assert client.settle_usage(run, usage) == settlement
    assert client.apply(apply_request) == receipt
    assert client.receipt("action-1") == receipt
    with pytest.raises(TransportError):
        connection.post("/_supervisor/v1/admin", {})
    hook = OpenClawHookClient("http://localhost:18789", "openclaw-hook-token")
    hook.opener = opener
    assert hook.send(RunReference.from_run(RUN)).gateway_run_id == "gateway-run-1"

    malformed = StubOpener([json.dumps({"status": "applied", "data": receipt}).encode()])
    rejected = SupervisorHttpClient(JsonHttpConnection("http://127.0.0.1:9134", "journal-service-token"))
    rejected.connection.opener = malformed
    with pytest.raises(TransportError, match="receipt envelope"):
        rejected.receipt("action-1")

    service_request, service_timeout = opener.requests[0]
    usage_request, usage_timeout = opener.requests[1]
    apply_request_sent, apply_timeout = opener.requests[2]
    receipt_request, receipt_timeout = opener.requests[3]
    hook_request_sent, hook_timeout = opener.requests[4]
    assert service_request.full_url == "http://127.0.0.1:9134/_supervisor/v1/admit"
    assert service_request.get_header("Authorization") == "Bearer journal-service-token"
    assert json.loads(service_request.data) == {
        "protocol_version": 1, "source": "timer", "observation_cursor": None,
        "wakeup_id": "wakeup-1", "kind": "scheduled",
    }
    assert usage_request.full_url == "http://127.0.0.1:9134/_supervisor/v1/usage"
    assert usage_request.get_header("Authorization") == "Bearer journal-service-token"
    assert usage_request.get_header("Idempotency-key") == run.run_id
    assert json.loads(usage_request.data) == {"protocol_version": 1, "run_ref": run.to_dict(), "usage": usage}
    assert apply_request_sent.full_url == "http://127.0.0.1:9134/_supervisor/v1/apply"
    assert json.loads(apply_request_sent.data) == apply_request
    assert receipt_request.full_url == "http://127.0.0.1:9134/_supervisor/v1/receipt"
    assert json.loads(receipt_request.data) == {"protocol_version": 1, "action_id": "action-1"}
    assert service_timeout == usage_timeout == apply_timeout == receipt_timeout == hook_timeout == 20
    assert hook_request_sent.full_url == "http://localhost:18789/hooks/journal-supervisor"
    assert hook_request_sent.get_header("Authorization") == "Bearer openclaw-hook-token"
    assert hook_request_sent.get_header("Idempotency-key") == "run-1"
    assert json.loads(hook_request_sent.data) == {"run_ref": run.to_dict()}


def test_wakeup_result_report_uses_the_authenticated_service_route():
    opener = StubOpener([b'{"status":"recorded","wakeup_id":"wakeup-1","entry_id":25,"result":"Acted","skip_reason":"","duplicate":false}'])
    connection = JsonHttpConnection("http://127.0.0.1:9134", "journal-service-token")
    connection.opener = opener

    result = SupervisorHttpClient(connection).record_wakeup("wakeup-1", "scheduled", "Acted")

    request, timeout = opener.requests[0]
    assert result["status"] == "recorded"
    assert result["result"] == "Acted"
    assert result["skip_reason"] == ""
    assert request.full_url == "http://127.0.0.1:9134/_supervisor/v1/wakeups"
    assert request.get_header("Authorization") == "Bearer journal-service-token"
    assert json.loads(request.data) == {
        "protocol_version": 1, "wakeup_id": "wakeup-1", "kind": "scheduled", "result": "Acted", "skip_reason": "",
    }
    assert timeout == 20


def test_pinned_command_and_tool_config_match_contract(tmp_path):
    fixture = json.loads(FIXTURE_PATH.read_text())
    validate_pinned_fixture(fixture)
    contract_schema = load_contract_schema()
    schemas = tool_input_schemas(contract_schema)
    input_limit = contract_schema["$defs"]["BudgetLimits"]["properties"]["max_input_tokens_per_turn"]
    supervisor = fixture["openclaw_config"]["agents"]["entries"]["supervisor"]

    assert tuple(schemas) == TOOL_NAMES
    assert schemas[OBSERVE_TOOL]["required"] == ["run_ref"]
    assert "cursor" in schemas[OBSERVE_TOOL]["properties"]
    read_commands = {
        (area, noun, verb)
        for area, nouns in CAPABILITY_CATALOGUE.items()
        for noun, verbs in nouns.items()
        for verb, tier in verbs.items()
        if tier == "read"
    }
    assert set(READ_TOOL_COMMANDS.values()) == read_commands
    assert RUN_OR_PROPOSE_TOOL in schemas
    assert "apply_maintenance" not in " ".join(TOOL_NAMES)
    assert input_limit == {"type": "integer", "minimum": 1, "maximum": 80000}
    assert PINNED_OPENCLAW_VERSION == "2026.10.8"
    assert PINNED_OPENCLAW_COMMIT.startswith("dc2523e")
    assert "default" not in supervisor
    assert fixture["openclaw_config"]["gateway"] == {
        "mode": "local", "bind": "lan", "auth": {"mode": "token"}
    }
    assert fixture["openclaw_config"]["plugins"] == {
        "enabled": True,
        "allow": ["anthropic"],
        "deny": ["memory-core"],
        "entries": {"memory-core": {
            "enabled": False,
            "config": {"dreaming": {"enabled": False}},
        }},
    }
    assert fixture["openclaw_config"]["agents"]["defaults"]["model"] == {
        "primary": "anthropic/claude-sonnet-5"
    }
    assert fixture["cron_add_params"]["payload"]["argv"] == [
        "/opt/journal-supervisor/bin/journal-supervisor-bridge", "reconcile"
    ]
    assert fixture["cron_add_params"]["enabled"] is False
    assert fixture["openclaw_config"]["mcp"]["servers"]["journal"]["args"] == []
    assert fixture["openclaw_config"]["mcp"]["servers"]["journal"]["enabled"] is False
    assert list(fixture["openclaw_config"]["mcp"]["servers"]) == ["journal"]
    assert fixture["openclaw_config"]["tools"]["allow"] == list(OPENCLAW_TOOL_NAMES)
    assert fixture["openclaw_config"]["tools"]["toolSearch"] is False
    policy = json.loads(FIXTURE_PATH.with_name("gateway-policy.fixture.json").read_text())
    assert policy["tools"]["allowlist"] == list(OPENCLAW_TOOL_NAMES)
    assert effective_tool_inventory(fixture, set()) == []
    assert effective_tool_inventory(fixture, {"journal__journal_supervisor-observe", "shell", "browser"}) == [
        "journal__journal_supervisor-observe"
    ]
    server = McpServer(SupervisorBridge(StubJournal(), StateStore(tmp_path)))
    listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in listed["result"]["tools"]] == list(TOOL_NAMES)
    assert "Omit cursor on the first read" in listed["result"]["tools"][0]["description"]

    expanded = json.loads(json.dumps(fixture))
    expanded["openclaw_config"]["agents"]["entries"]["supervisor"]["tools"]["allow"].append("shell")
    with pytest.raises(ContractError):
        validate_pinned_fixture(expanded)

    legacy_default = json.loads(json.dumps(fixture))
    legacy_default["openclaw_config"]["agents"]["entries"]["supervisor"]["default"] = True
    with pytest.raises(ContractError):
        validate_pinned_fixture(legacy_default)

    implicit_model = json.loads(json.dumps(fixture))
    implicit_model["openclaw_config"]["agents"]["defaults"].pop("model")
    with pytest.raises(ContractError):
        validate_pinned_fixture(implicit_model)

    broad_plugins = json.loads(json.dumps(fixture))
    broad_plugins["openclaw_config"]["plugins"]["allow"].append("browser")
    with pytest.raises(ContractError):
        validate_pinned_fixture(broad_plugins)


def test_catalogue_read_tool_returns_the_fenced_observation(tmp_path):
    journal = StubJournal()
    state = StateStore(tmp_path)
    state.record_admitted(RunReference.from_run(RUN))
    server = McpServer(SupervisorBridge(journal, state))
    name, command = next(iter(READ_TOOL_COMMANDS.items()))

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": name, "arguments": {"run_ref": RUN_REF}},
    })

    content = json.loads(result["result"]["content"][0]["text"])
    assert result["result"]["isError"] is False
    assert content["command"] == {"area": command[0], "noun": command[1], "verb": command[2]}
    assert content["snapshot"]["grant"]["grant_id"] == RUN["grant_id"]
    assert [call[0] for call in journal.calls] == ["observe"]


def test_observation_contains_five_matching_feedback_examples_as_data(app, monkeypatch):
    from datetime import timedelta

    from journal.models.entry import Entry
    from journal.models.plan import Plan
    from journal.repositories.supervisor_entries import SupervisorEntries
    from journal.repositories.supervisor_feedbacks import SupervisorFeedbacks
    from tests.test_supervisor_actions import _admitted_maintenance_context

    fixture = authority_seeded(app)
    context = _admitted_maintenance_context(app, monkeypatch, fixture, "bounded_write")
    scope = app.container.get(Scope)
    feedback = app.container.get(SupervisorFeedbacks)
    control_entries = app.container.get(SupervisorEntries)
    plans = app.container.get(Plans)
    try:
        with scope.environment(fixture.owner_environment.row_id):
            other_plan = plans.save(Plan(
                environment_id=fixture.owner_environment.row_id, title="another plan", brief="another plan brief",
            ), fixture.owner)
            plan_wakeup = control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorWakeup",
                actor=context["principal"].actor,
                data={
                    "tenant_id": context["principal"].scope["tenant_id"],
                    "plan_id": fixture.plan.row_id,
                    "wakeup_id": "feedback-example-plan-wakeup",
                },
                idempotency="test:feedback-example-plan-wakeup",
            ), context["principal"].actor)
            other_wakeup = control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorWakeup",
                actor=context["principal"].actor,
                data={
                    "tenant_id": context["principal"].scope["tenant_id"],
                    "plan_id": other_plan.row_id,
                    "wakeup_id": "feedback-example-other-wakeup",
                },
                idempotency="test:feedback-example-other-wakeup",
            ), context["principal"].actor)

            def record(plan_id, wakeup, verb, comment, area="Plans and tasks"):
                return feedback.create(plan_id, {
                    "decision_kind": "wakeup",
                    "decision_id": wakeup.row_id,
                    "verdict": "Useful",
                    "comment": comment,
                    "correction": "Should have done nothing",
                    "scenario": {
                        "plan": plan_id,
                        "area": area,
                        "verb": verb,
                        "wake_event": "failed_check",
                    },
                }, fixture.owner)

            record(fixture.plan.row_id, plan_wakeup, "plan priorities", "same-plan-oldest")
            record(fixture.plan.row_id, plan_wakeup, "plan priorities", "same-plan-middle")
            record(fixture.plan.row_id, plan_wakeup, "plan priorities", "same-plan-newest")
            record(other_plan.row_id, other_wakeup, "plan add", "same-area-oldest")
            record(other_plan.row_id, other_wakeup, "plan add", "same-area-middle")
            record(other_plan.row_id, other_wakeup, "plan add", "same-area-newest")
            record(other_plan.row_id, other_wakeup, "secret delete", "different-area", "Secrets")

        principal = context["principal"]
        with scope.environment(PROJECT):
            run = control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorRun",
                actor=principal.actor,
                data={
                    "tenant_id": principal.scope["tenant_id"],
                    "grant_id": context["grant"]["grant_id"],
                    "grant_version": context["grant"]["grant_version"],
                    "plan_id": context["grant"]["plan_id"],
                    "node_id": principal.scope["writer_node_id"],
                    "episode_id": "feedback-examples-episode",
                    "run_ref": "feedback-examples-run",
                    "pending_action_id": "feedback-examples-action",
                    "installation_epoch": principal.scope["installation_epoch"],
                    "fence": 2,
                    "lease_until": (context["time_source"].moment() + timedelta(minutes=5)).isoformat(),
                    "reservation": {"cost_usd": "0.000001"},
                    "status": "admitted",
                },
                idempotency="test:feedback-examples-run",
            ), principal.actor)

        observation_service = app.container.get(SupervisorObservations)
        request = {
            "protocol_version": 1,
            "run_id": run.data["run_ref"],
            "installation_epoch": principal.scope["installation_epoch"],
            "fence": run.data["fence"],
            "cursor": None,
        }
        with scope.environment(principal.scope["environment_id"]):
            observation = observation_service.observe(principal, request)

        examples = observation["snapshot"]["feedback_examples"]
        assert [example["comment"] for example in examples] == [
            "same-plan-newest", "same-plan-middle", "same-plan-oldest",
            "same-area-newest", "same-area-middle",
        ]
        assert len(examples) == 5
        assert all(len(example["comment"]) <= 1000 for example in examples)
        assert all(set(example) == {"id", "verdict", "comment", "correction", "scenario"} for example in examples)
        _title, brief = diagnostic_task_values(fixture.template)
        assert all(example["comment"] not in brief for example in examples)
    finally:
        fixture.authority.secrets_store.drop(fixture.credentials)


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


def test_mcp_observe_and_run_or_propose_require_current_fence(tmp_path):
    journal = StubJournal([admitted()])
    state = StateStore(tmp_path)
    state.record_admitted(RunReference.from_run(RUN))
    server = McpServer(SupervisorBridge(journal, state))
    wrong = dict(RUN_REF, fence=8)

    observe = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": OBSERVE_TOOL, "arguments": {"run_ref": wrong, "cursor": None}},
    })
    apply = server.handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": action_arguments(wrong)},
    })

    assert observe["result"]["isError"] is True
    assert apply["result"]["isError"] is True
    assert not [call for call in journal.calls if call[0] in {"observe", "apply", "receipt"}]


def test_run_or_propose_translates_catalogue_command_and_settles_usage(tmp_path):
    journal = StubJournal()
    state = metered_state_with_usage(tmp_path)
    server = McpServer(SupervisorBridge(journal, state))

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": action_arguments()},
    })

    assert result["result"]["isError"] is False
    assert json.loads(result["result"]["content"][0]["text"])["verification"] == "verified"
    assert [call[0] for call in journal.calls] == ["settle_usage", "apply"]
    assert journal.calls[-1][1]["operations"] == [{
        "kind": "plan_priorities", "plan_id": 1, "text": "Review the failed check.",
    }]


def test_run_or_propose_translates_a_tier_two_plan_tell_command(tmp_path):
    journal = StubJournal()
    state = metered_state_with_usage(tmp_path)
    server = McpServer(SupervisorBridge(journal, state))
    arguments = action_arguments()
    arguments.update({
        "verb": "tell",
        "arguments": {"plan_id": 1, "text": "Review the failed check first."},
    })

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": arguments},
    })

    assert result["result"]["isError"] is False
    assert journal.calls[-1][1]["operations"] == [{
        "kind": "plan_tell", "plan_id": 1, "text": "Review the failed check first.",
    }]


def test_run_or_propose_returns_journal_selected_proposal(tmp_path):
    journal = ProposalJournal()
    state = metered_state_with_usage(tmp_path)
    server = McpServer(SupervisorBridge(journal, state))

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": action_arguments()},
    })

    assert result["result"]["isError"] is False
    assert json.loads(result["result"]["content"][0]["text"])["status"] == "proposed"
    assert "mode" not in server.schemas[RUN_OR_PROPOSE_TOOL]["properties"]
    assert [call[0] for call in journal.calls] == ["settle_usage", "apply"]


def test_run_or_propose_refuses_a_never_catalogue_verb_before_settlement(tmp_path):
    journal = StubJournal()
    state = metered_state_with_usage(tmp_path)
    server = McpServer(SupervisorBridge(journal, state))
    arguments = action_arguments()
    arguments.update({"area": "Rules and reminders", "noun": "memory", "verb": "weigh", "arguments": {}})

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": arguments},
    })

    assert result["result"]["isError"] is True
    assert "not enabled" in result["result"]["content"][0]["text"]
    assert journal.calls == []


def test_run_or_propose_refuses_a_grant_change_reported_by_journal(tmp_path):
    journal = GrantChangedJournal()
    state = metered_state_with_usage(tmp_path)
    server = McpServer(SupervisorBridge(journal, state))

    result = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": action_arguments()},
    })

    assert result["result"]["isError"] is True
    assert "grant version changed" in result["result"]["content"][0]["text"]
    assert [call[0] for call in journal.calls] == ["settle_usage", "apply"]


def test_apply_reads_back_canonical_receipt_before_reporting_completion(tmp_path):
    journal = StubJournal([admitted()])
    state = metered_state_with_usage(tmp_path)
    hook = StubHook()
    bridge = SupervisorBridge(journal, state, VerifiedBudget(), hook)
    bridge.reconcile("timer")
    server = McpServer(bridge)
    observe_attempts = []
    observe = bridge.observe

    def capture_observe(*arguments):
        try:
            result = observe(*arguments)
        except Exception as error:
            observe_attempts.append((type(error).__name__, str(error)))
            raise
        observe_attempts.append(("observed", result))
        return result

    bridge.observe = capture_observe

    observed = server.handle({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": OBSERVE_TOOL, "arguments": {"run_ref": RUN_REF, "cursor": None}},
    })
    assert observed["result"]["isError"] is False, observe_attempts
    assert state.observation_cursor() is None

    applied = server.handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": RUN_OR_PROPOSE_TOOL, "arguments": action_arguments()},
    })

    assert applied["result"]["isError"] is False
    assert [call[0] for call in journal.calls] == ["admit", "observe", "observe", "settle_usage", "apply"]
    assert journal.calls[3][2] == {
        "input_tokens": 3, "output_tokens": 2, "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0, "total_input_tokens": 3, "provider_requests": 2,
        "provider_retries": 0,
    }
    assert json.loads(applied["result"]["content"][0]["text"])["verification"] == "verified"
    assert state.observation_cursor() == "cursor-after-page"
    assert state.snapshot()["receipt"]["action_id"] == RUN["pending_action_id"]


def test_apply_ack_without_readback_is_not_reported_as_complete(tmp_path):
    journal = PendingReceiptJournal()
    state = metered_state_with_usage(tmp_path)
    bridge = SupervisorBridge(journal, state)

    with pytest.raises(ContractError, match="receipt has an unsupported shape"):
        bridge.apply(action_arguments())

    assert [call[0] for call in journal.calls] == ["settle_usage", "apply"]
    assert state.snapshot()["receipt"] is None
    assert state.snapshot()["usage_settlement"] == "settled"


def test_tool_loop_stops_at_the_grant_token_caps(tmp_path):
    state = metered_state(tmp_path, max_input=8, max_output=8, max_requests=8)
    provider = StubProvider([
        provider_input_tokens(3), provider_response(2, 3, 1),
        provider_input_tokens(5), provider_response(3, 5, 1, 1),
    ])
    proxy = MeteringProxy(state, provider)

    first = proxy.forward(model_request())
    second = proxy.forward(model_request())

    assert first.status == 200 and second.status == 200
    assert second_body_max_tokens(provider.requests) == 5
    with pytest.raises(MeteringError, match="token cap") as refused:
        proxy.forward(model_request())
    assert refused.value.status_code == 403
    assert len(provider.requests) == 4
    usage = state.snapshot()["metering"]
    assert (usage["input_tokens"], usage["output_tokens"]) == (5, 8)
    assert (usage["cache_creation_input_tokens"], usage["cache_read_input_tokens"]) == (2, 1)
    assert usage["status"] == "capped"


def test_four_live_sized_generations_fit_under_the_eighty_thousand_input_cap(tmp_path):
    state = metered_state(tmp_path, max_input=80000, max_output=8000, max_requests=8)
    responses = [
        response
        for _ in range(4)
        for response in (
            provider_input_tokens(16144),
            provider_response(4, 612, 8605, 7535),
        )
    ]
    proxy = MeteringProxy(state, StubProvider(responses))

    replies = [proxy.forward(model_request(max_tokens=1000)) for _ in range(4)]
    usage = state.snapshot()["metering"]
    total_input = (
        usage["input_tokens"]
        + usage["cache_creation_input_tokens"]
        + usage["cache_read_input_tokens"]
    )

    assert [reply.status for reply in replies] == [200, 200, 200, 200]
    assert total_input == 64576
    assert total_input < 80000
    assert usage["output_tokens"] == 2448
    assert usage["provider_requests"] == 8
    assert usage["status"] == "capped"


def test_a_capped_turn_returns_a_non_retryable_anthropic_error(tmp_path):
    state = metered_state(tmp_path, max_input=4, max_output=8, max_requests=8)
    provider = StubProvider([provider_input_tokens(4), provider_response(4, 1)])
    proxy = MeteringProxy(state, provider)
    assert proxy.forward(model_request()).status == 200
    server = MeteringProxyServer(proxy, port=0)
    server.start()

    try:
        request = Request(
            f"http://127.0.0.1:{server.server.server_port}/v1/messages",
            data=json.dumps(model_request()).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as refused:
            urlopen(request, timeout=2)

        assert refused.value.code == 403
        assert refused.value.headers.get_content_type() == "application/json"
        assert json.loads(refused.value.read()) == {
            "type": "error",
            "error": {
                "type": "permission_error",
                "message": "supervisor turn ended at its input token cap",
            },
        }
        assert len(provider.requests) == 2
    finally:
        server.close()


def test_anthropic_transport_pins_messages_host_and_api_key_headers(monkeypatch):
    observed = {}
    response = SimpleNamespace(
        status=200,
        read=lambda _maximum: b'{"input_tokens":2}',
        getheaders=lambda: [("Content-Type", "application/json")],
    )
    connection = SimpleNamespace(
        request=lambda method, path, body, headers: observed.update({
            "method": method, "path": path, "body": body, "headers": headers,
        }),
        getresponse=lambda: response,
        close=lambda: observed.update({"closed": True}),
    )
    monkeypatch.setattr(
        "supervisor_bridge.metering.HTTPSConnection",
        lambda host, port, timeout: observed.update({"host": host, "port": port, "timeout": timeout}) or connection,
    )
    response = AnthropicProviderTransport("test-anthropic-key").post(
        "/v1/messages/count_tokens", {"model": "claude-sonnet-5"}, "application/json"
    )

    assert response.status == 200
    assert (observed["host"], observed["port"], observed["method"], observed["path"]) == (
        "api.anthropic.com", 443, "POST", "/v1/messages/count_tokens"
    )
    assert observed["headers"]["x-api-key"] == "test-anthropic-key"
    assert observed["headers"]["anthropic-version"] == "2023-06-01"
    assert "Authorization" not in observed["headers"]
    assert observed["closed"] is True


def test_bounded_provider_retries_consume_the_request_cap(tmp_path):
    state = metered_state(tmp_path, max_requests=4)
    provider = StubProvider([
        provider_input_tokens(2),
        ProviderResponse(429, b'{"error":"rate limited"}', headers={"Retry-After": "0"}),
        provider_response(2, 1),
    ])
    proxy = MeteringProxy(state, provider, retry_wait=lambda _seconds: None)

    assert proxy.forward(model_request()).status == 200
    usage = state.snapshot()["metering"]
    assert usage["provider_requests"] == 3
    assert usage["provider_retries"] == 1
    with pytest.raises(MeteringError, match="request cap"):
        proxy.forward(model_request())
    assert len(provider.requests) == 3


def test_eight_provider_requests_cover_four_counted_model_responses(tmp_path):
    state = metered_state(tmp_path, max_input=20, max_output=20, max_requests=8)
    provider = StubProvider([
        response
        for _ in range(4)
        for response in (provider_input_tokens(2), provider_response(2, 1))
    ])
    proxy = MeteringProxy(state, provider)

    for _ in range(4):
        assert proxy.forward(model_request()).status == 200

    usage = state.snapshot()["metering"]
    assert usage["provider_requests"] == 8
    assert usage["status"] == "capped"
    assert [path for path, _payload, _accept in provider.requests] == [
        "/v1/messages/count_tokens", "/v1/messages",
    ] * 4


@pytest.mark.parametrize("missing", [
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
])
def test_anthropic_missing_usage_figure_fails_closed(tmp_path, missing):
    state = metered_state(tmp_path)
    usage = {
        "input_tokens": 1,
        "output_tokens": 1,
        "cache_creation_input_tokens": 1,
        "cache_read_input_tokens": 1,
    }
    del usage[missing]
    provider = StubProvider([
        provider_input_tokens(4),
        ProviderResponse(200, json.dumps({"id": "message-1", "usage": usage}).encode()),
    ])

    with pytest.raises(MeteringError, match="usage"):
        MeteringProxy(state, provider).forward(model_request())

    assert state.snapshot()["budget_gate"] == "unknown_cost"
    assert state.snapshot()["active_run"] is None


def test_anthropic_stream_usage_records_input_cache_and_output_tokens(tmp_path):
    state = metered_state(tmp_path)
    body = b"\n".join([
        b'data: {"type":"message_start","message":{"usage":{"input_tokens":1,"output_tokens":1,"cache_creation_input_tokens":1,"cache_read_input_tokens":1}}}',
        b'data: {"type":"message_delta","usage":{"output_tokens":3}}',
        b'data: {"type":"message_stop"}',
    ])
    provider = StubProvider([
        provider_input_tokens(3),
        ProviderResponse(200, body, "text/event-stream"),
    ])

    assert MeteringProxy(state, provider).forward(model_request()).status == 200

    usage = state.snapshot()["metering"]
    assert usage["input_tokens"] == 1
    assert usage["output_tokens"] == 3
    assert usage["cache_creation_input_tokens"] == 1
    assert usage["cache_read_input_tokens"] == 1


def test_successful_provider_response_without_usage_fails_closed(tmp_path):
    state = metered_state(tmp_path)
    provider = StubProvider([provider_input_tokens(2), ProviderResponse(200, b'{"id":"response-1"}')])
    proxy = MeteringProxy(state, provider)

    with pytest.raises(MeteringError, match="usage"):
        proxy.forward(model_request())

    snapshot = state.snapshot()
    assert snapshot["budget_gate"] == "unknown_cost"
    assert snapshot["active_run"] is None
    assert snapshot["blocked_run"] == RUN_REF
    assert snapshot["metering"]["status"] == "unknown_cost"
    assert len(provider.requests) == 2


def test_provider_credentials_fail_without_an_alternate_route(tmp_path):
    state = metered_state(tmp_path)
    provider = StubProvider([ProviderResponse(401, b'{"error":"unauthorized"}')])
    proxy = MeteringProxy(state, provider)

    with pytest.raises(MeteringError, match="no fallback") as error:
        proxy.forward(model_request())

    assert error.value.status_code == 401
    assert [path for path, _, _ in provider.requests] == ["/v1/messages/count_tokens"]
    assert state.snapshot()["budget_gate"] == "unknown_cost"


def test_provider_usage_totals_survive_a_bridge_restart(tmp_path):
    state = metered_state(tmp_path, max_input=5, max_output=10, max_requests=8)
    first_provider = StubProvider([provider_input_tokens(3), provider_response(1, 2, 1, 1)])
    assert MeteringProxy(state, first_provider).forward(model_request()).status == 200

    restarted_state = StateStore(tmp_path)
    second_provider = StubProvider([provider_input_tokens(3)])
    restarted_proxy = MeteringProxy(restarted_state, second_provider)

    with pytest.raises(MeteringError, match="input token cap"):
        restarted_proxy.forward(model_request())
    assert len(second_provider.requests) == 1
    usage = restarted_state.snapshot()["metering"]
    assert (usage["input_tokens"], usage["output_tokens"]) == (1, 2)
    assert (usage["cache_creation_input_tokens"], usage["cache_read_input_tokens"]) == (1, 1)


def test_previous_provider_meter_state_blocks_an_active_run_after_the_route_change(tmp_path):
    state = StateStore(tmp_path)
    old_state = state.empty_state()
    metering = old_state["metering"]
    metering.pop("cache_creation_input_tokens")
    metering.pop("cache_read_input_tokens")
    metering["cached_tokens"] = 1
    metering.update({"run_ref": RUN_REF, "limits": {
        "max_input_tokens_per_turn": 10,
        "max_output_tokens_per_turn": 10,
        "max_provider_requests_per_turn": 8,
    }, "status": "known", "input_tokens": 2, "output_tokens": 1, "provider_requests": 2})
    old_state.update({"active_run": RUN_REF, "budget_gate": "verified", "usage_settlement": "reserved"})
    state.path.write_text(json.dumps(old_state))

    migrated = StateStore(tmp_path).snapshot()

    assert migrated["active_run"] is None
    assert migrated["blocked_run"] == RUN_REF
    assert migrated["budget_gate"] == "unknown_cost"
    assert migrated["metering"]["status"] == "unknown_cost"


def test_under_cap_provider_usage_settles_against_the_readback_receipt(tmp_path):
    state = metered_state(tmp_path, max_input=10, max_output=10, max_requests=8)
    provider = StubProvider([provider_input_tokens(3), provider_response(1, 2, 1, 1)])
    proxy = MeteringProxy(state, provider)
    assert proxy.forward(model_request()).status == 200
    bridge = SupervisorBridge(StubJournal(), state)

    receipt = bridge.receipt(RUN_REF)

    assert receipt["verification"] == "verified"
    bridge.receipt(RUN_REF)
    snapshot = state.snapshot()
    assert snapshot["usage_settlement"] == "settled"
    assert snapshot["receipt"]["usage"] == {
        "input_tokens": 1,
        "output_tokens": 2,
        "cache_creation_input_tokens": 1,
        "cache_read_input_tokens": 1,
        "total_input_tokens": 3,
        "provider_requests": 2,
        "provider_retries": 0,
    }
    assert snapshot["metering"]["status"] == "settled"
    with pytest.raises(MeteringError, match="budget is closed"):
        proxy.forward(model_request())
    assert len(provider.requests) == 2


def test_metered_budget_gate_requires_the_live_proxy_and_pinned_route(tmp_path):
    state = metered_state(tmp_path)
    fixture = json.loads(FIXTURE_PATH.read_text())
    config_path = tmp_path / "openclaw.json"
    config_path.write_text(json.dumps(fixture["openclaw_config"]))
    proof = MeteredAggregateBudgetProof(state, config_path, health_probe=lambda: True)
    run = RunReference.from_run(RUN)

    assert proof.is_verified(run) is True
    assert NoAggregateBudgetProof().is_verified(run) is False
    config = fixture["openclaw_config"]
    provider = config["models"]["providers"]["anthropic"]
    assert "auth" not in config
    assert set(provider) == {
        "baseUrl", "auth", "api", "apiKey", "agentRuntime", "maxTokens", "timeoutSeconds"
    }
    assert provider["api"] == "anthropic-messages"
    assert provider["apiKey"] == METERED_PROVIDER_API_KEY_PLACEHOLDER
    assert fixture["openclaw_config"]["agents"]["entries"]["supervisor"]["model"] == {
        "primary": "anthropic/claude-sonnet-5", "fallbacks": []
    }
    assert fixture["openclaw_config"]["agents"]["entries"]["supervisor"]["thinkingDefault"] == "high"

    provider["baseUrl"] = "https://api.anthropic.com"
    config_path.write_text(json.dumps(config))
    assert proof.is_verified(run) is False

    provider["baseUrl"] = METERED_PROVIDER_BASE_URL
    provider["apiKey"] = "a-real-provider-secret-must-not-be-configured"
    config_path.write_text(json.dumps(config))
    assert proof.is_verified(run) is False

    provider["apiKey"] = METERED_PROVIDER_API_KEY_PLACEHOLDER
    config["auth"] = {"order": {"anthropic": ["anthropic:supervisor-api"]}}
    config_path.write_text(json.dumps(config))
    assert proof.is_verified(run) is False

    del config["auth"]
    config_path.write_text(json.dumps(config))
    offline = MeteredAggregateBudgetProof(state, config_path, health_probe=lambda: False)
    assert offline.is_verified(run) is False

    fixture["openclaw_config"]["agents"]["defaults"]["maxConcurrent"] = 2
    config_path.write_text(json.dumps(fixture["openclaw_config"]))
    concurrent = MeteredAggregateBudgetProof(state, config_path, health_probe=lambda: True)
    assert concurrent.is_verified(run) is False


@pytest.mark.parametrize("status", [401, 403])
def test_authorization_refusal_is_bounded_and_redacts_the_service_token(status):
    token = "writer-credential-value"
    message = f"writer refused credential {token}: " + "x" * 400
    response = json.dumps({"error": message}).encode()
    connection = JsonHttpConnection("https://writer", token)

    class RefusingWriter:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, status, "Forbidden", {}, BytesIO(response))

    connection.opener = RefusingWriter()
    with pytest.raises(AuthorizationError) as refused:
        connection.post("/_supervisor/v1/admit", {})

    assert refused.value.cause.startswith("writer refused credential [redacted]:")
    assert len(refused.value.cause) == 240
    assert token not in refused.value.cause


def test_proxy_command_runs_the_gateway_metering_server(monkeypatch, tmp_path):
    state, provider, proxy = object(), object(), object()
    served = []

    class Server:
        def __init__(self, received):
            assert received is proxy

        def serve(self):
            served.append(True)

    monkeypatch.setattr(supervisor_main, "state_directory", lambda: tmp_path)
    monkeypatch.setattr(supervisor_main, "StateStore", lambda _directory: state)
    monkeypatch.setattr(supervisor_main, "AnthropicProviderTransport", lambda key: provider if key == "provider-key" else None)
    monkeypatch.setattr(supervisor_main, "MeteringProxy", lambda received_state, received_provider: proxy if (received_state, received_provider) == (state, provider) else None)
    monkeypatch.setattr(supervisor_main, "MeteringProxyServer", Server)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "provider-key")

    assert supervisor_main.run(["proxy"]) == 0
    assert served == [True]


def test_gateway_waits_for_proxy_health_before_starting_openclaw(monkeypatch):
    health = iter((False, True))
    sleeps = []
    monkeypatch.setattr(MeteredAggregateBudgetProof, "proxy_is_healthy", lambda: next(health))
    monkeypatch.setattr(supervisor_main.time, "sleep", sleeps.append)

    assert supervisor_main.run(["wait-for-proxy"]) == 0
    assert sleeps == [0.1]


def test_reconcile_command_forwards_the_staged_event_wakeup(monkeypatch, tmp_path, capsys):
    state = object()
    calls = []

    class Result:
        status = "skipped"

        def to_dict(self):
            return {"status": self.status, "reason": "empty"}

    class Bridge:
        def reconcile(self, *args, **kwargs):
            calls.append((args, kwargs))
            return Result()

    monkeypatch.setattr(supervisor_main, "state_directory", lambda: tmp_path)
    monkeypatch.setattr(supervisor_main, "StateStore", lambda _directory: state)
    monkeypatch.setattr(supervisor_main, "configured_bridge", lambda received: Bridge() if received is state else None)

    assert supervisor_main.run(["reconcile", "event", "failed_check", "PSU-02"]) == 0
    assert calls == [(("hint",), {"wakeup_id": "PSU-02", "event_kind": "failed_check", "event_id": "PSU-02"})]
    assert json.loads(capsys.readouterr().out) == {"status": "skipped", "reason": "empty"}


def test_mcp_command_uses_the_gateway_proxy_without_starting_another(monkeypatch, tmp_path):
    state, bridge = object(), object()
    served = []

    class Mcp:
        def __init__(self, received):
            assert received is bridge

        def serve(self):
            served.append(True)

    monkeypatch.setattr(supervisor_main, "state_directory", lambda: tmp_path)
    monkeypatch.setattr(supervisor_main, "StateStore", lambda _directory: state)
    monkeypatch.setattr(supervisor_main, "service_client", lambda: object())
    monkeypatch.setattr(supervisor_main, "SupervisorBridge", lambda *args: bridge)
    monkeypatch.setattr(supervisor_main, "McpServer", Mcp)
    monkeypatch.setattr(supervisor_main, "MeteringProxy", lambda *_args: pytest.fail("MCP must use the gateway proxy"))
    monkeypatch.setattr(supervisor_main, "MeteringProxyServer", lambda *_args: pytest.fail("MCP must not start its own proxy"))

    assert supervisor_main.run(["mcp"]) == 0
    assert served == [True]


def test_reconcile_invokes_hook_only_with_live_metered_proxy(tmp_path):
    fixture = json.loads(FIXTURE_PATH.read_text())
    config_path = tmp_path / "openclaw.json"
    config_path.write_text(json.dumps(fixture["openclaw_config"]))
    state = StateStore(tmp_path / "routed")
    hook = StubHook()
    journal = StubJournal([admitted()])
    proof = MeteredAggregateBudgetProof(state, config_path, health_probe=lambda: True)

    result = SupervisorBridge(journal, state, proof, hook).reconcile("timer")

    assert result.status == "hook_acknowledged"
    assert hook.calls == [RunReference.from_run(RUN)]

    fixture["openclaw_config"]["models"]["providers"]["anthropic"]["baseUrl"] = "https://api.anthropic.com"
    config_path.write_text(json.dumps(fixture["openclaw_config"]))
    blocked_state = StateStore(tmp_path / "unrouted")
    blocked_hook = StubHook()
    blocked_journal = StubJournal([admitted()])
    blocked_proof = MeteredAggregateBudgetProof(blocked_state, config_path, health_probe=lambda: True)

    blocked = SupervisorBridge(blocked_journal, blocked_state, blocked_proof, blocked_hook).reconcile("timer")

    assert blocked.status == "blocked" and blocked.reason == "unknown_cost"
    assert blocked_hook.calls == []


def test_controlled_loop_reaches_normal_driver_and_canonical_receipt(tmp_path, monkeypatch):
    for name in ("JOURNAL_ROOT", "JOURNAL_ENV", "JOURNAL_ACTOR", "JOURNAL_SESSION"):
        monkeypatch.delenv(name, raising=False)
    tenant_root = tmp_path / "tenants" / "tenant-a"
    app = booted(tenant_root, monkeypatch)
    driver_processes = prepare_driver_processes(app, monkeypatch)
    fixture = start_normal_driver(app, driver_processes)
    current_work = add_phase_task(app, fixture, "current work", "Complete the existing work")
    proxy_server = None
    try:
        grant, token, _principal = authority_admitted(fixture, "bounded_write")
        time_source = app.container.get(TimeSource)
        time_source.pin(time_source.seconds() + 15 * 60)
        check = app.container.get(Checks).find(fixture.check.row_id)
        observations = app.container.get(SupervisorObservations)
        observed_at = time_source.seconds()
        observations.completed(check, CheckCompleted(
            environment_id=fixture.owner_environment.row_id,
            time=observed_at,
            check_id=check.row_id,
            title=check.title,
            passed=False,
            output="health check failed",
            prior_failure=False,
            wait_target=False,
            failure_reported_at=0,
        ), observed_at - 1, "")

        service = SupervisorHttpClient(JsonHttpConnection(
            f"http://127.0.0.1:{app.runtime().server.port}", token,
        ))
        state = StateStore(tenant_root / "gateway_state")
        pinned = json.loads(FIXTURE_PATH.read_text())
        config_path = tenant_root / "gateway_state" / "openclaw.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(pinned["openclaw_config"]))
        scripted_answers = []
        provider_requests = []

        def scripted_provider(path, payload, _accept):
            provider_requests.append((path, payload))
            if path == "/v1/messages/count_tokens":
                return provider_input_tokens(8)
            name, arguments = scripted_answers.pop(0)
            return ProviderResponse(200, json.dumps({
                "id": "scripted-message",
                "content": [{"type": "tool_use", "id": "scripted-tool", "name": name, "input": arguments}],
                "usage": {"input_tokens": 8, "output_tokens": 5,
                    "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
            }).encode())

        proxy = MeteringProxy(state, SimpleNamespace(post=scripted_provider), retry_wait=lambda _seconds: None)
        proxy_server = MeteringProxyServer(proxy)
        proxy_server.start()
        proof = MeteredAggregateBudgetProof(
            state, config_path,
            health_probe=lambda: proxy_server.thread.is_alive() and proxy_server.server.fileno() >= 0,
        )
        hook_calls = []

        def scripted_hook(run):
            hook_calls.append(run)
            hook, _headers = hook_request(run)
            assert hook == {"run_ref": run.to_dict()}
            mcp = McpServer(bridge)
            listed = mcp.handle({"jsonrpc": "2.0", "id": "tools", "method": "tools/list"})
            tools = listed["result"]["tools"]
            assert [tool["name"] for tool in tools] == list(TOOL_NAMES)
            model_tools = [{"name": tool["name"], "description": tool["description"],
                "input_schema": tool["inputSchema"]} for tool in tools]

            def scripted_call(name, arguments, step):
                scripted_answers.append((name, arguments))
                request = {
                    "model": "anthropic/claude-sonnet-5",
                    "messages": [{"role": "user", "content": json.dumps({"run_ref": run.to_dict(), "step": step})}],
                    "tools": model_tools,
                    "max_tokens": 32,
                    "stream": False,
                    "thinking": {"type": "adaptive"},
                }
                reply = urlopen(Request(
                    f"{METERED_PROVIDER_BASE_URL}/v1/messages",
                    data=json.dumps(request).encode(),
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    method="POST",
                ), timeout=5)
                model_answer = json.loads(reply.read())
                tool_call = model_answer["content"][0]
                assert tool_call["name"] == name and tool_call["input"] == arguments
                return mcp.handle({"jsonrpc": "2.0", "id": step, "method": "tools/call",
                    "params": {"name": name, "arguments": tool_call["input"]}})

            observed = scripted_call(OBSERVE_TOOL, {"run_ref": run.to_dict(), "cursor": None}, "observe")
            assert observed["result"]["isError"] is False
            observation = json.loads(observed["result"]["content"][0]["text"])
            assert len(observation["page"]["observations"]) == 1
            snapshot = observation["snapshot"]
            page_observation = observation["page"]["observations"][0]
            action = {
                "run_ref": run.to_dict(),
                "observation_ids": [page_observation["observation_id"]],
                "expected_revisions": [
                    {"ref": {"table": "plans", "id": grant["plan_id"]}, "revision": snapshot["plan_revision"]},
                    {"ref": {"table": "phases", "id": snapshot["current_phase"]["phase_id"]},
                        "revision": snapshot["current_phase"]["revision"]},
                ],
                "area": "Plans and tasks",
                "noun": "task",
                "verb": "create",
                "arguments": {
                    "plan_id": grant["plan_id"],
                    "phase_id": snapshot["current_phase"]["phase_id"],
                    "template_id": grant["diagnostic_template_id"],
                    "template_revision": grant["diagnostic_template_revision"],
                    "evidence_ids": [page_observation["observation_id"]],
                },
                "rationale": "The current failed check needs a bounded diagnostic task.",
            }
            applied = scripted_call(RUN_OR_PROPOSE_TOOL, action, "run_or_propose")
            assert applied["result"]["isError"] is False, applied
            applied_receipt = json.loads(applied["result"]["content"][0]["text"])
            assert applied_receipt["verification"] == "verified"
            canonical_receipt = applied_receipt
            assert canonical_receipt["verification"] == "verified"
            return HookAcknowledgement("scripted-model-run")

        bridge = SupervisorBridge(service, state, proof, SimpleNamespace(send=scripted_hook))
        result = bridge.reconcile("timer")
        app.runtime().deferred.drain()
        status, answer = posted(app, "/hooks/codex", {
            "hook_event_name": "Stop", "session_id": fixture.agent.session,
        }, {"X-Journal-Env": fixture.driver_environment.name})
        assert status < 400, answer
        app.runtime().deferred.drain()
        with app.container.get(Scope).environment(fixture.owner_environment.row_id):
            current_work = app.container.get(Tasks).find(current_work.row_id)
        assert current_work.state == TaskState.STARTED

        assert result.status == "hook_acknowledged" and result.reason == "ack_is_not_completion", (
            result.status, result.reason, state.snapshot(),
        )
        active = state.active_run()
        assert hook_calls == [active]
        snapshot = state.snapshot()
        assert active is not None and snapshot["receipt"]["verification"] == "verified"
        assert snapshot["usage_settlement"] == "settled"
        assert snapshot["receipt"]["usage"] == {
            "input_tokens": 16,
            "output_tokens": 10,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "total_input_tokens": 16,
            "provider_requests": 4,
            "provider_retries": 0,
        }
        assert len(provider_requests) == 4
        assert [path for path, _payload in provider_requests] == [
            "/v1/messages/count_tokens", "/v1/messages",
        ] * 2
        assert all(payload["model"] == "claude-sonnet-5" for _path, payload in provider_requests)

        title, brief = diagnostic_task_values(fixture.template)
        scope = app.container.get(Scope)
        with scope.environment(fixture.owner_environment.row_id):
            diagnostics = [task for task in app.container.get(Plans).phase_tasks(fixture.phase)
                if task.title == title and task.brief == brief]
        assert len(diagnostics) == 1
        diagnostic = diagnostics[0]
        with scope.environment(fixture.owner_environment.row_id):
            current = app.container.get(Tasks).find(current_work.row_id)
            app.container.get(Tasks).save(
                current.completed(time_source.moment(), "current work completed"),
                Actor.agent(fixture.agent.session),
            )
        app.runtime().deferred.drain()
        with scope.environment(fixture.owner_environment.row_id):
            current = app.container.get(Tasks).find(current_work.row_id)
            diagnostic = app.container.get(Tasks).find(diagnostic.row_id)
        with scope.environment(fixture.driver_environment.row_id):
            holder = app.container.get(Tasks).task_holder(diagnostic.row_id)
        assert current.state == TaskState.COMPLETED
        assert diagnostic.state == TaskState.STARTED and holder == Ref.build(fixture.agent)
        assert fixture.agent.environment_id in driver_processes.running
        with scope.environment(PROJECT):
            usage_rows = app.container.get(Entries).supervisor_records(
                "SupervisorUsage", last=10, run_ref=active.run_id,
            )
        assert usage_rows and usage_rows[-1].data["status"] == "known"
        assert usage_rows[-1].data["provider_requests"] == 4
        with scope.environment(PROJECT):
            action_receipts = app.container.get(Entries).supervisor_records(
                "SupervisorActionReceipt", last=10, run_id=active.run_id,
            )
        assert action_receipts and usage_rows[-1].row_id < action_receipts[-1].row_id
        assert action_receipts[-1].data["actor_kind"] == "plugin"
        assert action_receipts[-1].data["actor_id"] == "journal-supervisor"
    finally:
        if proxy_server is not None:
            proxy_server.close()
        stop_normal_driver(fixture)
        app.runtime().stop()


def test_two_tenant_replay_restore_and_injection_boundaries(tmp_path, monkeypatch):
    for name in ("JOURNAL_ROOT", "JOURNAL_ENV", "JOURNAL_ACTOR", "JOURNAL_SESSION"):
        monkeypatch.delenv(name, raising=False)
    staging_root = tmp_path / "two-tenants"
    tenant_a = staging_root / "tenant-a"
    tenant_b = staging_root / "tenant-b"
    app_a = App(Config(tenant_a, port=0))
    app_b = App(Config(tenant_b, port=0))
    server_a = app_a.container.call(Server)
    server_b = app_b.container.call(Server)
    started_a = False
    started_b = False
    stopped_a = False
    restored = None
    fixture_a = fixture_b = None
    try:
        server_a.start()
        started_a = True
        server_b.start()
        started_b = True
        fixture_a = authority_seeded(app_a, owner_id=101)
        fixture_b = authority_seeded(app_b, owner_id=202)
        monkeypatch.setattr(fixture_a.authority.agents, "is_running", lambda _environment: True)
        monkeypatch.setattr(fixture_b.authority.agents, "is_running", lambda _environment: True)
        grant_a, token_a, _principal_a = authority_admitted(fixture_a, "bounded_write")
        grant_b, token_b, _principal_b = authority_admitted(fixture_b, "bounded_write")
        assert grant_a["scope"]["tenant_id"] != grant_b["scope"]["tenant_id"]
        base_a = f"http://127.0.0.1:{server_a.port}"
        base_b = f"http://127.0.0.1:{server_b.port}"
        client_a = SupervisorHttpClient(JsonHttpConnection(base_a, token_a))
        client_b = SupervisorHttpClient(JsonHttpConnection(base_b, token_b))

        entries_b = app_b.container.get(Entries)
        before_b = entries_b.global_last_id()
        foreign_client = SupervisorHttpClient(JsonHttpConnection(base_b, token_a))
        with pytest.raises(AuthorizationError) as refused:
            foreign_client.admit("timer", None)
        assert refused.value.cause == "the supervisor service credential is invalid or revoked"
        unauthorized_state = StateStore(tmp_path / "unauthorized_bridge_state")
        result = SupervisorBridge(foreign_client, unauthorized_state).reconcile("timer")
        snapshot = unauthorized_state.snapshot()
        assert result.reason == "service_unauthorized"
        assert snapshot["last_error"] == "service_unauthorized: the supervisor service credential is invalid or revoked"
        assert token_a not in json.dumps(snapshot)
        with pytest.raises(AuthorizationError):
            foreign_client.settle_usage(RunReference.from_run(RUN), {
                "input_tokens": 1, "output_tokens": 1, "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0, "total_input_tokens": 1, "provider_requests": 1,
                "provider_retries": 0,
            })
        assert entries_b.global_last_id() == before_b
        assert client_a.admit("timer", None)["status"] == "skipped"

        mcp = McpServer(SupervisorBridge(client_a, StateStore(tenant_a / "gateway_state")))
        listed = mcp.handle({"jsonrpc": "2.0", "id": "tools", "method": "tools/list"})
        assert [tool["name"] for tool in listed["result"]["tools"]] == list(TOOL_NAMES)
        unknown = mcp.handle({"jsonrpc": "2.0", "id": "injection", "method": "tools/call",
            "params": {"name": "shell", "arguments": {"command": "printenv"}}})
        assert unknown["error"]["code"] == -32602
        with pytest.raises(ContractError, match="operation kind is not enabled"):
            validate_operation({"kind": "shell_command", "argv": ["printenv"]})

        state_directory = tenant_a / "gateway_state"
        state = metered_state(state_directory)
        provider = StubProvider([provider_input_tokens(3), provider_response(3, 2)])
        assert MeteringProxy(state, provider).forward(model_request()).status == 200
        first_receipt = SupervisorBridge(StubJournal(), state).receipt(RUN_REF)
        restarted = StateStore(state_directory)
        second_receipt = SupervisorBridge(StubJournal(), restarted).receipt(RUN_REF)
        assert second_receipt == first_receipt
        assert restarted.snapshot()["usage_settlement"] == "settled"
        assert restarted.snapshot()["receipt"]["usage"]["input_tokens"] == 3
        assert len(provider.requests) == 2

        server_a.stop()
        app_a.container.get(Connection).close()
        stopped_a = True
        restore_root = staging_root / "restore-candidate"
        copytree(tenant_a, restore_root)
        restored = App(Config(restore_root, port=0))
        restored_entries = restored.container.get(Entries)
        restored_grants = restored_entries.selected_globally(
            restored_entries.query().filter(entry_type="SupervisorGrant")
                .filter_json("data->grant_id", grant_a["grant_id"]).limit(10),
        )
        assert len(restored_grants) == 1
        assert tenant_a.resolve() != tenant_b.resolve() != restore_root.resolve()
        assert (tenant_a / ".journal" / "journal.db").resolve() != (tenant_b / ".journal" / "journal.db").resolve()
    finally:
        if restored is not None:
            restored.container.get(Connection).close()
        if started_a and not stopped_a:
            server_a.stop()
            app_a.container.get(Connection).close()
        if started_b:
            server_b.stop()
            app_b.container.get(Connection).close()
        if fixture_a is not None:
            fixture_a.authority.secrets_store.drop(fixture_a.credentials)
        if fixture_b is not None:
            fixture_b.authority.secrets_store.drop(fixture_b.credentials)


def second_body_max_tokens(provider_requests):
    generation = [payload for path, payload, _ in provider_requests if path == "/v1/messages"]
    return generation[-1]["max_tokens"]



def test_mcp_initialize_answers_a_newer_protocol_version_with_the_latest_it_supports(tmp_path):
    server = McpServer(SupervisorBridge(StubJournal(), StateStore(tmp_path)))

    def version(requested):
        answer = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": requested}})
        return answer["result"]["protocolVersion"]

    assert version("2025-03-26") == "2025-03-26", "a supported version is answered as asked"
    assert version("2025-11-25") == "2025-06-18", "a newer client version gets the latest the bridge supports"
    missing = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert missing["error"]["code"] == -32602, "a request without a version is refused"
