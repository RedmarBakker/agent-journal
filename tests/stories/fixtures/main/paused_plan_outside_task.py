from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.choosing_plan_return import ChoosingPlanReturn
from journal.features.tasks.states.ready import Ready
from journal.features.tasks.states.working import Working
from tests.stories.fixtures.main.agent_paused_plan import AgentPausedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PausedPlanOutsideTask(StateFixture):
    """With the plan it paused, the agent took up a task outside it, and at its first write the journal asks whether it returns to the plan once that task is done: start.fix."""

    stack = (Ready, Working, ChoosingPlanReturn)

    parent = AgentPausedPlan

    def steps(self, story) -> None:
        self.fix = story.agent_takes_a_task(story.agents.subject, "the broken build")
        story.agent_writes(story.agents.subject, "build.py")

    def expected(self, story) -> None:
        story.expect_refused(story.agents.subject, PlansNudges.PLAN_RETURN_QUESTION, n=self.plan, task=self.fix)
        story.expect_stack(story.agents.subject, Ready, Working, ChoosingPlanReturn)
