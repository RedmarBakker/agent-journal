from datetime import datetime, timezone

from journal.events.listener import Listener
from journal.events.rows.row_resolved import RowResolved
from journal.features.shell.support.reader_judge import TOTAL_MISSING, ReaderJudge
from journal.models.command_output import CommandOutput
from journal.models.support.ref import Ref
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.reader_reports import ReaderReports
from journal.support.actor import Actor


class ReaderJudgement(Listener[RowResolved]):
    """A watched run that ended is judged on what its reader showed, and a report is kept when the reader fell short."""

    def __init__(self, outputs: CommandOutputs, judge: ReaderJudge, reports: ReaderReports) -> None:
        self.outputs, self.judge, self.reports = outputs, judge, reports

    def handle(self, event: RowResolved) -> None:
        ref = Ref.parse(event.ref)
        if ref.type != CommandOutput.table():
            return
        output = self.outputs.find(ref.id)
        report = self.judge.report(output, datetime.fromtimestamp(event.time, timezone.utc)) if output.watch_reader else None
        if report is not None:
            self.reports.save(report, Actor.system())
        if output.watch_reader and self.judge.prints_total(output):
            for demand in self.reports.open_with_finding(output.command, TOTAL_MISSING):
                self.reports.save(demand.cleared(datetime.fromtimestamp(event.time, timezone.utc)), Actor.system())
