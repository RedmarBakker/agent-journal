from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart
from journal.features.plans.support.plan_task_assigner import PlanTaskAssigner
from journal.features.tasks.support.default_task_assigner import DefaultTaskAssigner
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks


class PlanStartTaskAssigner:
    """The task assigner the builder's and the solo agent's floor names: the default one's rules, with, between the agent's own paused task and a free task, the next task of the started plan the closed task was in, else the oldest approved plan started, its first task put in the agent's hand."""

    def __init__(self, default: DefaultTaskAssigner, start: ApprovedPlanStart, plan_assigner: PlanTaskAssigner, tasks: Tasks) -> None:
        self.default, self.start, self.plan_assigner, self.tasks = default, start, plan_assigner, tasks

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent, quantity: int = 1) -> Assignment:
        if not self.default.is_free_moment(agent, event):
            return Assignment()
        paused = self.default.paused_task(agent)
        if paused is not None:
            return self.default.with_following(self.default.started(agent, paused), quantity)
        plan_task = self.plan_assigner.next_plan_task(agent, event, quantity)
        if plan_task.has_task():
            return plan_task
        plan = self.start.started(agent)
        if plan is not None:
            return self.plan_assignment(agent, plan)
        return self.default.with_following(self.default.started(agent, self.default.unheld_task(agent, event)), quantity)

    def plan_assignment(self, agent: Agent, plan: Plan) -> Assignment:
        task = self.tasks.holder_task(Ref.build(agent))
        return Assignment(task.row_id, task.title, f"the first task of plan {plan.id}") if task is not None else Assignment()
