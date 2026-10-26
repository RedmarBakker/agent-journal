from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.support.demands_part import DemandsPart
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting


@dataclass(frozen=True)
class DemandBlock(BaseState):
    """The agent let a demand's span run out: every tool in the demand's block scope is refused with its refusal and any other tool told its line, until the requirement is met; then it is popped and the tool in hand handed to the state beneath. It holds tools, not the work, so the task assigner beneath it still answers a stop or a close."""

    name = "demand_block"
    assigner = None
    title = "Demand block"
    key: str = ""

    def takes_pushes(self) -> bool:
        return False

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        progress = next((entry for entry in event.data.part(DemandsPart) if entry.demand.key == self.key), None)
        if progress is None or not progress.is_active():
            return self.forward()
        if progress.exempts(event):
            return self.none()
        return self.refuse(progress.refusal()) if progress.blocks(event) else self.none(progress.line(settings))
