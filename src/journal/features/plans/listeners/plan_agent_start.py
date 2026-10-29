from journal.events.listener import Listener
from journal.events.rows.plan_started import PlanStarted
from journal.features.plans.support.plan_agents import PlanAgents
from journal.repositories.plans import Plans
from journal.support.actor import Actor


class PlanAgentStart(Listener[PlanStarted]):
    """A plan started, resumed or reopened starts its Plan agent in its own environment while Plan agents are on."""

    def __init__(self, plans: Plans, agents: PlanAgents) -> None:
        self.plans, self.agents = plans, agents

    def handle(self, event: PlanStarted) -> None:
        self.agents.started(self.plans.find(event.plan_id), event.environment_id, Actor.parse(event.actor))
