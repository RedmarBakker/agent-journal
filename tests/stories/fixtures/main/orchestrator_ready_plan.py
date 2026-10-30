from journal.features.workers.states.orchestrating import Orchestrating
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from tests.stories.fixtures.main.agent_ready_plan import AgentReadyPlan
from tests.stories.fixtures.state_fixture import StateFixture


class OrchestratorReadyPlan(StateFixture):
    """In orchestrator mode, the agent's plan is ready for approval: story.plans.first and story.tasks.slab."""

    stack = (Orchestrating,)

    parent = AgentReadyPlan

    settings = ((WorkersOptions.MODE, ORCHESTRATOR_MODE),)

    def steps(self, story) -> None:
        story.agent_reads(story.agents.main)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Orchestrating)
