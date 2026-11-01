from journal.events.listener import Listener
from journal.events.rows.plan_closed import PlanClosed
from journal.features.plans.support.plan_agents import PlanAgents


class PlanAgentClose(Listener[PlanClosed]):
    """A closed plan ends its Plan agent before the close is answered."""

    def __init__(self, agents: PlanAgents) -> None:
        self.agents = agents

    def handle(self, event: PlanClosed) -> None:
        self.agents.close_agent(event)
