from journal.events.agent.ticked import Ticked
from journal.events.agent_listener import AgentListener
from journal.supervisor_link import SupervisorLink


class LineBatchRelease(AgentListener[Ticked]):
    """On the clock, an agent that stopped with lines waiting for it is woken, since no hook of its own comes to carry them."""

    def __init__(self, supervisor: SupervisorLink) -> None:
        self.supervisor = supervisor

    def handle(self, event: Ticked) -> None:
        self.supervisor.release(event.environment_id)
