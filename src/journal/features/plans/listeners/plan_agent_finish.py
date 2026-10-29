from journal.events.listener import Listener
from journal.events.rows.plan_finished import PlanFinished
from journal.features.plans.support.plan_agents import PlanAgents


class PlanAgentFinish(Listener[PlanFinished]):
    """A plan finished stops its Plan agent; its environment, agent row and link stay for its next start."""

    def __init__(self, agents: PlanAgents) -> None:
        self.agents = agents

    def handle(self, event: PlanFinished) -> None:
        self.agents.stopped(event.plan_id)
