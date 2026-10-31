from journal.console.support.outcome import Outcome
from journal.support.agent_role import AgentRole
from journal.support.agent_token import AgentToken
from tests.stories.builder.story_agent import StoryAgent
from tests.stories.builder.story_agents import StoryAgents
from journal.support.actor import Actor
from journal.support.listener_queue import ListenerQueue
from journal.features.workers.support.owned_task_line import owned_task_line
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.models.worker_state import WorkerState
import threading
import time
from journal.http.controllers.hooks import ACTOR_HEADER, ACTOR_TOKEN_HEADER
from journal.repositories.reviewers import Reviewers
from journal.repositories.scope import Scope
from journal.repositories.verifiers import Verifiers
from journal.support.caller import ACTOR, ACTOR_TOKEN, AGENT_SHELL, Caller
from journal.support.researcher_session import ResearcherSession
from journal.features.workers.workers_options import BUILDER_MODE
from journal.features.organization.support.seat_runtime import SeatRuntime
from tests.lab.simulated_seats import SimulatedSeats
from tests.in_process import posted
from tests.agent_hooks import TOOLS
from tests.stories.builder.agent_steps import AgentSteps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.developer_steps import DeveloperSteps
from tests.stories.builder.launcher_steps import LauncherSteps
from tests.stories.builder.hook_verdict import HookVerdict
from tests.stories.builder.journal_log import JournalLog
from tests.stories.builder.time_steps import TimeSteps
from tests.stories.builder.main_session import MAIN_SESSION
from tests.stories.builder.worker_steps import WorkerSteps, worker_session
from tests.stories.builder.reviewer_steps import ReviewerSteps
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.step_result import StepResult
from tests.stories.builder.story_checks import StoryChecks
from tests.stories.builder.story_rows import StoryRows
from tests.stories.builder.user_steps import UserSteps
from tests.stories.fixtures.state_fixture import StateFixture


class Story(AgentSteps, UserSteps, LauncherSteps, WorkerSteps, ReviewerSteps, TimeSteps, DeveloperSteps, StoryChecks, StoryRows):
    """One story played against a journal in-process for one provider: each step plays a real hook, command or viewer request and keeps what it brought, the lines the journal gave, the hook's verdict and the command's outcome, for the checks after it, and adds its action and what the journal did to the story's path, which counts from the fixture's state on; the settings it sets are noted with the place they were set, to ask whether the journal read them after, and its fixture is the one it began from, whose rows the story reads by kind, story.tasks.started, and its agents as story.agents, asked at the end whether the story used them all."""

    def __init__(self, app, program: type, reads: SettingReads, copies: FixtureCopies, monkeypatch) -> None:
        self.copies = copies
        self.monkeypatch = monkeypatch
        self.app, self.program, self.provider, self.tools, self.reads = app, program, program.name, TOOLS[program.name], reads
        self.set_positions: dict[str, int] = {}
        self.main_session_id = MAIN_SESSION
        self.session_environments = {MAIN_SESSION: "main"}
        self.agent = Caller.agent("main", MAIN_SESSION, program.name)
        self.log = JournalLog(app)
        self.said, self.verdict, self.command = (), None, None
        self.path: list[str] = []
        self.line_keys: set[str] = set()
        self.fixture = StateFixture()
        self.scope = AgentRole.MAIN
        self.stack_checked_at = -1
        self.shell_text, self.shell_exit, self.shell_outputs = "", 0, 0
        self.background_heartbeats = set()
        self.viewer_status, self.viewer_answer = 0, {}
        self.closers: list = []
        self.team_addresses: dict[str, str] = {}
        self.worker_sessions: dict[int, str] = {}
        self.openrig: SimulatedSeats | None = None
        self.typed: list[str] = []
        self.typed_from = 0
        self.mode = BUILDER_MODE
        self.last_step = StepResult(self, (), None, None, "", 0, 0, {})

    def reach(self, fixture: type[StateFixture]) -> None:
        self.fixture = self.copies.reached(self, fixture)
        self.observed("", None, None)
        self.path = [f"starts from {fixture.__name__}"]
        self.typed_from = len(self.typed)
        self.stack_checked_at = -1
        self.set_positions = {key: self.reads.position() for key in self.copies.settings_left.get((fixture, self.provider), ())}

    @property
    def agents(self) -> StoryAgents:
        return StoryAgents(self.scope, self.fixture)

    def posted_hook(self, agent: StoryAgent, type_name: str, **body) -> tuple[int, object]:
        return self.session_posted_hook(self.hook_session_of(agent), self.headers_of(agent), type_name, {**self.hook_fields_of(agent), **body})

    def session_posted_hook(self, session: str, headers: dict, type_name: str, body: dict) -> tuple[int, object]:
        environment = self.session_environments.get(session, "main")
        return posted(
            self.app,
            f"/hooks/{self.provider}",
            {"hook_event_name": type_name, "session_id": session, **body},
            {"X-Journal-Env": environment, **headers},
        )

    def is_stack_checked_last(self) -> bool:
        return self.stack_checked_at == len(self.path)

    def scoped_session(self) -> str:
        return self.session_of(self.agents.subject)

    def session_of(self, agent: StoryAgent) -> str:
        if agent.session:
            return agent.session
        return {AgentRole.MAIN: self.main_session, AgentRole.WORKER: lambda: self.worker_sessions.get(agent.number, worker_session(agent.number)), AgentRole.SUBAGENT: self.subagent_scope_session, AgentRole.REVIEWER: lambda: self.checker_session(Reviewers, agent.number), AgentRole.VERIFIER: lambda: self.checker_session(Verifiers, agent.number)}[agent.role]()

    def subagent_scope_session(self) -> str:
        return ResearcherSession.joined(self.main_session(), self.agents.subagent.agent_id)

    def hook_session_of(self, agent: StoryAgent) -> str:
        return self.main_session() if agent.role == AgentRole.SUBAGENT else self.session_of(agent)

    def hook_fields_of(self, agent: StoryAgent) -> dict:
        return {"agent_id": agent.agent_id} if agent.role == AgentRole.SUBAGENT else {}

    def main_session(self) -> str:
        return self.main_session_id

    def simulated_seats(self):
        return self.app.container.get(SeatRuntime).execute.__self__

    def settle(self) -> None:
        self.app.container.get(ListenerQueue).drain()
        if self.openrig is not None and WorkerRunner.start is self.app.original_worker_start:
            self.settle_seat_jobs()
        self.app.container.get(ListenerQueue).drain()

    def settle_seat_jobs(self) -> None:
        runner = self.app.container.get(WorkerRunner)
        deadline = time.monotonic() + 5
        while True:
            pending = []
            ready = []
            with self.app.container.get(Scope).environment(1):
                for worker in runner.seat_workers():
                    if not runner.seats.applies(worker):
                        continue
                    task = runner.seats.job_task(worker)
                    if task is None:
                        continue
                    if not worker.session or worker.began < worker.job_start_time():
                        pending.append(worker.id)
                    else:
                        ready.append((worker, task))
            for worker, task in ready:
                self.role_job_prompt(StoryAgent(AgentRole.WORKER, worker.id), worker.brief,
                                     owned_task_line(worker.id, task.id))
            if not pending:
                return
            self.app.container.get(ListenerQueue).drain()
            if time.monotonic() >= deadline:
                raise AssertionError(f"Role seats did not start their current jobs: {pending}")
            time.sleep(0.01)

    def drain_seat_runner(self) -> None:
        runtime = self.app.container.get(SeatRuntime)
        simulated = isinstance(getattr(runtime.execute, "__self__", None), SimulatedSeats)
        while True:
            self.app.container.get(ListenerQueue).drain()
            if simulated:
                self.stop_simulated_seat_jobs()
            threads = self.seat_runner_threads()
            if not threads:
                return
            self.join_seat_runner_threads(threads)

    def stop_simulated_seat_jobs(self) -> None:
        runner = self.app.container.get(WorkerRunner)
        with runner.seats._guard:
            active = tuple(runner.seats._active)
        for worker_id in active:
            matches = runner.workers.global_matching(id=worker_id)
            if not matches:
                continue
            worker = matches[0]
            with self.app.container.get(Scope).environment(worker.environment_id):
                worker = runner.workers.find(worker.row_id)
                if not runner.seats.applies(worker):
                    continue
                if worker.state in (WorkerState.DISPATCHED, WorkerState.READY):
                    runner.recorded_end(worker, Actor.system())
                runner.seats.stop(worker, "the story restores its fixture")

    def clear_seat_runner(self) -> None:
        seats = self.app.container.get(WorkerRunner).seats
        with seats._guard:
            seats._active.clear()
            seats._active_jobs.clear()
            seats._finishing.clear()

    @staticmethod
    def seat_runner_threads() -> tuple[threading.Thread, ...]:
        return tuple(thread for thread in threading.enumerate()
                     if thread.name.startswith(("seat-worker-", "seat-recovery-")))

    @staticmethod
    def join_seat_runner_threads(threads: tuple[threading.Thread, ...]) -> None:
        for thread in threads:
            thread.join(5)
            assert not thread.is_alive(), f"seat runner thread {thread.name} did not finish before the fixture was restored"

    def openrig_starts(self, rig: str) -> StepResult:
        self.configure_simulated_openrig()
        runtime = self.app.container.get(SeatRuntime)
        runtime.start_rig(runtime.spec_folder(rig) / "rig.yaml")
        return self.observed(f"OpenRig starts rig {rig}", None, None)

    def configure_simulated_openrig(self) -> SimulatedSeats:
        self.openrig = SimulatedSeats()
        runtime = self.app.container.get(SeatRuntime)
        self.monkeypatch.setattr(runtime, "execute", self.openrig.execute)
        self.monkeypatch.setattr(runtime, "health_request", self.openrig.health_request, raising=False)
        return self.openrig

    def replace_main_session(self, session: str, provider: str, environment: str = "main") -> None:
        self.main_session_id, self.agent = session, Caller.agent("main", session, provider)
        self.session_environments[session] = environment

    def headers_of(self, agent: StoryAgent) -> dict:
        return {AgentRole.MAIN: dict, AgentRole.WORKER: lambda: {"X-Journal-Actor": f"worker:{agent.number}"}, AgentRole.SUBAGENT: dict, AgentRole.REVIEWER: lambda: self.checker_headers(f"reviewer:{agent.number}"), AgentRole.VERIFIER: lambda: self.checker_headers(f"verifier:{agent.number}")}[agent.role]()

    def shell_variables_of(self, agent: StoryAgent) -> dict[str, str]:
        variables = {"JOURNAL_ENV": "main", "JOURNAL_SESSION": self.session_of(agent), AGENT_SHELL: "1"}
        return {AgentRole.MAIN: lambda: variables, AgentRole.WORKER: lambda: {**variables, ACTOR: f"worker:{agent.number}"}, AgentRole.SUBAGENT: lambda: {**variables, "JOURNAL_SESSION": self.main_session()}}[agent.role]()

    def caller_of(self, agent: StoryAgent) -> Caller:
        return {AgentRole.MAIN: lambda: self.agent, AgentRole.WORKER: lambda: Caller.worker("main", agent.number, self.session_of(agent), self.provider), AgentRole.SUBAGENT: lambda: self.agent.subagent_caller(self.subagent_scope_session()), AgentRole.REVIEWER: lambda: Caller.reviewer("main", agent.number, self.session_of(agent), self.provider), AgentRole.VERIFIER: lambda: Caller.verifier("main", agent.number, self.session_of(agent), self.provider)}[agent.role]()

    def checker_session(self, rows: type, number: int) -> str:
        with self.app.container.get(Scope).environment(1):
            return self.app.container.get(rows).find(number).session

    def checker_headers(self, stamp: str) -> dict:
        return {ACTOR_HEADER: stamp, ACTOR_TOKEN_HEADER: self.helper_token(stamp)}

    def helper_token(self, stamp: str) -> str:
        kind, _, number = stamp.partition(":")
        repository = {"reviewer": Reviewers, "verifier": Verifiers}[kind]
        with self.app.container.get(Scope).environment(1):
            token_hash = self.app.container.get(repository).find(int(number)).token_hash
        with self.app.helper_launches_ready:
            found = self.app.helper_launches_ready.wait_for(
                lambda: bool(self.helper_launch_token(stamp, token_hash)),
                timeout=5,
            )
            if not found:
                raise AssertionError(f"the current run of {stamp} did not reach the story")
            return self.helper_launch_token(stamp, token_hash)

    def helper_launch_token(self, stamp: str, token_hash: str) -> str:
        return next(
            (launch[ACTOR_TOKEN] for launch in reversed(self.app.helper_launches)
             if launch.get(ACTOR) == stamp and AgentToken.is_proof(launch.get(ACTOR_TOKEN), token_hash)),
            "",
        )

    def record_command(self, action: str, outcome: Outcome, environment: str = "main") -> StepResult:
        return self.observed(action, None, outcome, environment)

    def unread_settings(self) -> list[str]:
        return [key for key, position in self.set_positions.items() if not self.reads.is_read(key, position)]

    def observed(self, action: str, verdict: HookVerdict | None, outcome: Outcome | None, environment: str = "main") -> StepResult:
        self.said, steps = self.log.unread_entries(environment)
        self.line_keys |= {line.key for line in self.said}
        self.verdict, self.command = verdict, outcome
        self.path += [action, *steps] if action else list(steps)
        self.last_step = StepResult(self, self.said, verdict, outcome, self.shell_text, self.shell_exit, self.viewer_status, self.viewer_answer)
        return self.last_step
