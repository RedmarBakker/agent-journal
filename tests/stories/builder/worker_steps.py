from tests.stories.builder.story_agent import StoryAgent
import re
import shlex

from journal.repositories.reviewers import Reviewers
from journal.repositories.verifiers import Verifiers
from journal.support.caller import Caller


class WorkerSteps:
    """What a worker does in a story and how the agent sends one: dispatched on a task of its own, its clock-in, a proof of a point and its clock-out, each run as the worker it is, and a command it only tries, which may be refused."""

    def agent_dispatches_worker(self, agent: StoryAgent, name: str, task: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        return self.created_number("worker")

    def agent_dispatches_worktree_worker(self, agent: StoryAgent, name: str, task: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests' --worktree --no-libraries")
        self.expect_command_passed()
        return self.created_number("worker")

    def agent_dispatches_worker_on_plan(self, agent: StoryAgent, name: str, plan: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --plan {plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        self.expect_command_passed()
        return self.newest("workers")

    def agent_clocks_in(self, agent: StoryAgent) -> None:
        self.agent_runs_cleanly(agent, "clock-in")

    def agent_proves(self, agent: StoryAgent, point: int, proof: str) -> None:
        self.agent_runs_cleanly(agent, f"proof {point} '{proof}'")

    def agent_clocks_out(self, agent: StoryAgent, report: str) -> None:
        self.agent_runs_cleanly(agent, f"clock-out '{report}'")

    def agent_runs_cleanly(self, agent: StoryAgent, line: str) -> None:
        self.agent_runs(agent, line)
        assert self.command.code == 0, f"the {agent.role}'s {line} was refused: {self.command.error or self.command.text}"

def worker_session(worker: int) -> str:
    return f"w{worker}"
