from dataclasses import dataclass, field, replace

from journal.engine.base_state import BaseState
from journal.engine.nudge import Nudge
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.session_started import SessionStarted
from journal.events.agent.stop import Stop
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_starting import ToolStarting
from journal.events.feature_data import FeatureData
from journal.events.rows.sequence_run_abandoned import SequenceRunAbandoned
from journal.events.rows.sequence_run_cancelled import SequenceRunCancelled
from journal.events.rows.sequence_run_cannot_finish import SequenceRunCannotFinish
from journal.events.rows.sequence_run_paused import SequenceRunPaused
from journal.events.rows.sequence_step_finished import SequenceStepFinished
from journal.events.rows.sequence_step_adopted import SequenceStepAdopted
from journal.events.rows.sequence_step_skipped import SequenceStepSkipped
from journal.events.rows.plan_readied import PlanReadied
from journal.events.rows.plan_reviewed import PlanReviewed
from journal.events.rows.row_event import RowEvent
from journal.features.sequences.sequences_nudges import SequencesNudges
from journal.features.sequences.sequences_options import SequencesOptions
from journal.features.sequences.sequences_part import SequencesPart
from journal.features.sequences.support.stacked_runs import FOLLOWING_SEQUENCE
from journal.features.sequences.support.step_calls import StepCalls
from journal.support.sequence_run import SequenceRun
from journal.support.timeout import Timeout

# the moments a step may name as ending it by itself
PLAN_REVIEWED = "plan.reviewed"
PLAN_READIED = "plan.readied"
# how long an agent stays quiet before a step it has not heard for a while is typed to it again
SILENCE_SECONDS = 60.0


@dataclass(frozen=True)
class FollowingSequence(BaseState):
    """A sequence in hand, pushed over the work when it starts and popped when it ends, is abandoned or cannot finish; one started inside another is pushed over it, and the one beneath says its step again when it is on top once more. While it is on top a write or a run of anything but reading and journal commands waits until its step is taken up, and a step whose file edits wait refuses every write but the commands it lets through; reads and journal commands always go through. A stop with the step open is refused with the step, unless it was sent since the agent last used a tool; a quiet agent is typed the step again; nothing while the run is paused, a question to the user is open or the agent still has a duty to the journal."""

    name = FOLLOWING_SEQUENCE
    title = "Following a sequence"
    run: SequenceRun = field(default_factory=lambda: SequenceRun(0, "", ()))

    @classmethod
    def restored(cls, data: dict) -> "FollowingSequence":
        return cls(run=SequenceRun.build(data.get("run", {})))

    def serialized(self) -> dict:
        return {"run": self.run.as_dict()}

    def state_text(self) -> str:
        return f"{self.name}(sequence {self.run.sequence_id}, step {self.run.step + 1})"

    def on_resume(self, data: FeatureData, settings: Settings) -> tuple[Nudge, ...]:
        return (self.reminder(),)

    def is_mine(self, event: RowEvent) -> bool:
        return event.agent_session == event.session

    def on_sequence_step_adopted(self, event: SequenceStepAdopted, settings: Settings) -> Transition:
        return self.swap(replace(self, run=self.run.adopted(event.time_text()).announced(event.time_text()).paused(""))) if self.is_mine(event) else self.none()

    def on_sequence_step_finished(self, event: SequenceStepFinished, settings: Settings) -> Transition:
        if not self.is_mine(event):
            return self.none()
        if self.run.last:
            return self.pop()
        return self.swap(replace(self, run=self.run.advanced().announced(event.time_text())))

    def on_sequence_step_skipped(self, event: SequenceStepSkipped, settings: Settings) -> Transition:
        if not self.is_mine(event):
            return self.none()
        skipped = SequencesNudges.STEP_OMISSION.create(n=self.run.sequence_id, step=self.run.step + 1)
        if self.run.last:
            return self.pop().typing(skipped, SequencesNudges.SEQUENCE_ENDED.create(n=self.run.sequence_id))
        moved = replace(self, run=self.run.advanced().announced(event.time_text()))
        return self.swap(moved).typing(skipped, moved.step_line())

    def on_plan_reviewed(self, event: PlanReviewed, settings: Settings) -> Transition:
        return self.moment_answer(PLAN_REVIEWED, f"plans:{event.plan_id}", event.time_text())

    def on_plan_readied(self, event: PlanReadied, settings: Settings) -> Transition:
        return self.moment_answer(PLAN_READIED, f"plans:{event.plan_id}", event.time_text())

    def moment_answer(self, moment: str, subject: str, time: str) -> Transition:
        if self.run.subject != subject or moment not in (self.run.current_step.ending_moment, self.run.steps[-1].ending_moment):
            return self.none()
        if self.run.last or self.run.steps[-1].ending_moment == moment:
            return self.pop(SequencesNudges.SEQUENCE_ENDED.create(n=self.run.sequence_id))
        moved = replace(self, run=self.run.advanced().announced(time))
        return self.swap(moved, moved.step_line())

    def on_sequence_run_paused(self, event: SequenceRunPaused, settings: Settings) -> Transition:
        return self.swap(replace(self, run=self.run.paused(event.reason))) if self.is_mine(event) else self.none()

    def on_sequence_run_abandoned(self, event: SequenceRunAbandoned, settings: Settings) -> Transition:
        return self.pop() if self.is_mine(event) else self.none()

    def on_sequence_run_cancelled(self, event: SequenceRunCancelled, settings: Settings) -> Transition:
        return self.pop().typing(SequencesNudges.SEQUENCE_CANCELLED.create(n=self.run.sequence_id)) if self.is_mine(event) else self.none()

    def on_sequence_run_cannot_finish(self, event: SequenceRunCannotFinish, settings: Settings) -> Transition:
        if not self.is_mine(event) or event.sequence_id != self.run.sequence_id:
            return self.none()
        return self.pop(SequencesNudges.SEQUENCE_CANNOT_FINISH.create(n=self.run.sequence_id, why=event.reason))

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        runs = event.data.part(SequencesPart)
        if self.run.pause_reason or StepCalls.is_step_command(self.run.text, event.call.parts) or runs.obligations_due:
            return self.none()
        if not StepCalls.is_work(event.call):
            return self.none()
        if not self.run.adopted_at:
            return self.refuse(SequencesNudges.STEP_EDIT_BLOCK.create(n=self.run.sequence_id, step=self.run.step + 1, text=self.run.text))
        step = self.run.current_step
        if event.call.writes and not step.file_edits_allowed and not step.allows(event.call.command):
            return self.refuse(SequencesNudges.STEP_EDITS_WAIT.create(n=self.run.sequence_id, step=self.run.step + 1, heading=step.heading(), allowed=StepCalls.allowed_words(step)))
        return self.none()

    def on_stop(self, event: Stop, settings: Settings) -> Transition:
        runs = event.data.part(SequencesPart)
        if self.run.pause_reason or runs.question_open or runs.obligations_due or runs.step_repeated:
            return self.none()
        return self.refuse(self.step_line())

    def on_session_started(self, event: SessionStarted, settings: Settings) -> Transition:
        return self.none(self.reminder())

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        runs = event.data.part(SequencesPart)
        if self.run.pause_reason or runs.question_open or not runs.is_typable or not Timeout.seconds(SILENCE_SECONDS).is_elapsed(event.silence_seconds):
            return self.none()
        if not Timeout.minutes(settings.decimal(SequencesOptions.STEP_REPEAT_INTERVAL)).is_elapsed(runs.step_silence_seconds):
            return self.none()
        return self.none().typing(self.reminder())

    def step_line(self) -> Nudge:
        return SequencesNudges.PENDING_STEP.create(n=self.run.sequence_id, step=self.run.step + 1, text=self.run.text)

    def reminder(self) -> Nudge:
        if self.run.pause_reason:
            return SequencesNudges.SEQUENCE_PAUSED.create(n=self.run.sequence_id, step=self.run.step + 1, why=self.run.pause_reason)
        return self.step_line()
