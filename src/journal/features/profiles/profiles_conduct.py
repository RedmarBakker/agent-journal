from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.support.subagent_dispatch import SubagentDispatch
from journal.features.profiles.profiles_nudges import ProfilesNudges
from journal.features.profiles.profiles_part import ProfilesPart


class ProfilesConduct(Conduct):
    """The profiles feature's conduct in every state: a worker profile writes, so naming it as a subagent is blocked and the worker dispatch is named instead."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        dispatch = event.call.operation
        if not isinstance(dispatch, SubagentDispatch) or dispatch.role not in event.data.part(ProfilesPart).workers:
            return self.none()
        return self.refuse(ProfilesNudges.WORKER_PROFILE_MISUSE.create(name=dispatch.role))
