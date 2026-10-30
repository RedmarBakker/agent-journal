from typing import Any

from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal


class SupervisorActionReports:
    """Records verified maintenance effects and later independent evidence."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 tasks: Tasks, links: Links, scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.tasks, self.links, self.scope, self.time_source = tasks, links, scope, time_source

    def baseline(self, receipt: dict[str, Any], context: dict[str, Any]) -> Entry:
        data = receipt["data"]
        phase = context.get("phase")
        return self._record({
            "tenant_id": data["scope"]["tenant_id"],
            "grant_id": data["grant_id"],
            "grant_version": data["grant_version"],
            "plan_id": context.get("plan_id", 0),
            "action_id": data["action_id"],
            "receipt_id": receipt["receipt_id"],
            "report_kind": "baseline",
            "captured_at_ms": int(self.time_source.seconds() * 1000),
            "phase_id": phase.get("id") if isinstance(phase, dict) else 0,
            "tasks": [
                {"id": task["id"], "phase_id": task.get("phase_id"), "state": task.get("state"),
                 "revision": task.get("revision", "")}
                for task in context.get("tasks", []) if isinstance(task, dict) and type(task.get("id")) is int
            ],
        }, f"supervisor:action-baseline:{data['grant_id']}:{receipt['receipt_id']}")

    def reconcile(self, principal: SupervisorPrincipal, action_id: str) -> dict[str, Any]:
        if principal.actor != Actor.plugin(SUPERVISOR_ACTOR):
            raise SupervisorFailure(403, "supervisor service actor is not current")
        with self.scope.environment(PROJECT), self.entries.writing():
            receipt = self._receipt(principal, action_id)
            verification = self._reports(receipt, "verification")
            if receipt.data.get("status") == "applied" and not verification:
                report = self._verification(receipt)
                self._record(report, f"supervisor:action-verification:{receipt.row_id}")
        duplicate = receipt.data.get("status") != "applied" or bool(verification)
        return self.project(receipt, duplicate=duplicate)

    def measure(self, grant: dict[str, Any], observation: Entry) -> None:
        data = observation.data
        if (data.get("tenant_id") != grant["scope"]["tenant_id"]
                or data.get("grant_id") != grant["grant_id"]
                or data.get("grant_version") != grant["grant_version"]):
            return
        with self.scope.environment(PROJECT):
            receipts = self.entries.supervisor_records(
                "SupervisorActionReceipt", last=100, tenant_id=grant["scope"]["tenant_id"],
                grant_id=grant["grant_id"], grant_version=grant["grant_version"], status="applied",
            )
        for receipt in receipts:
            self._measure_receipt(grant, receipt, observation)

    def project(self, receipt: Entry, duplicate: bool = True) -> dict[str, Any]:
        verification_rows = self._reports(receipt, "verification")
        rollback_rows = self._reports(receipt, "rollback")
        outcomes = self._reports(receipt, "outcome")
        verification = verification_rows[0] if verification_rows else None
        rollback = rollback_rows[0] if rollback_rows else None
        data = dict(receipt.data)
        if verification:
            data["verification"] = verification.data["verification"]
        if any(row.data.get("outcome") == "useful_evidence" for row in outcomes):
            data["outcome"] = "useful_evidence"
        elif outcomes:
            data["outcome"] = outcomes[0].data["outcome"]
        evidence = {
            "status": data.get("outcome", "unmeasured"),
            "available": any(row.data.get("evidence_available") is True for row in outcomes) if outcomes else None,
            "observations": [
                {"observation_id": row.data.get("observation_id", ""),
                 "outcome": row.data.get("outcome", "unmeasured"),
                 "evidence_available": row.data.get("evidence_available")}
                for row in outcomes
            ],
            "checks": self._unique_evidence(outcomes, "check_evidence"),
            "tasks": self._unique_evidence(outcomes, "task_evidence"),
        }
        report = {
            "verification": verification.data if verification else None,
            "outcome_evidence": evidence,
            "rollback": rollback.data if rollback else None,
        }
        return {"status": data["status"], "reason": data["reason"], "receipt_id": receipt.row_id,
                "data": data, "report": report, "duplicate": duplicate}

    def _verification(self, receipt: Entry) -> dict[str, Any]:
        base = receipt.data
        plan_id = self._plan_id(receipt)
        common = {
            "tenant_id": base["scope"]["tenant_id"], "grant_id": base["grant_id"],
            "grant_version": base["grant_version"], "plan_id": plan_id,
            "action_id": base["action_id"], "receipt_id": receipt.row_id, "report_kind": "verification",
            "recorded_at_ms": int(self.time_source.seconds() * 1000),
        }
        baseline = self._baseline(receipt)
        if not baseline or not plan_id:
            return {**common, "verification": "superseded", "reason": "baseline_unavailable", "effects": []}
        try:
            plan = self.authority._plan(plan_id)
            with self.scope.environment(plan.environment_id):
                phases = self.authority.plans.phase_states(plan)
                phase_state = next((state for state in phases if state.phase.row_id == baseline.data.get("phase_id")), None)
        except SupervisorFailure:
            return {**common, "verification": "superseded", "reason": "plan_unavailable", "effects": []}
        phase = phase_state.phase if phase_state else None
        effects = [self._effect(change, plan, phase) for change in base.get("changes", [])]
        if any(operation.get("kind") == "diagnostic_task" for operation in base.get("proposed_operations", [])):
            task_refs = [ref for ref in base.get("affected_refs", []) if ref.get("table") == "tasks"]
            if not task_refs:
                effects.append({"field": "diagnostic_task", "status": "superseded", "reason": "task_reference_missing"})
            else:
                for ref in task_refs:
                    effects.append(self._task_effect(ref["id"], plan, phase))
        matched = all(effect["status"] == "matched" for effect in effects)
        return {**common, "verification": "verified" if matched else "superseded",
                "reason": "" if matched else "committed_effect_changed", "effects": effects}

    def _plan_id(self, receipt: Entry) -> int:
        baseline = self._baseline(receipt)
        if baseline:
            return int(baseline.data.get("plan_id", 0))
        return next((operation["plan_id"] for operation in receipt.data.get("proposed_operations", [])
                     if type(operation.get("plan_id")) is int), 0)

    def _baseline(self, receipt: Entry) -> Entry | None:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorActionReport", last=1, receipt_id=receipt.row_id, report_kind="baseline",
            )
        return rows[0] if rows else None

    def _effect(self, change: dict[str, Any], plan, phase) -> dict[str, Any]:
        ref, field = change["ref"], change["field"]
        if field == "priorities":
            revision = self.authority.priority_action_revision(plan)
            matched = revision == change["after_revision"] and plan.priorities == change["after_value"]
            return self._effect_value(ref, field, revision, change["after_revision"], matched)
        if field == "interval":
            check = self.authority._check(ref["id"])
            revision = self.authority.check_action_revision(check)
            matched = revision == change["after_revision"] and int(check.interval) == change["after_value"]
            return self._effect_value(ref, field, revision, change["after_revision"], matched)
        if field in ("plan_link", "phase_link"):
            actual = self._task_effect(ref["id"], plan, phase)
            actual["field"] = field
            actual["expected_value"] = change["after_value"]
            return actual
        return {"ref": ref, "field": field, "status": "superseded", "reason": "unknown_field"}

    def _task_effect(self, task_id: int, plan, phase) -> dict[str, Any]:
        with self.scope.environment(plan.environment_id):
            tasks = self.tasks.selected(self.tasks.query().filter(id=task_id).limit(1))
            if not tasks:
                return {"ref": {"table": "tasks", "id": task_id}, "field": "diagnostic_task", "status": "superseded", "reason": "task_missing"}
            task = tasks[0]
            plan_linked = bool(self.links.connecting(task, plan))
            phase_linked = bool(phase and self.links.connecting(task, phase))
        matched = plan_linked and phase_linked
        return {"ref": {"table": "tasks", "id": task_id}, "field": "diagnostic_task",
                "status": "matched" if matched else "superseded", "plan_linked": plan_linked,
                "current_phase_linked": phase_linked}

    def _measure_receipt(self, grant: dict[str, Any], receipt: Entry, observation: Entry) -> None:
        if observation.data.get("committed_at_ms", 0) <= receipt.data.get("recorded_at_ms", 0):
            return
        with self.scope.environment(PROJECT):
            baselines = self.entries.supervisor_records(
                "SupervisorActionReport", last=1, receipt_id=receipt.row_id, report_kind="baseline",
            )
            prior = self.entries.keyed(self._outcome_key(receipt, observation.data.get("observation_id", "")))
        if prior:
            return
        baseline = baselines[0].data if baselines else None
        check_evidence = self._check_evidence(grant, observation)
        task_evidence = self._task_evidence(receipt, baseline, observation)
        outcome = "useful_evidence" if check_evidence or task_evidence else "no_progress"
        base = receipt.data
        self._record({
            "tenant_id": base["scope"]["tenant_id"], "grant_id": base["grant_id"],
            "grant_version": base["grant_version"], "plan_id": grant["plan_id"],
            "action_id": base["action_id"], "receipt_id": receipt.row_id, "report_kind": "outcome",
            "outcome": outcome, "observation_id": observation.data.get("observation_id", ""),
            "observed_at_ms": observation.data["committed_at_ms"], "check_evidence": check_evidence,
            "task_evidence": task_evidence, "evidence_available": baseline is not None,
        }, self._outcome_key(receipt, observation.data.get("observation_id", "")))

    def _check_evidence(self, grant: dict[str, Any], observation: Entry) -> list[dict[str, Any]]:
        data = observation.data
        facts = data.get("observation", {}).get("facts", {})
        check_ids = {item["check_id"] for item in grant.get("checks", [])}
        if (data.get("check_id") not in check_ids or data.get("stopped") is not False
                or not isinstance(facts, dict) or facts.get("verdict") != "passed"):
            return []
        return [{"check_id": data["check_id"], "observation_id": data["observation_id"],
                 "observed_at_ms": data["committed_at_ms"]}]

    def _task_evidence(self, receipt: Entry, baseline: dict[str, Any] | None, observation: Entry) -> list[dict[str, Any]]:
        if baseline is None:
            return []
        before = {item["id"]: item for item in baseline.get("tasks", []) if type(item.get("id")) is int}
        context = observation.data.get("context", {})
        tasks = context.get("tasks", []) if isinstance(context, dict) else []
        phase_id = baseline.get("phase_id")
        evidence = []
        for task in tasks:
            if (not isinstance(task, dict) or task.get("phase_id") != phase_id or type(task.get("id")) is not int
                    or task.get("state") not in ("started", "completed")
                    or task.get("updater") == Actor.plugin(SUPERVISOR_ACTOR).stamp):
                continue
            prior = before.get(task["id"])
            if prior and prior.get("state") in ("started", "completed"):
                continue
            evidence.append({"task_id": task["id"], "from_state": prior.get("state") if prior else None,
                             "to_state": task["state"], "observation_id": observation.data["observation_id"],
                             "observed_at_ms": observation.data["committed_at_ms"]})
        return evidence

    def _receipt(self, principal: SupervisorPrincipal, action_id: str) -> Entry:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorActionReceipt", last=100, grant_id=principal.grant_id,
                grant_version=principal.grant_version, action_id=action_id,
            )
        if not rows or rows[0].data.get("scope") != principal.scope:
            raise SupervisorFailure(403, "supervisor receipt is not available")
        return rows[0]

    def _reports(self, receipt: Entry, kind: str) -> list[Entry]:
        with self.scope.environment(PROJECT):
            return self.entries.supervisor_records(
                "SupervisorActionReport", last=100, receipt_id=receipt.row_id, report_kind=kind,
            )

    def _record(self, data: dict[str, Any], key: str) -> Entry:
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        return self.control_entries.recorded(Entry(
            environment_id=PROJECT, entry_type="SupervisorActionReport", actor=actor,
            data=data, idempotency=key,
        ), actor)

    @staticmethod
    def _effect_value(ref: dict[str, Any], field: str, current: str, expected: str, matched: bool) -> dict[str, Any]:
        return {"ref": ref, "field": field, "status": "matched" if matched else "superseded",
                "current_revision": current, "expected_revision": expected}

    @staticmethod
    def _outcome_key(receipt: Entry, observation_id: str) -> str:
        return f"supervisor:action-outcome:{receipt.row_id}:{observation_id}"

    @staticmethod
    def _unique_evidence(rows: list[Entry], field: str) -> list[dict[str, Any]]:
        values = {item["observation_id"] + ":" + str(item.get("task_id", item.get("check_id", ""))): item
                  for row in rows for item in row.data.get(field, []) if isinstance(item, dict)}
        return [values[key] for key in sorted(values)]
