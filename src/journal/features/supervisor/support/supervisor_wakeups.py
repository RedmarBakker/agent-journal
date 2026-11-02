from typing import Any

from supervisor_bridge.hints import ROW_EVENTS

from journal.features.plans.support.plan_owners import PlanOwners
from journal.features.supervisor.support.admissions import supervisor_key
from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

WAKEUP_ENTRY = "SupervisorWakeup"
RESULT_COUNTS = {
    "Acted": ("Acted", ""),
    "Proposed": ("Proposed", ""),
    "Nothing to do": ("Nothing to do", ""),
    "Skipped as quiet": ("Skipped as quiet", "quiet"),
    "Skipped (busy)": ("Skipped", "busy"),
    "Skipped (evidence stale)": ("Skipped", "evidence stale"),
    "Skipped (budget used up)": ("Skipped", "budget used up"),
    "Handed to you": ("Handed to you", "needs owner"),
}
RESULTS = frozenset(result for result, _ in RESULT_COUNTS.values())
SKIP_REASONS = frozenset(reason for _, reason in RESULT_COUNTS.values() if reason)


class SupervisorWakeups:
    """Stores one checked outcome per supervisor wake-up and counts it for its plan owner."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 plans: Plans, owners: PlanOwners, scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.plans, self.owners, self.scope, self.time_source = plans, owners, scope, time_source

    def record(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        request = self._request(body)
        self._service_actor(principal)
        grant = self.authority.revalidate(principal)
        return self.record_for_grant(grant, request)

    def record_skip(self, grant: dict[str, Any], wakeup: dict[str, Any], reason: str) -> dict[str, Any]:
        if reason in {"empty", "empty_work"}:
            result, skip_reason = "Nothing to do", ""
        elif reason in {"ineligible", "ineligible_work", "ineligible_gate"}:
            result, skip_reason = "Skipped as quiet", "quiet"
        elif reason in {"busy", "overlapping_run"}:
            result, skip_reason = "Skipped", "busy"
        elif reason in {"stale_evidence", "stale_installation_epoch", "stale_observation", "stale_phase_revision"}:
            result, skip_reason = "Skipped", "evidence stale"
        elif reason in {"budget_exhausted", "unknown_cost", "unknown_budget"}:
            result, skip_reason = "Skipped", "budget used up"
        else:
            result, skip_reason = "Handed to you", "needs owner"
        return self.record_for_grant(grant, {
            "wakeup_id": wakeup["wakeup_id"], "kind": wakeup["kind"],
            "result": result, "skip_reason": skip_reason,
        })

    def record_run(self, principal: SupervisorPrincipal, run_ref: str, status: str) -> dict[str, Any] | None:
        self._service_actor(principal)
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorRun", last=1, tenant_id=principal.scope["tenant_id"], run_ref=run_ref,
            )
        if (not rows or rows[0].data.get("grant_id") != principal.grant_id
                or rows[0].data.get("grant_version") != principal.grant_version):
            raise SupervisorFailure(403, "supervisor wake-up run is not current")
        wakeup_id, kind = rows[0].data.get("wakeup_id"), rows[0].data.get("kind")
        if not isinstance(wakeup_id, str) or not isinstance(kind, str):
            return None
        if status == "applied":
            result, skip_reason = "Acted", ""
        elif status == "proposed":
            result, skip_reason = "Proposed", ""
        else:
            result, skip_reason = "Handed to you", "needs owner"
        grant = {
            "scope": principal.scope, "grant_id": principal.grant_id,
            "grant_version": principal.grant_version, "plan_id": rows[0].data["plan_id"],
        }
        return self.record_for_grant(grant, {
            "wakeup_id": wakeup_id, "kind": kind,
            "result": result, "skip_reason": skip_reason,
        })

    def record_for_grant(self, grant: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        with self.scope.environment(PROJECT), self.entries.writing():
            return self._record(grant, request)

    def read(self, plan_id: int, actor: Actor) -> dict[str, Any]:
        plan = self.plans.find(plan_id)
        owner_id = self.owners.number(plan)
        if not actor.is_user() or not owner_id or actor.number() != owner_id:
            raise Rejection("only the plan owner may read supervisor wake-ups")
        tenant_id = f"owner:{owner_id}"
        with self.scope.environment(PROJECT):
            counts = {
                name: self._count(tenant_id, plan_id, stored_result, reason)
                for name, (stored_result, reason) in RESULT_COUNTS.items()
            }
        return {"schema_version": "supervisor-wakeups-v1", "plan_id": plan_id, "counts": counts}

    def _record(self, grant: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        scope = grant["scope"]
        tenant_id = scope["tenant_id"]
        intent_data = {
            "tenant_id": tenant_id,
            "grant_id": grant["grant_id"],
            "grant_version": grant["grant_version"],
            "plan_id": grant["plan_id"],
            "wakeup_id": request["wakeup_id"],
            "kind": request["kind"],
            "result": request["result"],
            "skip_reason": request["skip_reason"],
        }
        key = supervisor_key("wakeup", tenant_id, request["wakeup_id"])
        intent = supervisor_key("wakeup-intent", *[str(item) for item in intent_data.values()])
        if prior := self.entries.keyed(key):
            if prior[0].data.get("intent") != intent:
                raise SupervisorFailure(409, "the supervisor wake-up result changed after it was recorded")
            return self._answer(prior[0], True)
        row = self.control_entries.recorded(Entry(
            environment_id=PROJECT,
            entry_type=WAKEUP_ENTRY,
            actor=Actor.plugin(SUPERVISOR_ACTOR),
            data={**intent_data, "intent": intent, "recorded_at_ms": int(self.time_source.seconds() * 1000)},
            idempotency=key,
        ), Actor.plugin(SUPERVISOR_ACTOR))
        return self._answer(row, False)

    def _count(self, tenant_id: str, plan_id: int, result: str, reason: str) -> int:
        query = self.entries.query().filter(entry_type=WAKEUP_ENTRY)
        query = query.filter_json("data->tenant_id", tenant_id).filter_json("data->plan_id", plan_id)
        query = query.filter_json("data->result", result)
        if reason:
            query = query.filter_json("data->skip_reason", reason)
        return self.entries.counted(query)

    @staticmethod
    def _answer(row: Entry, duplicate: bool) -> dict[str, Any]:
        return {"status": "recorded", "wakeup_id": row.data["wakeup_id"], "entry_id": row.row_id, "duplicate": duplicate}

    @staticmethod
    def _request(body: object) -> dict[str, Any]:
        fields = {"protocol_version", "wakeup_id", "kind", "result", "skip_reason"}
        if (not isinstance(body, dict) or set(body) != fields
                or type(body["protocol_version"]) is not int or body["protocol_version"] != 1
                or not isinstance(body["wakeup_id"], str) or not 1 <= len(body["wakeup_id"]) <= 256
                or not isinstance(body["kind"], str) or body["kind"] != "scheduled" and body["kind"] not in ROW_EVENTS
                or not isinstance(body["result"], str) or body["result"] not in RESULTS
                or not isinstance(body["skip_reason"], str)):
            raise SupervisorFailure(400, "the supervisor wake-up result is invalid")
        result, reason = body["result"], body["skip_reason"]
        if (result in {"Acted", "Proposed", "Nothing to do"} and reason
                or result == "Skipped as quiet" and reason != "quiet"
                or result == "Skipped" and reason not in SKIP_REASONS - {"quiet", "needs owner"}
                or result == "Handed to you" and reason != "needs owner"):
            raise SupervisorFailure(400, "the supervisor wake-up result and skip reason do not match")
        return {"wakeup_id": body["wakeup_id"], "kind": body["kind"], "result": result, "skip_reason": reason}

    @staticmethod
    def _service_actor(principal: SupervisorPrincipal) -> None:
        if principal.actor != Actor.plugin(SUPERVISOR_ACTOR):
            raise SupervisorFailure(403, "supervisor service actor is not current")
