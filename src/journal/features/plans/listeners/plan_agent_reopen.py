from journal.events.listener import Listener
from journal.events.rows.plan_reopened import PlanReopened
from journal.features.plans.support.plan_agents import PlanAgents


class PlanAgentReopen(Listener[PlanReopened]):
    """A reopened plan starts its existing Plan agent through the plan start path."""

    def __init__(self, agents: PlanAgents) -> None:
        self.agents = agents

    def handle(self, event: PlanReopened) -> None:
        self.agents.started(event)
