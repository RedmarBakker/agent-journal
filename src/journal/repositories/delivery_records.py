import hashlib
import json
from datetime import datetime, timezone

from journal.features.organization.support.definition_of_done import DefinitionOfDone
from journal.features.organization.support.evidence_requirement import EvidenceRequirement
from journal.features.organization.support.organization import Organization
from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.plans.support.plan_owners import PlanOwners
from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.delivery_record import DeliveryRecord
from journal.models.link import Link
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.domain_rows import DomainRows
from journal.repositories.links import Links
from journal.repositories.plans import PLAN_LINK, Plans
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.sprints import Sprints
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import WORKED_LINK, Tasks
from journal.repositories.task_outcomes import TaskOutcomes
from journal.repositories.workers import Workers
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.actor_type import ActorType
from journal.support.rejection import Rejection
from journal.support.time_source import TimeSource

PLAN_DELIVERY_LINK = "plan_delivery_record"
DELIVERY_TASK_LINK = "delivery_record_task"


class DeliveryRecords(ScopedRepository[DeliveryRecord]):
    """The actor-checked, append-only evidence and read projection for plan delivery by each task's frozen domain policy."""

    model = DeliveryRecord

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, time_source: TimeSource, links: Links, plans: Plans, tasks: Tasks, domains: DomainRows,
                 organization: Organization, owners: PlanOwners, sprints: Sprints, workers: Workers, settings: SettingRows,
                 outcomes: TaskOutcomes) -> None:
        super().__init__(connection, bus, scope, time_source)
        self.links, self.plans, self.tasks, self.domains = links, plans, tasks, domains
        self.organization, self.owners, self.sprints, self.workers, self.settings = organization, owners, sprints, workers, settings
        self.outcomes = outcomes

    def show(self, plan_id: int) -> dict:
        plan = self.plans.find(plan_id)
        if self.mode() == "off":
            return {"plan_id": plan.row_id, "status": "off", "task_ids": [], "delivered_task_ids": [], "tasks": [], "history": []}
        tasks = self.plans.plan_tasks(plan)
        rows = self.plan_records(plan)
        projected = [self.task_data(plan, task, rows) for task in tasks]
        delivered = [row["task_id"] for row in projected if row["status"] == "delivered"]
        return {"plan_id": plan.row_id, "status": self.plan_status(projected), "task_ids": [task.row_id for task in tasks],
                "delivered_task_ids": delivered, "tasks": projected, "history": [self.history_data(row) for row in rows]}

    def record(self, plan_id: int, body: dict, actor: Actor) -> dict:
        if self.mode() == "off":
            raise Rejection("delivery evidence is unavailable while estimates mode is off")
        plan = self.plans.find(plan_id)
        action = body.get("action", "accept")
        if action == "reopen":
            return self.reopen(plan, body, actor)
        if action == "submit":
            state, assurance = "proposed", "worker_submitted"
        elif action in ("accept", "correct"):
            self.owner(plan, actor)
            state, assurance = "accepted", "owner_attested"
        else:
            raise Rejection("delivery action must be accept, submit, correct or reopen")
        evidence = body.get("evidence")
        if not isinstance(evidence, dict):
            raise Rejection("delivery evidence must be an object")
        tasks, version, domain, definition = self.validated_scope(plan, evidence)
        if state == "proposed":
            self.submitter(actor, tasks)
        if state == "accepted":
            self.execution_complete(tasks)
        fingerprint = self.fingerprint({"state": state, "evidence": evidence, "task_ids": [task.row_id for task in tasks], "policy_version": version})
        rows = self.plan_records(plan)
        duplicate = next((row for row in rows if row.fingerprint == fingerprint), None)
        if duplicate:
            if state == "proposed":
                return self.record_data(duplicate)
            if state == "accepted" and all(self.current_delivery(rows, task) and self.current_delivery(rows, task).state == "accepted" for task in tasks):
                return self.record_data(duplicate)
            raise Rejection("reopened delivery evidence cannot be replayed; record new evidence")
        current = [self.current_delivery(rows, task) for task in tasks]
        if action == "correct":
            if not current or any(row.state != "accepted" for row in current):
                raise Rejection("only accepted delivery evidence can be corrected")
            generation = max(row.generation for row in current) + 1
        elif action == "accept" and any(row.state == "accepted" for row in current):
            raise Rejection("accepted delivery evidence must be reopened before it is replaced")
        elif action == "accept" and any(row.state == "reopened" for row in current):
            generation = max(row.generation for row in current)
        else:
            generation = max((row.generation for row in current), default=0) + 1
        row = self.append(plan, tasks, state, generation, assurance, version, fingerprint, evidence, "", actor)
        return self.record_data(row)

    def merged(self, event) -> None:
        if self.mode() == "off":
            return
        task = self.tasks.find(event.task)
        for plan_ref in self.links.targets(task, PLAN_LINK):
            plan = self.plans.find(plan_ref.id)
            domain, definition, version = self.policy(plan, task)
            if definition and definition.evidence == EvidenceRequirement.VERIFIED_OUTPUT and self.execution_ready(task):
                evidence = {"kind": "verified_output", "source": "checked worker merge", "reference": f"worker:{event.worker}/task:{event.task}",
                            "artifact": list(event.merged_shas), "target": definition.target, "task_ids": [task.row_id],
                            "occurred_at": datetime.fromtimestamp(event.time, timezone.utc).isoformat()}
                self.trusted(plan, task, evidence, version)

    def trusted(self, plan: Plan, task: Task, evidence: dict, version: str) -> DeliveryRecord:
        rows = self.plan_records(plan)
        tasks, policy_version, _domain, definition = self.validated_scope(plan, evidence)
        if len(tasks) != 1 or tasks[0].row_id != task.row_id or definition.evidence != EvidenceRequirement.VERIFIED_OUTPUT or policy_version != version:
            raise Rejection("trusted merge evidence must match the task's verified output policy")
        self.execution_complete(tasks)
        fingerprint = self.fingerprint({"state": "accepted", "evidence": evidence, "task_ids": [task.row_id], "policy_version": version})
        duplicate = next((row for row in rows if row.fingerprint == fingerprint), None)
        if duplicate:
            return duplicate
        current = self.current_delivery(rows, task)
        if current and current.state == "accepted":
            return current
        generation = current.generation if current and current.state == "reopened" else current.generation + 1 if current else 1
        return self.append(plan, tasks, "accepted", generation, "journal_verified", version, fingerprint, evidence, "", Actor.system())

    def reopen(self, plan: Plan, body: dict, actor: Actor) -> dict:
        self.owner(plan, actor)
        reason = body.get("reason", "")
        if not isinstance(reason, str) or not reason.strip():
            raise Rejection("reopening delivery needs a reason")
        tasks = self.scoped_tasks(plan, body.get("task_ids"))
        rows = self.plan_records(plan)
        current = [self.current_delivery(rows, task) for task in tasks]
        if not tasks or any(row is None or row.state != "accepted" for row in current):
            raise Rejection("only accepted delivery evidence can be reopened")
        fingerprint = self.fingerprint({"action": "reopen", "task_ids": [task.row_id for task in tasks], "reason": reason.strip()})
        duplicate = next((row for row in rows if row.fingerprint == fingerprint), None)
        if duplicate and all(self.current_delivery(rows, task).state == "reopened" for task in tasks):
            return self.record_data(duplicate)
        version = current[0].policy_version
        generation = max(row.generation for row in current) + 1
        row = self.append(plan, tasks, "reopened", generation, "", version, fingerprint,
                          {"task_ids": [task.row_id for task in tasks]}, reason.strip(), actor)
        return self.record_data(row)

    def validated_scope(self, plan: Plan, evidence: dict) -> tuple[list[Task], str, str, DefinitionOfDone]:
        kind = evidence.get("kind")
        task_ids = evidence.get("task_ids")
        if not isinstance(task_ids, list) or not task_ids or not all(isinstance(number, int) and not isinstance(number, bool) for number in task_ids):
            raise Rejection("delivery evidence must name its affected task ids")
        if len(set(task_ids)) != len(task_ids):
            raise Rejection("delivery evidence repeats an affected task")
        tasks = self.scoped_tasks(plan, task_ids)
        policies = [self.policy(plan, task) for task in tasks]
        if any(definition is None for _domain, definition, _version in policies):
            missing = next((domain for domain, definition, _version in policies if definition is None), "unknown")
            raise Rejection(f"definition of done not set for {missing}")
        names = {domain for domain, _definition, _version in policies}
        versions = {version for _domain, _definition, version in policies}
        definitions = {definition for _domain, definition, _version in policies}
        if len(names) != 1 or len(versions) != 1 or len(definitions) != 1:
            raise Rejection("one delivery record can cover tasks with the same domain policy only")
        domain, definition, version = policies[0]
        if kind != definition.evidence.value:
            label = definition.evidence.value.replace("_", " ")
            raise Rejection(f"evidence does not match {domain}'s {label} requirement")
        self.evidence_fields(evidence, definition)
        return tasks, version, domain, definition

    def evidence_fields(self, evidence: dict, definition: DefinitionOfDone) -> None:
        kind = definition.evidence
        required = ("source", "reference", "task_ids", "occurred_at")
        if kind == EvidenceRequirement.PRODUCTION_DEPLOYMENT:
            required = (*required, "artifact", "environment", "result")
        elif kind in (EvidenceRequirement.PUBLISHED_OUTPUT, EvidenceRequirement.ACCEPTED_OUTPUT):
            required = (*required, "target", "output")
        elif kind == EvidenceRequirement.VERIFIED_OUTPUT:
            required = (*required, "target")
        if any(not evidence.get(key) for key in required):
            raise Rejection(f"{kind.value.replace('_', ' ')} evidence needs {', '.join(required)}")
        text_fields = tuple(key for key in required if key != "task_ids")
        if any(not isinstance(evidence[key], str) or not evidence[key].strip() for key in text_fields):
            raise Rejection(f"{kind.value.replace('_', ' ')} evidence fields must be non-empty text: {', '.join(text_fields)}")
        if kind == EvidenceRequirement.PRODUCTION_DEPLOYMENT:
            if evidence.get("result") != "succeeded" or evidence.get("environment") != definition.target:
                raise Rejection("production evidence must identify a successful deployment to the configured production environment")
        elif evidence.get("target") != definition.target:
            raise Rejection("delivery evidence target does not match the domain policy")
        moment = evidence.get("occurred_at")
        try:
            parsed = datetime.fromisoformat(str(moment).replace("Z", "+00:00"))
        except ValueError as broken:
            raise Rejection("delivery evidence time must be an ISO timestamp with a timezone") from broken
        if parsed.tzinfo is None:
            raise Rejection("delivery evidence time must include a timezone")

    def scoped_tasks(self, plan: Plan, values) -> list[Task]:
        if not isinstance(values, list) or not values or not all(isinstance(number, int) and not isinstance(number, bool) for number in values):
            raise Rejection("delivery scope must name task ids in the plan")
        tasks = {task.row_id: task for task in self.plans.plan_tasks(plan)}
        if any(task_id not in tasks for task_id in values):
            raise Rejection("delivery scope names a task outside the plan")
        return [tasks[task_id] for task_id in dict.fromkeys(values)]

    def policy(self, plan: Plan, task: Task) -> tuple[str | None, DefinitionOfDone | None, str | None]:
        committed = self.sprints.committed_task_snapshot(plan, task.row_id)
        if committed is not None:
            definition = DefinitionOfDone.from_data(committed.get("definition_of_done"))
            return committed.get("domain"), definition, committed.get("criteria_version")
        domain_name = self.domains.planned_domain_name(task)
        domain = self.organization.contracts().domain(domain_name) if domain_name else None
        definition = domain.definition_of_done if domain else None
        return domain_name, definition, definition.version if definition else None

    def task_data(self, plan: Plan, task: Task, rows: list[DeliveryRecord]) -> dict:
        domain, definition, version = self.policy(plan, task)
        current = self.current_delivery(rows, task)
        reason = ""
        if definition is None:
            status, reason = "unknown", "definition of done not set" if domain else "domain not set"
        elif not self.execution_ready(task):
            status, reason = self.execution_status(task), "existing proof, review and merge conditions are incomplete"
        elif current and current.state == "accepted" and current.policy_version == version:
            status = "delivered"
        else:
            status = "awaiting_deployment" if definition.evidence == EvidenceRequirement.PRODUCTION_DEPLOYMENT else "awaiting_evidence"
            reason = definition.criterion
        return {"task_id": task.row_id, "domain": domain, "criteria_version": version,
                "definition_of_done": definition.data() if definition else None, "status": status, "reason": reason,
                "evidence_id": current.row_id if current and current.state == "accepted" and current.policy_version == version else None,
                "generation": current.generation if current else 0}

    def execution_complete(self, tasks: list[Task]) -> None:
        if any(not self.execution_ready(task) for task in tasks):
            raise Rejection("delivery evidence cannot be accepted before the existing proof, review and merge gate")

    def accepted_for_task(self, task: Task) -> bool:
        return any(self.accepted(self.plans.find(ref.id), task) for ref in self.links.targets(task, PLAN_LINK) if ref.type == Plan.table())

    def accepted(self, plan: Plan, task: Task) -> bool:
        _domain, definition, version = self.policy(plan, task)
        current = self.current_delivery(self.plan_records(plan), task)
        return bool(self.mode() != "off" and self.execution_ready(task) and definition and current and current.state == "accepted" and current.policy_version == version)

    def execution_ready(self, task: Task) -> bool:
        if task.state != TaskState.COMPLETED:
            return False
        workers = [self.workers.find(ref.id) for ref in self.links.sources(task, WORKED_LINK) if ref.type == Worker.table()]
        return not workers or any(worker.state == WorkerState.MERGED and worker.merged_task == task.row_id for worker in workers)

    def execution_status(self, task: Task) -> str:
        holder = self.tasks.holder(task)
        return "awaiting_merge" if holder and holder.type == Worker.table() and self.workers.find(holder.id).state == WorkerState.DELIVERED else "awaiting_execution"

    def current_delivery(self, rows: list[DeliveryRecord], task: Task) -> DeliveryRecord | None:
        task_rows = [row for row in rows if task.row_id in row.evidence.get("task_ids", ()) and row.state != "proposed"]
        return task_rows[-1] if task_rows else None

    def plan_records(self, plan: Plan) -> list[DeliveryRecord]:
        return [self.find(ref.id) for ref in self.links.targets(plan, PLAN_DELIVERY_LINK)]

    def append(self, plan: Plan, tasks: list[Task], state: str, generation: int, assurance: str, version: str,
               fingerprint: str, evidence: dict, reason: str, actor: Actor) -> DeliveryRecord:
        with self.writing():
            row = self.save(DeliveryRecord(state=state, generation=generation, assurance=assurance,
                                           policy_version=version or "", fingerprint=fingerprint, evidence=evidence, reason=reason), actor)
            self.links.linked(Ref.build(plan), Ref.build(row), PLAN_DELIVERY_LINK, actor)
            for task in tasks:
                self.links.linked(Ref.build(row), Ref.build(task), DELIVERY_TASK_LINK, actor)
            self.outcomes.record_delivery(plan, tasks, row, actor)
            return row

    def record_data(self, row: DeliveryRecord) -> dict:
        return {"id": row.row_id, "state": row.state, "generation": row.generation, "assurance": row.assurance,
                "policy_version": row.policy_version, "reason": row.reason}

    def history_data(self, row: DeliveryRecord) -> dict:
        return {**self.record_data(row), "evidence": row.evidence, "created_at": row.created_at.isoformat() if row.created_at else "",
                "actor": row.creator.stamp if row.creator else ""}

    def plan_status(self, rows: list[dict]) -> str:
        statuses = [row["status"] for row in rows]
        if not statuses or "unknown" in statuses:
            return "unknown"
        if all(status == "delivered" for status in statuses):
            return "delivered"
        for status in ("awaiting_deployment", "awaiting_evidence", "awaiting_merge", "awaiting_execution"):
            if status in statuses:
                return status
        return "unknown"

    def mode(self) -> str:
        return str(self.settings.option(EstimatesOptions.MODE))

    def owner(self, plan: Plan, actor: Actor) -> None:
        if not actor.is_user() or self.owners.number(plan) != actor.number():
            raise Rejection("only the plan owner may accept or change delivery evidence")

    def submitter(self, actor: Actor, tasks: list[Task]) -> None:
        if actor.actor_type != ActorType.WORKER or any(
                not any(ref.type == Worker.table() and ref.id == actor.number() for ref in self.links.sources(task, WORKED_LINK)) for task in tasks):
            raise Rejection("only a worker assigned to every affected task may submit proposed delivery evidence")

    @staticmethod
    def fingerprint(value: dict) -> str:
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
