import shlex
import subprocess

from journal.features.workers.support.test_selection import TestSelection
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.workers_options import WorkersOptions
from journal.models.worker import Worker
from journal.repositories.setting_rows import SettingRows
from journal.support.rejection import Rejection

AFFECTED_SECONDS = 60


class AffectedTests:
    """The tests that cover what a worker changed, as the project's own command finds them: the command set in workers.affected_tests_command is handed the worker's changed files in its worktree and prints one test argument a line; none set, none found."""

    def __init__(self, settings: SettingRows, branch: WorkerBranch) -> None:
        self.settings, self.branch = settings, branch

    def selection(self, worker: Worker) -> TestSelection:
        command = str(self.settings.option(WorkersOptions.AFFECTED_TESTS_COMMAND)).strip()
        if not command:
            return TestSelection(())
        run = subprocess.run([*shlex.split(command), *(self.branch.touched(worker) or ())], cwd=self.branch.folder(worker), capture_output=True, text=True, timeout=AFFECTED_SECONDS)
        if run.returncode != 0:
            raise Rejection(f"{command}, which finds the tests your changes touch, failed with code {run.returncode}: {run.stderr.strip()[-400:]}")
        return TestSelection.listed(run.stdout)
