from journal.events.listener import Listener
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.support.process_check import ProcessCheck
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor


class VerifierRetirement(Listener[ReaderReportJudged]):
    """A verifier's verdict marks it judged; its process is left to end its turn, so the reply to its verdict reaches it, and it is sent its next judgement only once that process has ended."""

    def __init__(self, verifiers: Verifiers, dispatch: VerifierDispatch) -> None:
        self.verifiers, self.dispatch = verifiers, dispatch

    def handle(self, event: ReaderReportJudged) -> None:
        for verifier in self.verifiers.session_checkers(event.verifier_session):
            judged = verifier.judged()
            self.verifiers.save(judged if ProcessCheck.is_running(judged.pid) else judged.exited(), Actor.system())
        self.dispatch.released()
