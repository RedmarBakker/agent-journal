from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class ErrorsReader(StateFixture):
    """The agent at work added the reader errors for lines holding error, and ran a command whose kept output holds one: story.readers.first and story.outputs.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.readers.first = "errors"
        story.agent_runs(story.agents.main, f"reader add {self.readers.first} --pattern 'error' --about 'the error lines'")
        self.outputs.first = story.agent_runs_a_command(story.agents.main, "printf 'an error\\nfine\\n' | head -2")

    def expected(self, story) -> None:
        story.expect_new_output()
        story.expect_stack(story.agents.main, Ready)
