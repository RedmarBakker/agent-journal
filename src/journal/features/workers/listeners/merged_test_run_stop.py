from pathlib import Path

from journal.events.listener import Listener
from journal.events.rows.worker_merged import WorkerMerged
from journal.features.shell.support.output_files import OutputFiles
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor


class MergedTestRunStop(Listener[WorkerMerged]):
    """A test run still going in the checkout a worker's merge lands in tests a mix of old and new code: it is stopped and marked invalid, naming the merge, so it counts as neither passed nor failed."""

    def __init__(self, workers: Workers, outputs: CommandOutputs, branch: WorkerBranch, scope: Scope) -> None:
        self.workers, self.outputs, self.branch, self.scope = workers, outputs, branch, scope

    def handle(self, event: WorkerMerged) -> None:
        worker = self.workers.find(event.worker.id)
        checkout = self.branch.checkout(worker)
        reason = f"worker {worker.id}'s merge of task {worker.merged_task}"
        for output in self.outputs.unended_accepted(lambda output: self.is_test_run_in(output, checkout)):
            OutputFiles(Path(output.folder)).stop(f"stopped: the code changed under it, by {reason}")
            with self.scope.environment(output.environment_id):
                self.outputs.save(output.invalidated(reason, event.time), Actor.system())

    @staticmethod
    def is_test_run_in(output: CommandOutput, checkout: Path) -> bool:
        return bool(output.ran_in) and checkout in (Path(output.ran_in), *Path(output.ran_in).parents) and OutputFiles(Path(output.folder)).has_test_run()
