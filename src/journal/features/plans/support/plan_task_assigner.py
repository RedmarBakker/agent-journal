from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
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
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource

FOLLOWING_PLAN = "following_plan"


class PlanTaskAssigner:
    """The task assigner a followed plan names: when the agent finishes a task of a started plan, or stops with none in progress, it starts the plan's next task in the plan's order, a paused one first; the plan the closed task was in goes first, else the plan the agent follows now; nothing while a blocked task of the plan waits to be checked, at a checkpoint out of auto mode, at a phase end whose testing commands have not passed since, in the orchestrator's mode, or with the agent on a task. A close is followed in the name of whoever closed the task, so the agent that closed it is not told the start it caused."""

    def __init__(self, default: DefaultTaskAssigner, plans: Plans, tasks: Tasks, testing: PhaseTesting, orchestrator: WorkMode, settings: SettingRows, time_source: TimeSource) -> None:
        self.default, self.plans, self.tasks, self.testing, self.orchestrator, self.settings, self.time_source = default, plans, tasks, testing, orchestrator, settings, time_source

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int = 1) -> Assignment:
        if not self.default.is_free_moment(agent, event):
            return Assignment()
        return self.next_plan_task(agent, event, quantity)

    def next_plan_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int) -> Assignment:
        plan = self.current_plan(agent, event)
        if plan is None or not self.is_advancing(plan):
            return Assignment()
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
        return self.plans.find(plan_id) if plan_id else None

    def is_advancing(self, plan: Plan) -> bool:
        return plan.state == PlanState.STARTED and not self.orchestrator.delegates_work() and not self.testing.unpassed(plan)

    def passes_checkpoints(self) -> bool:
        return bool(self.settings.option(TasksOptions.AUTO))

    def following_task(self, plan: Plan) -> Task | None:
        if not self.passes_checkpoints() and self.plans.checkpoint_plans(plan) is not None:
            return None
        return self.plans.following_task(plan)
