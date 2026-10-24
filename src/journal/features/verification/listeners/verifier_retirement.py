from journal.events.listener import Listener
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.features.verification.support.verifier_runner import VerifierRunner
from journal.repositories.verifiers import Verifiers
from journal.support.actor import Actor


class VerifierRetirement(Listener[ReaderReportJudged]):
    """A verifier's verdict marks it judged and stops its process."""

    def __init__(self, verifiers: Verifiers, runner: VerifierRunner) -> None:
        self.verifiers, self.runner = verifiers, runner

    def handle(self, event: ReaderReportJudged) -> None:
        for verifier in self.verifiers.session_verifier(event.verifier_session):
            self.verifiers.save(verifier.judged(), Actor.system())
            self.runner.stop(verifier)
