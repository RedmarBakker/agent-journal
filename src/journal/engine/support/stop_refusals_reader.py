from journal.engine.safety_conduct import PANIC_REFUSAL_COUNT
from journal.models.agent import Agent
from journal.repositories.entries import Entries

# the newest turn events looked at for stops refused in a row: enough to reach the count that panics, past the stop being answered
RECENT_TURN_EVENTS = PANIC_REFUSAL_COUNT + 1
STOP = "Stop"


class StopRefusalsReader:
    """Counts the agent's stops refused in a row from its newest turn events: the stop being answered now is not counted, and a tool use, a message of the user's or a stop let through ends the run."""

    def __init__(self, entries: Entries) -> None:
        self.entries = entries

    def read(self, agent: Agent) -> int:
        events = self.entries.turn_events(agent.session, RECENT_TURN_EVENTS)
        if events and events[0].kind == STOP and "refused" not in events[0].data:
            events = events[1:]
        refusals = 0
        for entry in events:
            if entry.kind != STOP or "refused" not in entry.data:
                break
            refusals += 1
        return refusals

