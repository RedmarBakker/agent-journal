from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.states.following_plan import FollowingPlan
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.started_solo_plan_branch import PLAN_AGENT_SESSION, StartedSoloPlanBranch


class SoloPlanWithFirstTaskComplete(StartedSoloPlanBranch):
    """A solo Plan agent has completed its first task while its branch remains open."""

    parent = StartedSoloPlanBranch

    def steps(self, story) -> None:
        result = story.agent_in_runs(story.agents.subject, f"plan-{self.plans.first}", PLAN_AGENT_SESSION, f"task complete {self.tasks.first} --how done")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.subject, CoordinatingPlans, FollowingPlan)
