from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.three_approved_plans import ThreeApprovedPlans
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorStartedPlans(StateFixture):
    """In orchestrator mode the agent started the first two of the three approved plans, the third still approved: story.plans.first, story.plans.second and story.plans.third."""

    stack = (Orchestrating, OrchestratingPlan)

    parent = ThreeApprovedPlans

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}")
        story.agent_runs(story.agents.main, f"plan start {self.plans.second}")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_plan(self.plans.second, state=PlanState.STARTED)
