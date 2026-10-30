from typing import Any

from journal.features.supervisor.support.admissions import action_receipt_key, action_reuse_key, canonical, digest
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
from journal.models.entry import Entry
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.template import Template
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.links import Links
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

READ_ONLY_DIAGNOSTIC = "Inspect the supplied check evidence and report findings only. Do not change files, settings, plans, tasks, assignments, checks, or other journal rows."
OPERATION_FIELDS = {
    "plan_priorities": frozenset({"kind", "plan_id", "text"}),
    "diagnostic_task": frozenset({"kind", "plan_id", "phase_id", "template_id", "template_revision", "evidence_ids"}),
    "check_interval": frozenset({"kind", "check_id", "interval_minutes"}),
}


def diagnostic_task_values(template: Template) -> tuple[str, str]:
    title = f"Read-only diagnostic: {template.title}"
    brief = "\n\n".join(part.strip() for part in (template.purpose, template.brief, READ_ONLY_DIAGNOSTIC) if part.strip())
    return title, brief


class SupervisorMaintenance:
    """Applies one admitted supervisor maintenance bundle under the Entry write transaction."""

    def __init__(self, authority: SupervisorAuthority, observations: SupervisorObservations, entries: Entries,
                 control_entries: SupervisorEntries, plans: Plans, tasks: Tasks, links: Links, checks: Checks,
                 scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.observations, self.entries = authority, observations, entries
        self.control_entries, self.plans, self.tasks, self.links, self.checks = control_entries, plans, tasks, links, checks
        self.scope, self.time_source = scope, time_source

    def apply_maintenance(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        request = self._request(body)
        self._service_actor(principal)
        with self.scope.environment(PROJECT), self.entries.writing():
            grant, context = self.authority.action_context(principal)
            if request["grant_version"] != grant["grant_version"]:
                raise SupervisorFailure(403, "supervisor action is not current")
            run, epoch = self.observations.action_run(principal, grant, request)
            if run.data.get("episode_id") != request["episode_id"]:
                raise SupervisorFailure(403, "supervisor action is not current")
            evidence = self.observations.action_evidence(principal, grant, epoch, request["observation_ids"])
            episode = self._episode(grant, request["episode_id"])
            if any(row.data.get("evidence_generation") != episode.data.get("evidence_generation") for row in evidence):
                raise SupervisorFailure(403, "supervisor action evidence is not current")
            intent_hash = self._intent_hash(grant, request, episode)
            receipt_key = action_receipt_key(grant["scope"]["tenant_id"], request["action_id"])
            if prior := self.entries.keyed(receipt_key):
                return self._prior(prior[0], intent_hash, grant, request)
            if context.get("conflict_reason"):
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "conflicted", context["conflict_reason"])
            if reason := self._usage_reason(grant, run):
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "rejected", reason)
            if reason := self._capability_reason(grant, request["operations"]):
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "rejected", reason)
            if reason := self._revision_reason(grant, context, request):
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "conflicted", reason)
            if reason := self._evidence_reason(grant, request, evidence):
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "rejected", reason)
            if grant["mode"] == "shadow":
                return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "proposed", None)
            before = self._before_values(context, request)
            affected, diagnostic, created = self._apply(grant, context, request)
            readback = self.authority.action_readback(principal, grant["current_phase"]["phase_id"], context["binding_revision"])
            after = self.authority.observation_context(grant)
            self._verify_readback(grant, readback, request, diagnostic, before)
            changes = self._changes(before, after, grant, request, diagnostic, created)
            if diagnostic is not None:
                affected.extend([
                    {"table": "tasks", "id": diagnostic.row_id},
                    {"table": "plans", "id": grant["plan_id"]},
                    {"table": "phases", "id": grant["current_phase"]["phase_id"]},
                ])
            return self._receipt(grant, request, run.data["run_ref"], epoch, intent_hash, "applied", None, affected, changes)

    def _request(self, body: object) -> dict[str, Any]:
        fields = {
            "protocol_version", "run_id", "installation_epoch", "fence", "grant_version", "episode_id",
            "action_id", "observation_ids", "expected_revisions", "operations", "rationale",
        }
        if not isinstance(body, dict) or set(body) != fields:
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        if (type(body["protocol_version"]) is not int or body["protocol_version"] != 1
                or not self._text_id(body["run_id"]) or type(body["installation_epoch"]) is not int or body["installation_epoch"] < 1
                or type(body["fence"]) is not int or body["fence"] < 1
                or type(body["grant_version"]) is not int or body["grant_version"] < 1
                or not self._text_id(body["episode_id"]) or not self._text_id(body["action_id"])
                or not isinstance(body["rationale"], str) or not 1 <= len(body["rationale"]) <= 2048
                or not body["rationale"].strip()):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        observation_ids = body["observation_ids"]
        if (not isinstance(observation_ids, list) or not 1 <= len(observation_ids) <= 20
                or any(not self._text_id(value) for value in observation_ids)
                or len(observation_ids) != len(set(observation_ids))):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        operations = body["operations"]
        if not isinstance(operations, list) or not 1 <= len(operations) <= 5:
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        normalized = [self._operation(operation, observation_ids) for operation in operations]
        if len({(item["kind"], item.get("check_id", item.get("plan_id"))) for item in normalized}) != len(normalized):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        revisions = self._expected_revisions(body["expected_revisions"])
        return {
            **body,
            "observation_ids": sorted(observation_ids),
            "operations": sorted(normalized, key=self._operation_key),
            "expected_revisions": revisions,
        }

    def _operation(self, value: object, observation_ids: list[str]) -> dict[str, Any]:
        if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        kind = value["kind"]
        if kind not in OPERATION_FIELDS or set(value) != OPERATION_FIELDS[kind]:
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        if kind == "plan_priorities":
            text = value["text"]
            if (type(value["plan_id"]) is not int or value["plan_id"] < 1 or not isinstance(text, str)
                    or not 1 <= len(text) <= 2048):
                raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
            text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not text:
                raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
            return {"kind": kind, "plan_id": value["plan_id"], "text": text}
        if kind == "diagnostic_task":
            evidence_ids = value["evidence_ids"]
            if (type(value["plan_id"]) is not int or value["plan_id"] < 1
                    or type(value["phase_id"]) is not int or value["phase_id"] < 1
                    or not self._text_id(value["template_id"]) or not self._text_id(value["template_revision"])
                    or not isinstance(evidence_ids, list) or not 1 <= len(evidence_ids) <= 20
                    or any(not self._text_id(item) for item in evidence_ids)
                    or len(evidence_ids) != len(set(evidence_ids)) or not set(evidence_ids) <= set(observation_ids)):
                raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
            return {**value, "evidence_ids": sorted(evidence_ids)}
        if (type(value["check_id"]) is not int or value["check_id"] < 1
                or type(value["interval_minutes"]) is not int or not 5 <= value["interval_minutes"] <= 30):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        return value

    def _expected_revisions(self, value: object) -> list[dict[str, Any]]:
        if not isinstance(value, list) or not 2 <= len(value) <= 12:
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        rows = []
        for item in value:
            if (not isinstance(item, dict) or set(item) != {"ref", "revision"}
                    or not isinstance(item["ref"], dict) or set(item["ref"]) != {"table", "id"}
                    or item["ref"]["table"] not in ("plans", "phases", "checks")
                    or type(item["ref"]["id"]) is not int or item["ref"]["id"] < 1
                    or not self._text_id(item["revision"])):
                raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
            rows.append({"ref": dict(item["ref"]), "revision": item["revision"]})
        keys = [(item["ref"]["table"], item["ref"]["id"]) for item in rows]
        if len(keys) != len(set(keys)):
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        return sorted(rows, key=lambda item: (item["ref"]["table"], item["ref"]["id"]))

    def _episode(self, grant: dict[str, Any], episode_id: str) -> Entry:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorEpisode", last=1, tenant_id=grant["scope"]["tenant_id"],
                plan_id=grant["plan_id"], episode_id=episode_id,
            )
        if (not rows or type(rows[0].data.get("evidence_generation")) is not int
                or rows[0].data["evidence_generation"] < 1):
            raise SupervisorFailure(403, "supervisor action is not current")
        return rows[0]

    def _intent_hash(self, grant: dict[str, Any], request: dict[str, Any], episode: Entry) -> str:
        intent = {
            "protocol_version": 1,
            "scope": {**grant["scope"], "installation_epoch": request["installation_epoch"]},
            "grant_id": grant["grant_id"], "grant_version": grant["grant_version"],
            "plan_id": grant["plan_id"], "episode_id": request["episode_id"],
            "evidence_generation": episode.data["evidence_generation"],
            "observation_ids": request["observation_ids"],
            "expected_revisions": request["expected_revisions"],
            "operations": request["operations"],
        }
        text = canonical(intent)
        if text is None:
            raise SupervisorFailure(400, "the supervisor maintenance request is invalid")
        return digest(text)

    def _usage_reason(self, grant: dict[str, Any], run: Entry) -> str:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorUsage", last=1, tenant_id=grant["scope"]["tenant_id"], run_ref=run.data["run_ref"],
            )
        if not rows or rows[0].data.get("status") != "known":
            return "usage_unknown"
        return "usage_overrun" if rows[0].data.get("overrun") is True else ""

    def _capability_reason(self, grant: dict[str, Any], operations: list[dict[str, Any]]) -> str:
        if grant["mode"] == "shadow":
            if not self.authority.permits_proposal_receipt(grant):
                return "grant_not_current"
        elif grant["mode"] != "bounded_write":
            return "grant_mode_disabled"
        for operation in operations:
            if grant.get("capabilities", {}).get(operation["kind"]) is not True:
                return "capability_not_granted"
            if grant["mode"] == "bounded_write" and not self.authority.permits_domain_write(grant, operation["kind"]):
                return "capability_not_granted"
        return ""

    def _revision_reason(self, grant: dict[str, Any], context: dict[str, Any], request: dict[str, Any]) -> str:
        phase = context.get("current_phase_row")
        if phase is None:
            return "current_phase_changed"
        expected = {(item["ref"]["table"], item["ref"]["id"]): item["revision"] for item in request["expected_revisions"]}
        required = {
            ("plans", grant["plan_id"]): context["plan_revision"],
            ("phases", phase.row_id): context["current_phase"]["revision"],
        }
        for operation in request["operations"]:
            if operation["kind"] == "check_interval":
                enrolled = next((item for item in grant["checks"] if item["check_id"] == operation["check_id"]), None)
                if enrolled is None:
                    return "check_not_enrolled"
                check = self._check(operation["check_id"])
                interval = operation["interval_minutes"]
                if (not enrolled["minimum_interval_minutes"] <= interval <= enrolled["baseline_interval_minutes"]
                        or interval >= int(check.interval)):
                    return "interval_outside_enrolled_range"
                required[("checks", check.row_id)] = self.authority.check_action_revision(check)
        if set(expected) != set(required) or any(expected[key] != value for key, value in required.items()):
            return "expected_revision_conflict"
        for operation in request["operations"]:
            if operation["kind"] == "diagnostic_task" and (
                    operation["plan_id"] != grant["plan_id"] or operation["phase_id"] != phase.row_id
                    or operation["template_id"] != grant["diagnostic_template_id"]
                    or operation["template_revision"] != grant["diagnostic_template_revision"]):
                return "diagnostic_scope_mismatch"
            if operation["kind"] == "diagnostic_task":
                template = self.authority.diagnostic_template(grant)
                title, brief = diagnostic_task_values(template)
                if "plan" not in template.targets or len(title) > 256 or len(brief) > 2048:
                    return "diagnostic_template_invalid"
            if operation["kind"] == "plan_priorities" and operation["plan_id"] != grant["plan_id"]:
                return "plan_scope_mismatch"
        return ""

    def _evidence_reason(self, grant: dict[str, Any], request: dict[str, Any], evidence: list[Entry]) -> str:
        observations = {row.data["observation_id"]: row.data for row in evidence}
        enrolled = {item["check_id"] for item in grant["checks"]}
        for operation in request["operations"]:
            ids = operation.get("evidence_ids", request["observation_ids"])
            if operation["kind"] == "check_interval":
                ids = request["observation_ids"]
            if not any(observations[item].get("check_id") in enrolled for item in ids):
                return "evidence_not_qualified"
            if operation["kind"] == "check_interval" and not any(
                    observations[item].get("check_id") == operation["check_id"] for item in ids):
                return "check_evidence_mismatch"
        return ""

    def _before_values(self, context: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        values = {
            "plan": context["plan"], "plan_revision": context["plan_revision"],
            "phase_revision": context["current_phase"]["revision"],
            "priorities": context["plan"].priorities,
            "checks": {},
        }
        for operation in request["operations"]:
            if operation["kind"] == "check_interval":
                check = self._check(operation["check_id"])
                values["checks"][check.row_id] = check
        return values

    def _apply(self, grant: dict[str, Any], context: dict[str, Any], request: dict[str, Any]) -> tuple[list[dict[str, Any]], Task | None, bool]:
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        plan = context["plan"]
        phase = context["current_phase_row"]
        diagnostic = None
        created = False
        affected: list[dict[str, Any]] = []
        with self.scope.environment(plan.environment_id):
            for operation in request["operations"]:
                if operation["kind"] == "plan_priorities":
                    prioritized = plan.prioritised(operation["text"], context["current_phase"]["number"], self.time_source.seconds())
                    plan = self.plans.save(prioritized, actor)
                    affected.append({"table": "plans", "id": plan.row_id})
                elif operation["kind"] == "diagnostic_task":
                    diagnostic, created = self._diagnostic(grant, plan, phase, actor, request["episode_id"])
                    affected.append({"table": "tasks", "id": diagnostic.row_id})
                else:
                    check = self._check(operation["check_id"])
                    interval = operation["interval_minutes"]
                    self.checks.save(check.with_(interval=interval), actor)
                    affected.append({"table": "checks", "id": check.row_id})
        return affected, diagnostic, created

    def _diagnostic(self, grant: dict[str, Any], plan: Plan, phase: Phase,
                    actor: Actor, episode_id: str) -> tuple[Task, bool]:
        template = self.authority.diagnostic_template(grant)
        title, brief = diagnostic_task_values(template)
        with self.scope.environment(plan.environment_id):
            existing = next((task for task in self.plans.phase_tasks(phase)
                if task.title == title and task.brief == brief and self.links.connecting(task, plan)
                and self._eligible_diagnostic(task)), None)
            if existing:
                return existing, False
            allowance = min(1, grant["limits"]["max_new_diagnostics_per_episode"])
            if self._new_diagnostic_count(grant, episode_id) >= allowance:
                raise SupervisorFailure(409, "the episode has used its diagnostic task allowance")
            task = self.tasks.save(Task(environment_id=plan.environment_id, title=title, brief=brief), actor)
            self.plans.place_task_in_phase(task, plan, phase, actor)
            return self.tasks.find(task.row_id), True

    def _eligible_diagnostic(self, task: Task) -> bool:
        return bool(task.state == TaskState.OPEN and not task.delegated and not self.tasks.waiting_ids([task])
            and self.tasks.task_holder(task.row_id) is None and not self.tasks.has_worker_holder([task.row_id]))

    def _new_diagnostic_count(self, grant: dict[str, Any], episode_id: str) -> int:
        with self.scope.environment(PROJECT):
            receipts = self.entries.supervisor_records("SupervisorActionReceipt", last=100, episode_id=episode_id)
        created = set()
        for receipt in receipts:
            data = receipt.data
            scope = data.get("scope")
            if (not isinstance(scope, dict) or scope.get("tenant_id") != grant["scope"]["tenant_id"]
                    or data.get("grant_id") != grant["grant_id"] or data.get("status") != "applied"):
                continue
            for change in data.get("changes", []):
                if not isinstance(change, dict):
                    continue
                ref = change.get("ref")
                if change.get("field") == "phase_link" and isinstance(ref, dict) and ref.get("table") == "tasks":
                    created.add(change["ref"]["id"])
        return len(created)

    def _verify_readback(self, grant: dict[str, Any], context: dict[str, Any], request: dict[str, Any],
                         diagnostic: Task | None, before: dict[str, Any]) -> None:
        if context["current_phase"]["phase_id"] != grant["current_phase"]["phase_id"]:
            raise SupervisorFailure(409, "the current phase changed during supervisor maintenance")
        with self.scope.environment(context["plan"].environment_id):
            if any(operation["kind"] == "plan_priorities" for operation in request["operations"]):
                operation = next(operation for operation in request["operations"] if operation["kind"] == "plan_priorities")
                plan = self.plans.find(context["plan"].row_id)
                if (plan.priorities != operation["text"]
                        or plan.priorities_phase != context["current_phase"]["number"]):
                    raise SupervisorFailure(409, "the plan priorities did not read back")
            if diagnostic is not None:
                plan_link = self.links.connecting(diagnostic, context["plan"])
                phase_link = self.links.connecting(diagnostic, context["current_phase_row"])
                if (len(plan_link) != 1 or len(phase_link) != 1 or not self._eligible_diagnostic(diagnostic)
                        or diagnostic not in self.plans.phase_tasks(context["current_phase_row"])):
                    raise SupervisorFailure(409, "the diagnostic task did not read back in its enrolled current phase")
        for operation in request["operations"]:
            if operation["kind"] == "check_interval":
                prior = before["checks"][operation["check_id"]]
                check = self._check(operation["check_id"])
                if (check.interval != operation["interval_minutes"] or check.command != prior.command
                        or check.verdict() != prior.verdict() or check.last_output != prior.last_output
                        or check.last_run_at != prior.last_run_at or check.last_report != prior.last_report
                        or check.last_duration != prior.last_duration or check.last_fault != prior.last_fault
                        or check.failure_reported_at != prior.failure_reported_at or check.last_stopped != prior.last_stopped
                        or check.progress != prior.progress):
                    raise SupervisorFailure(409, "the enrolled check did not read back with its command and result unchanged")

    def _changes(self, before: dict[str, Any], after: dict[str, Any], grant: dict[str, Any],
                 request: dict[str, Any], diagnostic: Task | None, created: bool) -> list[dict[str, Any]]:
        changes = []
        if any(operation["kind"] == "plan_priorities" for operation in request["operations"]):
            operation = next(operation for operation in request["operations"] if operation["kind"] == "plan_priorities")
            changes.append({
                "ref": {"table": "plans", "id": grant["plan_id"]}, "field": "priorities",
                "before_revision": before["plan_revision"], "after_revision": after["plan_revision"],
                "before_value": before["priorities"], "after_value": operation["text"],
            })
        if diagnostic is not None and created:
            changes.extend([
                {"ref": {"table": "tasks", "id": diagnostic.row_id}, "field": "plan_link",
                    "before_revision": before["plan_revision"], "after_revision": after["plan_revision"],
                    "before_value": None, "after_value": grant["plan_id"]},
                {"ref": {"table": "tasks", "id": diagnostic.row_id}, "field": "phase_link",
                    "before_revision": before["phase_revision"], "after_revision": after["phase"]["revision"],
                    "before_value": None, "after_value": grant["current_phase"]["phase_id"]},
            ])
        for operation in request["operations"]:
            if operation["kind"] != "check_interval":
                continue
            prior = before["checks"][operation["check_id"]]
            current = self._check(operation["check_id"])
            changes.append({
                "ref": {"table": "checks", "id": current.row_id}, "field": "interval",
                "before_revision": self.authority.check_action_revision(prior),
                "after_revision": self.authority.check_action_revision(current),
                "before_value": int(prior.interval), "after_value": int(current.interval),
            })
        return changes

    def _receipt(self, grant: dict[str, Any], request: dict[str, Any], run_ref: str, epoch: int,
                 intent_hash: str, status: str, reason: str | None,
                 affected: list[dict[str, Any]] | None = None, changes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        scope = {**grant["scope"], "installation_epoch": epoch}
        data = {
            "protocol_version": 1, "action_id": request["action_id"], "episode_id": request["episode_id"],
            "run_id": run_ref, "grant_id": grant["grant_id"], "grant_version": grant["grant_version"],
            "scope": scope, "fence": request["fence"], "intent_sha256": intent_hash,
            "actor_kind": "plugin", "actor_id": SUPERVISOR_ACTOR, "status": status, "reason": reason,
            "recorded_at_ms": int(self.time_source.seconds() * 1000),
            "observation_ids": request["observation_ids"], "affected_refs": self._unique_refs(affected or []),
            "changes": changes or [], "verification": "verified" if status == "applied" else "not_applied",
            "outcome": "unmeasured", "proposed_operations": request["operations"],
        }
        key = action_receipt_key(scope["tenant_id"], request["action_id"])
        if reason == "action_id_reused":
            key = action_reuse_key(scope["tenant_id"], request["action_id"], intent_hash)
        row = self.control_entries.recorded(Entry(
            environment_id=PROJECT, entry_type="SupervisorActionReceipt", actor=Actor.plugin(SUPERVISOR_ACTOR),
            data=data, idempotency=key,
        ), Actor.plugin(SUPERVISOR_ACTOR))
        return {"status": status, "reason": reason, "receipt_id": row.row_id, "data": row.data, "duplicate": False}

    def _prior(self, prior: Entry, intent_hash: str, grant: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
        if prior.data.get("intent_sha256") == intent_hash:
            return {"status": prior.data["status"], "receipt_id": prior.row_id, "data": prior.data, "duplicate": True}
        return self._receipt(grant, request, request["run_id"], request["installation_epoch"], intent_hash, "rejected", "action_id_reused")

    def _unique_refs(self, refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique = {(item["table"], item["id"]): item for item in refs}
        return [unique[key] for key in sorted(unique)]

    def _check(self, check_id: int):
        rows = self.checks.selected(self.checks.query().filter(id=check_id).limit(1))
        if not rows:
            raise SupervisorFailure(409, "an enrolled check is unavailable")
        return rows[0]

    def _service_actor(self, principal: SupervisorPrincipal) -> None:
        if principal.actor != Actor.plugin(SUPERVISOR_ACTOR):
            raise SupervisorFailure(403, "supervisor service actor is not current")

    @staticmethod
    def _operation_key(operation: dict[str, Any]) -> tuple[str, str, int]:
        table = "checks" if operation["kind"] == "check_interval" else "plans"
        target = operation["check_id"] if table == "checks" else operation["plan_id"]
        return operation["kind"], table, target

    @staticmethod
    def _text_id(value: object) -> bool:
        if not isinstance(value, str) or not value:
            return False
        try:
            return len(value.encode("utf-8")) <= 256
        except UnicodeEncodeError:
            return False
