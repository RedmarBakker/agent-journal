from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.fitness_points import FitnessPoints
from journal.features.workers.support.load_meter import LoadMeter
from journal.support.agent_role import AgentRole
from journal.models.agent import Agent
from journal.repositories.agents import Agents

STALE_SECONDS = 60


class LoadTickRecord(AgentListener[Ticked]):
    """The main agent's load is measured on the clock too, at most once a minute, so while it waits with no tool use, on a long test, a question or a worker, its load and the minutes over its level run on, and its fitness is kept as a point when it moved."""

    def __init__(self, agents: Agents, meter: LoadMeter, points: FitnessPoints) -> None:
        self.agents, self.meter, self.points = agents, meter, points

    def handle(self, event: Ticked) -> None:
        rows = self.agents.session_rows(event.session)
        if not rows or not self.is_stale(rows[0], event.time):
            return
        self.meter.measure(rows[0], event.time)
        self.points.recorded(self.agents.session_rows(event.session)[0], event.time)

    @staticmethod
    def is_stale(agent: Agent, time: float) -> bool:
        return agent.role == AgentRole.MAIN and time - agent.work_queue.measured_at >= STALE_SECONDS
