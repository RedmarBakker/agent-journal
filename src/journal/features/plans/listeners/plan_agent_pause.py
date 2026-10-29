from journal.events.listener import Listener
from journal.events.rows.plan_postponed import PlanPostponed
from journal.features.plans.support.plan_agents import PlanAgents


class PlanAgentPause(Listener[PlanPostponed]):
    """A plan paused stops its Plan agent; its environment, agent row and link stay for its next start."""

    def __init__(self, agents: PlanAgents) -> None:
        self.agents = agents

    def handle(self, event: PlanPostponed) -> None:
        self.agents.stopped(event.plan_id)
