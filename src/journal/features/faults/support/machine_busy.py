import os

from journal.features.faults.support.test_run_files import TestRunFiles


class MachineBusy:
    """Whether the machine is too busy for a missed time limit to count as a fault: its load over the last minute above its cores, or a test suite running."""

    def __init__(self, test_runs: TestRunFiles) -> None:
        self.test_runs = test_runs

    def is_busy(self) -> bool:
        return os.getloadavg()[0] > (os.cpu_count() or 1) or self.test_runs.is_testing()
