from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.references import events

# the most stops refused in a row counted: enough to reach the count that panics, past the stop being answered
RECENT_TURN_EVENTS = PANIC_REFUSAL_COUNT + 1
STOP = events.STOP


class StopRefusalsReader:
    """Counts the agent's stops refused in a row from its newest turn events: the stop being answered now is not counted, and a tool use, a message of the user's or a stop let through ends the run."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def read(self, agent: Agent) -> int:
        newest = self.entries.turn_events(agent.session, 1)
        answered = newest[0].row_id if newest and newest[0].entry_type == STOP and "refused" not in newest[0].data else 0
        return self.entries.refusal_run_count(agent.session, answered, RECENT_TURN_EVENTS)

