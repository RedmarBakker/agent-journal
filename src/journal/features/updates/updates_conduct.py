from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.ticked import Ticked
from journal.events.rows.launch_carried_over import LaunchCarriedOver
from journal.events.feature_data import FeatureData
from journal.features.updates.updates_nudges import UpdatesNudges
from journal.features.updates.updates_part import UpdatesPart


class UpdatesConduct(Conduct):
    """The updates feature's conduct in every state: while release messages wait unread, the agent is pointed at them once per session, at its session start or a tick; a launch a newer journal server carried over is told so in one line at its next hook."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.none(*release_lines(event.data))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return self.none(*release_lines(event.data))

    def on_launch_carried_over(self, event: LaunchCarriedOver, settings: Settings) -> Transition:
        return self.none(UpdatesNudges.LAUNCH_CARRIED_OVER.create(version=event.version, previous=event.previous))


def release_lines(data: FeatureData) -> list[Nudge]:
    notes = data.part(UpdatesPart)
    return [UpdatesNudges.RELEASE_MESSAGES.create(count=notes.unread_count)] if notes.unread_count and not notes.is_announced else []
