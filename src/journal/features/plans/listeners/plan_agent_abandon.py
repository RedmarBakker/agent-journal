from journal.events.listener import Listener
from journal.events.rows.plan_abandoned import PlanAbandoned
from journal.features.plans.support.plan_agents import PlanAgents


class PlanAgentAbandon(Listener[PlanAbandoned]):
    """A plan abandoned stops its Plan agent; its environment, agent row and link stay for its next start."""

    def __init__(self, agents: PlanAgents) -> None:
        self.agents = agents

    def handle(self, event: PlanAbandoned) -> None:
        self.agents.stopped(event)
