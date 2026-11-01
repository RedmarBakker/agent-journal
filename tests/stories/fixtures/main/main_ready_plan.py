from journal.features.tasks.states.ready import Ready
from tests.stories.fixtures.main.agent_ready_plan import AgentReadyPlan
from tests.stories.fixtures.state_fixture import StateFixture


class MainReadyPlan(StateFixture):
    """The main agent marked its plan ready for approval: story.plans.first and story.tasks.slab."""

    stack = (Ready,)

    parent = AgentReadyPlan

    def steps(self, story) -> None:
        story.agent_reads(story.agents.main)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
