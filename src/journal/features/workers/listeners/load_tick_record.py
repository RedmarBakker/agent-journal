from journal.support.timeout import Timeout
from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.load_meter import LoadMeter
from journal.models.agent import Agent
from journal.repositories.agents import Agents

STALE_SECONDS = 60


class LoadTickRecord(AgentListener[Ticked]):
    """The main agent's load is measured on the clock, at most once a minute, while it waits without a tool use."""

    def __init__(self, agents: Agents, meter: LoadMeter) -> None:
        self.agents, self.meter = agents, meter

    def handle(self, event: Ticked) -> None:
        rows = self.agents.session_rows(event.session)
        if not rows or not self.is_stale(rows[0], event.time):
            return
        self.meter.measure(rows[0], event.time)

    @staticmethod
    def is_stale(agent: Agent, time: float) -> bool:
        return agent.is_main() and Timeout.seconds(STALE_SECONDS).started(agent.work_queue.measured_at).is_elapsed(time)
