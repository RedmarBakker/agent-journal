from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.naming_test_commands import NamingTestCommands
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class TestCommandWait(StateFixture):
    """The project names no test commands, and the agent started the approved plan, so the plan waits for them: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Ready, FollowingPlan, NamingTestCommands)

    parent = PlanApproved

    settings = ((PlansOptions.TEST_COMMANDS, ""),)

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, FollowingPlan, NamingTestCommands)
