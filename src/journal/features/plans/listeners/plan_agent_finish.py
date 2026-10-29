from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.plans import Plans


class PlanAgentFinish(Listener[PlanFinished]):
    """A plan finished stops its Plan agent; its environment, agent row and link stay for its next start."""

    def __init__(self, plans: Plans, agents: PlanAgents) -> None:
        self.plans, self.agents = plans, agents

    def handle(self, event: PlanFinished) -> None:
        self.agents.stopped(self.plans.find(event.plan_id))
