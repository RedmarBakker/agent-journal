from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.started_solo_plan_branch import PLAN_AGENT_SESSION, StartedSoloPlanBranch
from tests.stories.fixtures.state_fixture import StateFixture


class FinishedSoloPlanWithBranch(StateFixture):
    """A finished solo plan has a committed change on the Plan agent's worktree branch."""

    parent = StartedSoloPlanBranch
    stack = (CoordinatingPlans,)

    def steps(self, story) -> None:
        environment = f"plan-{self.plans.first}"
        story.agent_in_runs(story.agents.main, environment, PLAN_AGENT_SESSION, f"task complete {self.tasks.first} --how done")
        story.agent_in_runs(story.agents.main, environment, PLAN_AGENT_SESSION, f"task complete {self.tasks.second} --how done")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.FINISHED)
        story.last_step.expect_agent_told(story.agents.main, PlansNudges.PLAN_MERGE_READY, n=self.plans.first)
        story.expect_stack(story.agents.main, CoordinatingPlans)
