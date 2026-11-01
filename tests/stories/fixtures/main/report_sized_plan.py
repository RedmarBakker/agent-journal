from journal.features.estimates.estimates_options import EstimatesOptions
from journal.features.tasks.states.ready import Ready
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.enforced_draft_plan import EnforcedDraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class ReportSizedPlan(StateFixture):
    """The owner configured report estimates and the builder added a sized task to an explicitly solo plan."""

    stack = (Ready,)
    parent = EnforcedDraftPlan

    def steps(self, story) -> None:
        story.user_sets(EstimatesOptions.MODE, "report").expect_viewer_passed()
        story.agent_runs(story.agents.main, f"plan mode {self.plans.first} solo").expect_command_passed()
        phase = story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Delivery' --when 'production accepts the revision'")
        phase.expect_command_passed()
        task = story.agent_runs(story.agents.main, f"plan add {self.plans.first} 'release' --brief 'the release is deployed' --domain development --size 3 --phase 1")
        task.expect_command_passed()
        self.tasks.first = story.created_number("task")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT, mode=PlanMode.SOLO)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, size=3)
        story.expect_stack(story.agents.main, Ready)
