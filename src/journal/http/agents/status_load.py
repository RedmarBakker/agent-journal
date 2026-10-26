from dataclasses import dataclass

from journal.http.agents.queue_view import QueueView
from journal.models.agent import Agent


@dataclass(frozen=True)
class StatusLoad:
    """The one load the status bar shows: the work and the messages the agent clears, added as one server's load is, with each part as it stands."""

    rho: float
    work: QueueView | None
    messages: QueueView | None

    @classmethod
    def measured(cls, agent: Agent) -> "StatusLoad | None":
        work, messages = QueueView.measured(agent.work_queue), QueueView.measured(agent.message_queue)
        if work is None and messages is None:
            return None
        return cls(round(sum(part.rho for part in (work, messages) if part), 2), work, messages)
