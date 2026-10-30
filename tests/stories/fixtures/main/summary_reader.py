from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

# the command of a test run in the background, the failure and summary it prints and the status it ends with
TEST_RUN = "./scripts/run-tests.sh"
TEST_RUN_LINES = ("FAILED tests/a.py::test_b", "1 failed, 3 passed")
TEST_RUN_STATUS = 1


class SummaryReader(StateFixture):
    """The agent at work added a reader of a test run's summary: story.readers.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.readers.first = "summary-lines"
        story.agent_runs(story.agents.main, f"reader add {self.readers.first} --pattern '[0-9]+ (passed|failed)' --about 'the summary of a test run'")

    def expected(self, story) -> None:
        story.last_step.expect_command_passed()
