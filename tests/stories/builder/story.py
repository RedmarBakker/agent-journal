from journal.console.support.outcome import Outcome
from journal.support.caller import Caller
from tests.in_process import posted
from tests.replay import TOOLS
from tests.stories.builder.agent_steps import AgentSteps
from tests.stories.builder.fixture_copies import FixtureCopies
from tests.stories.builder.developer_steps import DeveloperSteps
from tests.stories.builder.hook_verdict import HookVerdict
from tests.stories.builder.journal_log import JournalLog
from tests.stories.builder.time_steps import TimeSteps
from tests.stories.builder.worker_steps import WorkerSteps
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
        self.agent = Caller.agent("main", "s1", program.name)
        self.log = JournalLog(app)
        self.said, self.verdict, self.command = (), None, None
        self.path: list[str] = []
        self.line_keys: set[str] = set()
        self.start = StateFixture()
        self.end_stack: list[type] | None = None

    def reach(self, fixture: type[StateFixture]) -> None:
        self.start = self.copies.reached(self, fixture)
        self.observed("", None, None)
        self.path = [f"starts from {fixture.__name__}"]
        self.set_positions = {key: self.reads.position() for key in self.copies.settings_left.get((fixture, self.provider), ())}

    def posted_hook(self, type_name: str, **body) -> tuple[int, object]:
        return self.session_posted_hook("s1", {}, type_name, body)

    def session_posted_hook(self, session: str, headers: dict, type_name: str, body: dict) -> tuple[int, object]:
        return posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": type_name, "session_id": session, **body}, {"X-Journal-Env": "main", **headers})

    def record_command(self, action: str, outcome: Outcome) -> None:
        self.observed(action, None, outcome)

    def unread_settings(self) -> list[str]:
        return [key for key, position in self.set_positions.items() if not self.reads.is_read(key, position)]

    def observed(self, action: str, verdict: HookVerdict | None, outcome: Outcome | None) -> None:
        self.said, steps = self.log.new_entries()
        self.line_keys |= {line.key for line in self.said}
        self.verdict, self.command = verdict, outcome
        self.path += [action, *steps] if action else list(steps)
