from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class SequenceRunEvent(RowEvent):
    """A change of a sequence run, naming the session of the agent the run is with, which alone answers it."""

    feature_name = "sequences"

    agent_session: str

    def is_agents_own(self) -> bool:
        return self.agent_session == self.session
