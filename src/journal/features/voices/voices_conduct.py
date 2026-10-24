from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.rows.setting_changed import SettingChanged
from journal.features.voices.voices_nudges import VoicesNudges
from journal.features.voices.voices_options import VoicesOptions
from journal.features.voices.voices_part import VoicesPart

STARTS = ("startup", "resume")


class VoicesConduct(Conduct):
    """The voices feature's conduct in every state: how to talk to the user at a start but a resume, whose conversation already holds it, the introduction when the journal started the agent, and the new voice when the user changes it."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return Transition.merged(self, [voices_check(self, event, settings), introduce_check(self, event, settings)])

    def on_setting_changed(self, event: SettingChanged, settings: Settings) -> Transition:
        if event.setting not in {option.key for option in VoicesOptions.VOICE_OPTIONS}:
            return self.none()
        return self.none(VoicesNudges.VOICE_CHANGE.create(voice=event.data.part(VoicesPart).instruction))


def voices_check(state: BaseState, event: SessionStarted, settings: Settings) -> Transition:
    if event.is_resume():
        return state.none()
    return state.none(VoicesNudges.VOICE_INSTRUCTION.create(voice=event.data.part(VoicesPart).instruction))


def introduce_check(state: BaseState, event: SessionStarted, settings: Settings) -> Transition:
    if event.source not in STARTS:
        return state.none()
    return state.none().typing((VoicesNudges.RETURN_GREETING if event.is_resume() else VoicesNudges.INTRODUCE_YOURSELF).create())
