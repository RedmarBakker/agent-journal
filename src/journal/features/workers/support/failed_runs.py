from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.readers import Readers
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs

LIMIT = 40
CLOCKED_OUT = "clocked out"


class FailedRuns:
    """The lines the project's reader picks from the latest failed run of a command in a worker's worktree after the worker's last clock-out, at most forty with one line counting the rest; none when no such run is stored."""

    def __init__(self, outputs: CommandOutputs, readers: Readers, branch: WorkerBranch) -> None:
        self.outputs, self.readers, self.branch = outputs, readers, branch

    def under(self, worker: Worker, reason: str) -> str:
        lines = self.picked(worker)
        return "\n".join([reason, *lines]) if lines else reason

    def picked(self, worker: Worker) -> list[str]:
        clocked_out = max((time for word, time in worker.moves.steps if word == CLOCKED_OUT), default=0.0)
        for output in self.outputs.ran_in(str(self.branch.folder(worker))):
            reader = self.readers.reading(output.command)
            if output.creation_time.timestamp() < clocked_out:
                return []
            if reader and output.ended:
                return self.cut(reader.card_lines(OutputFiles(Path(output.folder)).lines())) if output.status else []
        return []

    @staticmethod
    def cut(lines: list[str]) -> list[str]:
        return lines if len(lines) <= LIMIT else [*lines[:LIMIT], f"and {len(lines) - LIMIT} more lines"]
