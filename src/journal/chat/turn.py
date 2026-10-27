from journal.models.agent import Agent
from journal.repositories.entries import Entries
from journal.repositories.scope import Scope
from journal.references import events

MOVES = (events.STOP, events.TURN_FAILED, events.SESSION_STARTED, events.PROMPT_SUBMITTED, events.TOOL_STARTING, events.TOOL_FINISHED)
TURN_ENDS = (events.STOP, events.TURN_FAILED, events.SESSION_STARTED)
TOOL_MOVES = (events.TOOL_STARTING, events.TOOL_FINISHED)


class Turn:
    """Where an agent is in its turn, read from its latest move: between turns after a stop, a failed turn or a start, or none at all; using tools after a tool started or finished."""

    def __init__(self, entries: Entries, scope: Scope) -> None:
        self.entries, self.scope = entries, scope

    def is_finished(self, agent: Agent) -> bool:
        with self.scope.environment(agent.environment_id):
            moves = self.entries.session_moves(MOVES, agent.session)
        return not moves or moves[0].entry_type in TURN_ENDS

    def is_using_tools(self, agent: Agent) -> bool:
        with self.scope.environment(agent.environment_id):
            moves = self.entries.session_moves(MOVES, agent.session)
        return bool(moves) and moves[0].entry_type in TOOL_MOVES
