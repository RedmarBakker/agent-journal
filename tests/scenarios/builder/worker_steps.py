import re
import shlex

from journal.support.caller import Caller


class WorkerSteps:
    """What a worker does in a story and how the agent sends one: dispatched on a task of its own, its clock-in, a proof of a point and its clock-out, each run as the worker it is, and a command it only tries, which may be refused."""

    def agent_dispatches_worker(self, name: str, task: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        return int(re.search(r"worker (\d+)", self.command.text)[1])

    def worker_clocks_in(self, worker: int) -> None:
        self.worker_runs(worker, "clock-in")

    def worker_proves(self, worker: int, point: int, proof: str) -> None:
        self.worker_runs(worker, f"proof {point} '{proof}'")

    def worker_clocks_out(self, worker: int, report: str) -> None:
        self.worker_runs(worker, f"clock-out '{report}'")

    def worker_runs(self, worker: int, line: str) -> None:
        self.worker_tries(worker, line)
        assert self.command.code == 0, f"the worker's {line} was refused: {self.command.error or self.command.text}"

    def worker_tries(self, worker: int, line: str) -> None:
        words = shlex.split(line)
        self.ran(f"worker runs {' '.join(words[:2])}", self.app.console().run(words, Caller.worker("main", worker, f"w{worker}", self.provider)))
