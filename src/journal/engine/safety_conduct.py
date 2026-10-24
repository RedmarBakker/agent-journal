from journal.engine.conduct import Conduct
from journal.engine.states.compacting import Compacting as CompactingState
from journal.engine.states.ended import Ended
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.compacting import Compacting
from journal.events.agent.session_ended import SessionEnded
from journal.events.rows.session_retired import SessionRetired


class SafetyConduct(Conduct):
    """The engine's own conduct in every state, folded in before any feature's: a compaction pushes Compacting, and a session that ends or is retired pushes Ended, unless the state on top is already the end of the session."""

    def on_compacting(self, event: Compacting, settings: Settings) -> Transition:
        return self.push(CompactingState())

    def on_session_ended(self, event: SessionEnded, settings: Settings) -> Transition:
        return self.none() if self.session_over else self.push(Ended())

    def on_session_retired(self, event: SessionRetired, settings: Settings) -> Transition:
        return self.push(Ended()) if event.agent_session == event.session and not self.session_over else self.none()
