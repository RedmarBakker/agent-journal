from datetime import datetime, timezone

from journal.events.rows.task_closed import TaskClosed
from journal.events.listener import Listener
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.repositories.plans import Plans
from journal.repositories.tasks import WORKERS, Tasks
from journal.features.plans.support.phase_testing import PhaseTesting
from journal.features.tasks.support.task_offers import TaskOffers
from journal.features.workers.support.orchestrator_mode import OrchestratorMode
from journal.support.time_source import TimeSource


class AdvancePlan(Listener[TaskClosed]):
    """A plan is done when its last task closes, whoever closes it, heard after the closed task's own mark is in the chat. A task an agent held is followed by that agent's plan task assigner; for a task a worker or nobody held, for each started plan it is in, by its plan link, the next task in the plan's order is started by writing its row, a paused one resumed before any other and none while a blocked one waits to be checked, assigned to the agent that had the closed one, or to the main agent when a worker had it or none did; in orchestrator mode, whose open tasks wait for workers, at a checkpoint out of auto mode, at a phase end whose testing commands have not passed since, with no task that can start, or with that agent already on a task, nothing is written, and the state decides what to do."""

    def __init__(self, plans: Plans, tasks: Tasks, agents: Agents, offers: TaskOffers, testing: PhaseTesting, orchestrator: OrchestratorMode, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.orchestrator = orchestrator
        self.plans, self.tasks, self.agents, self.offers, self.testing = plans, tasks, agents, offers, testing

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
            following, holder = self.offers.plan_following(plan), self.next_holder(task)
            if following is not None and self.is_advancing(plan, holder):
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
        return plan.state == PlanState.STARTED and not self.orchestrator.is_set() and not self.testing.unpassed(plan) and (holder is None or self.tasks.holder_task(holder) is None)
