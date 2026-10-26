from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from journal.events.agent.agent_event import AgentEvent

if TYPE_CHECKING:
    from journal.engine.base_state import BaseState


@dataclass(frozen=True)
class HelperAssignment(AgentEvent):
    """The journal gives a helper its job: the state it works in, which Void, the helper's floor, pushes over itself."""

    answers_hook: ClassVar[bool] = False

    state: "BaseState"
