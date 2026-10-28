from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class ErrorsReader(StateFixture):
    """The agent at work added the reader errors for lines holding error, and ran a command whose kept output holds one: start.reader and start.output."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.reader = "errors"
        story.agent_runs(f"reader add {self.reader} --pattern 'error' --about 'the error lines'")
        self.output = story.agent_runs_a_command("printf 'an error\\nfine\\n' | head -2")

    def expected(self, story) -> None:
        story.expect_new_output()
        story.expect_stack(Ready)
