from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.demand_progress import DemandProgress
from journal.engine.states.demand_block import DemandBlock
from journal.engine.support.demands_part import DemandsPart
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting


class DemandConduct(Conduct):
    """The engine's conduct toward the agent's demands: at each of its tool uses an active demand says its line with the balance of uses left, once past its silence, and one whose span ran out puts the agent into a DemandBlock, refusing the tool in hand when its block scope covers it; a tool the demand exempts passes in silence; a state that holds every tool, as the user's pause, hears no demand, so none is pushed over it to swallow its resume."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if self.blocks_tools():
            return self.none()
        active = [entry for entry in event.data.part(DemandsPart) if entry.is_active() and not entry.exempts(event)]
        expired = next((entry for entry in active if entry.is_expired(settings)), None)
        if expired is not None and self != DemandBlock(key=expired.demand.key):
            return block_transition(self, expired, event, settings)
        return self.none(*(entry.line(settings) for entry in active if entry.has_announcement(settings)))


def block_transition(state: BaseState, expired: DemandProgress, event: ToolStarting, settings: Settings) -> Transition:
    if expired.blocks(event):
        return Transition.merged(state, [state.push(DemandBlock(key=expired.demand.key)), state.refuse(expired.refusal())])
    return state.push(DemandBlock(key=expired.demand.key), expired.line(settings))
