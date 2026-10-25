import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path

from journal.features.shell.support.readers import Readers
from journal.features.shell.support.shell_request import ShellRequest
from journal.features.shell.support.shell_runner import EXIT, ShellRunner
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.workers_options import WorkersOptions
from journal.models.test_turn import TestTurn
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.setting_rows import SettingRows
from journal.repositories.test_turns import TestTurns as TurnRows
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.rejection import Rejection

POLL_SECONDS = 0.2
LAST_LINES = 10


class TestTurns:
    """The test budget: a worker's turn to run tests is a row, started through the shell runner in the worker's own worktree as soon as fewer runs go than the budget allows and it is first of those that wait, else it waits in order; one that would wait when the waiting cap is full is refused. Its result is what the project's reader for the command picks, and the turn ends when the run does, or, for a run moved to the background, when its output ends."""

    __test__ = False

    def __init__(self, turns: TurnRows, runner: ShellRunner, branch: WorkerBranch, readers: Readers, settings: SettingRows, outputs: CommandOutputs) -> None:
        self.turns, self.runner, self.branch, self.readers, self.settings, self.outputs = turns, runner, branch, readers, settings, outputs
        self.lock = threading.Lock()

    def take(self, worker: Worker, ids: str, caller: Caller) -> str:
        if worker.pool_request:
            raise Rejection(f"worker {worker.id}, {worker.name}, runs on another machine of the team: its tests run there, not through a turn here")
        cwd = str(self.branch.folder(worker))
        turn = self.asked(worker, ids, f"pytest -q {ids}")
        self.waited(turn)
        text = self.ran(turn, ShellRequest(line=turn.command, cwd=cwd, shell="bash", environment={}), caller, worker.environment_id)
        return self.result(turn.command, text)

    def asked(self, worker: Worker, ids: str, command: str) -> TestTurn:
        with self.lock:
            waiting, cap = self.turns.waiting(), self.waiting_cap()
            if (waiting or len(self.running()) >= self.budget()) and cap is not None and len(waiting) >= cap:
                raise Rejection(f"{len(waiting)} turns already wait for a test run: ask again once one has run")
            return self.turns.save(TestTurn(environment_id=worker.environment_id, worker=worker.id, ids=ids, command=command), Actor.worker(worker.id))

    def waited(self, turn: TestTurn) -> None:
        while True:
            with self.lock:
                waiting = self.turns.waiting()
                if waiting and waiting[0].id == turn.id and len(self.running()) < self.budget():
                    self.turns.save(self.turns.find(turn.id).started(), Actor.system())
                    return
            time.sleep(POLL_SECONDS)

    def ran(self, turn: TestTurn, request: ShellRequest, caller: Caller, environment: int) -> str:
        started = time.time()
        try:
            text = b"".join(self.runner.run(request, caller, environment)).decode(errors="replace")
        except Exception:
            self.turns.save(self.turns.find(turn.id).ended(), Actor.system())
            raise
        output = next((row for row in self.outputs.ran_in(request.cwd) if row.creation_time.timestamp() >= started), None)
        later = self.turns.find(turn.id)
        self.turns.save(later.backgrounded(output.row_id) if output is not None and not output.ended else later.ended(), Actor.system())
        return text

    def running(self) -> list[TestTurn]:
        return [turn for turn in self.turns.running() if turn.output == 0 or not self.outputs.find(turn.output).ended]

    def result(self, command: str, text: str) -> str:
        lines = [line for line in text.splitlines() if not line.startswith(EXIT)]
        reader = self.readers.reading(command)
        picked = reader.card_lines(lines) if reader is not None else []
        return "\n".join(picked or lines[-LAST_LINES:])

    def budget(self) -> int:
        return self.settings.integer(WorkersOptions.TEST_RUNS)

    def waiting_cap(self) -> int | None:
        value = str(self.settings.option(WorkersOptions.TEST_WAITING)).strip()
        return int(value) if value else None
