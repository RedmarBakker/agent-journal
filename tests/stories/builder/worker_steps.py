import re
import shlex

from journal.repositories.reviewers import Reviewers
from journal.repositories.verifiers import Verifiers
from journal.support.caller import Caller


class WorkerSteps:
    """What a worker does in a story and how the agent sends one: dispatched on a task of its own, its clock-in, a proof of a point and its clock-out, each run as the worker it is, and a command it only tries, which may be refused."""

    def agent_dispatches_worker(self, name: str, task: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        return self.created_number("worker")

    def agent_dispatches_worktree_worker(self, name: str, task: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests' --worktree --no-libraries")
        self.expect_command_passed()
        return self.created_number("worker")

    def agent_dispatches_worker_on_plan(self, name: str, plan: int) -> int:
        self.agent_runs(f"worker dispatch '{name}' --plan {plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        self.expect_command_passed()
        return self.newest("workers")

    def reviewer_session_starts(self, reviewer: int) -> None:
        stamp = f"reviewer:{reviewer}"
        self.hook_observed("the reviewer session starts", *self.session_posted_hook(self.checker_session(Reviewers, reviewer), self.checker_headers(stamp), "SessionStart", {"source": "startup"}))

    def verifier_session_starts(self, verifier: int) -> None:
        stamp = f"verifier:{verifier}"
        self.hook_observed("the verifier session starts", *self.session_posted_hook(self.checker_session(Verifiers, verifier), self.checker_headers(stamp), "SessionStart", {"source": "startup"}))

    def worker_session_starts(self, worker: int) -> None:
        self.worker_hooked(worker, "worker session starts", "SessionStart", source="startup")

    def worker_clocks_in(self, worker: int) -> None:
        self.worker_runs(worker, "clock-in")

    def worker_proves(self, worker: int, point: int, proof: str) -> None:
        self.worker_runs(worker, f"proof {point} '{proof}'")

    def worker_clocks_out(self, worker: int, report: str) -> None:
        self.worker_runs(worker, f"clock-out '{report}'")

    def worker_runs(self, worker: int, line: str) -> None:
        self.worker_tries(worker, line)
        assert self.command.code == 0, f"the worker's {line} was refused: {self.command.error or self.command.text}"

    def worker_hooked(self, worker: int, action: str, type_name: str, **body) -> None:
        self.hook_observed(action, *self.session_posted_hook(worker_session(worker), {"X-Journal-Actor": f"worker:{worker}"}, type_name, body))

    def worker_tries(self, worker: int, line: str) -> None:
        arguments = shlex.split(line)
        self.record_command(f"worker runs {' '.join(arguments[:2])}", self.app.console().run(arguments, Caller.worker("main", worker, worker_session(worker), self.provider)))


def worker_session(worker: int) -> str:
    return f"w{worker}"
