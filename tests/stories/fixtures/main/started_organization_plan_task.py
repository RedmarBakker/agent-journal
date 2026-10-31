from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.paused_organization_plan_task import PausedOrganizationPlanTask


class StartedOrganizationPlanTask(PausedOrganizationPlanTask):
    """A started organization plan has its first task open and its second task blocked."""

    parent = PausedOrganizationPlanTask

    def steps(self, story) -> None:
        story.user_starts_plan(self.plans.first).expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, delegated=False)
        story.expect_task(self.tasks.second, state=TaskState.BLOCKED, delegated=False)
