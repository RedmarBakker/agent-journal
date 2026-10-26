from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.load_meter import LoadMeter
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents

STALE_SECONDS = 60


class LoadTickRecord(AgentListener[Ticked]):
    """The main agent's load is measured on the clock too, at most once a minute, so while it waits with no tool use, on a long test, a question or a worker, its load and the minutes over its level run on."""

    def __init__(self, agents: Agents, meter: LoadMeter) -> None:
        self.agents, self.meter = agents, meter

    def handle(self, event: Ticked) -> None:
        rows = self.agents.session_rows(event.session)
        if rows and rows[0].role == AgentRole.MAIN and event.time - rows[0].load.measured_at >= STALE_SECONDS:
            self.meter.measure(rows[0], event.time)
