import re
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.readers import Readers
from journal.features.workers.support.test_run_folder import TestRunFolder
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs

LIMIT = 40
# a test a proof names: a test file, with a test of it after ::, or the words after -k
TEST_NAME = re.compile(r"[\w./-]*(?:test_\w+|\w+_test|\w+_run)\.py(?:::\w+)?|(?<=-k )[\w]+")


class FailedRuns:
    """The lines the project's reader picks from the latest failed run of a command in a worker's worktree after the worker's last clock-out, at most forty with one line counting the rest; none when no such run is stored. A run in the worktree is one that ran there or changed into it with a leading cd, and a run of the whole suite there runs every test a proof names."""

    def __init__(self, outputs: CommandOutputs, readers: Readers, branch: WorkerBranch, runs: TestRunFolder) -> None:
        self.outputs, self.readers, self.branch, self.runs = outputs, readers, branch, runs

    def under(self, worker: Worker, reason: str) -> str:
        lines = self.picked(worker)
        return "\n".join([reason, *lines]) if lines else reason

    def picked(self, worker: Worker) -> list[str]:
        clocked_out = worker.delivery_time()
        for output in reversed(self.outputs.ran_within(str(self.branch.folder(worker)))):
            reader = self.readers.reading(output.command)
            if output.creation_time.timestamp() < clocked_out:
                return []
            if reader and output.ended:
                return self.cut(reader.card_lines(OutputFiles(Path(output.folder)).lines())) if output.status else []
        return []

    def unrun(self, worker: Worker, proof: str) -> str:
        clocked_out = worker.delivery_time()
        commands = [output.command for output in self.outputs.ran_within(str(self.branch.folder(worker))) if output.creation_time.timestamp() >= clocked_out]
        if any(self.runs.is_whole_run(command) for command in commands):
            return ""
        missing = next((test for test in TEST_NAME.findall(proof) if not any(test.split("::")[0] in command for command in commands)), "")
        return f"no run of {missing} is recorded since worker {worker.id} clocked out: run it before you trust the point" if missing else ""

    @staticmethod
    def cut(lines: list[str]) -> list[str]:
        return lines if len(lines) <= LIMIT else [*lines[:LIMIT], f"and {len(lines) - LIMIT} more lines"]
