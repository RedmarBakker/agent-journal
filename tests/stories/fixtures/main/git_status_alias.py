from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class GitStatusAlias(StateFixture):
    """The agent at work added the alias gt for the line git status: start.alias."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.alias = "gt"
        story.agent_runs(f"alias add {self.alias} 'git status'")

    def expected(self, story) -> None:
        story.expect_command_passed()
        story.expect_stack(Ready)
