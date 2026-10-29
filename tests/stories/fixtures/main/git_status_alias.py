from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class GitStatusAlias(StateFixture):
    """The agent at work added the alias gt for the line git status: story.aliases.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.aliases.first = "gt"
        story.agent_runs(story.agents.main, f"alias add {self.aliases.first} 'git status'")

    def expected(self, story) -> None:
        story.expect_command_passed()
        story.expect_stack(story.agents.main, Ready)
