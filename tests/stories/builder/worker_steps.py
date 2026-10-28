import re
import shlex

from journal.features.workers.support.worker_runner import WorkerRunner
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller


class WorkerSteps:
    """What a worker does in a story and how the agent sends one: dispatched on a task of its own, its clock-in, a proof of a point and its clock-out, each run as the worker it is, and a command it only tries, which may be refused."""

    def agent_dispatches_worker(self, name: str, task: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        return self.created_number("worker")

    def agent_dispatches_worker_on_plan(self, name: str, plan: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --plan {plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        self.expect_command_passed()
        return self.newest("workers")

    def worker_clocks_in(self, worker: int) -> None:
        self.worker_runs(worker, "clock-in")

    def worker_proves(self, worker: int, point: int, proof: str) -> None:
        self.worker_runs(worker, f"proof {point} '{proof}'")

    def worker_clocks_out(self, worker: int, report: str) -> None:
        self.worker_runs(worker, f"clock-out '{report}'")

    def worker_runs(self, worker: int, line: str) -> None:
        self.worker_tries(worker, line)
        assert self.command.code == 0, f"the worker's {line} was refused: {self.command.error or self.command.text}"

    def worker_writes(self, worker: int, path: str) -> None:
        self.worker_hooked(worker, "worker writes", "PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def worker_runs_in_the_shell(self, worker: int, line: str) -> None:
        self.worker_hooked(worker, f"worker runs in the shell {line.split()[0]}", "PreToolUse", tool_name=self.tools.shell, tool_input={"command": line})

    def worker_stops(self, worker: int) -> None:
        self.worker_hooked(worker, "worker stops", "Stop")

    def worker_hooked(self, worker: int, action: str, type_name: str, **body) -> None:
        self.hook_observed(action, *self.session_posted_hook(worker_session(worker), {"X-Journal-Actor": f"worker:{worker}"}, type_name, body))

    def worker_run_ends(self, worker: int) -> None:
        with self.app.container.get(Scope).environment(1):
            self.app.container.get(WorkerRunner).finish(self.app.container.get(Workers).find(worker), 0, Actor.system())
        self.observed("worker's run ends", None, None)

    def worker_tries(self, worker: int, line: str) -> None:
        arguments = shlex.split(line)
        self.record_command(f"worker runs {' '.join(arguments[:2])}", self.app.console().run(arguments, Caller.worker("main", worker, worker_session(worker), self.provider)))


def worker_session(worker: int) -> str:
    return f"w{worker}"
