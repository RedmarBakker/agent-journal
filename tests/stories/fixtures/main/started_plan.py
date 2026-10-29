from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class StartedPlan(StateFixture):
    """The agent at work started the approved plan, so its first task is in hand and its second waits: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready, FollowingPlan)

    parent = PlanApproved

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.STARTED)
        story.expect_stack(story.agents.main, Ready, FollowingPlan)
