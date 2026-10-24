from journal.events.listener import Listener
from journal.events.rows.reader_report_dismissed import ReaderReportDismissed
from journal.features.verification.support.dismissal_evidence import DismissalEvidence
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.repositories.reader_reports import ReaderReports


class VerifierStart(Listener[ReaderReportDismissed]):
    """A reader report the agent dismissed is judged by a verifier the journal sends itself, handed the evidence, so the agent never chooses, steers or skips its own critic."""

    def __init__(self, reports: ReaderReports, evidence: DismissalEvidence, dispatch: VerifierDispatch) -> None:
        self.reports, self.evidence, self.dispatch = reports, evidence, dispatch

    def handle(self, event: ReaderReportDismissed) -> None:
        report = self.reports.find(event.row_id)
        self.dispatch.sent(report, self.evidence.brief(report))
