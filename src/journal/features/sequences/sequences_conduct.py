from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.rows.row_event import RowEvent
from journal.events.rows.sequence_run_abandoned import SequenceRunAbandoned
from journal.events.rows.sequence_run_cancelled import SequenceRunCancelled
from journal.events.rows.sequence_run_cannot_finish import SequenceRunCannotFinish
from journal.events.rows.sequence_run_paused import SequenceRunPaused
from journal.events.rows.sequence_run_started import SequenceRunStarted
from journal.events.rows.sequence_run_transferred import SequenceRunTransferred
from journal.events.rows.sequence_step_finished import SequenceStepFinished
from journal.events.rows.sequence_step_adopted import SequenceStepAdopted
from journal.events.rows.sequence_step_skipped import SequenceStepSkipped
from journal.features.sequences.states.following_sequence import FollowingSequence


class SequencesConduct(Conduct):
    """The sequences feature's conduct in every state: a sequence started for this agent pushes its state over whatever the agent was doing, a sequence already in hand among them, which the new one then drives until it ends; never over a state that pops on an event of its own, such as a compaction, a wait or the overview after a compaction, which the start path refuses first. A run a new session takes over from the last ended one is pushed the same way, with its step said once. A move of the run in hand made while a wait sits over it, a step followed, finished or skipped, the run paused, abandoned, cancelled or unable to finish, ends the wait and goes down to the sequence state beneath."""

    def on_sequence_run_started(self, event: SequenceRunStarted, settings: Settings) -> Transition:
        return self.push(FollowingSequence(run=event.run)) if event.agent_session == event.session and self.takes_pushes() else self.none()

    def on_sequence_run_transferred(self, event: SequenceRunTransferred, settings: Settings) -> Transition:
        if event.agent_session != event.session or not self.takes_pushes():
            return self.none()
        state = FollowingSequence(run=event.run)
        return self.push(state, state.reminder())

    def on_sequence_step_adopted(self, event: SequenceStepAdopted, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_step_finished(self, event: SequenceStepFinished, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_step_skipped(self, event: SequenceStepSkipped, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_run_paused(self, event: SequenceRunPaused, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_run_abandoned(self, event: SequenceRunAbandoned, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_run_cancelled(self, event: SequenceRunCancelled, settings: Settings) -> Transition:
        return wait_handover(self, event)

    def on_sequence_run_cannot_finish(self, event: SequenceRunCannotFinish, settings: Settings) -> Transition:
        return wait_handover(self, event)


def wait_handover(state: Conduct, event: RowEvent) -> Transition:
    return state.forward() if event.agent_session == event.session and state.is_waiting() else state.none()
