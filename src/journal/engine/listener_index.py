from typing import Callable

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct


class ListenerIndex:
    """Every state's listeners for every event kind, with each set of conducts folded in, worked out once at boot so no event looks them up on its way."""

    def __init__(self, listeners: dict[tuple[type, tuple[type[Conduct], ...], type], tuple[Callable, ...]]) -> None:
        self.listeners = listeners

    @classmethod
    def built(cls, states: list[type[BaseState]], conduct_sets: list[tuple[type[Conduct], ...]], kinds: list[type]) -> "ListenerIndex":
        listeners = {}
        for state in states:
            for conducts in conduct_sets:
                pairs = state.listeners(conducts)
                listeners.update({(state, conducts, kind): tuple(method for event_kind, method in pairs if issubclass(kind, event_kind)) for kind in kinds})
        return cls(listeners)

    def state_listeners(self, state: type[BaseState], conducts: tuple[type[Conduct], ...], kind: type) -> tuple[Callable, ...]:
        return self.listeners[(state, conducts, kind)]
