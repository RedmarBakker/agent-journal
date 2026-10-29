from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.choosing_plan_return import ChoosingPlanReturn
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.agent_paused_plan import AgentPausedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PausedPlanOutsideTask(StateFixture):
    """With the plan it paused, the agent took up a task outside it, and at its first write the journal asks whether it returns to the plan once that task is done: story.tasks.outside."""

    stack = (Ready, Working, ChoosingPlanReturn)

    parent = AgentPausedPlan

    def steps(self, story) -> None:
        self.tasks.outside = story.agent_takes_a_task(story.agents.main, "the broken build")
        story.agent_writes(story.agents.main, "build.py")

    def expected(self, story) -> None:
        story.expect_refused(story.agents.main, PlansNudges.PLAN_RETURN_QUESTION, n=self.plans.first, task=self.tasks.outside)
        story.expect_stack(story.agents.main, Ready, Working, ChoosingPlanReturn)
