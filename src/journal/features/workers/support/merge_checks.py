from journal.features.workers.support.merge_check import MergeCheck
from journal.features.workers.support.whole_suite import TEST_COMMANDS
from journal.features.workers.support.whole_suite import WholeSuite
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.workers import Workers

# the newest ended test runs read to find the whole suite's last passing and failing runs, a page at a time until one passed
RECENT_TEST_RUNS = 20
RUN_PAGE_ROWS = 5


class MergeChecks:
    """The merges the whole suite has not passed since, read from the newest ended test runs down to the newest whole run that passed and the workers' last merges; a stop asks only whether a whole run failed since, and reads the merges only then."""

    def __init__(self, outputs: CommandOutputs, workers: Workers) -> None:
        self.outputs, self.workers = outputs, workers

    def check(self) -> MergeCheck:
        return self.checked(self.suite_runs())

    def failure(self) -> MergeCheck:
        runs = self.suite_runs()
        pass_time = self.last_pass_time(runs)
        return self.checked(runs) if any(run.status != 0 and run.update_time.timestamp() > pass_time for run in runs) else MergeCheck()

    def checked(self, runs: list[CommandOutput]) -> MergeCheck:
        merged = tuple(self.workers.recently_merged(self.last_pass_time(runs)))
        failed = next((run.row_id for run in runs if run.status != 0 and merged and run.update_time.timestamp() > merged[0].merged_at), 0)
        return MergeCheck(merged, failed)

    @staticmethod
    def last_pass_time(runs: list[CommandOutput]) -> float:
        return next((run.update_time.timestamp() for run in runs if run.status == 0), 0.0)

    def suite_runs(self) -> list[CommandOutput]:
        runs: list[CommandOutput] = []
        upper_id = 0
        for _ in range(RECENT_TEST_RUNS // RUN_PAGE_ROWS):
            page = self.outputs.ended_run_results(TEST_COMMANDS, RUN_PAGE_ROWS, upper_id)
            runs.extend(run for run in page if WholeSuite.is_run(run.command))
            if len(page) < RUN_PAGE_ROWS or self.last_pass_time(runs):
                return runs
            upper_id = page[-1].row_id
        return runs
