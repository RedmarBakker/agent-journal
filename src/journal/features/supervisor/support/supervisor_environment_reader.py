import hashlib
from typing import Any

from journal.models.entry import Entry
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.models.supervisor_grant import SupervisorGrant
from journal.repositories.checks import Checks
from journal.repositories.entries import Entries
from journal.repositories.messages import Messages
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.sequences import Sequences
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.triggers import Triggers
from journal.repositories.workers import Workers
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_principal import SupervisorPrincipal
from journal.support.time_source import TimeSource

ENVIRONMENT_READ_ENTRY = "SupervisorEnvironmentRead"
MAX_ENVIRONMENT_PLANS = 20
MAX_ENVIRONMENT_PHASES_PER_PLAN = 10
MAX_ENVIRONMENT_TASKS = 50
MAX_ENVIRONMENT_WAITS = 100
MAX_ENVIRONMENT_CHECKS = 40
MAX_ENVIRONMENT_WORKERS = 50
MAX_ENVIRONMENT_MESSAGES = 25
MAX_ENVIRONMENT_SEQUENCES = 25
MAX_ENVIRONMENT_TRIGGERS = 25
MAX_SEQUENCE_DETAILS = 10
MAX_ENVIRONMENT_SUMMARY_BYTES = 262_144
MAX_SUMMARY_TEXT = 160


class SupervisorEnvironmentReader:
    """Reads a bounded view of the plans and project items visible to a supervisor grant."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 plans: Plans, checks: Checks, messages: Messages, workers: Workers, sequences: Sequences,
                 triggers: Triggers, scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.plans, self.checks, self.messages, self.workers = plans, checks, messages, workers
        self.sequences, self.triggers, self.scope, self.time_source = sequences, triggers, scope, time_source

    def read(self, principal: SupervisorPrincipal, grant: dict[str, Any], run: dict[str, Any],
             cursor: str | None) -> tuple[dict[str, Any], int]:
        permissions = self.authority.observation_permissions(principal)
        plan_rows, more_plans = self._plans(permissions)
        summary = self._summary(permissions.environment_id, plan_rows, more_plans, grant)
        digest = hashlib.sha256((cursor or "initial").encode("utf-8")).hexdigest()[:16]
        with self.scope.environment(PROJECT):
            prior = self.entries.supervisor_records(ENVIRONMENT_READ_ENTRY, last=1,
                tenant_id=principal.scope["tenant_id"], grant_id=grant["grant_id"],
                run_id=run["run_ref"], cursor_digest=digest)
            entry = prior[0] if prior else self.control_entries.recorded(Entry(
                environment_id=PROJECT, entry_type=ENVIRONMENT_READ_ENTRY, actor=principal.actor,
                data={
                    "tenant_id": principal.scope["tenant_id"], "grant_id": grant["grant_id"],
                    "grant_version": grant["grant_version"], "plan_id": grant["plan_id"],
                    "run_id": run["run_ref"], "environment_id": permissions.environment_id,
                    "cursor_digest": digest, "what_it_saw": summary,
                },
                idempotency=f"supervisor:environment-read:{principal.scope['tenant_id']}:{grant['grant_id']}:{run['run_ref']}:{digest}",
            ), principal.actor)
        return entry.data["what_it_saw"], entry.row_id

    def change_marker(self, principal: SupervisorPrincipal) -> int:
        permissions = self.authority.observation_permissions(principal)
        plan_rows, _more_plans = self._plans(permissions)
        environment_ids = {PROJECT, permissions.environment_id}
        environment_ids.update(plan.environment_id for plan in plan_rows)
        return self.entries.latest_row_event_id(tuple(sorted(environment_ids)))

    def _plans(self, permissions: SupervisorGrant) -> tuple[list[Plan], bool]:
        query = self.plans.query().order("id")
        if permissions.watched_plans != "all":
            query = query.filter_listed("id", permissions.watched_plans)
        with self.scope.environment(permissions.environment_id):
            rows = self.plans.selected(query.limit(MAX_ENVIRONMENT_PLANS + 1))
        return rows[:MAX_ENVIRONMENT_PLANS], len(rows) > MAX_ENVIRONMENT_PLANS

    def _summary(self, environment_id: int, plans: list[Plan], more_plans: bool,
                 grant: dict[str, Any]) -> dict[str, Any]:
        plan_summary = self._plan_rows(plans)
        failing_checks = self._failing_checks(grant, plan_summary["waits"])
        with self.scope.environment(environment_id):
            unanswered = self._unanswered_messages()
            triggers = self._trigger_rows()
        workers = self._worker_rows([plan.row_id for plan in plans])
        sequences = self._sequence_rows()
        return {
            "environment_id": environment_id,
            "plan_ids": [plan.row_id for plan in plans],
            "plans": plan_summary["plans"],
            "phases": plan_summary["phases"],
            "open_tasks": plan_summary["open_tasks"],
            "blocked_tasks": plan_summary["blocked_tasks"],
            "waits": plan_summary["waits"],
            "failing_checks": failing_checks[0],
            "workers": workers[0],
            "unanswered_messages": unanswered[0],
            "sequences": sequences[0],
            "triggers": triggers[0],
            "truncated": {
                "plans": more_plans, **plan_summary["truncated"], "failing_checks": failing_checks[1],
                "workers": workers[1], "unanswered_messages": unanswered[1],
                "sequences": sequences[1], "triggers": triggers[1],
            },
        }

    def _plan_rows(self, plans: list[Plan]) -> dict[str, Any]:
        plan_rows, phases, open_tasks, blocked_tasks, waits = [], [], [], [], []
        phase_more = open_more = blocked_more = wait_more = False
        for plan in plans:
            with self.scope.environment(plan.environment_id):
                states = self.plans.phase_states(plan)
                visible_states = states[:MAX_ENVIRONMENT_PHASES_PER_PLAN]
                phase_more = phase_more or len(states) > MAX_ENVIRONMENT_PHASES_PER_PLAN
                phase_ids = {task.row_id: state.phase.row_id for state in visible_states
                             for task in self.plans.phase_tasks(state.phase)}
                plan_rows.append({"plan_id": plan.row_id, "title": self._text(plan.title),
                    "brief": self._text(plan.brief), "state": plan.state.value})
                phases.extend({"plan_id": plan.row_id, "phase_id": state.phase.row_id, "number": state.number,
                    "title": self._text(state.phase.title),
                    "completion_rule": self._text(state.phase.completion_rule),
                    "task_counts": {key.value: value for key, value in state.state_counts.items()}}
                    for state in visible_states)
                open_rows = self.plans.tasks.selected(self.plans.plan_task_query(plan)
                    .filter(state=TaskState.OPEN).order("id").limit(MAX_ENVIRONMENT_TASKS + 1))
                blocked_rows = self.plans.tasks.selected(self.plans.plan_task_query(plan)
                    .filter(state=TaskState.BLOCKED).order("id").limit(MAX_ENVIRONMENT_TASKS + 1))
                open_tasks.extend(self._task_row(plan, task, phase_ids) for task in open_rows[:MAX_ENVIRONMENT_TASKS])
                blocked_tasks.extend(self._task_row(plan, task, phase_ids) for task in blocked_rows[:MAX_ENVIRONMENT_TASKS])
                open_more = open_more or len(open_rows) > MAX_ENVIRONMENT_TASKS
                blocked_more = blocked_more or len(blocked_rows) > MAX_ENVIRONMENT_TASKS
                waits.extend(self._wait_row(plan, task, ref) for task in [*open_rows, *blocked_rows]
                    for ref in self.plans.tasks.open_waits(task))
                waits.extend(self._plan_wait_row(plan, ref) for ref in self.plans.tasks.open_waits(plan))
                if len(waits) > MAX_ENVIRONMENT_WAITS:
                    wait_more = True
                    waits = waits[:MAX_ENVIRONMENT_WAITS]
        return {
            "plans": plan_rows,
            "phases": phases[:MAX_ENVIRONMENT_PLANS * MAX_ENVIRONMENT_PHASES_PER_PLAN],
            "open_tasks": open_tasks[:MAX_ENVIRONMENT_TASKS],
            "blocked_tasks": blocked_tasks[:MAX_ENVIRONMENT_TASKS],
            "waits": waits,
            "truncated": {
                "phases": phase_more or len(phases) > MAX_ENVIRONMENT_PLANS * MAX_ENVIRONMENT_PHASES_PER_PLAN,
                "open_tasks": open_more or len(open_tasks) > MAX_ENVIRONMENT_TASKS,
                "blocked_tasks": blocked_more or len(blocked_tasks) > MAX_ENVIRONMENT_TASKS,
                "waits": wait_more,
            },
        }

    def _task_row(self, plan: Plan, task: Task, phase_ids: dict[int, int]) -> dict[str, Any]:
        return {"task_id": task.row_id, "plan_id": plan.row_id, "phase_id": phase_ids.get(task.row_id),
            "title": self._text(task.title), "brief": self._text(task.brief), "state": task.state.value,
            "block_reason": self._text(task.block_reason) if task.state == TaskState.BLOCKED else ""}

    @staticmethod
    def _wait_row(plan: Plan, task: Task, target: Ref) -> dict[str, Any]:
        return {"plan_id": plan.row_id, "source_task_id": task.row_id, "target_type": target.type, "target_id": target.id}

    @staticmethod
    def _plan_wait_row(plan: Plan, target: Ref) -> dict[str, Any]:
        return {"plan_id": plan.row_id, "source_task_id": None, "target_type": target.type, "target_id": target.id}

    def _failing_checks(self, grant: dict[str, Any], waits: list[dict]) -> tuple[list[dict], bool]:
        ids = {item["target_id"] for item in waits if item["target_type"] == "checks"}
        ids.update(item["check_id"] for item in grant["checks"])
        rows = self.checks.selected(self.checks.query().filter_listed("id", sorted(ids))
            .filter(last_passed=False, is_retired=False).order("id").limit(MAX_ENVIRONMENT_CHECKS + 1)) if ids else []
        return ([{"check_id": check.row_id, "title": self._text(check.title), "brief": self._text(check.brief),
            "last_output": self._text(check.last_output), "last_fault": self._text(check.last_fault),
            "last_run_at": check.last_run_at.isoformat() if check.last_run_at else ""}
            for check in rows[:MAX_ENVIRONMENT_CHECKS]], len(rows) > MAX_ENVIRONMENT_CHECKS)

    def _worker_rows(self, plan_ids: list[int]) -> tuple[list[dict], bool]:
        rows = self.workers.selected_globally(self.workers.query().filter_listed("plan_id", plan_ids)
            .order("id").limit(MAX_ENVIRONMENT_WORKERS + 1)) if plan_ids else []
        now = self.time_source.seconds()
        return ([{"worker_id": worker.row_id, "plan_id": worker.plan_id, "name": self._text(worker.name),
            "role": self._text(worker.role), "state": worker.state.value,
            "seconds_since_heard": max(0, int(now - worker.silence.timeout.start))}
            for worker in rows[:MAX_ENVIRONMENT_WORKERS]], len(rows) > MAX_ENVIRONMENT_WORKERS)

    def _unanswered_messages(self) -> tuple[list[dict], bool]:
        rows = self.messages.selected(self.messages.unanswered_query().order_descending("id").limit(MAX_ENVIRONMENT_MESSAGES + 1))
        return ([{"message_id": message.row_id, "author": message.author.value,
            "kind": self._text(str(message.data.get("kind", ""))), "text": self._text(message.text),
            "created_at": message.created_at.isoformat()}
            for message in rows[:MAX_ENVIRONMENT_MESSAGES]], len(rows) > MAX_ENVIRONMENT_MESSAGES)

    def _sequence_rows(self) -> tuple[list[dict], bool]:
        rows = self.sequences.selected(self.sequences.query().order_descending("id").limit(MAX_ENVIRONMENT_SEQUENCES + 1))
        return ([{"sequence_id": sequence.row_id, "title": self._text(sequence.title), "locked": sequence.locked,
            "steps": [self._text(step.heading()) for step in sequence.steps[:MAX_SEQUENCE_DETAILS]],
            "triggers": [{"type": trigger.trigger_type.value, "moment": self._text(trigger.moment),
                "text": self._text(trigger.text), "pattern": self._text(trigger.pattern),
                "tool": self._text(trigger.tool)} for trigger in sequence.triggers[:MAX_SEQUENCE_DETAILS]],
            "steps_truncated": len(sequence.steps) > MAX_SEQUENCE_DETAILS,
            "triggers_truncated": len(sequence.triggers) > MAX_SEQUENCE_DETAILS}
            for sequence in rows[:MAX_ENVIRONMENT_SEQUENCES]], len(rows) > MAX_ENVIRONMENT_SEQUENCES)

    def _trigger_rows(self) -> tuple[list[dict], bool]:
        query = self.triggers.query()
        listed = query.filter_alternatives(query.filter(is_scheduled=False), query.filter_present("next_at"))
        rows = self.triggers.selected(listed.order_descending("id").limit(MAX_ENVIRONMENT_TRIGGERS + 1))
        return ([{"trigger_id": trigger.row_id, "text": self._text(trigger.text), "scheduled": trigger.is_scheduled,
            "next_at": trigger.next_at.isoformat() if trigger.next_at else ""}
            for trigger in rows[:MAX_ENVIRONMENT_TRIGGERS]], len(rows) > MAX_ENVIRONMENT_TRIGGERS)

    @staticmethod
    def _text(value: str) -> str:
        return value[:MAX_SUMMARY_TEXT]
