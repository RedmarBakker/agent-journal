from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.mid_phase_test_plan import MidPhaseTestPlan
from tests.stories.fixtures.state_fixture import StateFixture

PHASE_TESTS = "python3 -m pytest -q tests/test_pages.py"


class PhaseWaitingForTests(StateFixture):
    """Under tests at each phase end the agent finished the phase's last two tasks, each waiting in testing as the next started, then ran the phase's tests and named that run their test: story.tasks.second, story.tasks.third and story.outputs.first."""

    stack = (Ready, FollowingPlan)

    parent = MidPhaseTestPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"task complete {self.tasks.second} --how 'the about page stands'")
        story.expect_task(self.tasks.second, state=TaskState.TESTING)
        story.expect_task(self.tasks.third, state=TaskState.STARTED)
        story.agent_runs(story.agents.main, f"task complete {self.tasks.third} --how 'the footer stands'")
        self.outputs.first = story.agent_has_a_background_run_printing(story.agents.main, PHASE_TESTS, "3 collected")
        story.agent_runs(story.agents.main, f"output test {self.outputs.first}")

    def expected(self, story) -> None:
        story.expect_task(self.tasks.second, state=TaskState.TESTING)
        story.expect_task(self.tasks.third, state=TaskState.TESTING)
