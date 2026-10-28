from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.draft_plan import DraftPlan


class TwoPhasePlan(StateFixture):
    """The agent built the drafted plan into two phases with one task each, the first ending at a checkpoint, the user approved it in the viewer, and the agent started it: start.plan, start.first_phase_task in hand and start.second_phase_task waiting."""

    stack = (Ready, FollowingPlan)

    parent = DraftPlan

    def steps(self, story) -> None:
        story.agent_runs("sequence follow")
        story.agent_runs("sequence abandon --why 'the plan is built step by step right here' --sure")
        story.agent_runs(f"plan phase {self.plan} 'Layout' --when 'the layout stands' --checkpoint")
        story.agent_runs(f"plan phase {self.plan} 'Content' --when 'the pages hold their words'")
        self.first_phase_task = story.agent_adds_plan_task(self.plan, "the grid")
        self.second_phase_task = story.agent_adds_plan_task(self.plan, "the about page")
        story.agent_runs(f"plan todos {self.plan} 1 {self.first_phase_task}")
        story.agent_runs(f"plan todos {self.plan} 2 {self.second_phase_task}")
        story.agent_runs(f"plan ready {self.plan}")
        story.user_approves_plan(self.plan)
        story.agent_runs(f"plan start {self.plan}")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.STARTED)
        story.expect_task(self.first_phase_task, state=TaskState.STARTED)
        story.expect_stack(Ready, FollowingPlan)
