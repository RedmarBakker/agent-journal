from journal.engine.job import Job
from journal.features.faults.support.developer_tally import DeveloperTally


class DeveloperWrite(Job):
    """Every five minutes the developer numbers gathered in memory are written to their rows in one transaction, so neither a request nor a hook waits on them."""

    interval_seconds = 300.0

    def __init__(self, tally: DeveloperTally) -> None:
        self.tally = tally

    def tick(self, time: float) -> None:
        self.tally.write()
