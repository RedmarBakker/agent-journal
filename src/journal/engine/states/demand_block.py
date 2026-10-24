from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.demands_part import DemandsPart
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting


@dataclass(frozen=True)
class DemandBlock(BaseState):
    """The agent let a demand's span run out: every tool in the demand's block scope is refused with its refusal until the requirement is met, and then it is popped."""

    name = "demand_block"
    title = "Demand block"
    key: str = ""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        progress = next((entry for entry in event.data.part(DemandsPart) if entry.demand.key == self.key), None)
        if progress is None or not progress.is_active():
            return self.pop()
        return self.refuse(progress.refusal()) if progress.blocks(event) else self.none()
