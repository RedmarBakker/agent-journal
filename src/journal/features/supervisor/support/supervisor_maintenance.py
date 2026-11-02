from typing import Any

from journal.features.supervisor.capability_catalogue import CAPABILITY_CATALOGUE
from journal.features.supervisor.support.admissions import (
    action_receipt_key,
    action_reuse_key,
    canonical,
    digest,
    supervisor_key,
)
from journal.features.supervisor.support.supervisor_action_reports import SupervisorActionReports
from journal.features.supervisor.support.supervisor_command_changes import SupervisorCommandChanges
from journal.features.supervisor.support.supervisor_observations import SupervisorObservations
from journal.features.supervisor.support.supervisor_work_available import SupervisorWorkAvailable
from journal.features.supervisor.support.supervisor_wakeups import SupervisorWakeups
from journal.features.supervisor.support.diagnostic_eligibility import eligible_diagnostic
from journal.models.entry import Entry
from journal.models.phase import Phase
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
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
OPERATION_COMMANDS = {
    "plan_priorities": ("Plans and tasks", "plan", "priorities"),
    "diagnostic_task": ("Plans and tasks", "task", "create"),
    "check_interval": ("Checks", "check", "edit"),
}


def diagnostic_task_values(template: Template) -> tuple[str, str]:
    title = "Read-only diagnostic"
    brief = "\n\n".join(part.strip() for part in (f"Template {template.title}", template.purpose, template.brief, READ_ONLY_DIAGNOSTIC) if part.strip())
    return title, brief


class SupervisorMaintenance:
    """Applies one admitted supervisor maintenance bundle under the Entry write transaction."""

    def __init__(self, authority: SupervisorAuthority, observations: SupervisorObservations, entries: Entries,
                 control_entries: SupervisorEntries, plans: Plans, tasks: Tasks, links: Links, checks: Checks,
                 scope: Scope, time_source: TimeSource, work_available: SupervisorWorkAvailable,
                 action_reports: SupervisorActionReports, wakeups: SupervisorWakeups,
                 command_changes: SupervisorCommandChanges) -> None:
        self.authority, self.observations, self.entries = authority, observations, entries
        self.control_entries, self.plans, self.tasks, self.links, self.checks = control_entries, plans, tasks, links, checks
        self.scope, self.time_source = scope, time_source
        self.work_available = work_available
        self.action_reports = action_reports
        self.wakeups = wakeups
        self.command_changes = command_changes

    def apply_maintenance(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        request = self._request(body)
        self._service_actor(principal)
        self._apply_request(principal, request)
        receipt = self.reconcile_receipt(principal, request["action_id"])
        self.wakeups.record_run(principal, request["run_id"], receipt["status"])
        return receipt

    def settle_usage(self, principal: SupervisorPrincipal, body: object) -> dict[str, Any]:
        request = self._usage_settlement_request(body)
        self._service_actor(principal)
        with self.scope.environment(PROJECT), self.entries.writing():
            grant = self.authority.revalidate(principal)
            run, epoch = self.observations.action_run(principal, grant, request["run_ref"])
            expected = {
                "run_id": run.data["run_ref"], "episode_id": run.data["episode_id"],
                "pending_action_id": run.data["pending_action_id"], "grant_id": grant["grant_id"],
                "grant_version": grant["grant_version"], "installation_epoch": epoch,
                "fence": run.data["fence"],
            }
            if request["run_ref"] != expected:
                raise SupervisorFailure(403, "metered usage is not for the current fenced run")
            usage = request["usage"]
            limits = grant["limits"]
            overrun = (
                usage["total_input_tokens"] > limits["max_input_tokens_per_turn"]
                or usage["output_tokens"] > limits["max_output_tokens_per_turn"]
                or usage["provider_requests"] > limits["max_provider_requests_per_turn"]
            )
            tenant_id = principal.scope["tenant_id"]
            data = {
                "tenant_id": tenant_id, "run_ref": run.data["run_ref"], "fence": run.data["fence"],
                **usage, "overrun": overrun,
            }
            intent = canonical(data)
            if intent is None:
                raise SupervisorFailure(400, "metered usage report is too large")
            key = supervisor_key("metered-usage", tenant_id, run.data["run_ref"])
            prior = self.entries.keyed(key)
            if prior:
                if prior[0].data.get("intent") != intent:
                    raise SupervisorFailure(409, "metered usage report changed for this run")
                row, duplicate = prior[0], True
            else:
                status = "overrun" if overrun else "known"
                row = self.control_entries.recorded(Entry(
                    environment_id=PROJECT, entry_type="SupervisorUsage", actor=Actor.plugin(SUPERVISOR_ACTOR),
                    data={**data, "intent": intent, "status": status}, idempotency=key,
                ), Actor.plugin(SUPERVISOR_ACTOR))
                duplicate = False
            return {
                "status": "settled", "usage_id": row.row_id, "run_id": run.data["run_ref"],
                "fence": run.data["fence"], "usage_status": row.data["status"], "duplicate": duplicate,
            }

    def _apply_request(self, principal: SupervisorPrincipal, request: dict[str, Any]) -> dict[str, Any]:
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
            before_context = self.authority.observation_context(grant)
            affected, diagnostic, created, command_changes = self._apply(grant, context, request)
            readback = self.authority.action_readback(principal, grant["current_phase"]["phase_id"], context["binding_revision"])
            after = self.authority.observation_context(grant)
            self._verify_readback(grant, readback, request, diagnostic, before)
            changes = self._changes(before, after, readback, grant, request, diagnostic, created)
            if diagnostic is not None:
                affected.extend([
                    {"table": "tasks", "id": diagnostic.row_id},
                    {"table": "plans", "id": grant["plan_id"]},
                    {"table": "phases", "id": grant["current_phase"]["phase_id"]},
                ])
            receipt = self._receipt(
                grant, request, run.data["run_ref"], epoch, intent_hash, "applied", None,
                affected, changes, command_changes,
            )
            self.action_reports.baseline(receipt, before_context)
            if diagnostic is not None:
                self.work_available.after_commit(principal, receipt, diagnostic.row_id)
            return receipt

    def reconcile_receipt(self, principal: SupervisorPrincipal, action_id: str) -> dict[str, Any]:
        self._service_actor(principal)
        return self.action_reports.reconcile(principal, action_id)

    def receipt(self, principal: SupervisorPrincipal, action_id: str) -> dict[str, Any]:
        return self.reconcile_receipt(principal, action_id)

    def rollback(self, principal: SupervisorPrincipal, receipt_id: int) -> dict[str, Any]:
        self._service_actor(principal)
        with self.scope.environment(PROJECT), self.entries.writing():
            grant, context = self.authority.action_context(principal)
            row = self.entries.selected(self.entries.query().filter(id=receipt_id, entry_type="SupervisorActionReceipt").limit(1))
            if (not row or row[0].data.get("grant_id") != grant["grant_id"]
                    or row[0].data.get("grant_version") != grant["grant_version"]
                    or row[0].data.get("scope") != principal.scope):
                raise SupervisorFailure(403, "supervisor receipt is not available")
            receipt = row[0]
            if receipt.data.get("status") != "applied":
                return self.action_reports.project(receipt)
            prior = self.entries.supervisor_records(
                "SupervisorActionReport", last=1, receipt_id=receipt.row_id, report_kind="rollback",
            )
            if prior:
                return self.action_reports.project(receipt)
            baseline = self.entries.supervisor_records(
                "SupervisorActionReport", last=1, receipt_id=receipt.row_id, report_kind="baseline",
            )
            conflict = context.get("conflict_reason")
            if not conflict and (not baseline or context["current_phase"]["phase_id"] != baseline[0].data.get("phase_id")):
                conflict = "current_phase_changed"
            results = []
            if conflict:
                results.append({"status": "needs_owner", "reason": conflict})
            else:
                for change in receipt.data.get("changes", []):
                    results.append(self._rollback_change(
                        grant, context, change, Actor.plugin(SUPERVISOR_ACTOR),
                    ))
            needs_owner = any(result["status"] == "owner_edit_preserved" for result in results)
            status = "needs_owner" if needs_owner or conflict else "rolled_back"
            report_data = {
                "tenant_id": receipt.data["scope"]["tenant_id"],
                "grant_id": receipt.data["grant_id"],
                "grant_version": receipt.data["grant_version"],
                "plan_id": grant["plan_id"],
                "action_id": receipt.data["action_id"],
                "receipt_id": receipt.row_id,
                "report_kind": "rollback",
                "status": status,
                "reason": conflict or ("owner_edit_preserved" if needs_owner else ""),
                "recorded_at_ms": int(self.time_source.seconds() * 1000),
                "fields": results,
            }
            self.control_entries.recorded(Entry(
                environment_id=PROJECT, entry_type="SupervisorActionReport", actor=Actor.plugin(SUPERVISOR_ACTOR),
                data=report_data, idempotency=f"supervisor:action-rollback:{receipt.row_id}",
            ), Actor.plugin(SUPERVISOR_ACTOR))
        return self.action_reports.project(receipt)

    def undo_owner(self, plan_id: int, receipt_id: int, actor: Actor) -> dict[str, Any]:
        with self.scope.environment(PROJECT), self.entries.writing():
            plan = self.authority._plan(plan_id)
            owner_id = self.authority._owner(actor, plan)
            rows = self.entries.selected(self.entries.query().filter(
                id=receipt_id, entry_type="SupervisorActionReceipt",
            ).limit(1))
            if not rows:
                raise SupervisorFailure(403, "supervisor receipt is not available")
            receipt = rows[0]
            scope = receipt.data.get("scope", {})
            if scope.get("tenant_id") != f"owner:{owner_id}":
                raise SupervisorFailure(403, "supervisor receipt is not available")
            if receipt.data.get("status") != "applied":
                raise SupervisorFailure(409, "only an applied tier 1 action can be undone")
            grant_entry = self.authority._latest_entry(receipt.data.get("grant_id", ""))
            if not grant_entry:
                raise SupervisorFailure(403, "supervisor receipt is not available")
            grant = self.authority._public_grant(grant_entry)
            if (grant.get("plan_id") != plan_id or grant.get("owner_user_id") != owner_id
                    or grant.get("grant_version") != receipt.data.get("grant_version")):
                raise SupervisorFailure(409, "the supervisor action is no longer current")
            prior = self.action_reports._reports(receipt, "owner_undo")
            if prior:
                return self.action_reports.project(receipt)
            commands = receipt.data.get("command_receipts")
            if not self._tier_one(receipt, commands):
                raise SupervisorFailure(409, "only a tier 1 action can be undone")
            principal = self.authority._principal(grant)
            grant, context = self.authority.action_context(principal)
            baseline = self.entries.supervisor_records(
                "SupervisorActionReport", last=1, receipt_id=receipt.row_id, report_kind="baseline",
            )
            if (context.get("conflict_reason") or not baseline
                    or context["current_phase"]["phase_id"] != baseline[0].data.get("phase_id")):
                raise SupervisorFailure(409, "the action rows changed since this receipt")
            changes = receipt.data.get("changes", [])
            if not changes:
                raise SupervisorFailure(409, "the receipt has no reversible changes")
            for change in changes:
                field = change.get("field")
                if field in {"priorities", "interval"}:
                    if self._rollback_conflict(grant, context, change):
                        raise SupervisorFailure(409, "the action rows changed since this receipt")
                elif field not in {"plan_link", "phase_link"}:
                    raise SupervisorFailure(409, "the receipt has no reversible tier 1 changes")
            with self.scope.environment(plan.environment_id):
                created_rows = self._created_rows(commands)
                results = [
                    self._rollback_change(grant, context, change, actor)
                    for change in changes if change["field"] in {"priorities", "interval"}
                ]
                for ref, row in sorted(created_rows.values(), key=lambda item: item[0]["table"] == "tasks"):
                    self._delete_created_row(ref, row, actor)
                    results.append({"ref": ref, "field": "created_row", "status": "removed"})
            self.action_reports.record_owner_undo(receipt, plan_id, actor, results)
        return self.action_reports.project(receipt)

    def owner_undo_counts(self, plan_id: int, actor: Actor) -> dict[str, Any]:
        return self.action_reports.owner_undo_counts(plan_id, actor)

    def accept_owner_proposal(self, plan_id: int, receipt_id: int, actor: Actor) -> dict[str, Any]:
        return self._decide_owner_proposal(plan_id, receipt_id, actor, "accepted")

    def decline_owner_proposal(self, plan_id: int, receipt_id: int, actor: Actor) -> dict[str, Any]:
        return self._decide_owner_proposal(plan_id, receipt_id, actor, "declined")

    def _decide_owner_proposal(self, plan_id: int, receipt_id: int, actor: Actor,
                               decision: str) -> dict[str, Any]:
        with self.scope.environment(PROJECT), self.entries.writing():
            plan = self.authority._plan(plan_id)
            owner_id = self.authority._owner(actor, plan)
            rows = self.entries.selected(self.entries.query().filter(
                id=receipt_id, entry_type="SupervisorActionReceipt",
            ).limit(1))
            if not rows:
                raise SupervisorFailure(403, "supervisor proposal is not available")
            receipt = rows[0]
            data = receipt.data
            tenant_id = data.get("scope", {}).get("tenant_id", data.get("tenant_id"))
            grant_entry = self.authority._latest_entry(data.get("grant_id", ""))
            if grant_entry is None:
                raise SupervisorFailure(403, "supervisor proposal is not available")
            grant = self.authority._public_grant(grant_entry)
            if tenant_id != f"owner:{owner_id}" or grant.get("owner_user_id") != owner_id:
                raise SupervisorFailure(403, "supervisor proposal is not available")
            if grant.get("plan_id") != plan_id:
                raise SupervisorFailure(403, "supervisor proposal is not available")
            if decision == "accepted" and grant.get("grant_version") != data.get("grant_version"):
                raise SupervisorFailure(409, "the proposal is no longer current")
            runs = self.entries.supervisor_records(
                "SupervisorRun", last=100, tenant_id=tenant_id, grant_id=grant["grant_id"],
                run_ref=data.get("run_id"),
            )
            if not runs or runs[0].data.get("plan_id") != plan_id:
                raise SupervisorFailure(403, "supervisor proposal is not available")
            if data.get("status") != "proposed":
                raise SupervisorFailure(409, "only a pending proposal can be decided")
            if self.action_reports.proposal_decision(receipt):
                raise SupervisorFailure(409, "proposal already decided")
            report = self.action_reports.record_proposal_decision(receipt, plan_id, actor, decision)
        return {"decision": decision, "receipt_id": receipt_id, "report_id": report.row_id}

    def _tier_one(self, receipt: Entry, commands: object) -> bool:
        operations = receipt.data.get("proposed_operations")
        if (not isinstance(operations, list) or not operations
                or not isinstance(commands, list) or len(commands) != len(operations)):
            return False
        for operation, command in zip(operations, commands):
            if (not isinstance(operation, dict) or operation.get("kind") not in OPERATION_COMMANDS
                    or not isinstance(command, dict) or command.get("status") != "applied"
                    or command.get("readback_verification") != "verified"):
                return False
            area, noun, verb = OPERATION_COMMANDS[operation["kind"]]
            if (command.get("command") != f"{noun} {verb}" or command.get("area") != area
                    or CAPABILITY_CATALOGUE[area][noun][verb] != "tier 1"):
                return False
        return True

    def _created_rows(self, commands: list[dict[str, Any]]) -> dict[tuple[str, int], tuple[dict[str, Any], Any]]:
        created = {}
        for command in commands:
            changes = command.get("rows_changed")
            if not isinstance(changes, list) or not changes:
                raise SupervisorFailure(409, "the receipt has no reversible tier 1 changes")
            for change in changes:
                if not isinstance(change, dict) or not isinstance(change.get("ref"), dict):
                    raise SupervisorFailure(409, "the receipt has no reversible tier 1 changes")
                ref = change["ref"]
                if change.get("event") == "updated":
                    after = change.get("after")
                    row = self._command_row(ref)
                    if not isinstance(after, dict) or row is None or not self.command_changes.matches(row, after):
                        raise SupervisorFailure(409, "the action rows changed since this receipt")
                    continue
                if change.get("event") != "created" or ref.get("table") not in {"links", "tasks"}:
                    raise SupervisorFailure(409, "the receipt has no reversible tier 1 changes")
                row = self._command_row(ref)
                after = change.get("after")
                key = (ref["table"], ref["id"]) if type(ref.get("id")) is int else None
                if (row is None or not isinstance(after, dict) or key is None
                        or key in created or not self.command_changes.matches(row, after)):
                    raise SupervisorFailure(409, "the action rows changed since this receipt")
                created[key] = (ref, row)
        tasks = [row for (table, _), (_, row) in created.items() if table == "tasks"]
        for task in tasks:
            expected_links = {
                ref["id"] for (table, _), (ref, link) in created.items()
                if table == "links" and (link.source == Ref.build(task) or link.target == Ref.build(task))
            }
            current_links = [link for link in self.links.row_links([task])
                             if link.source == Ref.build(task) or link.target == Ref.build(task)]
            if {link.row_id for link in current_links} != expected_links:
                raise SupervisorFailure(409, "the action rows changed since this receipt")
        return created

    def _command_row(self, ref: dict[str, Any]):
        repositories = {
            "plans": self.plans, "checks": self.checks, "tasks": self.tasks, "links": self.links,
        }
        repository = repositories.get(ref.get("table"))
        if repository is None or type(ref.get("id")) is not int:
            return None
        rows = repository.selected(repository.query().filter(id=ref["id"]).limit(1))
        return rows[0] if rows else None

    def _delete_created_row(self, ref: dict[str, Any], row: Any, actor: Actor) -> None:
        repositories = {"links": self.links, "tasks": self.tasks}
        repository = repositories.get(ref["table"])
        if repository is None:
            raise SupervisorFailure(409, "the receipt has no reversible tier 1 changes")
        repository.delete(row, actor)

    def _rollback_change(self, grant: dict[str, Any], context: dict[str, Any], change: dict[str, Any],
                         actor: Actor) -> dict[str, Any]:
        ref, field = change["ref"], change["field"]
        reason = self._rollback_conflict(grant, context, change)
        if reason:
            return {"ref": ref, "field": field, "status": "owner_edit_preserved", "reason": reason}
        if field == "priorities":
            plan = context["plan"]
            restored = plan.prioritised(change["before_value"] or "", context["current_phase"]["number"], self.time_source.seconds())
            with self.scope.environment(plan.environment_id):
                self.plans.save(restored, actor)
            return {"ref": ref, "field": field, "status": "rolled_back"}
        if field == "interval":
            check = self._check(ref["id"])
            before_interval = change["before_value"]
            self.checks.save(check.with_(interval=float(before_interval)), actor)
            return {"ref": ref, "field": field, "status": "rolled_back"}
        return {"ref": ref, "field": field, "status": "diagnostic_preserved"}

    def _rollback_conflict(self, grant: dict[str, Any], context: dict[str, Any], change: dict[str, Any]) -> str:
        ref, field = change["ref"], change["field"]
        if field == "priorities":
            plan = context["plan"]
            if not self.authority.permits_domain_write(grant, "plan_priorities"):
                return "capability_not_current"
            if (self.authority.priority_action_revision(plan) != change["after_revision"]
                    or plan.priorities != change["after_value"]):
                return "owner_edit_preserved"
            return ""
        if field == "interval":
            if not self.authority.permits_domain_write(grant, "check_interval"):
                return "capability_not_current"
            check = self._check(ref["id"])
            enrolled = next((item for item in grant["checks"] if item["check_id"] == ref["id"]), None)
            before_interval = change["before_value"]
            if (self.authority.check_action_revision(check) != change["after_revision"]
                    or int(check.interval) != change["after_value"] or enrolled is None
                    or not enrolled["minimum_interval_minutes"] <= before_interval <= enrolled["baseline_interval_minutes"]):
                return "owner_edit_preserved"
            return ""
        return ""

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
        if not rows or rows[0].data.get("status") not in {"known", "overrun"}:
            return "usage_unknown"
        return "usage_overrun" if rows[0].data.get("status") == "overrun" or rows[0].data.get("overrun") is True else ""

    @staticmethod
    def _usage_settlement_request(body: object) -> dict[str, Any]:
        run_fields = {
            "run_id", "episode_id", "pending_action_id", "grant_id", "grant_version", "installation_epoch", "fence",
        }
        usage_fields = {
            "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
            "total_input_tokens", "provider_requests", "provider_retries",
        }
        if (not isinstance(body, dict) or set(body) != {"protocol_version", "run_ref", "usage"}
                or type(body["protocol_version"]) is not int or body["protocol_version"] != 1
                or not isinstance(body["run_ref"], dict) or set(body["run_ref"]) != run_fields
                or not isinstance(body["usage"], dict) or set(body["usage"]) != usage_fields):
            raise SupervisorFailure(400, "the metered usage request is invalid")
        run_ref, usage = body["run_ref"], body["usage"]
        if (any(not isinstance(run_ref[key], str) or not 1 <= len(run_ref[key]) <= 256
                for key in ("run_id", "episode_id", "pending_action_id", "grant_id"))
                or any(type(run_ref[key]) is not int or run_ref[key] < 1
                       for key in ("grant_version", "installation_epoch", "fence"))
                or any(type(usage[key]) is not int or usage[key] < 0 for key in usage_fields)
                or usage["provider_requests"] < 1 or usage["provider_retries"] > usage["provider_requests"]
                or usage["total_input_tokens"] != usage["input_tokens"] + usage["cache_creation_input_tokens"] + usage["cache_read_input_tokens"]):
            raise SupervisorFailure(400, "the metered usage request is invalid")
        return {"run_ref": dict(run_ref), "usage": dict(usage)}

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
            "priority_revision": self.authority.priority_action_revision(context["plan"]),
            "checks": {},
        }
        for operation in request["operations"]:
            if operation["kind"] == "check_interval":
                check = self._check(operation["check_id"])
                values["checks"][check.row_id] = check
        return values

    def _apply(self, grant: dict[str, Any], context: dict[str, Any], request: dict[str, Any]) -> tuple[list[dict[str, Any]], Task | None, bool, list[list[dict[str, Any]]]]:
        actor = Actor.plugin(SUPERVISOR_ACTOR)
        plan = context["plan"]
        phase = context["current_phase_row"]
        diagnostic = None
        created = False
        affected: list[dict[str, Any]] = []
        command_changes = []
        with self.scope.environment(plan.environment_id):
            for operation in request["operations"]:
                with self.command_changes.capture() as changes:
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
                        self.checks.save(check.with_(interval=float(interval)), actor)
                        affected.append({"table": "checks", "id": check.row_id})
                command_changes.append(changes)
        return affected, diagnostic, created, command_changes

    def _diagnostic(self, grant: dict[str, Any], plan: Plan, phase: Phase,
                    actor: Actor, episode_id: str) -> tuple[Task, bool]:
        template = self.authority.diagnostic_template(grant)
        title, brief = diagnostic_task_values(template)
        with self.scope.environment(plan.environment_id):
            existing = next((task for task in self.plans.phase_tasks(phase)
                if task.title == title and task.brief == brief and self.links.connecting(task, plan)
                and eligible_diagnostic(task, self.tasks)), None)
            if existing:
                return existing, False
            allowance = min(1, grant["limits"]["max_new_diagnostics_per_episode"])
            if self._new_diagnostic_count(grant, episode_id) >= allowance:
                raise SupervisorFailure(409, "the episode has used its diagnostic task allowance")
            task = self.tasks.save(Task(environment_id=plan.environment_id, title=title, brief=brief), actor)
            self.plans.place_task_in_phase(task, plan, phase, actor)
            return self.tasks.find(task.row_id), True

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
                if (len(plan_link) != 1 or len(phase_link) != 1 or not eligible_diagnostic(diagnostic, self.tasks)
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

    def _changes(self, before: dict[str, Any], after: dict[str, Any], readback: dict[str, Any], grant: dict[str, Any],
                 request: dict[str, Any], diagnostic: Task | None, created: bool) -> list[dict[str, Any]]:
        changes = []
        if any(operation["kind"] == "plan_priorities" for operation in request["operations"]):
            operation = next(operation for operation in request["operations"] if operation["kind"] == "plan_priorities")
            changes.append({
                "ref": {"table": "plans", "id": grant["plan_id"]}, "field": "priorities",
                "before_revision": before["priority_revision"],
                "after_revision": self.authority.priority_action_revision(readback["plan"]),
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
                 affected: list[dict[str, Any]] | None = None, changes: list[dict[str, Any]] | None = None,
                 command_changes: list[list[dict[str, Any]]] | None = None) -> dict[str, Any]:
        scope = {**grant["scope"], "installation_epoch": epoch}
        data = {
            "protocol_version": 1, "action_id": request["action_id"], "episode_id": request["episode_id"],
            "run_id": run_ref, "grant_id": grant["grant_id"], "grant_version": grant["grant_version"],
            "scope": scope, "fence": request["fence"], "intent_sha256": intent_hash,
            "actor_kind": "plugin", "actor_id": SUPERVISOR_ACTOR, "status": status, "reason": reason,
            "rationale": request["rationale"],
            "recorded_at_ms": int(self.time_source.seconds() * 1000),
            "observation_ids": request["observation_ids"], "affected_refs": self._unique_refs(affected or []),
            "changes": changes or [], "verification": "pending" if status == "applied" else "not_applied",
            "outcome": "unmeasured", "proposed_operations": request["operations"],
            "command_receipts": self._command_receipts(grant, request, run_ref, status, reason, command_changes),
        }
        key = action_receipt_key(scope["tenant_id"], request["action_id"])
        if reason == "action_id_reused":
            key = action_reuse_key(scope["tenant_id"], request["action_id"], intent_hash)
        row = self.control_entries.recorded(Entry(
            environment_id=PROJECT, entry_type="SupervisorActionReceipt", actor=Actor.plugin(SUPERVISOR_ACTOR),
            data=data, idempotency=key,
        ), Actor.plugin(SUPERVISOR_ACTOR))
        return {"status": status, "reason": reason, "receipt_id": row.row_id, "data": row.data, "duplicate": False}

    def _command_receipts(self, grant: dict[str, Any], request: dict[str, Any], run_ref: str,
                          status: str, reason: str | None,
                          command_changes: list[list[dict[str, Any]]] | None) -> list[dict[str, Any]]:
        if status == "proposed":
            return []
        cost = self._settled_cost(grant["scope"]["tenant_id"], run_ref)
        commands = []
        for index, operation in enumerate(request["operations"]):
            area, noun, verb = OPERATION_COMMANDS[operation["kind"]]
            commands.append({
                "command": f"{noun} {verb}",
                "arguments": {key: value for key, value in operation.items() if key != "kind"},
                "area": area,
                "tier": CAPABILITY_CATALOGUE[area][noun][verb],
                "status": status,
                "reason": reason,
                "rows_changed": command_changes[index] if command_changes and index < len(command_changes) else [],
                "readback_verification": "verified" if status == "applied" else "not_applied",
                "settled_cost": dict(cost),
            })
        return commands

    def _settled_cost(self, tenant_id: str, run_ref: str) -> dict[str, Any]:
        with self.scope.environment(PROJECT):
            rows = self.entries.supervisor_records(
                "SupervisorUsage", last=1, tenant_id=tenant_id, run_ref=run_ref,
            )
        usage = rows[0].data if rows else {}
        cost = usage.get("cost_usd")
        usage_status = usage.get("status")
        settled = (isinstance(usage_status, str) and usage_status in {"known", "overrun"}
                   and isinstance(cost, str) and bool(cost))
        return {"status": "settled" if settled else "unknown", "usd": cost if settled else None, "scope": "run"}

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
