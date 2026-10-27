from dataclasses import dataclass


@dataclass(frozen=True)
class ReaderReportRate:
    """The reader reports raised on one reader of the project, by the runs it read and its reports per ten of them, its rate."""

    reader: str
    runs: int
    reports: int
    report_rate: float
