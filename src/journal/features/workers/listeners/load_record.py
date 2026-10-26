from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.load_meter import LoadMeter
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents


class LoadRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, its load is measured (LoadMeter)."""

    def __init__(self, agents: Agents, meter: LoadMeter) -> None:
        self.agents, self.meter = agents, meter

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        rows = self.agents.session_rows(event.session)
        if rows and rows[0].role == AgentRole.MAIN:
            self.meter.measure(rows[0], event.time)
