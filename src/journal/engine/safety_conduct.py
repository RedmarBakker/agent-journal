from journal.engine.conduct import Conduct
from journal.engine.states.compacting import Compacting as CompactingState
from journal.engine.states.ended import Ended
from journal.engine.states.locked_out import LockedOut
from journal.engine.states.panicking import Panicking
from journal.engine.support.stop_refusals_part import StopRefusalsPart
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.compacting import Compacting
from journal.events.agent.journal_returned import JournalReturned
from journal.events.agent.session_ended import SessionEnded
from journal.events.agent.stop import Stop
from journal.events.rows.session_retired import SessionRetired


# the stops refused in a row, with nothing done between, after which the next stop goes through
PANIC_REFUSAL_COUNT = 5


class SafetyConduct(Conduct):
    """The engine's own conduct in every state, heard even by a state that hears no feature's conduct: a compaction pushes Compacting; a worker's hook answered after its journal stopped answering pushes LockedOut; the session's end or retirement pushes Ended over every state but a final one; a stop held five times in a row with nothing between pushes Panicking."""

    essential = True

    def on_compacting(self, event: Compacting, settings: Settings) -> Transition:
        return self.push(CompactingState())

    def on_journal_returned(self, event: JournalReturned, settings: Settings) -> Transition:
        return self.push(LockedOut(silence_start=event.silence_start, return_time=event.time))

    def on_session_ended(self, event: SessionEnded, settings: Settings) -> Transition:
        return self.none() if self.final else self.push(Ended())

    def on_session_retired(self, event: SessionRetired, settings: Settings) -> Transition:
        return self.push(Ended()) if event.agent_session == event.session and not self.final else self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        return self.push(Panicking()) if event.data.part(StopRefusalsPart) >= PANIC_REFUSAL_COUNT - 1 and not self.conduct_free else self.none()
