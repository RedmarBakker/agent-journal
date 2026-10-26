from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.features.plans.support.approved_plan_start import ApprovedPlanStart
from journal.features.tasks.support.default_task_assigner import DefaultTaskAssigner
from journal.models.agent import Agent
from journal.models.plan import Plan
from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks


class PlanStartTaskAssigner:
    """The task assigner the builder's and the solo agent's floor names: the default one's rules, with the oldest approved plan started between the agent's own paused task and a free task, its first task put in the agent's hand."""

    def __init__(self, default: DefaultTaskAssigner, start: ApprovedPlanStart, tasks: Tasks) -> None:
        self.default, self.start, self.tasks = default, start, tasks

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent) -> Assignment:
        if not self.default.is_free_moment(agent, event):
            return Assignment()
        paused = self.default.paused_task(agent)
        if paused is not None:
            return self.default.started(agent, paused)
        plan = self.start.started(agent)
        if plan is not None:
            return self.plan_assignment(agent, plan)
        return self.default.started(agent, self.default.free_task())

    def plan_assignment(self, agent: Agent, plan: Plan) -> Assignment:
        task = self.tasks.holder_task(Ref.build(agent))
        return Assignment(task.row_id, task.title, f"the first task of plan {plan.id}") if task is not None else Assignment()
