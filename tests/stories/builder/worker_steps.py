from tests.stories.builder.story_agent import StoryAgent
import json
import re
import shlex
import time

from journal.features.workers.support.worker_runner import WorkerRunner
from journal.http.controllers.hooks import ACTOR_HEADER, ACTOR_TOKEN_HEADER
from journal.repositories.scope import Scope
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import ACTOR_TOKEN
from journal.repositories.reviewers import Reviewers
from journal.repositories.verifiers import Verifiers
from journal.support.caller import Caller
from tests.stories.builder.step_result import StepResult


class WorkerSteps:
    """What a worker does in a story and how the agent sends one: dispatched on a task of its own, its clock-in, a proof of a point and its clock-out, each run as the worker it is, and a command it only tries, which may be refused."""

    def agent_dispatches_worker(self, agent: StoryAgent, name: str, task: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        return self.created_number("worker")

    def agent_dispatches_worktree_worker(self, agent: StoryAgent, name: str, task: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --profile journal-medior --model sonnet --tests 'Scoped tests' --worktree --no-libraries")
        self.last_step.expect_command_passed()
        return self.created_number("worker")

    def agent_dispatches_worker_on_plan(self, agent: StoryAgent, name: str, plan: int) -> int:
        self.agent_runs(agent, f"worker dispatch '{name}' --plan {plan} --changes 'the files of its tasks' --profile journal-medior --model sonnet --tests 'Scoped tests'")
        self.last_step.expect_command_passed()
        return self.newest("workers")

    def agent_clocks_in(self, agent: StoryAgent) -> StepResult:
        return self.agent_runs_cleanly(agent, "clock-in")

    def agent_starts_role_session(self, agent: StoryAgent) -> StepResult:
        self.settle()
        member = self.organization_role_member(agent)
        seats = self.simulated_seats()
        deadline = time.monotonic() + 5
        with self.app.container.get(Scope).environment(1):
            worker = self.app.container.get(Workers).find(agent.number)
        while (
            (member.target not in seats.sessions or worker.began < worker.job_start_time())
            and time.monotonic() < deadline
        ):
            time.sleep(0.01)
            with self.app.container.get(Scope).environment(1):
                worker = self.app.container.get(Workers).find(agent.number)
        session = str(seats.sessions.get(member.target, {}).get("sessionId", ""))
        assert (
            session and worker.began >= worker.job_start_time()
        ), f"Role worker {worker.id} did not receive its current OpenRig session"
        self.settle()
        self.worker_sessions[agent.number] = session
        environment = seats.member_environment(member.rig, member.pod, member.member)
        journal_environment = environment["JOURNAL_ENV"]
        self.session_environments[session] = journal_environment
        status, answer = self.session_posted_hook(
            session,
            {
                "X-Journal-Env": journal_environment,
                ACTOR_HEADER: f"worker:{agent.number}",
                ACTOR_TOKEN_HEADER: environment[ACTOR_TOKEN],
            },
            "SessionStart", {"source": "startup"},
        )
        return self.hook_observed("worker starts a session", status, answer, journal_environment)

    def role_seat_starts_a_new_session(self, agent: StoryAgent, seat: str) -> StepResult:
        member = self.organization_seat_member(seat)
        environment = self.openrig_organization_seat_environment(seat)
        self.simulated_seats().start_session(member.target, environment)
        session = str(self.simulated_seats().sessions[member.target]["sessionId"])
        self.worker_sessions[agent.number] = session
        journal_environment = environment["JOURNAL_ENV"]
        self.session_environments[session] = journal_environment
        headers = {
            "X-Journal-Env": journal_environment,
            ACTOR_HEADER: f"worker:{agent.number}",
            ACTOR_TOKEN_HEADER: environment[ACTOR_TOKEN],
        }
        status, answer = self.session_posted_hook(session, headers, "SessionStart", {"source": "startup"})
        return self.hook_observed(f"Role seat {seat} starts a new session", status, answer, journal_environment)

    def organization_role_seat_starts_a_session(self, agent: StoryAgent, seat: str) -> StepResult:
        member = self.organization_seat_member(seat)
        environment = self.openrig_organization_seat_environment(seat)
        self.simulated_seats().start_session(member.target, environment)
        session = str(self.simulated_seats().sessions[member.target]["sessionId"])
        journal_environment = environment["JOURNAL_ENV"]
        self.worker_sessions[agent.number] = session
        self.session_environments[session] = journal_environment
        status, answer = self.session_posted_hook(
            session, {"X-Journal-Env": journal_environment}, "SessionStart", {"source": "startup"},
        )
        return self.hook_observed(f"Role seat {seat} starts a session", status, answer, journal_environment)

    def agent_reads_from_organization_role_seat(self, agent: StoryAgent, seat: str, path: str) -> StepResult:
        return self.organization_role_tool(agent, seat, self.tools.read, {"file_path": path})

    def agent_writes_from_organization_role_seat(self, agent: StoryAgent, seat: str, path: str) -> StepResult:
        return self.organization_role_tool(agent, seat, self.tools.write, {"file_path": path, "content": "x"})

    def organization_role_tool(self, agent: StoryAgent, seat: str, tool: str, tool_input: dict) -> StepResult:
        member = self.organization_role_member(agent)
        environment = self.simulated_seats().member_environment(member.rig, member.pod, member.member)
        session = self.session_of(agent)
        journal_environment = environment["JOURNAL_ENV"]
        self.worker_sessions[agent.number] = session
        self.session_environments[session] = journal_environment
        headers = {
            "X-Journal-Env": journal_environment,
            ACTOR_HEADER: f"worker:{agent.number}",
            ACTOR_TOKEN_HEADER: environment[ACTOR_TOKEN],
        }
        status, answer = self.session_posted_hook(
            session, headers, "PreToolUse", {"tool_name": tool, "tool_input": tool_input},
        )
        return self.hook_observed(f"Role seat {seat} uses {tool}", status, answer, journal_environment)

    def agent_proves(self, agent: StoryAgent, point: int, proof: str) -> StepResult:
        return self.agent_runs_cleanly(agent, f"proof {point} '{proof}'")

    def agent_clocks_out(self, agent: StoryAgent, report: str) -> StepResult:
        return self.agent_runs_cleanly(agent, f"clock-out '{report}'")

    def worker_proves_its_point_again(self, agent: StoryAgent, point: int, proof: str) -> StepResult:
        self.agent_resumes_the_session(agent)
        self.agent_clocks_in(agent)
        self.agent_proves(agent, point, proof)
        self.agent_clocks_out(agent, f"point {point} again: {proof}")
        return self.worker_run_ends_with_its_session(agent, proof)

    def worker_run_ends_with_its_session(self, agent: StoryAgent, report: str) -> StepResult:
        self.agent_has_written(agent, report)
        return self.worker_run_ends_printing(agent, json.dumps({"result": report, "session_id": self.session_of(agent)}))

    def worker_run_ends_without_clocking_out(self, agent: StoryAgent) -> StepResult:
        self.agent_has_written(agent, "the worker started its task")
        return self.worker_run_ends_printing(agent, "")

    def worker_run_ends_printing(self, agent: StoryAgent, printed: str) -> StepResult:
        self.settle()
        runner = self.app.container.get(WorkerRunner)
        with self.app.container.get(Scope).environment(1):
            worker = self.app.container.get(Workers).find(agent.number)
            output, _ = runner.outputs(worker)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(printed)
            runner.recorded_end(worker, Actor.system())
        return self.observed(f"the {agent.role}'s run ends", None, None)

    def agent_runs_cleanly(self, agent: StoryAgent, line: str) -> StepResult:
        result = self.agent_runs(agent, line)
        assert result.command.code == 0, f"the {agent.role}'s {line} was refused: {result.command.error or result.command.text}"
        return result

def worker_session(worker: int) -> str:
    return f"w{worker}"
