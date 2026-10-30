from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class AgentReadyPlan(StateFixture):
    """The agent built its draft into one phase with one task and marked it ready for the user: story.plans.first and story.tasks.slab."""

    stack = (Ready,)

    parent = ManualDraftPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Lay the floor' --when 'the slab is poured'")
        self.tasks.slab = story.agent_creates_task(story.agents.main, "pour the slab")
        story.agent_runs(story.agents.main, f"plan todos {self.plans.first} 1 {self.tasks.slab}")
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.READY)
