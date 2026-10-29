from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.fitness_points import FitnessPoints
from journal.repositories.agents import Agents


class FitnessRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, its fitness is kept as a point of its timeline when it changed."""

    def __init__(self, agents: Agents, points: FitnessPoints) -> None:
        self.agents, self.points = agents, points

    def handle(self, event: ToolFinished) -> None:
        rows = self.agents.session_rows(event.session)
        if not rows or not rows[0].is_main():
            return
        self.points.recorded(rows[0], event.time)
