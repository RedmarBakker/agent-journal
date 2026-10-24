from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.features.hydration.hydration_nudges import HydrationNudges
from journal.features.hydration.hydration_part import HydrationPart


class HydrationConduct(Conduct):
    """The hydration feature's conduct in every state: the first session in an environment whose chat was filled from an earlier conversation is asked to read that chat and record what it holds."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        hydrated = event.data.part(HydrationPart)
        if not hydrated.session:
            return self.none()
        return self.none(HydrationNudges.READ_CHAT.create(session=hydrated.session[:8]))
