from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.subagent_dispatch import SubagentDispatch

SOLO = "solo"


class SoloConduct(Conduct):
    """The solo agent's conduct, brought by its mode state to every state above it: a subagent's dispatch is refused when the user has not allowed the solo agent subagents."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if isinstance(event.call.operation, SubagentDispatch) and not settings.value(WorkersOptions.SOLO_SUBAGENTS_ALLOWED):
            return self.refuse(WorkersNudges.MODE_REFUSAL.create(mode=SOLO, act="send subagents"))
        return self.none()
