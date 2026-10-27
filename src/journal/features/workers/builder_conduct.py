from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.features.workers.workers_conduct import HANDOVERS
from journal.features.workers.workers_nudges import WorkersNudges
from journal.features.workers.workers_options import WorkersOptions
from journal.support.subagent_dispatch import SubagentDispatch

BUILDER = "builder"


class BuilderConduct(Conduct):
    """The builder's conduct, brought by its mode state to every state above it: a subagent's dispatch, a worker's dispatch or a queued task is refused when the user has not allowed the builder that."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        if isinstance(event.call.operation, SubagentDispatch):
            return self.none() if settings.value(WorkersOptions.BUILDER_SUBAGENTS_ALLOWED) else self.refuse(WorkersNudges.MODE_REFUSAL.create(mode=BUILDER, act="send subagents"))
        refused = [act for part in event.call.parts for command, (act, option) in HANDOVERS.items() if part.text.startswith(command) and not settings.value(option)]
        return self.refuse(WorkersNudges.MODE_REFUSAL.create(mode=BUILDER, act=refused[0])) if refused else self.none()
