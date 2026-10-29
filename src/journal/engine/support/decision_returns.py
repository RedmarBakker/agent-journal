from journal.engine.base_state import BaseState
from journal.engine.support.decision_return import DecisionReturn
from journal.engine.support.queued_return import QueuedReturn
from journal.engine.support.return_kinds import QUEUED, TERMINAL
from journal.engine.support.terminal_return import TerminalReturn


class DecisionReturns:
    """The way a reply goes back, chosen by the floor of the agent's stack."""

    def __init__(self, terminal: TerminalReturn, queued: QueuedReturn) -> None:
        self.returns: dict[str, DecisionReturn] = {TERMINAL: terminal, QUEUED: queued}

    def chosen(self, bottom_state: BaseState) -> DecisionReturn:
        return self.returns[bottom_state.decision_return]
