from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.typist import Typist


@dataclass(frozen=True)
class Stack:
    """The agent's states, bottom to top, as the row keeps them; the bottom state is never popped. Replacing an earlier stack whose top was another state, the top leaving is informed it exits and the new top that it enters, with the typist they may switch off or on: only the state on top decides whether lines are typed."""

    states: tuple[BaseState, ...]

    def top(self) -> BaseState:
        return self.states[-1]

    def with_top(self, state: BaseState) -> "Stack":
        return Stack((*self.states[:-1], state))

    def pushed(self, state: BaseState) -> "Stack":
        return Stack((*self.states, state))

    def popped(self) -> "Stack":
        return self if len(self.states) == 1 else Stack(self.states[:-1])

    def serialized(self) -> list[dict]:
        return [{"state": state.name, "data": state.serialized()} for state in self.states]

    def replace(self, previous: "Stack", typist: Typist) -> None:
        if type(previous.top()) is type(self.top()):
            return
        previous.top().on_exit(typist)
        self.top().on_enter(typist)
