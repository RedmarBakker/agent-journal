from journal.console.support.outcome import Outcome
from journal.support.caller import Caller
from tests.in_process import posted
from tests.replay import TOOLS
from tests.scenarios.builder.agent_actions import AgentActions
from tests.scenarios.builder.agent_steps import AgentSteps
from tests.scenarios.builder.hook_verdict import HookVerdict
from tests.scenarios.builder.journal_log import JournalLog
from tests.scenarios.builder.step_checks import StepChecks
from tests.scenarios.builder.story_sugar import StorySugar
from tests.scenarios.builder.user_steps import UserSteps
from tests.scenarios.state_fixtures.state_fixture import StateFixture


class Scenario(AgentSteps, AgentActions, UserSteps, StepChecks, StorySugar):
    """One story played against a journal in-process for one provider: each step plays a real hook, command or viewer request and keeps what it brought, the lines said, the hook's verdict and the command's result, for the checks after it, and adds its action and what the journal did to the story's path, which counts from the fixture's state on."""

    def __init__(self, app, provider: str) -> None:
        self.app, self.provider, self.tools = app, provider, TOOLS[provider]
        self.agent = Caller.agent("main", "s1", provider)
        self.log = JournalLog(app)
        self.said, self.verdict, self.command = (), None, None
        self.path: list[str] = []

    def starts_from(self, fixture: type[StateFixture]) -> None:
        fixture().seed(self)
        self.observed("", None, None)
        self.path = []

    def posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": type_name, "session_id": "s1", **body}, {"X-Journal-Env": "main"})

    def ran(self, action: str, result: Outcome) -> None:
        self.observed(action, None, result)

    def observed(self, action: str, verdict: HookVerdict | None, result: Outcome | None) -> None:
        self.said, steps = self.log.since_last()
        self.verdict, self.command = verdict, result
        self.path += [action, *steps] if action else list(steps)
