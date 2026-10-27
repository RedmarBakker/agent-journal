from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from journal.engine.nudge import Nudge

if TYPE_CHECKING:
    from journal.engine.base_state import BaseState
    from journal.events.agent.agent_event import AgentEvent


@dataclass(frozen=True)
class Transition:
    """What a state answered an event with: the state as it is now, a state pushed on top of it, whether it popped itself, the nudges sent, the nudges typed, the nudge that blocks the event, if any, the moves dropped because an earlier answer already moved, whether a pop passes the event on to the state beneath, and an event the machine answers next as it would one that arrived, its answer said to the agent."""

    target: "BaseState"
    pushed: "BaseState | None" = None
    popped: bool = False
    nudges: tuple[Nudge, ...] = ()
    terminal_lines: tuple[Nudge, ...] = ()
    refusal: Nudge | None = None
    extra_refusals: tuple[Nudge, ...] = ()
    dropped: tuple[str, ...] = ()
    handed_down: bool = False
    next_event: "AgentEvent | None" = None

    def typing(self, *keystrokes: Nudge) -> "Transition":
        return replace(self, terminal_lines=keystrokes)

    def has_move(self) -> bool:
        return self.pushed is not None or self.popped

    def move_name(self) -> str:
        return f"push {self.pushed.name}" if self.pushed else "pop"

    @classmethod
    def merged(cls, state: "BaseState", answers: list["Transition"]) -> "Transition":
        moving = [answer for answer in answers if answer.has_move()]
        move = moving[0] if moving else cls(state)
        return cls(
            target=next((answer.target for answer in answers if answer.target is not state), state),
            pushed=move.pushed,
            popped=move.popped,
            nudges=tuple(nudge for answer in answers for nudge in answer.nudges),
            terminal_lines=tuple(nudge for answer in answers for nudge in answer.terminal_lines),
            refusal=next((answer.refusal for answer in answers if answer.refusal), None),
            extra_refusals=tuple(answer.refusal for answer in answers if answer.refusal)[1:],
            dropped=tuple(answer.move_name() for answer in moving[1:]),
            handed_down=move.handed_down,
            next_event=next((answer.next_event for answer in answers if answer.next_event is not None), None),
        )
