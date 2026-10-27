from dataclasses import dataclass

from journal.features.shell.support.reader_report_rate import ReaderReportRate


@dataclass(frozen=True)
class ReaderMeasurement:
    """How well the project's readers read its runs: the runs moved to the background and those a project reader read, the report rate of each reader, the reader suggestions said and those a reader now reads, and the sessions that moved a run to the background."""

    background_runs: int
    reader_runs: int
    readers: tuple[ReaderReportRate, ...]
    suggestions: int
    followed_suggestions: int
    sessions: int
