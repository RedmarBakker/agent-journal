from dataclasses import dataclass
import re
from typing import Protocol

from supervisor_bridge.contracts import (
    ContractError,
    RunReference,
    bounded_cursor,
    bounded_text,
    nonnegative_integer,
    positive_integer,
    strict_object,
    validate_operation,
)
from supervisor_bridge.metering import grant_token_limits
from supervisor_bridge.state import StateError, StateStore
from supervisor_bridge.transport import (
    AuthorizationError,
    HookAcknowledgement,
    OpenClawHookClient,
    ReceiptNotFound,
    RetryableTransportError,
    SupervisorHttpClient,
    TransportError,
)


MAX_HOOK_ATTEMPTS = 2


class AggregateBudgetProof(Protocol):
    """A deployment-owned proof that every billable request is bounded."""

    def is_verified(self, run: RunReference) -> bool: ...


class NoAggregateBudgetProof:
    """The reviewed OpenClaw pin has no proven whole-turn request/token ceiling."""

    def is_verified(self, run: RunReference) -> bool:
        return False


@dataclass(frozen=True)
class ReconcileResult:
    status: str
    reason: str = ""
    run_ref: dict | None = None
    hook_acknowledgement: HookAcknowledgement | None = None

    def to_dict(self) -> dict:
        value = {"status": self.status}
        if self.reason:
            value["reason"] = self.reason
        if self.run_ref:
            value["run_ref"] = self.run_ref
        if self.hook_acknowledgement:
            value["hook_acknowledgement"] = self.hook_acknowledgement.gateway_run_id
        return value


class SupervisorBridge:
    """The shared hint/timer admission path and its fail-closed model gate."""

    def __init__(
        self,
        client: SupervisorHttpClient,
        state: StateStore,
        budget: AggregateBudgetProof | None = None,
        hook: OpenClawHookClient | None = None,
    ):
        self.client = client
        self.state = state
        self.budget = budget or NoAggregateBudgetProof()
        self.hook = hook

    def reconcile(self, source: str) -> ReconcileResult:
        if source not in {"hint", "timer"}:
            raise ContractError("reconcile source is not enabled")
        try:
            admission = self.client.admit(source, self.state.observation_cursor())
        except AuthorizationError:
            self.state.record_failure("service_unauthorized", False)
            return ReconcileResult("failed", "service_unauthorized")
        except RetryableTransportError:
            self.state.record_failure("service_unavailable", True)
            return ReconcileResult("failed", "service_unavailable")
        except TransportError:
            self.state.record_failure("service_rejected", False)
            return ReconcileResult("failed", "service_rejected")

        if not isinstance(admission, dict):
            self.state.record_failure("service_rejected", False)
            return ReconcileResult("failed", "invalid_admission")
        if admission.get("status") == "skipped":
            reason = admission.get("reason")
            if set(admission) != {"status", "reason"} or not isinstance(reason, str) or reason not in {
                "empty", "busy", "ineligible", "stale_evidence", "budget_exhausted", "unknown_cost", "revoked", "needs_owner"
            }:
                self.state.record_failure("service_rejected", False)
                return ReconcileResult("failed", "invalid_admission")
            self.state.record_skipped(reason)
            return ReconcileResult("skipped", reason)
        if set(admission) != {"status", "run"} or admission.get("status") != "admitted":
            self.state.record_failure("service_rejected", False)
            return ReconcileResult("failed", "invalid_admission")

        try:
            previous = self.state.snapshot()
            run = RunReference.from_run(admission["run"])
            previous_run = RunReference.from_reference(previous["active_run"]) if previous["active_run"] else None
            self.state.record_admitted(run)
        except (ContractError, KeyError, StateError):
            self.state.record_failure("service_rejected", False)
            return ReconcileResult("failed", "invalid_admission")

        if (previous_run == run and previous["budget_gate"] == "unknown_cost") or previous["blocked_run"] == run.to_dict():
            self.state.record_unknown_cost()
            return ReconcileResult("blocked", "unknown_cost", run.to_dict())
        if previous_run == run and previous["metering"]["status"] == "settled":
            return ReconcileResult("skipped", "run_settled", run.to_dict())

        try:
            observed = self.observe(run.to_dict(), None)
            self.state.record_budget_limits(run, grant_token_limits(observed["snapshot"], run))
        except (ContractError, KeyError, StateError, TransportError, TypeError):
            self.state.record_unknown_cost()
            return ReconcileResult("blocked", "unknown_cost", run.to_dict())
        if not self.budget.is_verified(run):
            self.state.record_unknown_cost()
            return ReconcileResult("blocked", "unknown_cost", run.to_dict())
        self.state.record_budget_verified(run)
        if self.hook is None:
            self.state.record_failure("hook_unavailable", False)
            return ReconcileResult("failed", "hook_unavailable", run.to_dict())

        with self.state.hook_locked() as acquired:
            if not acquired:
                return ReconcileResult("admitted", "hook_in_progress", run.to_dict())
            for _ in range(MAX_HOOK_ATTEMPTS):
                if not self.state.claim_hook(run, MAX_HOOK_ATTEMPTS):
                    return ReconcileResult("admitted", "hook_not_repeated", run.to_dict())
                try:
                    acknowledgement = self.hook.send(run)
                    self.state.record_hook_status("acknowledged")
                    return ReconcileResult("hook_acknowledged", "ack_is_not_completion", run.to_dict(), acknowledgement)
                except AuthorizationError:
                    self.state.record_hook_status("unauthorized")
                    self.state.record_failure("hook_unauthorized", False)
                    return ReconcileResult("failed", "hook_unauthorized", run.to_dict())
                except RetryableTransportError:
                    self.state.record_failure("hook_unavailable", True)
                except TransportError:
                    self.state.record_failure("hook_unavailable", False)
                    return ReconcileResult("failed", "hook_unavailable", run.to_dict())
            return ReconcileResult("hook_uncertain", "retry_limit", run.to_dict())

    def observe(self, run_ref: object, cursor: object) -> dict:
        run = self.require_active(run_ref)
        request_cursor = bounded_cursor(cursor)
        request = {
            "protocol_version": 1,
            "run_id": run.run_id,
            "installation_epoch": run.installation_epoch,
            "fence": run.fence,
            "cursor": request_cursor,
        }
        result = self.call_service(self.client.observe, request)
        if not isinstance(result, dict) or set(result) != {"protocol_version", "run", "snapshot", "page", "server_now_ms"}:
            raise ContractError("observe response has an unsupported shape")
        if type(result["protocol_version"]) is not int or result["protocol_version"] != 1 or not isinstance(result["snapshot"], dict):
            raise ContractError("observe response version or snapshot is unsupported")
        nonnegative_integer(result["server_now_ms"], "server_now_ms")
        if RunReference.from_run(result["run"]) != run:
            raise ContractError("observe response changed the admitted fence")
        page = result["page"]
        if not isinstance(page, dict) or set(page) != {
            "protocol_version", "cursor", "next_cursor", "node_heartbeat_at_ms", "observation_watermark_ms", "observations"
        }:
            raise ContractError("observation page has an unsupported shape")
        if not isinstance(page["observations"], list) or len(page["observations"]) > 100:
            raise ContractError("observation page exceeds the fixed limit")
        if type(page["protocol_version"]) is not int or page["protocol_version"] != 1:
            raise ContractError("observation page version is unsupported")
        if page["cursor"] != request_cursor:
            raise ContractError("observation page cursor differs from the request")
        next_cursor = page["next_cursor"]
        if next_cursor is not None:
            bounded_cursor(next_cursor)
        nonnegative_integer(page["node_heartbeat_at_ms"], "node_heartbeat_at_ms")
        nonnegative_integer(page["observation_watermark_ms"], "observation_watermark_ms")
        if not all(isinstance(observation, dict) for observation in page["observations"]):
            raise ContractError("observation page contains a non-object reference")
        return result

    def apply(self, arguments: object) -> dict:
        from supervisor_bridge.contracts import action_request

        reference = self.reference_from_action(arguments)
        run = self.require_active(reference.to_dict())
        action = action_request(run, arguments)
        usage = self.state.settlement_usage(run)
        settlement = self.call_service(self.client.settle_usage, run, usage)
        self.state.record_usage_settlement(run, settlement)
        receipt = self.call_service(self.client.apply, action)
        self.validate_receipt(receipt, run)
        self.state.record_receipt(receipt, run)
        return receipt

    def receipt(self, run_ref: object) -> dict:
        run = self.require_active(run_ref)
        try:
            result = self.call_service(self.client.receipt, run.pending_action_id)
        except ReceiptNotFound:
            self.state.record_receipt_pending()
            raise
        self.validate_receipt(result, run)
        self.state.record_receipt(result, run)
        return result

    def call_service(self, call, *arguments):
        try:
            return call(*arguments)
        except AuthorizationError:
            self.state.record_failure("service_unauthorized", False)
            raise
        except RetryableTransportError:
            self.state.record_failure("service_unavailable", True)
            raise
        except ReceiptNotFound:
            raise
        except TransportError:
            self.state.record_failure("service_rejected", False)
            raise

    def require_active(self, value: object) -> RunReference:
        supplied = RunReference.from_reference(value)
        active = self.state.active_run()
        if active is None or supplied != active:
            raise ContractError("run_ref is not the current admitted fenced run")
        return active

    @staticmethod
    def reference_from_action(value: object) -> RunReference:
        if not isinstance(value, dict) or "run_ref" not in value:
            raise ContractError("apply_maintenance requires a fenced run_ref")
        return RunReference.from_reference(value["run_ref"])

    @staticmethod
    def validate_receipt(receipt: object, run: RunReference) -> None:
        expected = {
            "protocol_version", "action_id", "episode_id", "run_id", "grant_id", "grant_version", "scope", "fence",
            "intent_sha256", "actor_kind", "actor_id", "status", "reason", "recorded_at_ms", "observation_ids",
            "affected_refs", "changes", "verification", "outcome", "proposed_operations",
        }
        if not isinstance(receipt, dict) or set(receipt) != expected:
            raise ContractError("receipt has an unsupported shape")
        if type(receipt["protocol_version"]) is not int or receipt["protocol_version"] != 1:
            raise ContractError("receipt protocol version is unsupported")
        for key in ("action_id", "episode_id", "run_id", "grant_id", "actor_id"):
            bounded_text(receipt[key], key, 1, 256)
        positive_integer(receipt["grant_version"], "grant_version")
        positive_integer(receipt["fence"], "fence")
        nonnegative_integer(receipt["recorded_at_ms"], "recorded_at_ms")
        scope = strict_object(receipt["scope"], frozenset({
            "tenant_id", "project_id", "environment_id", "manager_id", "writer_node_id", "installation_epoch",
        }), frozenset({
            "tenant_id", "project_id", "environment_id", "manager_id", "writer_node_id", "installation_epoch",
        }), "receipt scope")
        for key in ("tenant_id", "project_id", "manager_id", "writer_node_id"):
            bounded_text(scope[key], key, 1, 256)
        positive_integer(scope["environment_id"], "environment_id")
        positive_integer(scope["installation_epoch"], "scope installation_epoch")
        if scope["installation_epoch"] != run.installation_epoch:
            raise ContractError("receipt scope epoch differs from the admitted run")
        if not isinstance(receipt["intent_sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", receipt["intent_sha256"]):
            raise ContractError("receipt intent hash is invalid")
        if not isinstance(receipt["status"], str) or receipt["status"] not in {"proposed", "applied", "conflicted", "rejected"}:
            raise ContractError("receipt status is unsupported")
        if receipt["reason"] is not None:
            bounded_text(receipt["reason"], "receipt reason", 0, 256)
        if not isinstance(receipt["observation_ids"], list) or not 1 <= len(receipt["observation_ids"]) <= 20:
            raise ContractError("receipt observation references are outside the contract bounds")
        for observation_id in receipt["observation_ids"]:
            bounded_text(observation_id, "receipt observation_id", 1, 256)
        if not isinstance(receipt["affected_refs"], list) or len(receipt["affected_refs"]) > 12:
            raise ContractError("receipt affected references exceed the contract bound")
        for row_ref in receipt["affected_refs"]:
            reference = strict_object(row_ref, frozenset({"table", "id"}), frozenset({"table", "id"}), "receipt row reference")
            if not isinstance(reference["table"], str) or reference["table"] not in {"plans", "phases", "tasks", "checks", "review_rounds"}:
                raise ContractError("receipt row reference table is unsupported")
            positive_integer(reference["id"], "receipt row id")
        if not isinstance(receipt["changes"], list) or len(receipt["changes"]) > 12:
            raise ContractError("receipt changes exceed the contract bound")
        change_keys = frozenset({"ref", "field", "before_revision", "after_revision", "before_value", "after_value"})
        for change in receipt["changes"]:
            fields = strict_object(change, change_keys, change_keys, "receipt field change")
            validate_receipt_ref(fields["ref"])
            if not isinstance(fields["field"], str) or fields["field"] not in {"priorities", "diagnostic_template", "plan_link", "phase_link", "interval"}:
                raise ContractError("receipt changed a field outside the contract")
            bounded_text(fields["before_revision"], "before_revision", 1, 256)
            bounded_text(fields["after_revision"], "after_revision", 1, 256)
            for key in ("before_value", "after_value"):
                value = fields[key]
                if value is not None and type(value) not in {str, int}:
                    raise ContractError(f"{key} is not a supported receipt value")
                if isinstance(value, str) and len(value) > 2048:
                    raise ContractError(f"{key} exceeds its text bound")
        if not isinstance(receipt["proposed_operations"], list) or not 1 <= len(receipt["proposed_operations"]) <= 5:
            raise ContractError("receipt operations are outside the contract bounds")
        for operation in receipt["proposed_operations"]:
            validate_operation(operation)
        if receipt["action_id"] != run.pending_action_id or receipt["episode_id"] != run.episode_id:
            raise ContractError("receipt action differs from the admitted run")
        if receipt["run_id"] != run.run_id or receipt["grant_id"] != run.grant_id:
            raise ContractError("receipt run differs from the admitted run")
        if receipt["grant_version"] != run.grant_version or receipt["fence"] != run.fence:
            raise ContractError("receipt fence differs from the admitted run")
        if receipt["actor_kind"] != "plugin" or not isinstance(receipt["verification"], str) or receipt["verification"] not in {"pending", "verified", "superseded", "not_applied"}:
            raise ContractError("receipt actor or verification is unsupported")
        if not isinstance(receipt["outcome"], str) or receipt["outcome"] not in {"unmeasured", "useful_evidence", "no_progress", "needs_owner"}:
            raise ContractError("receipt outcome is unsupported")


def validate_receipt_ref(value: object) -> None:
    reference = strict_object(value, frozenset({"table", "id"}), frozenset({"table", "id"}), "receipt row reference")
    if not isinstance(reference["table"], str) or reference["table"] not in {"plans", "phases", "tasks", "checks", "review_rounds"}:
        raise ContractError("receipt row reference table is unsupported")
    positive_integer(reference["id"], "receipt row id")

