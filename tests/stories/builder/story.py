from journal.console.support.outcome import Outcome
from journal.support.agent_role import AgentRole
from journal.support.caller import ACTOR, AGENT_SHELL, Caller
from journal.support.researcher_session import ResearcherSession
from journal.features.workers.workers_options import BUILDER_MODE
from tests.in_process import posted
from tests.replay import TOOLS
from tests.stories.builder.agent_steps import AgentSteps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.developer_steps import DeveloperSteps
from tests.stories.builder.hook_verdict import HookVerdict
from tests.stories.builder.journal_log import JournalLog
from tests.stories.builder.time_steps import TimeSteps
from tests.stories.builder.main_session import MAIN_SESSION
from tests.stories.builder.worker_steps import WorkerSteps, worker_session
from tests.stories.builder.setting_reads import SettingReads
from tests.stories.builder.story_checks import StoryChecks
from tests.stories.builder.user_steps import UserSteps
from tests.stories.fixtures.state_fixture import StateFixture


class Story(AgentSteps, UserSteps, WorkerSteps, TimeSteps, DeveloperSteps, StoryChecks):
    """One story played against a journal in-process for one provider: each step plays a real hook, command or viewer request and keeps what it brought, the lines the journal gave, the hook's verdict and the command's outcome, for the checks after it, and adds its action and what the journal did to the story's path, which counts from the fixture's state on; the settings it sets are noted with the place they were set, to ask whether the journal read them after, and its start is the fixture it began from, whose rows the story reads as start.<row>, asked at the end whether the story used them all."""

    def __init__(self, app, program: type, reads: SettingReads, copies: FixtureCopies) -> None:
        self.copies = copies
        self.app, self.program, self.provider, self.tools, self.reads = app, program, program.name, TOOLS[program.name], reads
        self.set_positions: dict[str, int] = {}
        self.main_session_id = MAIN_SESSION
        self.agent = Caller.agent("main", MAIN_SESSION, program.name)
        self.log = JournalLog(app)
        self.said, self.verdict, self.command = (), None, None
        self.path: list[str] = []
        self.line_keys: set[str] = set()
        self.start = StateFixture()
        self.scope = AgentRole.MAIN
        self.stack_checked_at = -1
        self.shell_text, self.shell_exit, self.shell_outputs = "", 0, 0
        self.runner_threads: list = []
        self.mode = BUILDER_MODE

    def reach(self, fixture: type[StateFixture]) -> None:
        self.start = self.copies.reached(self, fixture)
        self.observed("", None, None)
        self.path = [f"starts from {fixture.__name__}"]
        self.stack_checked_at = -1
        self.set_positions = {key: self.reads.position() for key in self.copies.settings_left.get((fixture, self.provider), ())}

    def posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return self.session_posted_hook(self.scoped_hook_session(), self.scoped_headers(), type_name, {**self.scoped_hook_fields(), **body})

    def main_posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return self.session_posted_hook(self.main_session_id, {}, type_name, body)

    def session_posted_hook(self, session: str, headers: dict, type_name: str, body: dict) -> tuple[int, object]:
        return posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": type_name, "session_id": session, **body}, {"X-Journal-Env": "main", **headers})

    def is_stack_checked_last(self) -> bool:
        return self.stack_checked_at == len(self.path)

    def scoped_session(self) -> str:
        return {AgentRole.MAIN: self.main_session, AgentRole.WORKER: self.worker_scope_session, AgentRole.SUBAGENT: self.subagent_scope_session}[self.scope]()

    def subagent_scope_session(self) -> str:
        return ResearcherSession.joined(self.main_session(), self.start.subagent)

    def scoped_hook_session(self) -> str:
        return self.main_session() if self.scope == AgentRole.SUBAGENT else self.scoped_session()

    def scoped_hook_fields(self) -> dict:
        return {"agent_id": self.start.subagent} if self.scope == AgentRole.SUBAGENT else {}

    def main_session(self) -> str:
        return self.main_session_id

    def replace_main_session(self, session: str, provider: str) -> None:
        self.main_session_id, self.agent = session, Caller.agent("main", session, provider)

    def worker_scope_session(self) -> str:
        return worker_session(self.start.worker)

    def scoped_headers(self) -> dict:
        return {AgentRole.MAIN: dict, AgentRole.WORKER: self.worker_scope_headers, AgentRole.SUBAGENT: dict}[self.scope]()

    def worker_scope_headers(self) -> dict:
        return {"X-Journal-Actor": f"worker:{self.start.worker}"}

    def scoped_shell_variables(self) -> dict[str, str]:
        variables = {"JOURNAL_ENV": "main", "JOURNAL_SESSION": self.scoped_session(), AGENT_SHELL: "1"}
        return {AgentRole.MAIN: lambda: variables, AgentRole.WORKER: lambda: {**variables, ACTOR: f"worker:{self.start.worker}"}, AgentRole.SUBAGENT: lambda: {**variables, "JOURNAL_SESSION": self.main_session()}}[self.scope]()

    def scoped_caller(self) -> Caller:
        return {AgentRole.MAIN: lambda: self.agent, AgentRole.WORKER: self.worker_scope_caller, AgentRole.SUBAGENT: lambda: self.agent.subagent_caller(self.subagent_scope_session())}[self.scope]()

    def worker_scope_caller(self) -> Caller:
        return Caller.worker("main", self.start.worker, worker_session(self.start.worker), self.provider)

    def record_command(self, action: str, outcome: Outcome) -> None:
        self.observed(action, None, outcome)

    def unread_settings(self) -> list[str]:
        return [key for key, position in self.set_positions.items() if not self.reads.is_read(key, position)]

    def observed(self, action: str, verdict: HookVerdict | None, outcome: Outcome | None) -> None:
        self.said, steps = self.log.new_entries()
        self.line_keys |= {line.key for line in self.said}
        self.verdict, self.command = verdict, outcome
        self.path += [action, *steps] if action else list(steps)
