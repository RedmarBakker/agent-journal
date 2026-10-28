from journal.console.support.outcome import Outcome
from journal.support.caller import Caller
from tests.in_process import posted
from tests.replay import TOOLS
from tests.scenarios.builder.agent_actions import AgentActions
from tests.scenarios.builder.agent_steps import AgentSteps
from tests.scenarios.builder.hook_verdict import HookVerdict
from tests.scenarios.builder.journal_log import JournalLog
from tests.scenarios.builder.session_steps import SessionSteps
from tests.scenarios.builder.shell_steps import ShellSteps
from tests.scenarios.builder.time_steps import TimeSteps
from tests.scenarios.builder.worker_steps import WorkerSteps
from tests.scenarios.builder.setting_reads import SettingReads
from tests.scenarios.builder.step_checks import StepChecks
from tests.scenarios.builder.story_sugar import StorySugar
from tests.scenarios.builder.user_steps import UserSteps
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class Scenario(AgentSteps, AgentActions, UserSteps, WorkerSteps, SessionSteps, ShellSteps, TimeSteps, StepChecks, StorySugar):
    """One story played against a journal in-process for one provider: each step plays a real hook, command or viewer request and keeps what it brought, the lines said, the hook's verdict and the command's result, for the checks after it, and adds its action and what the journal did to the story's path, which counts from the fixture's state on; the settings it sets are noted with the place they were set, to ask whether the journal read them after."""

    def __init__(self, app, provider: str, reads: SettingReads) -> None:
        self.app, self.provider, self.tools, self.reads = app, provider, TOOLS[provider], reads
        self.set_positions: dict[str, int] = {}
        self.agent = Caller.agent("main", "s1", provider)
        self.log = JournalLog(app)
        self.said, self.verdict, self.command = (), None, None
        self.path: list[str] = []
        self.said_keys: set[str] = set()

    def starts_from(self, fixture: type[StateFixture]) -> None:
        fixture().seed(self)
        self.observed("", None, None)
        self.path = []

    def posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": type_name, "session_id": "s1", **body}, {"X-Journal-Env": "main"})

    def ran(self, action: str, result: Outcome) -> None:
        self.observed(action, None, result)

    def settings_never_read(self) -> list[str]:
        return [key for key, position in self.set_positions.items() if not self.reads.is_read_since(key, position)]

    def observed(self, action: str, verdict: HookVerdict | None, result: Outcome | None) -> None:
        self.said, steps = self.log.since_last()
        self.said_keys |= {said.key for said in self.said}
        self.verdict, self.command = verdict, result
        self.path += [action, *steps] if action else list(steps)
