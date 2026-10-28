from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.plans.states.naming_test_commands import NamingTestCommands
from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class TestCommandWait(StateFixture):
    """The project names no test commands, and the agent started the approved plan, so the plan waits for them: start.plan, start.first_task and start.second_task."""

    stack = (Ready, FollowingPlan, NamingTestCommands)

    parent = PlanApproved

    settings = ((PlansOptions.TEST_COMMANDS, ""),)

    def steps(self, story) -> None:
        story.agent_runs(f"plan start {self.plan}")

    def expected(self, story) -> None:
        story.expect_stack(Ready, FollowingPlan, NamingTestCommands)
