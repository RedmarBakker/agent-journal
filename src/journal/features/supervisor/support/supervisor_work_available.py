from typing import Any

from journal.events.announcer import Announcer
from journal.events.rows.plan_work_available import PlanWorkAvailable
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.features.supervisor.support.admissions import supervisor_key
from journal.features.supervisor.support.diagnostic_eligibility import eligible_diagnostic
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task_state import TaskState
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.plans import Plans
from journal.repositories.scope import PROJECT, Scope
from journal.repositories.supervisor_entries import SupervisorEntries
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.supervisor_authority import SUPERVISOR_ACTOR, SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal


class SupervisorWorkAvailable:
    """Rechecks an applied diagnostic after commit and signals only its bound Plan agent."""

    def __init__(self, authority: SupervisorAuthority, entries: Entries, control_entries: SupervisorEntries,
                 plans: Plans, tasks: Tasks, agents: Agents, assigner: PlanTaskAssigner,
                 announcer: Announcer, scope: Scope, time_source: TimeSource) -> None:
        self.authority, self.entries, self.control_entries = authority, entries, control_entries
        self.plans, self.tasks, self.agents, self.assigner, self.announcer = plans, tasks, agents, assigner, announcer
        self.scope, self.time_source = scope, time_source

    def after_commit(self, principal: SupervisorPrincipal, receipt: dict[str, Any], task_id: int) -> None:
        self.entries.connection.commit_callback(lambda: self.notify(principal, receipt, task_id))

    def notify(self, principal: SupervisorPrincipal, receipt: dict[str, Any], task_id: int) -> Entry | None:
        data = receipt.get("data", {})
        if receipt.get("status") != "applied" or data.get("status") != "applied":
            return None
        tenant_id = principal.scope.get("tenant_id", "")
        key = supervisor_key("action-delivery", tenant_id, str(receipt.get("receipt_id", 0)))
        with self.scope.environment(PROJECT):
            previous = self.entries.keyed(key)
        if previous:
            return previous[0]
        try:
            grant, context = self.authority.action_context(principal)
        except SupervisorFailure:
            return self.record(principal, receipt, task_id, "needs_owner", "grant_not_current", key)
        if context.get("conflict_reason"):
            return self.record(principal, receipt, task_id, "needs_owner", context["conflict_reason"], key, grant)
        operation = next((item for item in data.get("proposed_operations", ()) if item.get("kind") == "diagnostic_task"), None)
        affected_task = next((item.get("id") for item in data.get("affected_refs", ()) if item.get("table") == "tasks"), 0)
        if (operation is None or data.get("grant_id") != grant["grant_id"]
                or data.get("grant_version") != grant["grant_version"]
                or operation.get("plan_id") != grant["plan_id"]
                or operation.get("phase_id") != context["current_phase"]["phase_id"] or affected_task != task_id):
            return self.record(principal, receipt, task_id, "needs_owner", "grant_context_changed", key, grant)
        plan, agent, environment = context["plan"], context["agent"], context["environment"]
        if agent.state not in ("following_plan", "working") or not self.authority.is_plan_driver_state(agent, plan.row_id):
            return self.record(principal, receipt, task_id, "needs_owner", "driver_state_changed", key, grant)
        with self.scope.environment(plan.environment_id):
            bound_agent_id = self.plans.agent_id(plan)
        if self.agents.unended_agent(agent.row_id) != agent or bound_agent_id != agent.row_id:
            return self.record(principal, receipt, task_id, "needs_owner", "driver_binding_changed", key, grant)
        phase_id = context["current_phase"]["phase_id"]
        with self.scope.environment(environment.row_id):
            current_plan = self.plans.find(plan.row_id)
            if not self.assigner.is_current_phase(current_plan, phase_id):
                return self.record(principal, receipt, task_id, "needs_owner", "grant_context_changed", key, grant)
            if reason := self.assigner.advancement_block(current_plan):
                return self.record(principal, receipt, task_id, "needs_owner", reason, key, grant)
        if not self.current_diagnostic(plan, phase_id, task_id, agent):
            return self.record(principal, receipt, task_id, "needs_owner", "diagnostic_not_current", key, grant)
        event = PlanWorkAvailable(
            environment_id=environment.row_id, time=self.time_source.seconds(), row_id=task_id,
            actor=Actor.plugin(SUPERVISOR_ACTOR).stamp, target_agent_id=agent.row_id,
            plan_id=plan.row_id, phase_id=phase_id, task_id=task_id, receipt_id=receipt["receipt_id"],
        )
        self.announcer.announce(event)
        return self.record(principal, receipt, task_id, "notified", "", key)

    def current_diagnostic(self, plan: Plan, phase_id: int, task_id: int, agent: Agent) -> bool:
        with self.scope.environment(plan.environment_id):
            phase = next((state.phase for state in self.plans.phase_states(plan) if state.phase.row_id == phase_id), None)
            if phase is None:
                return False
            task = self.tasks.find(task_id)
            if task not in self.plans.phase_tasks(phase) or task not in self.plans.plan_tasks(plan):
                return False
            if eligible_diagnostic(task, self.tasks):
                return True
            return task.state == TaskState.STARTED and self.tasks.task_holder(task.row_id) == Ref.build(agent)

    def record(self, principal: SupervisorPrincipal, receipt: dict[str, Any], task_id: int,
               status: str, reason: str, key: str, grant: dict[str, Any] | None = None) -> Entry:
        data = receipt["data"]
        tenant_id = principal.scope["tenant_id"]
        operation = next((item for item in data.get("proposed_operations", ()) if item.get("kind") == "diagnostic_task"), {})
        with self.scope.environment(PROJECT):
            return self.control_entries.recorded(Entry(
                environment_id=PROJECT,
                entry_type="SupervisorActionDelivery",
                actor=Actor.plugin(SUPERVISOR_ACTOR),
                data={
                    "tenant_id": tenant_id,
                    "grant_id": data.get("grant_id", principal.grant_id),
                    "grant_version": data.get("grant_version", principal.grant_version),
                    "receipt_id": receipt["receipt_id"],
                    "plan_id": operation.get("plan_id", grant.get("plan_id", 0) if grant else 0),
                    "phase_id": operation.get("phase_id", 0),
                    "task_id": task_id,
                    "driver_agent_id": grant.get("driver_agent_id", 0) if grant else 0,
                    "driver_environment_id": principal.scope["environment_id"],
                    "status": status,
                    "reason": reason,
                    "recorded_at_ms": int(self.time_source.seconds() * 1000),
                },
                idempotency=key,
            ), Actor.plugin(SUPERVISOR_ACTOR))
