from typing import Protocol, runtime_checkable

from journal.engine.base_state import BaseState
from journal.engine.support.modes import Modes
from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.support.agent_role import AgentRole
from journal.support.option import Option
from journal.engine.demand import Demand


@runtime_checkable
class FeatureRegistry(Protocol):
    """What the engine asks of the features without knowing any: the states they add, the work modes they offer, the state each kind of sent agent they add rests on, and whether a line of theirs is switched off."""

    def states(self) -> list[type[BaseState]]: ...

    def demands(self) -> tuple[Demand, ...]: ...

    def modes(self) -> list[Modes]: ...

    def floors(self) -> dict[AgentRole, type[BaseState]]: ...

    def options(self) -> list[Option]: ...

    def conducts(self, role: AgentRole) -> tuple[type[Conduct], ...]: ...

    def roles(self) -> tuple[AgentRole, ...]: ...

    def refused_parts(self, role: AgentRole) -> frozenset[str]: ...

    def receives_row_event(self, feature_name: str, role: AgentRole) -> bool: ...

    def silenced(self, nudge: Nudge) -> bool: ...
