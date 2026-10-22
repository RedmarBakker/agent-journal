from dataclasses import dataclass

from journal.engine.nudge import Nudge


@dataclass(frozen=True)
class Block:
    """The nudge that blocks an event or refuses a push: the agent is informed why and nothing moves."""

    nudge: Nudge
