from datetime import datetime, timezone
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_judge import ReaderJudge
from journal.models.reader_report import ReaderReport
from journal.repositories.reader_reports import ReaderReports
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue

# the older stored runs a new reader is tried on after it was accepted
OLDER_RUNS = 20
FIX = "write the reader again so it also picks the lines of this older run"


class ReaderBackfill:
    """A reader just accepted is tried in the background on the stored runs older than the ones its add tried at once; a run it misses becomes a report, as any run it reads poorly does."""

    def __init__(self, judge: ReaderJudge, reports: ReaderReports, deferred: ListenerQueue, scope: Scope) -> None:
        self.judge, self.reports, self.deferred, self.scope = judge, reports, deferred, scope

    def queue_trial(self, reader: Reader, tried: int, environment_id: int) -> None:
        self.deferred.add(lambda: self.tried(reader, tried, environment_id))

    def tried(self, reader: Reader, tried: int, environment_id: int) -> None:
        with self.scope.environment(environment_id):
            for run in self.judge.stored_runs(reader)[tried:tried + OLDER_RUNS]:
                misses = self.judge.misses(reader, OutputFiles(Path(run.folder)).lines())
                if misses:
                    self.reports.save(ReaderReport(environment_id=environment_id, reader=reader.name, output=run.id, command=run.command, session=run.session, findings=tuple(misses), fixes=(FIX,) * len(misses)), Actor.system())
