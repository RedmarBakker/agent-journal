from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.features.verification.states.verifying import Verifying


class VerifierConduct(Conduct):
    """A verifier's conduct: at its start it is pushed into Verifying, which it never leaves."""

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.push(Verifying())
