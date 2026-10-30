from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorUserPlan(StateFixture):
    """In orchestrator mode, the agent marked ready the plan the user drafted: story.plans.first, story.tasks.first and story.tasks.second."""

    stack = (Orchestrating,)

    parent = UserDraftedPlan

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Orchestrating)
