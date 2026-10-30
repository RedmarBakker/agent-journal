from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture

# the command of a test run in the background, the failure and summary it prints at its end and the status it ends with
TEST_RUN = "./scripts/run-tests.sh"
TEST_RUN_LINES = ("FAILED tests/a.py::test_b", "1 failed, 3 passed")
TEST_RUN_STATUS = 1


class SummaryReader(StateFixture):
    """The agent at work has a test run in the background that has printed nothing yet, and added a reader of a test run's summary: story.outputs.first and story.readers.first."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.outputs.first = story.agent_has_a_background_run_printing(story.agents.main, TEST_RUN)
        self.readers.first = "summary-lines"
        story.agent_runs(story.agents.main, f"reader add {self.readers.first} --pattern '[0-9]+ (passed|failed)' --about 'the summary of a test run'")

    def expected(self, story) -> None:
        story.last_step.expect_command_passed()
