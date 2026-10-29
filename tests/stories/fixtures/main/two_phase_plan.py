from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan


class TwoPhasePlan(StateFixture):
    """The agent built the drafted plan into two phases with one task each, the first ending at a checkpoint, the user approved it in the viewer, and the agent started it: story.plans.first, story.tasks.first_phase in hand and story.tasks.second_phase waiting."""

    stack = (Ready, FollowingPlan)

    parent = ManualDraftPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Layout' --when 'the layout stands' --checkpoint")
        story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Content' --when 'the pages hold their words'")
        self.tasks.first_phase = story.agent_adds_plan_task(story.agents.main, self.plans.first, "the grid")
        self.tasks.second_phase = story.agent_adds_plan_task(story.agents.main, self.plans.first, "the about page")
        story.agent_runs(story.agents.main, f"plan todos {self.plans.first} 1 {self.tasks.first_phase}")
        story.agent_runs(story.agents.main, f"plan todos {self.plans.first} 2 {self.tasks.second_phase}")
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}")
        story.user_approves_plan(self.plans.first)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.first_phase, state=TaskState.STARTED)
        story.expect_stack(story.agents.main, Ready, FollowingPlan)
