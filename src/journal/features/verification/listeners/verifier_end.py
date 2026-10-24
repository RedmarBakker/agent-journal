from journal.events.listener import Listener
from journal.events.rows.reader_report_judged import ReaderReportJudged
from journal.features.workers.support.worker_actions import WorkerActions
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class VerifierEnd(Listener[ReaderReportJudged]):
    """A verifier's verdict ends its run: its worker is retired and its process stopped, once the verdict is answered."""

    def __init__(self, workers: Workers, actions: WorkerActions) -> None:
        self.workers, self.actions = workers, actions

    def handle(self, event: ReaderReportJudged) -> None:
        for worker in self.workers.session_worker(event.verifier_session):
            self.actions.retired(worker.row_id, f"gave its verdict: {event.reason}", Actor.system())
