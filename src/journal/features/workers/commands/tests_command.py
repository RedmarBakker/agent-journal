import shlex
from argparse import Namespace
from datetime import datetime, timedelta, timezone

from journal.config import Config
from journal.console.command import WORKER_KINDS, Command
from journal.features.workers.support.machine_load import MachineLoad
from journal.features.workers.support.test_turns import TestTurns
from journal.features.workers.workers_options import WorkersOptions
from journal.models.test_outcome import TestOutcome
from journal.models.test_turn import TestTurn
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.test_turns import TestTurns as TurnRows
from journal.repositories.workers import Workers
from journal.support.caller import Caller
from journal.support.rejection import Rejection

# how far back the counts of passed and failed runs reach
COUNTED_HOURS = 1


class TestsCommand(Command):
    """A worker's turn to run tests within the test budget; the project's test command, set only once a run of it with the arguments of one test passes; the machine's load with the turns going and waiting, for the orchestrator to judge the budget by; and the budget set, written as the Settings page writes it, the next turns following it and runs already going left to end."""

    __test__ = False

    noun = "tests"
    callers = {"turn": WORKER_KINDS}

    def __init__(self, turns: TestTurns, rows: TurnRows, workers: Workers, settings: SettingRows, config: Config, scope: Scope) -> None:
        self.turns, self.rows, self.workers, self.settings, self.config, self.scope = turns, rows, workers, settings, config, scope

    def arguments(self, verbs) -> None:
        self.verb(verbs, "turn", "a worker's turn to run tests within the test budget: they run in your worktree when a run is free, and the result is what the project's reader for the command picks").add_argument("ids", nargs="+", help="the test ids to run")
        command = self.verb(verbs, "command", "set the project's test command, which the journal runs each worker's tests with: it is set only once it passes with the arguments of one test")
        command.add_argument("line", help="the command without the tests, such as journal suite or vendor/bin/phpunit")
        command.add_argument("--proof", required=True, help="the arguments that run one test that passes, such as tests/test_cli.py -k version")
        self.verb(verbs, "load", "the machine's load and free memory, the load beyond what the test runs going explain, the turns going and waiting, and the runs passed and failed in the last hour")
        budget = self.verb(verbs, "budget", "set the test budget: the test runs at once, and the test ids one run may name; the next turns follow it, runs already going end as they are")
        budget.add_argument("runs", type=int, help="the test runs at once")
        budget.add_argument("per_run", type=int, nargs="?", help="the test ids one run may name")

    def turn(self, args: Namespace, caller: Caller) -> int:
        if caller.worker_number is None:
            raise Rejection("only a worker asks for a turn to run tests: the agent that sent it runs them itself")
        print(self.turns.take(self.workers.find(caller.worker_number), shlex.join(args.ids), caller))
        return 0

    def command(self, args: Namespace, caller: Caller) -> int:
        line = args.line.strip()
        code, tail = self.turns.proved(f"{line} {args.proof}", str(self.config.root), caller, self.scope.id)
        if code != 0:
            raise Rejection(f"the test command is not set: {line} {args.proof} failed with code {code}, and a test command is set only once it passes\n{tail}")
        self.settings.set(WorkersOptions.TEST_COMMAND.key, line, caller.actor)
        self.settings.set(WorkersOptions.TEST_COMMAND_PROOF.key, args.proof, caller.actor)
        print(f"test command set: {line}, proved with {args.proof}; each worker's tests now run with it when it clocks out")
        return 0

    def load(self, args: Namespace, caller: Caller) -> int:
        going, waiting = self.rows.running(), self.rows.waiting()
        machine = MachineLoad.read()
        beyond = machine.beyond(len(going))
        marked = f"; {beyond} beyond what {len(going)} test runs going explain" if beyond else ""
        print(f"load {' '.join(map(str, machine.averages))} on {machine.cores} cores, {machine.free_megabytes:,} MB free{marked}")
        names = {worker.row_id: worker.name for worker in self.workers.selected_globally(self.workers.query().filter_listed("id", sorted({turn.worker for turn in [*going, *waiting]})))}
        for state, turns in (("going", going), ("waiting", waiting)):
            for turn in turns:
                print(f"{state}: {self.turn_line(turn, names)}")
        if not going and not waiting:
            print("no turn going or waiting")
        counts = self.rows.outcome_counts(datetime.now(timezone.utc) - timedelta(hours=COUNTED_HOURS))
        print(f"last hour: {counts.get(TestOutcome.PASSED, 0)} passed, {counts.get(TestOutcome.FAILED, 0)} failed")
        return 0

    @staticmethod
    def turn_line(turn: TestTurn, names: dict[int, str]) -> str:
        worker = f"worker {turn.worker}, {names[turn.worker]}" if turn.worker in names else f"worker {turn.worker}"
        return f"turn {turn.id}, {worker}: {turn.ids}"

    def budget(self, args: Namespace, caller: Caller) -> int:
        if args.runs < 1 or (args.per_run is not None and args.per_run < 1):
            raise Rejection("a test budget is at least 1 run at once and 1 test id a run")
        self.settings.set(WorkersOptions.TEST_RUNS.key, args.runs, caller.actor)
        if args.per_run is not None:
            self.settings.set(WorkersOptions.TESTS_PER_RUN.key, args.per_run, caller.actor)
        per_run = self.settings.integer(WorkersOptions.TESTS_PER_RUN)
        print(f"test budget: {args.runs} runs at once, {per_run} test ids a run; the next turns follow it, runs already going end as they are")
        return 0
