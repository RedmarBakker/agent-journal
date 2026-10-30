from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.readers import Readers
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs

LIMIT_LINES = 40
# a test a proof names: a test file, with a test of it after ::, or the words after -k


class FailedRuns:
    """The lines the project's reader picks from the latest failed run of a command in a worker's worktree after the worker's last clock-out, at most forty with one line counting the rest; none when no such run is stored. A run in the worktree is one that ran there or changed into it with a leading cd, and a run of the whole suite there runs every test a proof names."""

    def __init__(self, outputs: CommandOutputs, readers: Readers, branch: WorkerBranch) -> None:
        self.outputs, self.readers, self.branch = outputs, readers, branch

    def with_output(self, worker: Worker, reason: str) -> str:
        lines = self.picked(worker)
        return "\n".join([reason, *lines]) if lines else reason

    def picked(self, worker: Worker) -> list[str]:
        delivered_at = worker.delivery_time()
        for output in reversed(self.outputs.tree_runs(str(self.branch.folder(worker)))):
            reader = self.readers.reading(output.command)
            if output.creation_time.timestamp() < delivered_at:
                return []
            if reader and output.ended:
                return self.cut(reader.card_lines(OutputFiles(Path(output.folder)).lines())) if output.status else []
        return []

    @staticmethod
    def cut(lines: list[str]) -> list[str]:
        return lines if len(lines) <= LIMIT_LINES else [*lines[:LIMIT_LINES], f"and {len(lines) - LIMIT_LINES} more lines"]
