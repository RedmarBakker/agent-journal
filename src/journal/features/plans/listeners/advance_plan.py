from journal.events.listener import Listener
from journal.events.rows.task_closed import TaskClosed
from journal.features.estimates.support.work_in_progress import WorkInProgress
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.tasks import WORKERS, Tasks
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class AdvancePlan(Listener[TaskClosed]):
    """A plan is done when its last task closes; solo plan tasks may start their next task here, while organization tasks stay open for the Plan seat's handoff."""

    def __init__(self, plans: Plans, tasks: Tasks, agents: Agents, assigner: PlanTaskAssigner,
                 time_source: TimeSource, flow: WorkInProgress) -> None:
        self.time_source = time_source
        self.plans, self.tasks, self.agents, self.assigner, self.flow = plans, tasks, agents, assigner, flow

    def handle(self, event: TaskClosed) -> None:
        task = self.tasks.find(event.task_id)
        if not task.is_closed():
            return
        time, actor = self.time_source.moment(), Actor.parse(event.actor)
        for plan in self.plans.finished_plans(task):
            self.plans.save(plan.finished(time.timestamp()), actor)
        if self.is_agent_close(task):
            return
        for plan in self.plans.started_plans(task):
            with self.tasks.writing():
                following, holder = self.assigner.following_task(plan), self.next_holder(task)
                if following is not None and not self.flow.block_reason(following) and self.is_advancing(plan, holder):
                    self.tasks.holder_started(following.plan_started(time, plan.row_id), holder, actor)

    def is_agent_close(self, task: Task) -> bool:
        holder = self.tasks.holder(task)
        return holder is not None and holder.type != WORKERS

    def next_holder(self, task: Task) -> Ref | None:
        holder = self.tasks.holder(task)
        if holder is not None and holder.type != WORKERS:
            return holder
        present = self.agents.current()
        return None if present is None else Ref.build(present)

    def is_advancing(self, plan: Plan, holder: Ref | None) -> bool:
        return not self.assigner.advancement_block(plan) and (holder is None or self.tasks.holder_task(holder) is None)
