from dataclasses import dataclass

from journal.engine.nudge import Nudge
from journal.engine.support.block import Block
from journal.engine.support.stack import Stack


@dataclass(frozen=True)
class MachineAnswer:
    """The stack after the lifecycle hooks ran on a push or a pop: as it is now, the nudges the hooks produced, and the hold when on_push refused the push."""

    stack: Stack
    nudges: tuple[Nudge, ...] = ()
    refusal: Block | None = None
    refused: str = ""
