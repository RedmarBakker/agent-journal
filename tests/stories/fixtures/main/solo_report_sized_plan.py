from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class SoloReportSizedPlan(StateFixture):
    """The builder made a sized solo plan without an organization folder."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        story.user_sets(EstimatesOptions.MODE, "report").expect_viewer_passed()
        self.plans.first = story.user_creates_plan("the work", "finish the independent changes")
        story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Delivery' --when 'the changes are complete'").expect_command_passed()
        task = story.agent_runs(story.agents.main, f"plan add {self.plans.first} 'first change' --brief 'the first change is complete' --size 3 --phase 1")
        task.expect_command_passed()
        self.tasks.first = story.created_number("task")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT, mode=PlanMode.SOLO)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, size=3)
        story.expect_stack(story.agents.main, Ready)
