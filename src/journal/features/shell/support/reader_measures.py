from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.support.reader_measurement import ReaderMeasurement
from journal.features.shell.support.reader_report_rate import ReaderReportRate
from journal.features.shell.support.readers import Readers
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.entries import Entries
from journal.repositories.reader_reports import ReaderReports

# the number of runs a reader's reports are counted over
REPORT_RUNS = 10


class ReaderMeasures:
    """How well the project's readers read its runs, from the rows the journal keeps: the share of runs moved to the background that a reader of the project read rather than the base one, the reader reports raised per reader per ten of its runs, the reader suggestions that a reader now reads, and the reader suggestions per session that moved a run to the background."""

    def __init__(self, outputs: CommandOutputs, reports: ReaderReports, entries: Entries, readers: Readers) -> None:
        self.outputs, self.reports, self.entries, self.readers = outputs, reports, entries, readers

    def measurement(self) -> ReaderMeasurement:
        runs = self.outputs.reader_run_counts()
        parts = self.entries.environment_values(ShellNudges.READER_DRAFT.key, "part")
        return ReaderMeasurement(sum(runs.values()), sum(runs.values()) - runs.get("", 0), self.report_rates(runs), len(parts), len(self.readers.reading_parts(parts)), self.outputs.run_session_count())

    def report_rates(self, runs: dict[str, int]) -> tuple[ReaderReportRate, ...]:
        reports = self.reports.reader_counts()
        return tuple(ReaderReportRate(reader, count, reports.get(reader, 0), round(REPORT_RUNS * reports.get(reader, 0) / count, 1)) for reader, count in sorted(runs.items()) if reader)
