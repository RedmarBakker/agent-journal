from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.events.rows.plan_work_available import PlanWorkAvailable
from journal.events.rows.task_closed import TaskClosed
from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.tasks.support.default_task_assigner import DefaultTaskAssigner
from journal.features.tasks.tasks_options import TasksOptions
from journal.features.workers.support.work_mode import WorkMode
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.task_state import TaskState
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

FOLLOWING_PLAN = "following_plan"


class PlanTaskAssigner:
    """The task assigner a followed plan names: ordinary task completion may pass an owner checkpoint in auto mode, while supervisor work signals stop there; blocked tasks, unpassed phase tests, orchestrator mode and work already in hand hold both paths."""

    def __init__(self, default: DefaultTaskAssigner, plans: Plans, tasks: Tasks, testing: PhaseTesting, orchestrator: WorkMode, settings: SettingRows, time_source: TimeSource, scope: Scope) -> None:
        self.default, self.plans, self.tasks, self.testing, self.orchestrator, self.settings, self.time_source, self.scope = default, plans, tasks, testing, orchestrator, settings, time_source, scope

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int = 1) -> Assignment:
        if isinstance(event, PlanWorkAvailable):
            return self.work_available(agent, event, quantity)
        if not self.default.is_free_moment(agent, event):
            return Assignment()
        return self.next_plan_task(agent, event, quantity)

    def work_available(self, agent: Agent, event: PlanWorkAvailable, quantity: int) -> Assignment:
        if (event.environment_id != agent.environment_id or not agent.is_main() or self.default.is_working(agent)
                or not self.following_plan_idle(agent, event.plan_id)):
            return Assignment()
        plan = self.current_plan(agent, event)
        if plan is None:
            return Assignment()
        with self.scope.environment(plan.environment_id):
            if plan.row_id != event.plan_id or not self.is_current_phase(plan, event.phase_id):
                return Assignment()
            if not self.eligible_signal_task(plan, event):
                return Assignment()
            if self.supervisor_checkpoint_blocks(plan):
                return Assignment()
        return self.next_plan_task(agent, event, quantity)

    @staticmethod
    def following_plan_idle(agent: Agent, plan_id: int) -> bool:
        if not agent.stack:
            return False
        top = agent.stack[-1]
        data = top.get("data", {})
        return top.get("state") == FOLLOWING_PLAN and data.get("plan_id") == plan_id and not data.get("task_id")

    def is_current_phase(self, plan: Plan, phase_id: int) -> bool:
        states = self.plans.phase_states(plan)
        number = plan.current_phase(states)
        return any(state.number == number and state.phase.row_id == phase_id for state in states)

    def eligible_signal_task(self, plan: Plan, event: PlanWorkAvailable) -> bool:
        task = self.tasks.find(event.task_id)
        phase = next((state.phase for state in self.plans.phase_states(plan) if state.phase.row_id == event.phase_id), None)
        return bool(phase and task in self.plans.phase_tasks(phase) and task in self.plans.plan_tasks(plan)
            and task.state == TaskState.OPEN and not task.delegated and task.row_id not in self.tasks.unavailable_task_ids([task])
            and self.tasks.task_holder(task.row_id) is None and not self.tasks.has_worker_holder([task.row_id]))

    def next_plan_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int) -> Assignment:
        plan = self.current_plan(agent, event)
        if plan is None:
            return Assignment()
        if not self.is_advancing(plan):
            if (plan.is_blocked() or plan.state == PlanState.FINISHED) and not isinstance(event, PlanWorkAvailable):
                return self.default.next_task(agent, event, quantity)
            return Assignment()
        with self.scope.environment(plan.environment_id):
            task = self.following_task(plan)
            if task is None:
                return Assignment()
            self.tasks.holder_started(task.plan_started(self.time_source.moment(), plan.row_id), Ref.build(agent), self.actor(event))
            return Assignment(task.row_id, task.title, f"the next task of plan {plan.id}", self.following_ids(plan, quantity))

    def following_ids(self, plan: Plan, quantity: int) -> tuple[int, ...]:
        if quantity <= 1:
            return ()
        return tuple(queued.row_id for queued in self.plans.queued_tasks(plan))[:quantity - 1]

    @staticmethod
    def actor(event: AgentEvent | RowEvent) -> Actor:
        return Actor.parse(event.actor) if isinstance(event, TaskClosed) and event.actor else Actor.system()

    def current_plan(self, agent: Agent, event: AgentEvent | RowEvent) -> Plan | None:
        if isinstance(event, TaskClosed):
            started = self.plans.started_plans(self.tasks.find(event.task_id))
            if started:
                return started[0]
        plan_id = next((layer.get("data", {}).get("plan_id", 0) for layer in reversed(agent.stack) if layer.get("state") == FOLLOWING_PLAN), 0)
        return next(iter(self.plans.global_matching(id=plan_id)), None) if plan_id else None

    def advancement_block(self, plan: Plan) -> str:
        if not plan.is_started():
            return "plan_not_started"
        if self.orchestrator.delegates_work():
            return "work_delegated"
        with self.scope.environment(plan.environment_id):
            if self.checkpoint_blocks(plan):
                return "owner_checkpoint"
            if self.testing.unpassed(plan):
                return "phase_tests_unpassed"
        return ""

    def is_advancing(self, plan: Plan) -> bool:
        return not self.advancement_block(plan)

    def passes_checkpoints(self) -> bool:
        return bool(self.settings.option(TasksOptions.AUTO))

    def checkpoint_blocks(self, plan: Plan) -> bool:
        return self.plans.checkpoint_plans(plan) is not None and not self.passes_checkpoints()

    def supervisor_checkpoint_blocks(self, plan: Plan) -> bool:
        return self.plans.checkpoint_plans(plan) is not None

    def following_task(self, plan: Plan) -> Task | None:
        if self.checkpoint_blocks(plan):
            return None
        return self.plans.following_task(plan)
