from journal.features.tasks.states.ready import Ready
from journal.support.foreground_option import FOREGROUND_OPTION
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

# the command of a test run that outlasts the foreground time, then prints a failure and its summary
TEST_RUN = "sh -c 'sleep {seconds}; echo FAILED tests/a.py::test_b; echo 1 failed, 3 passed; exit 1'"


class SummaryReader(StateFixture):
    """The agent at work added a reader of a test run's summary, with commands going to the background after a second: story.readers.first."""

    stack = (Ready,)

    parent = WorkingAgent

    settings = ((FOREGROUND_OPTION, 1),)

    def steps(self, story) -> None:
        self.readers.first = "summary-lines"
        story.agent_runs(story.agents.main, f"reader add {self.readers.first} --pattern '[0-9]+ (passed|failed)' --about 'the summary of a test run'")

    def expected(self, story) -> None:
        story.expect_command_passed()
