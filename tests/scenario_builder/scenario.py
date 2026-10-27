from journal.console.support.outcome import Outcome
from journal.support.caller import Caller
from tests.in_process import posted
from tests.replay import TOOLS
from tests.scenario_builder.agent_steps import AgentSteps
from tests.scenario_builder.hook_verdict import HookVerdict
from tests.scenario_builder.nudge_log import NudgeLog
from tests.scenario_builder.scenario_checks import ScenarioChecks
from tests.scenario_builder.user_steps import UserSteps
from tests.state_fixtures.state_fixture import StateFixture


class Scenario(AgentSteps, UserSteps, ScenarioChecks):
    """One story played against a journal in-process for one provider: each step plays a real hook or command and keeps what it brought, the lines said, the hook's verdict and the command's result, for the checks after it."""

    def __init__(self, app, provider: str) -> None:
        self.app, self.provider, self.tools = app, provider, TOOLS[provider]
        self.agent = Caller.agent("main", "s1", provider)
        self.log = NudgeLog(app)
        self.said, self.verdict, self.command = (), None, None

    def starts_from(self, fixture: type[StateFixture]) -> None:
        fixture().seed(self)
        self.observed(None, None)

    def posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": type_name, "session_id": "s1", **body}, {"X-Journal-Env": "main"})

    def ran(self, result: Outcome) -> None:
        self.observed(None, result)

    def observed(self, verdict: HookVerdict | None, result: Outcome | None) -> None:
        self.said, self.verdict, self.command = self.log.since_last(), verdict, result
