from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.support.subagent_dispatch import SubagentDispatch
from journal.features.laws.laws_nudges import LawsNudges
from journal.features.profiles.profiles_part import ProfilesPart

LARGE_LINES = 400


class LawsConduct(Conduct):
    """The laws feature's conduct in every state: a subagent dispatch must name its model, one of the project's profiles and a concrete job or it is blocked, and a tool result of many lines is flagged, since every line stays in the context permanently."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        dispatch = event.call.operation
        if not isinstance(dispatch, SubagentDispatch):
            return self.none()
        if dispatch.model == "":
            return self.refuse(LawsNudges.MISSING_MODEL.create())
        profiles = event.data.part(ProfilesPart)
        if dispatch.role is not None and dispatch.role not in profiles.names:
            return self.refuse(LawsNudges.MISSING_PROFILE.create(asked=dispatch.role or "none", profiles=", ".join(profiles.subagents)))
        if not dispatch.title or dispatch.brief == "":
            return self.refuse(LawsNudges.UNBOUND_DISPATCH.create())
        return self.none()

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        lines = event.output.count("\n") + 1
        return self.none(LawsNudges.LONG_OUTPUT.create(lines=lines)) if lines >= LARGE_LINES else self.none()
