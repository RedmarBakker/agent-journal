from dataclasses import dataclass

from journal.engine.base_state import BaseState
from journal.engine.states.ended import Ended
from journal.engine.support.settings import Settings
from journal.engine.support.transition import Transition
from journal.events.agent.tool_starting import ToolStarting
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.events.rows.worker_model_judged import WorkerModelJudged
from journal.features.verification.verification_nudges import VerificationNudges
from journal.engine.no_task_assigner import NoTaskAssigner

VERDICT = "verdict"


@dataclass(frozen=True)
class Verifying(BaseState):
    """A verifier at its one job, which it never leaves: judging a dismissal, or whether a worker's model fit its merged work, on the evidence it was handed. Every tool but its verdict command is refused, file edits among them, it hears no feature's conduct, and its verdict ends its session."""

    name = "verifying"
    assigner = NoTaskAssigner
    title = "Verifying a dismissal"
    conduct_free = True

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return self.none() if event.call.is_journal_noun(VERDICT) else self.refuse(VerificationNudges.VERIFIER_REFUSAL.create())

    def on_reader_report_judged(self, event: ReaderReportJudged, settings: Settings) -> Transition:
        return self.push(Ended()) if event.verifier_session == event.session else self.none()

    def on_worker_model_judged(self, event: WorkerModelJudged, settings: Settings) -> Transition:
        return self.push(Ended()) if event.verifier_session == event.session else self.none()
