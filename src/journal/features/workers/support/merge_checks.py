from journal.features.workers.support.merge_check import MergeCheck
from journal.features.workers.support.tool_use_counts import TEST_COMMANDS
from journal.features.workers.support.whole_suite import WholeSuite
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.workers import Workers

# the newest ended test runs read to find the whole suite's last passing and failing runs
RECENT_TEST_RUNS = 20


class MergeChecks:
    """The merges the whole suite has not passed since, read from the newest ended test runs and the workers' last merges."""

    def __init__(self, outputs: CommandOutputs, workers: Workers) -> None:
        self.outputs, self.workers = outputs, workers

    def check(self) -> MergeCheck:
        runs = [run for run in self.outputs.ended_runs(TEST_COMMANDS, RECENT_TEST_RUNS) if WholeSuite.is_run(run.command)]
        passed_at = next((run.update_time.timestamp() for run in runs if run.status == 0), 0.0)
        merged = tuple(self.workers.merged_since(passed_at))
        failed = next((run.row_id for run in runs if run.status != 0 and merged and run.update_time.timestamp() > merged[0].merged_at), 0)
        return MergeCheck(merged, failed)
