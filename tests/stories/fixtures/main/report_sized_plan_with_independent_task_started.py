from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.report_sized_plan_with_dependent_task import ReportSizedPlanWithDependentTask
from tests.stories.fixtures.state_fixture import StateFixture


class ReportSizedPlanWithIndependentTaskStarted(StateFixture):
    """The report-sized plan's dependent and independent tasks are ready and its first task is started."""

    parent = ReportSizedPlanWithDependentTask
    stack = (Ready, FollowingPlan)

    def steps(self, story) -> None:
        task = story.agent_runs(
            story.agents.main,
            f"plan add {self.plans.first} 'notify' --brief 'the release notice is published' "
            "--domain development --size 2 --phase 1",
        )
        task.expect_command_passed()
        self.tasks.third = story.created_number("task")
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first, state=TaskState.STARTED)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, size=5)
        story.expect_task(self.tasks.third, state=TaskState.OPEN, size=2)
        story.expect_stack(story.agents.main, Ready, FollowingPlan)
