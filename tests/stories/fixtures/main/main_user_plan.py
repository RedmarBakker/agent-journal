from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class MainUserPlan(StateFixture):
    """The main agent marked ready the plan the user drafted: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready,)

    parent = UserDraftedPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
