from journal.features.tasks.states.ready import Ready
from journal.features.tasks.tasks_nudges import TasksNudges
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class PassedWaitCheck(StateFixture):
    """The agent's wait ended when its build check passed."""

    stack = (Ready,)

    parent = WorkingAgent

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, "await 'the nightly build' --until 'exit 0'")
        check = story.newest("checks")
        self.passed_check = check
        result = story.agent_reads(story.agents.main)
        result.expect_agent_told(story.agents.main, TasksNudges.WAIT_LIFTED, what="the nightly build", n=check)
        result = story.agent_runs(story.agents.main, f"check run {check}")
        result.expect_agent_told_count(story.agents.main, TasksNudges.WAIT_CHECK_PASSED, 1, what="the nightly build", lines="the check passed")

    def expected(self, story) -> None:
        story.expect_row_absent("checks", self.passed_check)
        story.expect_stack(story.agents.main, Ready)
