from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class ReportSizedPlanWithDependentTask(StateFixture):
    """The report-sized plan has a deploy task waiting on its existing task."""

    parent = ReportSizedPlan

    def steps(self, story) -> None:
        task = story.agent_runs(
            story.agents.main,
            f"plan add {self.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development "
            f"--size 5 --phase 1 --after {self.tasks.first} --reason 'deployment uses the built artifact'",
        )
        task.expect_command_passed()
        self.tasks.second = story.created_number("task")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, size=5)
