from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.load_meter import LoadMeter
from journal.repositories.agents import Agents


class LoadRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, its load is measured (LoadMeter)."""

    def __init__(self, agents: Agents, meter: LoadMeter) -> None:
        self.agents, self.meter = agents, meter

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        main = self.agents.main_row(event.session)
        if main is not None:
            self.meter.measure(main, event.time)
