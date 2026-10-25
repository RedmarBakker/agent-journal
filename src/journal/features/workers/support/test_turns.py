import os
import threading
import time
from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.shell_request import ShellRequest
from journal.features.shell.support.shell_runner import EXIT, ShellRunner
from journal.features.workers.support.test_run_result import TestRunResult
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.workers_options import WorkersOptions
from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.models.worker import Worker
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.test_turns import TestTurns as TurnRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller
from journal.support.rejection import Rejection

POLL_SECONDS = 0.2
LAST_LINES = 10


class TestTurns:
    """The test budget: a worker's turn to run tests is a row, started through the shell runner in the worker's own worktree as soon as fewer runs go than the budget allows and it is first of those that wait, else it waits in order; one that would wait when the waiting cap is full is refused. A run past the time limit is stopped and reported to its worker as timed out; a worker that ends takes out its turns, waiting or running; turns waiting at a restart start again in order. Its result is what the project's reader for the command picks, and the turn ends when the run does, or, for a run moved to the background, when its output ends; either way how the run ended is kept on its worker, its failed runs in a row counted and a passed one ending the count."""

    __test__ = False

    def __init__(self, turns: TurnRows, runner: ShellRunner, branch: WorkerBranch, readers: Readers, settings: SettingRows, outputs: CommandOutputs, scope: Scope, workers: Workers, environments: Environments) -> None:
        self.turns, self.runner, self.branch, self.readers, self.settings, self.outputs = turns, runner, branch, readers, settings, outputs
        self.scope, self.workers, self.environments = scope, workers, environments
        self.lock = threading.Lock()
        self.timed_out: set[int] = set()

    def take(self, worker: Worker, ids: str, caller: Caller) -> str:
        if worker.pool_request:
            raise Rejection(f"worker {worker.id}, {worker.name}, runs on another machine of the team: its tests run there, not through a turn here")
        folder = str(self.branch.folder(worker))
        turn = self.asked(worker, ids, f"{self.command(folder)} {ids}", folder)
        if not self.waited(turn):
            return "your turn was taken back: nothing ran"
        text = self.ran(turn, caller, worker.environment_id)
        return self.result(turn, text)

    def asked(self, worker: Worker, ids: str, command: str, folder: str) -> TestTurn:
        with self.lock:
            waiting, cap = self.turns.waiting(), self.waiting_cap()
            if any(turn.worker == worker.id for turn in [*waiting, *self.running()]):
                raise Rejection(f"worker {worker.id}, {worker.name}, has a turn open already: ask for the next once its result is back")
            if (waiting or len(self.running()) >= self.budget()) and cap is not None and len(waiting) >= cap:
                raise Rejection(f"{len(waiting)} turns already wait for a test run: ask again once one has run")
            return self.turns.save(TestTurn(environment_id=worker.environment_id, worker=worker.id, ids=ids, command=command, folder=folder), Actor.worker(worker.id))

    def waited(self, turn: TestTurn) -> bool:
        while True:
            with self.lock:
                if self.turns.find(turn.id).state != TestTurnState.WAITING:
                    return False
                running = self.running()
                free = [row for row in self.turns.waiting() if row.folder not in {going.folder for going in running}]
                if free and free[0].id == turn.id and len(running) < self.budget():
                    self.turns.save(self.turns.find(turn.id).started(), Actor.system())
                    return True
            time.sleep(POLL_SECONDS)

    def ran(self, turn: TestTurn, caller: Caller, environment: int) -> str:
        started = time.time()
        limit = threading.Timer(self.limit_seconds(), self.stopped, (turn, started))
        limit.start()
        try:
            text = b"".join(self.runner.run(ShellRequest(line=turn.command, cwd=turn.folder, shell="bash", environment=dict(os.environ)), caller, environment)).decode(errors="replace")
        except Exception:
            limit.cancel()
            self.turns.save(self.turns.find(turn.id).ended(), Actor.system())
            raise
        output = self.run_output(turn, started)
        later = self.turns.find(turn.id)
        if output is not None and not output.ended:
            self.turns.save(later.backgrounded(output.row_id), Actor.system())
            return text
        limit.cancel()
        self.turns.save(later.ended(), Actor.system())
        self.recorded(later, TestRunResult.printed(text, self.readers.reading(turn.command)))
        return text

    def recorded(self, turn: TestTurn, result: TestRunResult) -> None:
        worker = self.workers.find(turn.worker)
        self.workers.save(worker.passed_run() if result.is_passed() else worker.failed_run(result.failed, time.time()), Actor.system())

    def run_output(self, turn: TestTurn, started: float):
        return next((row for row in self.outputs.ran_in(turn.folder) if row.creation_time.timestamp() >= started), None)

    def stopped(self, turn: TestTurn, started: float) -> None:
        with self.scope.environment(turn.environment_id):
            output = self.run_output(turn, started)
            if output is None or output.ended:
                return
            self.timed_out.add(turn.id)
            OutputFiles(Path(output.folder)).stop(f"journal: this test run was stopped after {self.limit_seconds() / 60:g} minutes, the test budget's time limit")

    def release(self, worker: int) -> None:
        for turn in [turn for turn in [*self.turns.waiting(), *self.turns.running()] if turn.worker == worker]:
            self.turns.save(turn.ended(), Actor.system())
            if turn.state == TestTurnState.RUNNING:
                with self.scope.environment(turn.environment_id):
                    output = next(iter(self.outputs.ran_in(turn.folder)), None)
                    if output is not None and not output.ended:
                        OutputFiles(Path(output.folder)).stop("journal: this test run was stopped, its worker ended")

    def holders(self) -> list[int]:
        return sorted({turn.worker for turn in [*self.turns.waiting(), *self.turns.running()]})

    def resume(self) -> list[threading.Thread]:
        for turn in self.turns.running():
            if turn.output == 0:
                self.turns.save(turn.ended(), Actor.system())
        threads = [threading.Thread(target=self.resumed, args=(turn,), daemon=True, name="test-turn") for turn in self.turns.waiting()]
        for thread in threads:
            thread.start()
        return threads

    def resumed(self, turn: TestTurn) -> None:
        with self.scope.environment(turn.environment_id):
            worker = self.workers.find(turn.worker)
            caller = Caller.worker(self.environments.find(turn.environment_id).name, worker.id, worker.session, worker.provider)
            if self.waited(turn):
                self.ran(turn, caller, turn.environment_id)

    def running(self) -> list[TestTurn]:
        return [turn for turn in self.turns.running() if turn.output == 0 or not self.outputs.find(turn.output).ended]

    def result(self, turn: TestTurn, text: str) -> str:
        lines = [line for line in text.splitlines() if not line.startswith(EXIT)]
        reader = self.readers.reading(turn.command)
        picked = reader.card_lines(lines) if reader is not None else []
        timed = [f"timed out: the run was stopped after {self.limit_seconds() / 60:g} minutes, the test budget's time limit"] if turn.id in self.timed_out else []
        return "\n".join([*(picked or lines[-LAST_LINES:]), *timed])

    def command(self, folder: str) -> str:
        set = str(self.settings.option(WorkersOptions.TEST_COMMAND)).strip()
        if set:
            return set
        if (Path(folder) / "tests").is_dir():
            return "pytest -q"
        raise Rejection(f"this project has no test command: set {WorkersOptions.TEST_COMMAND.key}")

    def budget(self) -> int:
        return self.settings.integer(WorkersOptions.TEST_RUNS)

    def limit_seconds(self) -> float:
        return self.settings.decimal(WorkersOptions.TEST_RUN_MINUTES) * 60

    def waiting_cap(self) -> int | None:
        value = str(self.settings.option(WorkersOptions.TEST_WAITING)).strip()
        return int(value) if value else None
