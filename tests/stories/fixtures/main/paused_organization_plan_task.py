from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.plans_options import PlansOptions
from journal.features.workers.workers_options import ORCHESTRATOR_MODE, WorkersOptions
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.organization_hub_plan import OrganizationHubPlan


class PausedOrganizationPlanTask(OrganizationHubPlan):
    """An organization plan was paused with one task in hand and another paused for its own reason."""

    parent = OrganizationHubPlan
    task_domain = "alpha"

    def steps(self, story) -> None:
        super().steps(story)
        self.tasks.second = story.user_adds_plan_task(self.plans.first, "second")
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} organization").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        story.agent_runs(story.agents.main, f"task start {self.tasks.first}").expect_command_passed()
        story.user_pauses_plan(self.plans.first).expect_viewer_passed()
        story.agent_runs(story.agents.main, f"task start {self.tasks.second}").expect_command_passed()
        story.user_blocks_task(self.tasks.second, "wait for separate input").expect_viewer_passed()
        story.user_pauses_plan(self.plans.first).expect_viewer_passed()
        story.user_sets(PlansOptions.PLAN_AGENTS, True).expect_viewer_passed()
        story.user_sets(WorkersOptions.MODE, ORCHESTRATOR_MODE).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.PAUSED)
        story.expect_task(self.tasks.first, state=TaskState.BLOCKED, delegated=False)
        story.expect_task(self.tasks.second, state=TaskState.BLOCKED, delegated=False)
        story.expect_organization_domains("alpha", "beta")
        story.expect_stack(story.agents.main, CoordinatingPlans)
