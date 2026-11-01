from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.support.option import Option


@dataclass(frozen=True)
class StateFloor:
    """A setting whose values select a state at the bottom of the main agent's stack."""

    option: Option
    states: dict[object, type[BaseState]]
